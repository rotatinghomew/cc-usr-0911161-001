from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from treaty_tracker.commitments.pledge import ContractError, Decision, DomainRecord, records_from_fixture, stable_hash
from treaty_tracker.ledger.evidence_log import Repository
from treaty_tracker.lifecycle.fulfillment import advance_for_outcome, decide
from treaty_tracker.disclosure.member_report import export_bundle, verify_bundle, verify_trend_bundle
from treaty_tracker.harmonization.progress_model import derive_context

from treaty_tracker.progress_signal.commitment_health import augment_context
from treaty_tracker.trends.comparable_trends import build_trend_analysis

class Application:
    def __init__(self, database: str | Path, context: Mapping[str, Any] | None = None,
                 clock: Any | None = None):
        self.repository = Repository(database, clock=clock)
        self.context = dict(context or {})

    def ingest(self, record: DomainRecord) -> DomainRecord:
        current = self.repository.get_record(record.record_id)
        if current is None:
            self.repository.save_record(record)
            return record
        if current.fingerprint == record.fingerprint:
            return current
        replacement = DomainRecord(record.record_id, record.payload, current.state,
                                   current.version + 1, record.occurred_at, record.source)
        self.repository.save_record(replacement, expected_version=current.version)
        return replacement

    def process(self, record: DomainRecord) -> tuple[DomainRecord, Decision]:
        stored = self.ingest(record)
        context = dict(self.context)
        context.update(derive_context(stored, self.repository))
        context.update(augment_context(stored, self.repository))
        decision = decide(stored, context)
        self.repository.save_decision(decision)
        advanced = advance_for_outcome(stored, decision)
        if advanced.fingerprint != stored.fingerprint:
            self.repository.save_record(advanced, expected_version=stored.version)
        return advanced, decision

    def run_fixture(self, fixture: Mapping[str, Any], output: str | Path) -> dict[str, Any]:
        records = records_from_fixture(fixture)
        fixture_hash = stable_hash(fixture)
        run_id = self.repository.begin_run(fixture_hash, len(records))
        completed = self.repository.completed_run(run_id)
        if completed is not None:
            return completed
        decisions: dict[str, Decision] = {}
        final_records: list[DomainRecord] = []
        for record in records:
            final_record, decision = self.process(record)
            final_records.append(final_record)
            decisions[record.record_id] = decision
        snapshot = self.repository.snapshot()
        if snapshot["chain_errors"]:
            raise ContractError("audit chain verification failed")
        trend_analysis = build_trend_analysis(self.repository)
        manifest = export_bundle(output, final_records, decisions, snapshot, self.repository.event_rows(),
                                 trend_analysis=trend_analysis)
        result = {"run_id": run_id, "fixture_hash": fixture_hash, "records": len(final_records),
                  "decisions": len(decisions), "manifest": manifest, "snapshot": snapshot,
                  "trend_periods": len(trend_analysis["periods"]),
                  "trend_comparisons": len(trend_analysis["comparisons"])}
        self.repository.finish_run(run_id, result)
        return result

    def inspect(self) -> dict[str, Any]:
        return {"snapshot": self.repository.snapshot(), "records": [record.__dict__ for record in self.repository.list_records()],
                "decisions": self.repository.decision_rows()}


def load_fixture(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read fixture: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("fixture root must be an object")
    return value


def run(fixture_path: str | Path, database: str | Path, output: str | Path,
        context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return Application(database, context).run_fixture(load_fixture(fixture_path), output)


def verify(database: str | Path, output: str | Path) -> dict[str, Any]:
    repository = Repository(database)
    chain_errors = repository.verify_chain()
    bundle_errors = verify_bundle(output)
    trend_errors = verify_trend_bundle(output, repository)
    return {"ok": not chain_errors and not bundle_errors and not trend_errors,
            "chain_errors": chain_errors, "bundle_errors": bundle_errors,
            "trend_errors": trend_errors, "snapshot": repository.snapshot()}
