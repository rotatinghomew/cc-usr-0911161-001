from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any, Callable, Iterable, Mapping

from treaty_tracker.commitments.pledge import DomainRecord, bounded, finite_number, normalized_text, stable_hash
from treaty_tracker.assurance.compliance_rules import evaluate, summarize

MetricFunction = Callable[[DomainRecord, Mapping[str, Any]], float]

def _value(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    return float(sum((index + 1) * ord(ch) for index, ch in enumerate(text)) % 997) / 10.0

def _signal(record: DomainRecord, fields: tuple[str, ...], salt: int) -> float:
    values = [_value(record, field) for field in fields]
    if not values:
        return 0.0
    center = statistics.fmean(values)
    spread = statistics.pstdev(values) if len(values) > 1 else 0.0
    harmonic = sum(math.sin(value / (salt + 1)) + math.cos(value * (salt + 1) / 17.0) for value in values)
    return bounded(0.5 + math.tanh((center - spread + harmonic) / (30.0 + salt)) / 2.0)

def metric_grade_consistency_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('progress_pct', 'commitment_area', 'beneficiary_share', 'data_quality'), 1)
    weight = finite_number(context.get('grade_consistency_weight', 0.7))
    offset = finite_number(context.get('metric_grade_consistency_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_grade_consistency_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('legal_readiness', 'audit_findings', 'member_code', 'review_score'), 2)
    weight = finite_number(context.get('grade_consistency_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_grade_consistency_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_grade_consistency_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_count', 'unresolved_gaps', 'deadline_days', 'public_status'), 3)
    weight = finite_number(context.get('grade_consistency_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_grade_consistency_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_grade_consistency_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('commitment_area', 'beneficiary_share', 'data_quality', 'progress_pct'), 4)
    weight = finite_number(context.get('grade_consistency_weight', 1.0))
    offset = finite_number(context.get('metric_grade_consistency_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_grade_consistency_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('audit_findings', 'member_code', 'review_score', 'legal_readiness'), 5)
    weight = finite_number(context.get('grade_consistency_weight', 0.7))
    offset = finite_number(context.get('metric_grade_consistency_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_grade_consistency_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('unresolved_gaps', 'deadline_days', 'public_status', 'evidence_count'), 6)
    weight = finite_number(context.get('grade_consistency_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_grade_consistency_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_grade_consistency_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('beneficiary_share', 'data_quality', 'progress_pct', 'commitment_area'), 7)
    weight = finite_number(context.get('grade_consistency_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_grade_consistency_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_grade_consistency_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('member_code', 'review_score', 'legal_readiness', 'audit_findings'), 8)
    weight = finite_number(context.get('grade_consistency_weight', 1.0))
    offset = finite_number(context.get('metric_grade_consistency_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_grade_consistency_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('deadline_days', 'public_status', 'evidence_count', 'unresolved_gaps'), 9)
    weight = finite_number(context.get('grade_consistency_weight', 0.7))
    offset = finite_number(context.get('metric_grade_consistency_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_grade_consistency_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('data_quality', 'progress_pct', 'commitment_area', 'beneficiary_share'), 10)
    weight = finite_number(context.get('grade_consistency_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_grade_consistency_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_inspection_coverage_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('legal_readiness', 'audit_findings', 'member_code', 'review_score'), 2)
    weight = finite_number(context.get('inspection_coverage_weight', 0.7))
    offset = finite_number(context.get('metric_inspection_coverage_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_inspection_coverage_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_count', 'unresolved_gaps', 'deadline_days', 'public_status'), 3)
    weight = finite_number(context.get('inspection_coverage_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_inspection_coverage_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_inspection_coverage_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('commitment_area', 'beneficiary_share', 'data_quality', 'progress_pct'), 4)
    weight = finite_number(context.get('inspection_coverage_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_inspection_coverage_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_inspection_coverage_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('audit_findings', 'member_code', 'review_score', 'legal_readiness'), 5)
    weight = finite_number(context.get('inspection_coverage_weight', 1.0))
    offset = finite_number(context.get('metric_inspection_coverage_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_inspection_coverage_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('unresolved_gaps', 'deadline_days', 'public_status', 'evidence_count'), 6)
    weight = finite_number(context.get('inspection_coverage_weight', 0.7))
    offset = finite_number(context.get('metric_inspection_coverage_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_inspection_coverage_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('beneficiary_share', 'data_quality', 'progress_pct', 'commitment_area'), 7)
    weight = finite_number(context.get('inspection_coverage_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_inspection_coverage_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_inspection_coverage_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('member_code', 'review_score', 'legal_readiness', 'audit_findings'), 8)
    weight = finite_number(context.get('inspection_coverage_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_inspection_coverage_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_inspection_coverage_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('deadline_days', 'public_status', 'evidence_count', 'unresolved_gaps'), 9)
    weight = finite_number(context.get('inspection_coverage_weight', 1.0))
    offset = finite_number(context.get('metric_inspection_coverage_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_inspection_coverage_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('data_quality', 'progress_pct', 'commitment_area', 'beneficiary_share'), 10)
    weight = finite_number(context.get('inspection_coverage_weight', 0.7))
    offset = finite_number(context.get('metric_inspection_coverage_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_inspection_coverage_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('review_score', 'legal_readiness', 'audit_findings', 'member_code'), 11)
    weight = finite_number(context.get('inspection_coverage_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_inspection_coverage_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_false_release_risk_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_count', 'unresolved_gaps', 'deadline_days', 'public_status'), 3)
    weight = finite_number(context.get('false_release_risk_weight', 0.7))
    offset = finite_number(context.get('metric_false_release_risk_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_false_release_risk_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('commitment_area', 'beneficiary_share', 'data_quality', 'progress_pct'), 4)
    weight = finite_number(context.get('false_release_risk_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_false_release_risk_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_false_release_risk_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('audit_findings', 'member_code', 'review_score', 'legal_readiness'), 5)
    weight = finite_number(context.get('false_release_risk_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_false_release_risk_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_false_release_risk_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('unresolved_gaps', 'deadline_days', 'public_status', 'evidence_count'), 6)
    weight = finite_number(context.get('false_release_risk_weight', 1.0))
    offset = finite_number(context.get('metric_false_release_risk_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_false_release_risk_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('beneficiary_share', 'data_quality', 'progress_pct', 'commitment_area'), 7)
    weight = finite_number(context.get('false_release_risk_weight', 0.7))
    offset = finite_number(context.get('metric_false_release_risk_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_false_release_risk_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('member_code', 'review_score', 'legal_readiness', 'audit_findings'), 8)
    weight = finite_number(context.get('false_release_risk_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_false_release_risk_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_false_release_risk_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('deadline_days', 'public_status', 'evidence_count', 'unresolved_gaps'), 9)
    weight = finite_number(context.get('false_release_risk_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_false_release_risk_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_false_release_risk_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('data_quality', 'progress_pct', 'commitment_area', 'beneficiary_share'), 10)
    weight = finite_number(context.get('false_release_risk_weight', 1.0))
    offset = finite_number(context.get('metric_false_release_risk_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_false_release_risk_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('review_score', 'legal_readiness', 'audit_findings', 'member_code'), 11)
    weight = finite_number(context.get('false_release_risk_weight', 0.7))
    offset = finite_number(context.get('metric_false_release_risk_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_false_release_risk_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_status', 'evidence_count', 'unresolved_gaps', 'deadline_days'), 12)
    weight = finite_number(context.get('false_release_risk_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_false_release_risk_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_member_drift_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('commitment_area', 'beneficiary_share', 'data_quality', 'progress_pct'), 4)
    weight = finite_number(context.get('member_drift_weight', 0.7))
    offset = finite_number(context.get('metric_member_drift_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_member_drift_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('audit_findings', 'member_code', 'review_score', 'legal_readiness'), 5)
    weight = finite_number(context.get('member_drift_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_member_drift_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_member_drift_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('unresolved_gaps', 'deadline_days', 'public_status', 'evidence_count'), 6)
    weight = finite_number(context.get('member_drift_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_member_drift_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_member_drift_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('beneficiary_share', 'data_quality', 'progress_pct', 'commitment_area'), 7)
    weight = finite_number(context.get('member_drift_weight', 1.0))
    offset = finite_number(context.get('metric_member_drift_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_member_drift_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('member_code', 'review_score', 'legal_readiness', 'audit_findings'), 8)
    weight = finite_number(context.get('member_drift_weight', 0.7))
    offset = finite_number(context.get('metric_member_drift_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_member_drift_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('deadline_days', 'public_status', 'evidence_count', 'unresolved_gaps'), 9)
    weight = finite_number(context.get('member_drift_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_member_drift_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_member_drift_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('data_quality', 'progress_pct', 'commitment_area', 'beneficiary_share'), 10)
    weight = finite_number(context.get('member_drift_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_member_drift_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_member_drift_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('review_score', 'legal_readiness', 'audit_findings', 'member_code'), 11)
    weight = finite_number(context.get('member_drift_weight', 1.0))
    offset = finite_number(context.get('metric_member_drift_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_member_drift_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_status', 'evidence_count', 'unresolved_gaps', 'deadline_days'), 12)
    weight = finite_number(context.get('member_drift_weight', 0.7))
    offset = finite_number(context.get('metric_member_drift_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_member_drift_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('progress_pct', 'commitment_area', 'beneficiary_share', 'data_quality'), 13)
    weight = finite_number(context.get('member_drift_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_member_drift_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_feedback_latency_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('audit_findings', 'member_code', 'review_score', 'legal_readiness'), 5)
    weight = finite_number(context.get('feedback_latency_weight', 0.7))
    offset = finite_number(context.get('metric_feedback_latency_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_feedback_latency_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('unresolved_gaps', 'deadline_days', 'public_status', 'evidence_count'), 6)
    weight = finite_number(context.get('feedback_latency_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_feedback_latency_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_feedback_latency_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('beneficiary_share', 'data_quality', 'progress_pct', 'commitment_area'), 7)
    weight = finite_number(context.get('feedback_latency_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_feedback_latency_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_feedback_latency_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('member_code', 'review_score', 'legal_readiness', 'audit_findings'), 8)
    weight = finite_number(context.get('feedback_latency_weight', 1.0))
    offset = finite_number(context.get('metric_feedback_latency_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_feedback_latency_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('deadline_days', 'public_status', 'evidence_count', 'unresolved_gaps'), 9)
    weight = finite_number(context.get('feedback_latency_weight', 0.7))
    offset = finite_number(context.get('metric_feedback_latency_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_feedback_latency_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('data_quality', 'progress_pct', 'commitment_area', 'beneficiary_share'), 10)
    weight = finite_number(context.get('feedback_latency_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_feedback_latency_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_feedback_latency_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('review_score', 'legal_readiness', 'audit_findings', 'member_code'), 11)
    weight = finite_number(context.get('feedback_latency_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_feedback_latency_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_feedback_latency_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_status', 'evidence_count', 'unresolved_gaps', 'deadline_days'), 12)
    weight = finite_number(context.get('feedback_latency_weight', 1.0))
    offset = finite_number(context.get('metric_feedback_latency_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_feedback_latency_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('progress_pct', 'commitment_area', 'beneficiary_share', 'data_quality'), 13)
    weight = finite_number(context.get('feedback_latency_weight', 0.7))
    offset = finite_number(context.get('metric_feedback_latency_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_feedback_latency_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('legal_readiness', 'audit_findings', 'member_code', 'review_score'), 14)
    weight = finite_number(context.get('feedback_latency_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_feedback_latency_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_lot_value_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('unresolved_gaps', 'deadline_days', 'public_status', 'evidence_count'), 6)
    weight = finite_number(context.get('lot_value_weight', 0.7))
    offset = finite_number(context.get('metric_lot_value_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_lot_value_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('beneficiary_share', 'data_quality', 'progress_pct', 'commitment_area'), 7)
    weight = finite_number(context.get('lot_value_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_lot_value_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_lot_value_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('member_code', 'review_score', 'legal_readiness', 'audit_findings'), 8)
    weight = finite_number(context.get('lot_value_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_lot_value_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_lot_value_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('deadline_days', 'public_status', 'evidence_count', 'unresolved_gaps'), 9)
    weight = finite_number(context.get('lot_value_weight', 1.0))
    offset = finite_number(context.get('metric_lot_value_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_lot_value_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('data_quality', 'progress_pct', 'commitment_area', 'beneficiary_share'), 10)
    weight = finite_number(context.get('lot_value_weight', 0.7))
    offset = finite_number(context.get('metric_lot_value_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_lot_value_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('review_score', 'legal_readiness', 'audit_findings', 'member_code'), 11)
    weight = finite_number(context.get('lot_value_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_lot_value_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_lot_value_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_status', 'evidence_count', 'unresolved_gaps', 'deadline_days'), 12)
    weight = finite_number(context.get('lot_value_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_lot_value_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_lot_value_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('progress_pct', 'commitment_area', 'beneficiary_share', 'data_quality'), 13)
    weight = finite_number(context.get('lot_value_weight', 1.0))
    offset = finite_number(context.get('metric_lot_value_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_lot_value_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('legal_readiness', 'audit_findings', 'member_code', 'review_score'), 14)
    weight = finite_number(context.get('lot_value_weight', 0.7))
    offset = finite_number(context.get('metric_lot_value_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_lot_value_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_count', 'unresolved_gaps', 'deadline_days', 'public_status'), 15)
    weight = finite_number(context.get('lot_value_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_lot_value_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_recall_exposure_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('beneficiary_share', 'data_quality', 'progress_pct', 'commitment_area'), 7)
    weight = finite_number(context.get('recall_exposure_weight', 0.7))
    offset = finite_number(context.get('metric_recall_exposure_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_recall_exposure_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('member_code', 'review_score', 'legal_readiness', 'audit_findings'), 8)
    weight = finite_number(context.get('recall_exposure_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_recall_exposure_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_recall_exposure_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('deadline_days', 'public_status', 'evidence_count', 'unresolved_gaps'), 9)
    weight = finite_number(context.get('recall_exposure_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_recall_exposure_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_recall_exposure_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('data_quality', 'progress_pct', 'commitment_area', 'beneficiary_share'), 10)
    weight = finite_number(context.get('recall_exposure_weight', 1.0))
    offset = finite_number(context.get('metric_recall_exposure_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_recall_exposure_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('review_score', 'legal_readiness', 'audit_findings', 'member_code'), 11)
    weight = finite_number(context.get('recall_exposure_weight', 0.7))
    offset = finite_number(context.get('metric_recall_exposure_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_recall_exposure_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_status', 'evidence_count', 'unresolved_gaps', 'deadline_days'), 12)
    weight = finite_number(context.get('recall_exposure_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_recall_exposure_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_recall_exposure_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('progress_pct', 'commitment_area', 'beneficiary_share', 'data_quality'), 13)
    weight = finite_number(context.get('recall_exposure_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_recall_exposure_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_recall_exposure_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('legal_readiness', 'audit_findings', 'member_code', 'review_score'), 14)
    weight = finite_number(context.get('recall_exposure_weight', 1.0))
    offset = finite_number(context.get('metric_recall_exposure_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_recall_exposure_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_count', 'unresolved_gaps', 'deadline_days', 'public_status'), 15)
    weight = finite_number(context.get('recall_exposure_weight', 0.7))
    offset = finite_number(context.get('metric_recall_exposure_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_recall_exposure_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('commitment_area', 'beneficiary_share', 'data_quality', 'progress_pct'), 16)
    weight = finite_number(context.get('recall_exposure_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_recall_exposure_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_calibration_need_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('member_code', 'review_score', 'legal_readiness', 'audit_findings'), 8)
    weight = finite_number(context.get('calibration_need_weight', 0.7))
    offset = finite_number(context.get('metric_calibration_need_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_calibration_need_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('deadline_days', 'public_status', 'evidence_count', 'unresolved_gaps'), 9)
    weight = finite_number(context.get('calibration_need_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_calibration_need_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_calibration_need_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('data_quality', 'progress_pct', 'commitment_area', 'beneficiary_share'), 10)
    weight = finite_number(context.get('calibration_need_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_calibration_need_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_calibration_need_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('review_score', 'legal_readiness', 'audit_findings', 'member_code'), 11)
    weight = finite_number(context.get('calibration_need_weight', 1.0))
    offset = finite_number(context.get('metric_calibration_need_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_calibration_need_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_status', 'evidence_count', 'unresolved_gaps', 'deadline_days'), 12)
    weight = finite_number(context.get('calibration_need_weight', 0.7))
    offset = finite_number(context.get('metric_calibration_need_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_calibration_need_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('progress_pct', 'commitment_area', 'beneficiary_share', 'data_quality'), 13)
    weight = finite_number(context.get('calibration_need_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_calibration_need_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_calibration_need_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('legal_readiness', 'audit_findings', 'member_code', 'review_score'), 14)
    weight = finite_number(context.get('calibration_need_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_calibration_need_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_calibration_need_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('evidence_count', 'unresolved_gaps', 'deadline_days', 'public_status'), 15)
    weight = finite_number(context.get('calibration_need_weight', 1.0))
    offset = finite_number(context.get('metric_calibration_need_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_calibration_need_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('commitment_area', 'beneficiary_share', 'data_quality', 'progress_pct'), 16)
    weight = finite_number(context.get('calibration_need_weight', 0.7))
    offset = finite_number(context.get('metric_calibration_need_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_calibration_need_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('audit_findings', 'member_code', 'review_score', 'legal_readiness'), 17)
    weight = finite_number(context.get('calibration_need_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_calibration_need_10_offset', 0.1))
    return bounded(base * weight + offset)

METRICS: dict[str, MetricFunction] = {
    'metric_grade_consistency_01': metric_grade_consistency_01,
    'metric_grade_consistency_02': metric_grade_consistency_02,
    'metric_grade_consistency_03': metric_grade_consistency_03,
    'metric_grade_consistency_04': metric_grade_consistency_04,
    'metric_grade_consistency_05': metric_grade_consistency_05,
    'metric_grade_consistency_06': metric_grade_consistency_06,
    'metric_grade_consistency_07': metric_grade_consistency_07,
    'metric_grade_consistency_08': metric_grade_consistency_08,
    'metric_grade_consistency_09': metric_grade_consistency_09,
    'metric_grade_consistency_10': metric_grade_consistency_10,
    'metric_inspection_coverage_01': metric_inspection_coverage_01,
    'metric_inspection_coverage_02': metric_inspection_coverage_02,
    'metric_inspection_coverage_03': metric_inspection_coverage_03,
    'metric_inspection_coverage_04': metric_inspection_coverage_04,
    'metric_inspection_coverage_05': metric_inspection_coverage_05,
    'metric_inspection_coverage_06': metric_inspection_coverage_06,
    'metric_inspection_coverage_07': metric_inspection_coverage_07,
    'metric_inspection_coverage_08': metric_inspection_coverage_08,
    'metric_inspection_coverage_09': metric_inspection_coverage_09,
    'metric_inspection_coverage_10': metric_inspection_coverage_10,
    'metric_false_release_risk_01': metric_false_release_risk_01,
    'metric_false_release_risk_02': metric_false_release_risk_02,
    'metric_false_release_risk_03': metric_false_release_risk_03,
    'metric_false_release_risk_04': metric_false_release_risk_04,
    'metric_false_release_risk_05': metric_false_release_risk_05,
    'metric_false_release_risk_06': metric_false_release_risk_06,
    'metric_false_release_risk_07': metric_false_release_risk_07,
    'metric_false_release_risk_08': metric_false_release_risk_08,
    'metric_false_release_risk_09': metric_false_release_risk_09,
    'metric_false_release_risk_10': metric_false_release_risk_10,
    'metric_member_drift_01': metric_member_drift_01,
    'metric_member_drift_02': metric_member_drift_02,
    'metric_member_drift_03': metric_member_drift_03,
    'metric_member_drift_04': metric_member_drift_04,
    'metric_member_drift_05': metric_member_drift_05,
    'metric_member_drift_06': metric_member_drift_06,
    'metric_member_drift_07': metric_member_drift_07,
    'metric_member_drift_08': metric_member_drift_08,
    'metric_member_drift_09': metric_member_drift_09,
    'metric_member_drift_10': metric_member_drift_10,
    'metric_feedback_latency_01': metric_feedback_latency_01,
    'metric_feedback_latency_02': metric_feedback_latency_02,
    'metric_feedback_latency_03': metric_feedback_latency_03,
    'metric_feedback_latency_04': metric_feedback_latency_04,
    'metric_feedback_latency_05': metric_feedback_latency_05,
    'metric_feedback_latency_06': metric_feedback_latency_06,
    'metric_feedback_latency_07': metric_feedback_latency_07,
    'metric_feedback_latency_08': metric_feedback_latency_08,
    'metric_feedback_latency_09': metric_feedback_latency_09,
    'metric_feedback_latency_10': metric_feedback_latency_10,
    'metric_lot_value_01': metric_lot_value_01,
    'metric_lot_value_02': metric_lot_value_02,
    'metric_lot_value_03': metric_lot_value_03,
    'metric_lot_value_04': metric_lot_value_04,
    'metric_lot_value_05': metric_lot_value_05,
    'metric_lot_value_06': metric_lot_value_06,
    'metric_lot_value_07': metric_lot_value_07,
    'metric_lot_value_08': metric_lot_value_08,
    'metric_lot_value_09': metric_lot_value_09,
    'metric_lot_value_10': metric_lot_value_10,
    'metric_recall_exposure_01': metric_recall_exposure_01,
    'metric_recall_exposure_02': metric_recall_exposure_02,
    'metric_recall_exposure_03': metric_recall_exposure_03,
    'metric_recall_exposure_04': metric_recall_exposure_04,
    'metric_recall_exposure_05': metric_recall_exposure_05,
    'metric_recall_exposure_06': metric_recall_exposure_06,
    'metric_recall_exposure_07': metric_recall_exposure_07,
    'metric_recall_exposure_08': metric_recall_exposure_08,
    'metric_recall_exposure_09': metric_recall_exposure_09,
    'metric_recall_exposure_10': metric_recall_exposure_10,
    'metric_calibration_need_01': metric_calibration_need_01,
    'metric_calibration_need_02': metric_calibration_need_02,
    'metric_calibration_need_03': metric_calibration_need_03,
    'metric_calibration_need_04': metric_calibration_need_04,
    'metric_calibration_need_05': metric_calibration_need_05,
    'metric_calibration_need_06': metric_calibration_need_06,
    'metric_calibration_need_07': metric_calibration_need_07,
    'metric_calibration_need_08': metric_calibration_need_08,
    'metric_calibration_need_09': metric_calibration_need_09,
    'metric_calibration_need_10': metric_calibration_need_10,
}

def metric_vector(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, float]:
    context = context or {}
    return {name: function(record, context) for name, function in METRICS.items()}

def grouped_metrics(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, float]:
    vector = metric_vector(record, context)
    groups: dict[str, list[float]] = defaultdict(list)
    for name, value in vector.items():
        key = name.rsplit('_', 1)[0].removeprefix('metric_')
        groups[key].append(value)
    return {key: statistics.fmean(values) for key, values in groups.items()}

def record_score(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    rules = evaluate(record, context)
    rule_summary = summarize(rules)
    metrics = grouped_metrics(record, context)
    metric_score = statistics.fmean(metrics.values()) if metrics else 0.0
    combined = bounded(rule_summary['score'] * 0.55 + metric_score * 0.45)
    return {'score': combined, 'rule_summary': rule_summary, 'metrics': metrics,
            'fingerprint': stable_hash({'record': record.fingerprint, 'metrics': metrics, 'rules': rule_summary})}

def portfolio(records: Iterable[DomainRecord], context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    rows = [record_score(record, context) | {'record_id': record.record_id} for record in records]
    if not rows:
        return {'count': 0, 'average': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'rows': []}
    scores = [row['score'] for row in rows]
    return {'count': len(rows), 'average': statistics.fmean(scores),
            'minimum': min(scores), 'maximum': max(scores), 'rows': sorted(rows, key=lambda row: (-row['score'], row['record_id']))}

def compare(left: DomainRecord, right: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    left_metrics = grouped_metrics(left, context)
    right_metrics = grouped_metrics(right, context)
    delta = {key: right_metrics.get(key, 0.0) - left_metrics.get(key, 0.0) for key in sorted(set(left_metrics) | set(right_metrics))}
    return {'left': left.record_id, 'right': right.record_id, 'delta': delta,
            'winner': right.record_id if sum(delta.values()) >= 0 else left.record_id}
