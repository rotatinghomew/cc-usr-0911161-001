from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

@dataclass(frozen=True)
class DomainSignal:
    code: str
    score: float
    severity: str
    evidence: dict[str, Any]

def number(payload: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    try:
        value = float(payload.get(key, default))
    except (TypeError, ValueError):
        return default
    return default if value != value or value in (float('inf'), float('-inf')) else value

def ratio(payload: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    value = number(payload, key, default)
    if value > 1.0:
        value /= 100.0
    return max(0.0, min(1.0, value))

def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))

def commitment_health(payload: Mapping[str, Any]) -> DomainSignal:
    progress = ratio(payload, 'progress_pct')
    legal = ratio(payload, 'legal_readiness')
    quality = ratio(payload, 'data_quality')
    review = ratio(payload, 'review_score')
    beneficiaries = ratio(payload, 'beneficiary_share')
    evidence = number(payload, 'evidence_count')
    findings = number(payload, 'audit_findings')
    gaps = number(payload, 'unresolved_gaps')
    deadline = number(payload, 'deadline_days', 365.0)
    evidence_factor = min(1.0, evidence / 12.0)
    deadline_factor = 0.0 if deadline <= 0 else min(1.0, deadline / 365.0)
    penalty = min(0.7, findings * 0.03 + gaps * 0.05 + (1.0 - deadline_factor) * 0.2)
    score = clamp(progress * 0.25 + legal * 0.18 + quality * 0.16 + review * 0.16 + beneficiaries * 0.1 + evidence_factor * 0.15 - penalty)
    severity = 'critical' if deadline <= 0 or score < 0.28 else 'warning' if score < 0.58 else 'info'
    return DomainSignal('commitment_health', score, severity, {'progress': progress, 'legal': legal, 'evidence_factor': evidence_factor, 'penalty': penalty, 'deadline_days': deadline})

def peer_distribution(records: Iterable[Any], group_field: str = 'member_code') -> dict[str, Any]:
    rows = [(str(getattr(r, 'payload', r).get(group_field, 'unknown')), commitment_health(getattr(r, 'payload', r)).score) for r in records]
    overdue = sum(commitment_health(getattr(r, 'payload', r)).severity == 'critical' for r in records)
    return {'members': {key: score for key, score in rows}, 'count': len(rows), 'overdue': overdue, 'average': sum(score for _, score in rows) / len(rows) if rows else 0.0}

def augment_context(record: Any, repository: Any) -> dict[str, Any]:
    signal = commitment_health(record.payload); peers = peer_distribution(repository.list_records())
    return {'domain_signal': signal.score, 'domain_severity': signal.severity, 'overdue_members': peers['overdue'], 'peer_average': peers['average']}
