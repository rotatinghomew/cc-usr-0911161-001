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


def exterior_quality(record: DomainRecord) -> float:
    diameter = _numeric(record.payload, "legal_readiness")
    mass = _numeric(record.payload, "evidence_count")
    bruise = _numeric(record.payload, "audit_findings")
    coverage = _numeric(record.payload, "data_quality")
    shape_fit = bounded(1.0 - abs(diameter - 72.0) / 90.0)
    mass_fit = bounded(1.0 - abs(mass - 105.0) / 160.0)
    bruise_penalty = bounded(bruise / 40.0)
    return bounded(shape_fit * 0.34 + mass_fit * 0.26 + bounded(coverage) * 0.30 + (1.0 - bruise_penalty) * 0.10)


def interior_quality(record: DomainRecord) -> float:
    sweetness = bounded(_numeric(record.payload, "progress_pct") / 24.0)
    void_penalty = bounded(_numeric(record.payload, "unresolved_gaps") / 20.0)
    review_score = bounded(_numeric(record.payload, "review_score"))
    beneficiary_share = bounded(_numeric(record.payload, "beneficiary_share"))
    return bounded(sweetness * 0.35 + (1.0 - void_penalty) * 0.25 + review_score * 0.25 + beneficiary_share * 0.15)


def fulfillment_probability(record: DomainRecord) -> dict[str, float]:
    exterior = exterior_quality(record)
    interior = interior_quality(record)
    freshness = bounded(1.0 - _numeric(record.payload, "deadline_days") / 240.0)
    combined = bounded(exterior * 0.45 + interior * 0.45 + freshness * 0.10)
    premium = bounded((combined - 0.58) / 0.42)
    standard = bounded(1.0 - abs(combined - 0.55) / 0.45)
    processing = bounded(1.0 - premium - standard * 0.45)
    total = premium + standard + processing
    return {"premium": premium / total, "standard": standard / total, "processing": processing / total}


def commitment_calibration(records: Iterable[DomainRecord]) -> dict[str, float]:
    rows = list(records)
    if not rows:
        return {"exterior_mean": 0.0, "interior_mean": 0.0, "dispersion": 0.0, "sample_count": 0.0}
    exterior = [exterior_quality(row) for row in rows]
    interior = [interior_quality(row) for row in rows]
    combined = [(left + right) / 2.0 for left, right in zip(exterior, interior)]
    return {"exterior_mean": statistics.fmean(exterior), "interior_mean": statistics.fmean(interior),
            "dispersion": statistics.pstdev(combined) if len(combined) > 1 else 0.0,
            "sample_count": float(len(rows))}


def member_drift(records: Iterable[DomainRecord]) -> dict[str, float]:
    groups: dict[str, list[float]] = defaultdict(list)
    for record in records:
        groups[str(record.payload.get("member_code", "unknown"))].append(interior_quality(record))
    means = {origin: statistics.fmean(values) for origin, values in groups.items()}
    spread = max(means.values()) - min(means.values()) if means else 0.0
    return {"origin_count": float(len(means)), "quality_spread": spread, "drift_risk": bounded(spread * 2.0)}


def derive_context(record: DomainRecord, repository: Any) -> dict[str, float]:
    probabilities = fulfillment_probability(record)
    history = repository.list_records()
    calibration = commitment_calibration(history or [record])
    drift = member_drift(history or [record])
    return {"grade_consistency_weight": 0.8 + probabilities["premium"] * 0.3,
            "inspection_coverage_weight": 0.7 + exterior_quality(record) * 0.4,
            "false_release_risk_weight": 1.2 - interior_quality(record) * 0.4,
            "member_drift_weight": 0.8 + drift["drift_risk"] * 0.5,
            "calibration_need_weight": 0.8 + calibration["dispersion"] * 0.8}
