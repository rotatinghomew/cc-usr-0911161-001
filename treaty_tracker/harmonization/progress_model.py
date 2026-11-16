from __future__ import annotations

import statistics
from collections import defaultdict
from typing import Any, Iterable, Mapping

from treaty_tracker.commitments.pledge import DomainRecord, bounded, finite_number


def _numeric(payload: Mapping[str, Any], key: str) -> float:
    value = payload.get(key, 0.0)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return finite_number(value)
    return float(sum(ord(ch) for ch in str(value)) % 101)


def _rate(record: DomainRecord, field: str) -> float:
    value = _numeric(record.payload, field)
    return bounded(value / 100.0 if value > 1.0 else value)


def evidence_quality(record: DomainRecord) -> float:
    legal = _rate(record, "legal_readiness")
    evidence = bounded(_numeric(record.payload, "evidence_count") / 12.0)
    findings = bounded(_numeric(record.payload, "audit_findings") / 10.0)
    quality = _rate(record, "data_quality")
    return bounded(legal * 0.35 + evidence * 0.30 + quality * 0.25 + (1.0 - findings) * 0.10)


def delivery_quality(record: DomainRecord) -> float:
    progress = _rate(record, "progress_pct")
    gaps = bounded(_numeric(record.payload, "unresolved_gaps") / 10.0)
    review = _rate(record, "review_score")
    beneficiaries = _rate(record, "beneficiary_share")
    return bounded(progress * 0.40 + (1.0 - gaps) * 0.20 + review * 0.25 + beneficiaries * 0.15)


def fulfillment_probability(record: DomainRecord) -> dict[str, float]:
    evidence = evidence_quality(record)
    delivery = delivery_quality(record)
    freshness = bounded(1.0 - _numeric(record.payload, "deadline_days") / 240.0)
    combined = bounded(evidence * 0.45 + delivery * 0.45 + freshness * 0.10)
    fulfilled = bounded((combined - 0.58) / 0.42)
    reviewing = bounded(1.0 - abs(combined - 0.55) / 0.45)
    at_risk = bounded(1.0 - fulfilled - reviewing * 0.45)
    total = fulfilled + reviewing + at_risk
    return {"fulfilled": fulfilled / total, "reviewing": reviewing / total, "at_risk": at_risk / total}


def commitment_calibration(records: Iterable[DomainRecord]) -> dict[str, float]:
    rows = list(records)
    if not rows:
        return {"evidence_mean": 0.0, "delivery_mean": 0.0, "dispersion": 0.0, "sample_count": 0.0}
    evidence = [evidence_quality(row) for row in rows]
    delivery = [delivery_quality(row) for row in rows]
    combined = [(left + right) / 2.0 for left, right in zip(evidence, delivery)]
    return {"evidence_mean": statistics.fmean(evidence), "delivery_mean": statistics.fmean(delivery),
            "dispersion": statistics.pstdev(combined) if len(combined) > 1 else 0.0,
            "sample_count": float(len(rows))}


def member_drift(records: Iterable[DomainRecord]) -> dict[str, float]:
    groups: dict[str, list[float]] = defaultdict(list)
    for record in records:
        groups[str(record.payload.get("member_code", "unknown"))].append(delivery_quality(record))
    means = {origin: statistics.fmean(values) for origin, values in groups.items()}
    spread = max(means.values()) - min(means.values()) if means else 0.0
    return {"origin_count": float(len(means)), "quality_spread": spread, "drift_risk": bounded(spread * 2.0)}


def derive_context(record: DomainRecord, repository: Any) -> dict[str, float]:
    probabilities = fulfillment_probability(record)
    history = repository.list_records()
    calibration = commitment_calibration(history or [record])
    drift = member_drift(history or [record])
    return {"grade_consistency_weight": 0.8 + probabilities["fulfilled"] * 0.3,
            "inspection_coverage_weight": 0.7 + evidence_quality(record) * 0.4,
            "false_release_risk_weight": 1.2 - delivery_quality(record) * 0.4,
            "member_drift_weight": 0.8 + drift["drift_risk"] * 0.5,
            "calibration_need_weight": 0.8 + calibration["dispersion"] * 0.8}
