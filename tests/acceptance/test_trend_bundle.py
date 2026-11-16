from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from treaty_tracker.commitments.pledge import stable_hash
from treaty_tracker.disclosure.member_report import verify_bundle, verify_trend_bundle
from treaty_tracker.ledger.evidence_log import Repository
from treaty_tracker.service import Application, run, verify

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "acceptance.json"
TREND_FILE = "trend-analysis.json"


class MutableClock:
    def __init__(self, stamp: str):
        self.stamp = stamp

    def __call__(self) -> str:
        return self.stamp


def monthly_fixture(rows: list[tuple[str, float, str, str]]) -> dict:
    records = []
    for record_id, progress, member, area in rows:
        records.append({"record_id": record_id, "state": "pledged", "source": "monthly-bulletin",
                        "payload": {"progress_pct": progress, "legal_readiness": 0.8, "evidence_count": 10,
                                    "commitment_area": area, "audit_findings": 1, "unresolved_gaps": 1,
                                    "beneficiary_share": 0.6, "member_code": member, "deadline_days": 180,
                                    "data_quality": 0.9, "review_score": 0.8, "public_status": "reported"}})
    return {"records": records}


class TrendBundleAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.database = self.root / "run.sqlite3"
        self.output = self.root / "output"

    def test_run_bundle_includes_hashed_trend_analysis(self):
        run(FIXTURE, self.database, self.output)
        manifest = json.loads((self.output / "manifest.json").read_text(encoding="utf-8"))
        self.assertIn(TREND_FILE, manifest["files"])
        report = json.loads((self.output / TREND_FILE).read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["files"][TREND_FILE],
            stable_hash(report))
        self.assertEqual(len(report["periods"]), 1)
        self.assertEqual(report["periods"][0]["denominator"], 8)
        # 单期间没有可比队列，不得生成任何改善率
        self.assertEqual(report["comparisons"], [])

    def test_verify_entry_audits_trend_bundle_against_ledger(self):
        run(FIXTURE, self.database, self.output)
        result = verify(self.database, self.output)
        self.assertTrue(result["ok"])
        self.assertEqual(result["trend_errors"], [])
        self.assertEqual(verify_trend_bundle(self.output, Repository(self.database)), [])
        self.assertEqual(verify_bundle(self.output), [])

    def test_trend_file_tampering_fails_existing_verify_entry(self):
        run(FIXTURE, self.database, self.output)
        report = json.loads((self.output / TREND_FILE).read_text(encoding="utf-8"))
        report["periods"][0]["denominator"] = 999
        (self.output / TREND_FILE).write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
        result = verify(self.database, self.output)
        self.assertFalse(result["ok"])
        self.assertTrue(result["trend_errors"])

    def test_rerun_is_idempotent_and_old_report_is_not_recomputed(self):
        first = run(FIXTURE, self.database, self.output)
        frozen_report = (self.output / TREND_FILE).read_text(encoding="utf-8")
        frozen_manifest = json.loads((self.output / "manifest.json").read_text(encoding="utf-8"))
        second = run(FIXTURE, self.database, self.output)
        self.assertEqual(first["run_id"], second["run_id"])
        self.assertEqual((self.output / TREND_FILE).read_text(encoding="utf-8"), frozen_report)
        # 旧报告沿既有核验入口仍可审查，且不会被重算覆盖
        self.assertTrue(verify(self.database, self.output)["ok"])
        manifest_now = json.loads((self.output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest_now["manifest_hash"], frozen_manifest["manifest_hash"])

    def test_ledger_versions_and_events_back_every_adopted_row(self):
        run(FIXTURE, self.database, self.output)
        report = json.loads((self.output / TREND_FILE).read_text(encoding="utf-8"))
        repository = Repository(self.database)
        versions = {(row["record_id"], row["version"]): row for row in repository.version_rows()}
        events = {(row["record_id"], row["version"]): row for row in repository.record_saved_events()}
        self.assertTrue(report["adopted_versions"])
        for entry in report["adopted_versions"]:
            key = (entry["record_id"], entry["adopted_version"])
            self.assertIn(key, versions)
            self.assertEqual(entry["adopted_fingerprint"], versions[key]["fingerprint"])
            self.assertIn(key, events)
            self.assertEqual(entry["evidence_event_id"], events[key]["event_id"])
        # 证据链本身保持完整，逐条履约判定未被趋势分析改动
        self.assertEqual(repository.verify_chain(), [])
        self.assertEqual(repository.snapshot()["counts"]["decisions"],
                         repository.snapshot()["counts"]["records"])

    def test_per_item_decisions_remain_available_alongside_trends(self):
        run(FIXTURE, self.database, self.output)
        decisions = json.loads((self.output / "decisions.json").read_text(encoding="utf-8"))
        records = list(csv_rows(self.output / "records.csv"))
        self.assertEqual(len(decisions), len(records))
        self.assertTrue(all(item["outcome"] for item in decisions))
        report = json.loads((self.output / TREND_FILE).read_text(encoding="utf-8"))
        decided = sum(period["decided_count"] for period in report["periods"])
        self.assertEqual(decided, len(decisions))


def csv_rows(path: Path):
    import csv

    with path.open(encoding="utf-8") as handle:
        yield from csv.DictReader(handle)


class MonthlyBulletinTrendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.database = self.root / "monthly.sqlite3"
        self.output = self.root / "output"
        self.clock = MutableClock("2026-09-15T00:00:00+00:00")

    def test_two_monthly_runs_produce_comparable_frozen_trend(self):
        september = monthly_fixture([
            ("case-1", 40, "member-a", "safety"),
            ("case-2", 50, "member-b", "governance"),
        ])
        Application(self.database, clock=self.clock).run_fixture(september, self.output)

        self.clock.stamp = "2026-10-10T00:00:00+00:00"
        # 月内第一次补交：case-1 更正为 70
        Application(self.database, clock=self.clock).run_fixture(
            monthly_fixture([("case-1", 70, "member-a", "safety")]), self.output)

        self.clock.stamp = "2026-10-15T00:00:00+00:00"
        # 月内第二次更正：case-1 再改为 80；case-2 更正一次、case-3 为新统计对象
        october = monthly_fixture([
            ("case-1", 80, "member-a", "safety"),
            ("case-2", 55, "member-b", "governance"),
            ("case-3", 20, "member-a", "safety"),
        ])
        application = Application(self.database, clock=self.clock)
        application.run_fixture(october, self.output)

        self.assertEqual(application.repository.verify_chain(), [])
        result = verify(self.database, self.output)
        self.assertTrue(result["ok"], result)

        report = json.loads((self.output / TREND_FILE).read_text(encoding="utf-8"))
        self.assertEqual([item["period"] for item in report["periods"]], ["2026-09", "2026-10"])
        portfolio = next(item for item in report["comparisons"] if item["scope"] == "portfolio")
        self.assertEqual(portfolio["matched_record_ids"], ["case-1", "case-2"])
        self.assertEqual(portfolio["entered_record_ids"], ["case-3"])
        self.assertEqual(portfolio["improvement_rate"], 1.0)
        october_period = report["periods"][1]
        self.assertEqual(october_period["denominator"], 3)
        # 同月两个 case-1 版本只采用一次，候选版本仍可追溯
        adopted = next(item for item in report["adopted_versions"]
                       if item["record_id"] == "case-1" and item["period"] == "2026-10")
        self.assertEqual(len(adopted["candidate_versions"]), 2)
        self.assertIsNotNone(adopted["evidence_event_id"])

    def test_verify_uses_frozen_report_without_recomputing_it(self):
        september = monthly_fixture([("case-1", 40, "member-a", "safety")])
        Application(self.database, clock=self.clock).run_fixture(september, self.output)
        frozen = (self.output / TREND_FILE).read_text(encoding="utf-8")
        # 旧报告保持冻结；核验只读台账与冻结文件，不重写报告
        self.assertTrue(verify(self.database, self.output)["ok"])
        self.assertEqual((self.output / TREND_FILE).read_text(encoding="utf-8"), frozen)


if __name__ == "__main__":
    unittest.main()
