from __future__ import annotations

import math
from typing import Any, Callable, Mapping

from treaty_tracker.commitments.pledge import DomainRecord, RuleResult, bounded, finite_number, normalized_text

RuleFunction = Callable[[DomainRecord, Mapping[str, Any]], RuleResult]

def _number(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    if not text:
        return 0.0
    try:
        return finite_number(text)
    except ValueError:
        return float(sum(ord(ch) for ch in text) % 101)

def _context_number(context: Mapping[str, Any], key: str, default: float) -> float:
    try:
        return finite_number(context.get(key, default))
    except ValueError:
        return default

def _result(code: str, value: float, threshold: float, higher_is_better: bool, message: str, evidence: dict[str, Any]) -> RuleResult:
    distance = (value - threshold) if higher_is_better else (threshold - value)
    passed = distance >= 0
    scale = max(1.0, abs(threshold))
    score = bounded(0.5 + distance / (2.0 * scale))
    severity = 'info' if passed else ('critical' if score < 0.2 else 'error')
    return RuleResult(code, passed, score, severity, message, evidence)

def check_progress_pct_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'progress_pct')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_progress_pct_presence_threshold', 10.333)
    return _result('check_progress_pct_presence', adjusted, threshold, True, 'validates progress_pct presence',
                   {'field': 'progress_pct', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_progress_pct_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'progress_pct')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_progress_pct_range_threshold', 12.667)
    return _result('check_progress_pct_range', adjusted, threshold, True, 'validates progress_pct range',
                   {'field': 'progress_pct', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_progress_pct_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'progress_pct')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_progress_pct_stability_threshold', 15.0)
    return _result('check_progress_pct_stability', adjusted, threshold, False, 'validates progress_pct stability',
                   {'field': 'progress_pct', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_progress_pct_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'progress_pct')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_progress_pct_freshness_threshold', 17.333)
    return _result('check_progress_pct_freshness', adjusted, threshold, True, 'validates progress_pct freshness',
                   {'field': 'progress_pct', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_progress_pct_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'progress_pct')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_progress_pct_coverage_threshold', 19.667)
    return _result('check_progress_pct_coverage', adjusted, threshold, True, 'validates progress_pct coverage',
                   {'field': 'progress_pct', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_progress_pct_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'progress_pct')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_progress_pct_consistency_threshold', 22.0)
    return _result('check_progress_pct_consistency', adjusted, threshold, False, 'validates progress_pct consistency',
                   {'field': 'progress_pct', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_progress_pct_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'progress_pct')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_progress_pct_risk_threshold', 24.333)
    return _result('check_progress_pct_risk', adjusted, threshold, True, 'validates progress_pct risk',
                   {'field': 'progress_pct', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_progress_preview_score(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'progress_pct')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_progress_preview_score_threshold', 26.667)
    return _result('check_progress_preview_score', adjusted, threshold, True, 'validates progress_pct confidence',
                   {'field': 'progress_pct', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_progress_pct_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'progress_pct')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_progress_pct_dependency_threshold', 29.0)
    return _result('check_progress_pct_dependency', adjusted, threshold, False, 'validates progress_pct dependency',
                   {'field': 'progress_pct', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_progress_pct_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'progress_pct')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_progress_pct_readiness_threshold', 31.333)
    return _result('check_progress_pct_readiness', adjusted, threshold, True, 'validates progress_pct readiness',
                   {'field': 'progress_pct', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_legal_readiness_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'legal_readiness')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_legal_readiness_presence_threshold', 9.333)
    return _result('check_legal_readiness_presence', adjusted, threshold, True, 'validates legal_readiness presence',
                   {'field': 'legal_readiness', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_legal_readiness_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'legal_readiness')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_legal_readiness_range_threshold', 11.667)
    return _result('check_legal_readiness_range', adjusted, threshold, False, 'validates legal_readiness range',
                   {'field': 'legal_readiness', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_legal_readiness_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'legal_readiness')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_legal_readiness_stability_threshold', 14.0)
    return _result('check_legal_readiness_stability', adjusted, threshold, True, 'validates legal_readiness stability',
                   {'field': 'legal_readiness', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_legal_readiness_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'legal_readiness')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_legal_readiness_freshness_threshold', 16.333)
    return _result('check_legal_readiness_freshness', adjusted, threshold, True, 'validates legal_readiness freshness',
                   {'field': 'legal_readiness', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_legal_readiness_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'legal_readiness')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_legal_readiness_coverage_threshold', 18.667)
    return _result('check_legal_readiness_coverage', adjusted, threshold, False, 'validates legal_readiness coverage',
                   {'field': 'legal_readiness', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_legal_readiness_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'legal_readiness')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_legal_readiness_consistency_threshold', 21.0)
    return _result('check_legal_readiness_consistency', adjusted, threshold, True, 'validates legal_readiness consistency',
                   {'field': 'legal_readiness', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_legal_readiness_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'legal_readiness')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_legal_readiness_risk_threshold', 23.333)
    return _result('check_legal_readiness_risk', adjusted, threshold, True, 'validates legal_readiness risk',
                   {'field': 'legal_readiness', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_legal_readiness_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'legal_readiness')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_legal_readiness_confidence_threshold', 25.667)
    return _result('check_legal_readiness_confidence', adjusted, threshold, False, 'validates legal_readiness confidence',
                   {'field': 'legal_readiness', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_legal_readiness_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'legal_readiness')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_legal_readiness_dependency_threshold', 28.0)
    return _result('check_legal_readiness_dependency', adjusted, threshold, True, 'validates legal_readiness dependency',
                   {'field': 'legal_readiness', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_legal_readiness_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'legal_readiness')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_legal_readiness_readiness_threshold', 30.333)
    return _result('check_legal_readiness_readiness', adjusted, threshold, True, 'validates legal_readiness readiness',
                   {'field': 'legal_readiness', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_count_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_count')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_evidence_count_presence_threshold', 8.333)
    return _result('check_evidence_count_presence', adjusted, threshold, False, 'validates evidence_count presence',
                   {'field': 'evidence_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_count_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_count')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_evidence_count_range_threshold', 10.667)
    return _result('check_evidence_count_range', adjusted, threshold, True, 'validates evidence_count range',
                   {'field': 'evidence_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_count_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_count')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_evidence_count_stability_threshold', 13.0)
    return _result('check_evidence_count_stability', adjusted, threshold, True, 'validates evidence_count stability',
                   {'field': 'evidence_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_count_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_count')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_evidence_count_freshness_threshold', 15.333)
    return _result('check_evidence_count_freshness', adjusted, threshold, False, 'validates evidence_count freshness',
                   {'field': 'evidence_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_count_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_count')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_evidence_count_coverage_threshold', 17.667)
    return _result('check_evidence_count_coverage', adjusted, threshold, True, 'validates evidence_count coverage',
                   {'field': 'evidence_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_count_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_count')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_evidence_count_consistency_threshold', 20.0)
    return _result('check_evidence_count_consistency', adjusted, threshold, True, 'validates evidence_count consistency',
                   {'field': 'evidence_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_count_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_count')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_evidence_count_risk_threshold', 22.333)
    return _result('check_evidence_count_risk', adjusted, threshold, False, 'validates evidence_count risk',
                   {'field': 'evidence_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_count_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_count')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_evidence_count_confidence_threshold', 24.667)
    return _result('check_evidence_count_confidence', adjusted, threshold, True, 'validates evidence_count confidence',
                   {'field': 'evidence_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_count_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_count')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_evidence_count_dependency_threshold', 27.0)
    return _result('check_evidence_count_dependency', adjusted, threshold, True, 'validates evidence_count dependency',
                   {'field': 'evidence_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_evidence_count_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'evidence_count')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_evidence_count_readiness_threshold', 29.333)
    return _result('check_evidence_count_readiness', adjusted, threshold, False, 'validates evidence_count readiness',
                   {'field': 'evidence_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_commitment_area_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'commitment_area')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_commitment_area_presence_threshold', 31.667)
    return _result('check_commitment_area_presence', adjusted, threshold, True, 'validates commitment_area presence',
                   {'field': 'commitment_area', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_commitment_area_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'commitment_area')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_commitment_area_range_threshold', 9.667)
    return _result('check_commitment_area_range', adjusted, threshold, True, 'validates commitment_area range',
                   {'field': 'commitment_area', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_commitment_area_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'commitment_area')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_commitment_area_stability_threshold', 12.0)
    return _result('check_commitment_area_stability', adjusted, threshold, False, 'validates commitment_area stability',
                   {'field': 'commitment_area', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_commitment_area_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'commitment_area')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_commitment_area_freshness_threshold', 14.333)
    return _result('check_commitment_area_freshness', adjusted, threshold, True, 'validates commitment_area freshness',
                   {'field': 'commitment_area', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_commitment_area_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'commitment_area')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_commitment_area_coverage_threshold', 16.667)
    return _result('check_commitment_area_coverage', adjusted, threshold, True, 'validates commitment_area coverage',
                   {'field': 'commitment_area', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_commitment_area_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'commitment_area')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_commitment_area_consistency_threshold', 19.0)
    return _result('check_commitment_area_consistency', adjusted, threshold, False, 'validates commitment_area consistency',
                   {'field': 'commitment_area', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_commitment_area_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'commitment_area')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_commitment_area_risk_threshold', 21.333)
    return _result('check_commitment_area_risk', adjusted, threshold, True, 'validates commitment_area risk',
                   {'field': 'commitment_area', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_commitment_area_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'commitment_area')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_commitment_area_confidence_threshold', 23.667)
    return _result('check_commitment_area_confidence', adjusted, threshold, True, 'validates commitment_area confidence',
                   {'field': 'commitment_area', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_commitment_area_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'commitment_area')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_commitment_area_dependency_threshold', 26.0)
    return _result('check_commitment_area_dependency', adjusted, threshold, False, 'validates commitment_area dependency',
                   {'field': 'commitment_area', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_commitment_area_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'commitment_area')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_commitment_area_readiness_threshold', 28.333)
    return _result('check_commitment_area_readiness', adjusted, threshold, True, 'validates commitment_area readiness',
                   {'field': 'commitment_area', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_audit_findings_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'audit_findings')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_audit_findings_presence_threshold', 30.667)
    return _result('check_audit_findings_presence', adjusted, threshold, True, 'validates audit_findings presence',
                   {'field': 'audit_findings', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_audit_findings_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'audit_findings')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_audit_findings_range_threshold', 8.667)
    return _result('check_audit_findings_range', adjusted, threshold, False, 'validates audit_findings range',
                   {'field': 'audit_findings', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_audit_findings_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'audit_findings')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_audit_findings_stability_threshold', 11.0)
    return _result('check_audit_findings_stability', adjusted, threshold, True, 'validates audit_findings stability',
                   {'field': 'audit_findings', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_audit_findings_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'audit_findings')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_audit_findings_freshness_threshold', 13.333)
    return _result('check_audit_findings_freshness', adjusted, threshold, True, 'validates audit_findings freshness',
                   {'field': 'audit_findings', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_audit_findings_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'audit_findings')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_audit_findings_coverage_threshold', 15.667)
    return _result('check_audit_findings_coverage', adjusted, threshold, False, 'validates audit_findings coverage',
                   {'field': 'audit_findings', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_audit_findings_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'audit_findings')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_audit_findings_consistency_threshold', 18.0)
    return _result('check_audit_findings_consistency', adjusted, threshold, True, 'validates audit_findings consistency',
                   {'field': 'audit_findings', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_audit_findings_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'audit_findings')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_audit_findings_risk_threshold', 20.333)
    return _result('check_audit_findings_risk', adjusted, threshold, True, 'validates audit_findings risk',
                   {'field': 'audit_findings', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_audit_findings_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'audit_findings')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_audit_findings_confidence_threshold', 22.667)
    return _result('check_audit_findings_confidence', adjusted, threshold, False, 'validates audit_findings confidence',
                   {'field': 'audit_findings', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_audit_findings_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'audit_findings')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_audit_findings_dependency_threshold', 25.0)
    return _result('check_audit_findings_dependency', adjusted, threshold, True, 'validates audit_findings dependency',
                   {'field': 'audit_findings', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_audit_findings_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'audit_findings')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_audit_findings_readiness_threshold', 27.333)
    return _result('check_audit_findings_readiness', adjusted, threshold, True, 'validates audit_findings readiness',
                   {'field': 'audit_findings', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_gaps_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_gaps')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_unresolved_gaps_presence_threshold', 29.667)
    return _result('check_unresolved_gaps_presence', adjusted, threshold, False, 'validates unresolved_gaps presence',
                   {'field': 'unresolved_gaps', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_gaps_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_gaps')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_unresolved_gaps_range_threshold', 32.0)
    return _result('check_unresolved_gaps_range', adjusted, threshold, True, 'validates unresolved_gaps range',
                   {'field': 'unresolved_gaps', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_gaps_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_gaps')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_unresolved_gaps_stability_threshold', 10.0)
    return _result('check_unresolved_gaps_stability', adjusted, threshold, True, 'validates unresolved_gaps stability',
                   {'field': 'unresolved_gaps', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_gaps_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_gaps')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_unresolved_gaps_freshness_threshold', 12.333)
    return _result('check_unresolved_gaps_freshness', adjusted, threshold, False, 'validates unresolved_gaps freshness',
                   {'field': 'unresolved_gaps', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_gaps_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_gaps')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_unresolved_gaps_coverage_threshold', 14.667)
    return _result('check_unresolved_gaps_coverage', adjusted, threshold, True, 'validates unresolved_gaps coverage',
                   {'field': 'unresolved_gaps', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_gaps_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_gaps')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_unresolved_gaps_consistency_threshold', 17.0)
    return _result('check_unresolved_gaps_consistency', adjusted, threshold, True, 'validates unresolved_gaps consistency',
                   {'field': 'unresolved_gaps', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_gaps_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_gaps')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_unresolved_gaps_risk_threshold', 19.333)
    return _result('check_unresolved_gaps_risk', adjusted, threshold, False, 'validates unresolved_gaps risk',
                   {'field': 'unresolved_gaps', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_gaps_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_gaps')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_unresolved_gaps_confidence_threshold', 21.667)
    return _result('check_unresolved_gaps_confidence', adjusted, threshold, True, 'validates unresolved_gaps confidence',
                   {'field': 'unresolved_gaps', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_gaps_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_gaps')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_unresolved_gaps_dependency_threshold', 24.0)
    return _result('check_unresolved_gaps_dependency', adjusted, threshold, True, 'validates unresolved_gaps dependency',
                   {'field': 'unresolved_gaps', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_gaps_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_gaps')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_unresolved_gaps_readiness_threshold', 26.333)
    return _result('check_unresolved_gaps_readiness', adjusted, threshold, False, 'validates unresolved_gaps readiness',
                   {'field': 'unresolved_gaps', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_beneficiary_share_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'beneficiary_share')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_beneficiary_share_presence_threshold', 28.667)
    return _result('check_beneficiary_share_presence', adjusted, threshold, True, 'validates beneficiary_share presence',
                   {'field': 'beneficiary_share', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_beneficiary_share_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'beneficiary_share')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_beneficiary_share_range_threshold', 31.0)
    return _result('check_beneficiary_share_range', adjusted, threshold, True, 'validates beneficiary_share range',
                   {'field': 'beneficiary_share', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_beneficiary_share_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'beneficiary_share')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_beneficiary_share_stability_threshold', 9.0)
    return _result('check_beneficiary_share_stability', adjusted, threshold, False, 'validates beneficiary_share stability',
                   {'field': 'beneficiary_share', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_beneficiary_share_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'beneficiary_share')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_beneficiary_share_freshness_threshold', 11.333)
    return _result('check_beneficiary_share_freshness', adjusted, threshold, True, 'validates beneficiary_share freshness',
                   {'field': 'beneficiary_share', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_beneficiary_share_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'beneficiary_share')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_beneficiary_share_coverage_threshold', 13.667)
    return _result('check_beneficiary_share_coverage', adjusted, threshold, True, 'validates beneficiary_share coverage',
                   {'field': 'beneficiary_share', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_beneficiary_share_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'beneficiary_share')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_beneficiary_share_consistency_threshold', 16.0)
    return _result('check_beneficiary_share_consistency', adjusted, threshold, False, 'validates beneficiary_share consistency',
                   {'field': 'beneficiary_share', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_beneficiary_share_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'beneficiary_share')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_beneficiary_share_risk_threshold', 18.333)
    return _result('check_beneficiary_share_risk', adjusted, threshold, True, 'validates beneficiary_share risk',
                   {'field': 'beneficiary_share', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_beneficiary_share_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'beneficiary_share')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_beneficiary_share_confidence_threshold', 20.667)
    return _result('check_beneficiary_share_confidence', adjusted, threshold, True, 'validates beneficiary_share confidence',
                   {'field': 'beneficiary_share', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_beneficiary_share_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'beneficiary_share')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_beneficiary_share_dependency_threshold', 23.0)
    return _result('check_beneficiary_share_dependency', adjusted, threshold, False, 'validates beneficiary_share dependency',
                   {'field': 'beneficiary_share', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_beneficiary_share_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'beneficiary_share')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_beneficiary_share_readiness_threshold', 25.333)
    return _result('check_beneficiary_share_readiness', adjusted, threshold, True, 'validates beneficiary_share readiness',
                   {'field': 'beneficiary_share', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_member_code_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'member_code')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_member_code_presence_threshold', 27.667)
    return _result('check_member_code_presence', adjusted, threshold, True, 'validates member_code presence',
                   {'field': 'member_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_member_code_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'member_code')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_member_code_range_threshold', 30.0)
    return _result('check_member_code_range', adjusted, threshold, False, 'validates member_code range',
                   {'field': 'member_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_member_code_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'member_code')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_member_code_stability_threshold', 8.0)
    return _result('check_member_code_stability', adjusted, threshold, True, 'validates member_code stability',
                   {'field': 'member_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_member_code_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'member_code')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_member_code_freshness_threshold', 10.333)
    return _result('check_member_code_freshness', adjusted, threshold, True, 'validates member_code freshness',
                   {'field': 'member_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_member_code_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'member_code')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_member_code_coverage_threshold', 12.667)
    return _result('check_member_code_coverage', adjusted, threshold, False, 'validates member_code coverage',
                   {'field': 'member_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_member_code_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'member_code')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_member_code_consistency_threshold', 15.0)
    return _result('check_member_code_consistency', adjusted, threshold, True, 'validates member_code consistency',
                   {'field': 'member_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_member_code_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'member_code')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_member_code_risk_threshold', 17.333)
    return _result('check_member_code_risk', adjusted, threshold, True, 'validates member_code risk',
                   {'field': 'member_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_member_code_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'member_code')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_member_code_confidence_threshold', 19.667)
    return _result('check_member_code_confidence', adjusted, threshold, False, 'validates member_code confidence',
                   {'field': 'member_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_member_code_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'member_code')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_member_code_dependency_threshold', 22.0)
    return _result('check_member_code_dependency', adjusted, threshold, True, 'validates member_code dependency',
                   {'field': 'member_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_member_code_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'member_code')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_member_code_readiness_threshold', 24.333)
    return _result('check_member_code_readiness', adjusted, threshold, True, 'validates member_code readiness',
                   {'field': 'member_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deadline_days_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deadline_days')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_deadline_days_presence_threshold', 26.667)
    return _result('check_deadline_days_presence', adjusted, threshold, False, 'validates deadline_days presence',
                   {'field': 'deadline_days', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deadline_days_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deadline_days')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_deadline_days_range_threshold', 29.0)
    return _result('check_deadline_days_range', adjusted, threshold, True, 'validates deadline_days range',
                   {'field': 'deadline_days', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deadline_days_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deadline_days')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_deadline_days_stability_threshold', 31.333)
    return _result('check_deadline_days_stability', adjusted, threshold, True, 'validates deadline_days stability',
                   {'field': 'deadline_days', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deadline_days_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deadline_days')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_deadline_days_freshness_threshold', 9.333)
    return _result('check_deadline_days_freshness', adjusted, threshold, False, 'validates deadline_days freshness',
                   {'field': 'deadline_days', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deadline_days_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deadline_days')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_deadline_days_coverage_threshold', 11.667)
    return _result('check_deadline_days_coverage', adjusted, threshold, True, 'validates deadline_days coverage',
                   {'field': 'deadline_days', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deadline_days_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deadline_days')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_deadline_days_consistency_threshold', 14.0)
    return _result('check_deadline_days_consistency', adjusted, threshold, True, 'validates deadline_days consistency',
                   {'field': 'deadline_days', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deadline_days_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deadline_days')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_deadline_days_risk_threshold', 16.333)
    return _result('check_deadline_days_risk', adjusted, threshold, False, 'validates deadline_days risk',
                   {'field': 'deadline_days', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deadline_days_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deadline_days')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_deadline_days_confidence_threshold', 18.667)
    return _result('check_deadline_days_confidence', adjusted, threshold, True, 'validates deadline_days confidence',
                   {'field': 'deadline_days', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deadline_days_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deadline_days')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_deadline_days_dependency_threshold', 21.0)
    return _result('check_deadline_days_dependency', adjusted, threshold, True, 'validates deadline_days dependency',
                   {'field': 'deadline_days', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_deadline_days_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'deadline_days')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_deadline_days_readiness_threshold', 23.333)
    return _result('check_deadline_days_readiness', adjusted, threshold, False, 'validates deadline_days readiness',
                   {'field': 'deadline_days', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_data_quality_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'data_quality')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_data_quality_presence_threshold', 25.667)
    return _result('check_data_quality_presence', adjusted, threshold, True, 'validates data_quality presence',
                   {'field': 'data_quality', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_data_quality_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'data_quality')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_data_quality_range_threshold', 28.0)
    return _result('check_data_quality_range', adjusted, threshold, True, 'validates data_quality range',
                   {'field': 'data_quality', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_data_quality_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'data_quality')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_data_quality_stability_threshold', 30.333)
    return _result('check_data_quality_stability', adjusted, threshold, False, 'validates data_quality stability',
                   {'field': 'data_quality', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_data_quality_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'data_quality')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_data_quality_freshness_threshold', 8.333)
    return _result('check_data_quality_freshness', adjusted, threshold, True, 'validates data_quality freshness',
                   {'field': 'data_quality', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_data_quality_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'data_quality')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_data_quality_coverage_threshold', 10.667)
    return _result('check_data_quality_coverage', adjusted, threshold, True, 'validates data_quality coverage',
                   {'field': 'data_quality', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_data_quality_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'data_quality')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_data_quality_consistency_threshold', 13.0)
    return _result('check_data_quality_consistency', adjusted, threshold, False, 'validates data_quality consistency',
                   {'field': 'data_quality', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_data_quality_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'data_quality')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_data_quality_risk_threshold', 15.333)
    return _result('check_data_quality_risk', adjusted, threshold, True, 'validates data_quality risk',
                   {'field': 'data_quality', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_data_quality_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'data_quality')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_data_quality_confidence_threshold', 17.667)
    return _result('check_data_quality_confidence', adjusted, threshold, True, 'validates data_quality confidence',
                   {'field': 'data_quality', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_data_quality_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'data_quality')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_data_quality_dependency_threshold', 20.0)
    return _result('check_data_quality_dependency', adjusted, threshold, False, 'validates data_quality dependency',
                   {'field': 'data_quality', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_data_quality_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'data_quality')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_data_quality_readiness_threshold', 22.333)
    return _result('check_data_quality_readiness', adjusted, threshold, True, 'validates data_quality readiness',
                   {'field': 'data_quality', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_score_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_score')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_review_score_presence_threshold', 24.667)
    return _result('check_review_score_presence', adjusted, threshold, True, 'validates review_score presence',
                   {'field': 'review_score', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_score_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_score')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_review_score_range_threshold', 27.0)
    return _result('check_review_score_range', adjusted, threshold, False, 'validates review_score range',
                   {'field': 'review_score', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_score_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_score')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_review_score_stability_threshold', 29.333)
    return _result('check_review_score_stability', adjusted, threshold, True, 'validates review_score stability',
                   {'field': 'review_score', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_score_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_score')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_review_score_freshness_threshold', 31.667)
    return _result('check_review_score_freshness', adjusted, threshold, True, 'validates review_score freshness',
                   {'field': 'review_score', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_score_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_score')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_review_score_coverage_threshold', 9.667)
    return _result('check_review_score_coverage', adjusted, threshold, False, 'validates review_score coverage',
                   {'field': 'review_score', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_score_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_score')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_review_score_consistency_threshold', 12.0)
    return _result('check_review_score_consistency', adjusted, threshold, True, 'validates review_score consistency',
                   {'field': 'review_score', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_score_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_score')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_review_score_risk_threshold', 14.333)
    return _result('check_review_score_risk', adjusted, threshold, True, 'validates review_score risk',
                   {'field': 'review_score', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_score_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_score')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_review_score_confidence_threshold', 16.667)
    return _result('check_review_score_confidence', adjusted, threshold, False, 'validates review_score confidence',
                   {'field': 'review_score', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_score_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_score')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_review_score_dependency_threshold', 19.0)
    return _result('check_review_score_dependency', adjusted, threshold, True, 'validates review_score dependency',
                   {'field': 'review_score', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_score_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_score')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_review_score_readiness_threshold', 21.333)
    return _result('check_review_score_readiness', adjusted, threshold, True, 'validates review_score readiness',
                   {'field': 'review_score', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_status_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_status')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_public_status_presence_threshold', 23.667)
    return _result('check_public_status_presence', adjusted, threshold, False, 'validates public_status presence',
                   {'field': 'public_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_status_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_status')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_public_status_range_threshold', 26.0)
    return _result('check_public_status_range', adjusted, threshold, True, 'validates public_status range',
                   {'field': 'public_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_status_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_status')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_public_status_stability_threshold', 28.333)
    return _result('check_public_status_stability', adjusted, threshold, True, 'validates public_status stability',
                   {'field': 'public_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_status_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_status')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_public_status_freshness_threshold', 30.667)
    return _result('check_public_status_freshness', adjusted, threshold, False, 'validates public_status freshness',
                   {'field': 'public_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_status_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_status')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_public_status_coverage_threshold', 8.667)
    return _result('check_public_status_coverage', adjusted, threshold, True, 'validates public_status coverage',
                   {'field': 'public_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_status_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_status')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_public_status_consistency_threshold', 11.0)
    return _result('check_public_status_consistency', adjusted, threshold, True, 'validates public_status consistency',
                   {'field': 'public_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_status_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_status')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_public_status_risk_threshold', 13.333)
    return _result('check_public_status_risk', adjusted, threshold, False, 'validates public_status risk',
                   {'field': 'public_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_status_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_status')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_public_status_confidence_threshold', 15.667)
    return _result('check_public_status_confidence', adjusted, threshold, True, 'validates public_status confidence',
                   {'field': 'public_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_status_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_status')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_public_status_dependency_threshold', 18.0)
    return _result('check_public_status_dependency', adjusted, threshold, True, 'validates public_status dependency',
                   {'field': 'public_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_status_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_status')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_public_status_readiness_threshold', 20.333)
    return _result('check_public_status_readiness', adjusted, threshold, False, 'validates public_status readiness',
                   {'field': 'public_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

RULES: tuple[RuleFunction, ...] = (
    check_progress_pct_presence,
    check_progress_pct_range,
    check_progress_pct_stability,
    check_progress_pct_freshness,
    check_progress_pct_coverage,
    check_progress_pct_consistency,
    check_progress_pct_risk,
    check_progress_preview_score,
    check_progress_pct_dependency,
    check_progress_pct_readiness,
    check_legal_readiness_presence,
    check_legal_readiness_range,
    check_legal_readiness_stability,
    check_legal_readiness_freshness,
    check_legal_readiness_coverage,
    check_legal_readiness_consistency,
    check_legal_readiness_risk,
    check_legal_readiness_confidence,
    check_legal_readiness_dependency,
    check_legal_readiness_readiness,
    check_evidence_count_presence,
    check_evidence_count_range,
    check_evidence_count_stability,
    check_evidence_count_freshness,
    check_evidence_count_coverage,
    check_evidence_count_consistency,
    check_evidence_count_risk,
    check_evidence_count_confidence,
    check_evidence_count_dependency,
    check_evidence_count_readiness,
    check_commitment_area_presence,
    check_commitment_area_range,
    check_commitment_area_stability,
    check_commitment_area_freshness,
    check_commitment_area_coverage,
    check_commitment_area_consistency,
    check_commitment_area_risk,
    check_commitment_area_confidence,
    check_commitment_area_dependency,
    check_commitment_area_readiness,
    check_audit_findings_presence,
    check_audit_findings_range,
    check_audit_findings_stability,
    check_audit_findings_freshness,
    check_audit_findings_coverage,
    check_audit_findings_consistency,
    check_audit_findings_risk,
    check_audit_findings_confidence,
    check_audit_findings_dependency,
    check_audit_findings_readiness,
    check_unresolved_gaps_presence,
    check_unresolved_gaps_range,
    check_unresolved_gaps_stability,
    check_unresolved_gaps_freshness,
    check_unresolved_gaps_coverage,
    check_unresolved_gaps_consistency,
    check_unresolved_gaps_risk,
    check_unresolved_gaps_confidence,
    check_unresolved_gaps_dependency,
    check_unresolved_gaps_readiness,
    check_beneficiary_share_presence,
    check_beneficiary_share_range,
    check_beneficiary_share_stability,
    check_beneficiary_share_freshness,
    check_beneficiary_share_coverage,
    check_beneficiary_share_consistency,
    check_beneficiary_share_risk,
    check_beneficiary_share_confidence,
    check_beneficiary_share_dependency,
    check_beneficiary_share_readiness,
    check_member_code_presence,
    check_member_code_range,
    check_member_code_stability,
    check_member_code_freshness,
    check_member_code_coverage,
    check_member_code_consistency,
    check_member_code_risk,
    check_member_code_confidence,
    check_member_code_dependency,
    check_member_code_readiness,
    check_deadline_days_presence,
    check_deadline_days_range,
    check_deadline_days_stability,
    check_deadline_days_freshness,
    check_deadline_days_coverage,
    check_deadline_days_consistency,
    check_deadline_days_risk,
    check_deadline_days_confidence,
    check_deadline_days_dependency,
    check_deadline_days_readiness,
    check_data_quality_presence,
    check_data_quality_range,
    check_data_quality_stability,
    check_data_quality_freshness,
    check_data_quality_coverage,
    check_data_quality_consistency,
    check_data_quality_risk,
    check_data_quality_confidence,
    check_data_quality_dependency,
    check_data_quality_readiness,
    check_review_score_presence,
    check_review_score_range,
    check_review_score_stability,
    check_review_score_freshness,
    check_review_score_coverage,
    check_review_score_consistency,
    check_review_score_risk,
    check_review_score_confidence,
    check_review_score_dependency,
    check_review_score_readiness,
    check_public_status_presence,
    check_public_status_range,
    check_public_status_stability,
    check_public_status_freshness,
    check_public_status_coverage,
    check_public_status_consistency,
    check_public_status_risk,
    check_public_status_confidence,
    check_public_status_dependency,
    check_public_status_readiness,
)

RULE_INDEX = {rule.__name__: rule for rule in RULES}

def evaluate(record: DomainRecord, context: Mapping[str, Any] | None = None) -> tuple[RuleResult, ...]:
    context = context or {}
    return tuple(rule(record, context) for rule in RULES)

def summarize(results: tuple[RuleResult, ...]) -> dict[str, Any]:
    if not results:
        return {'score': 0.0, 'passed': 0, 'failed': 0, 'critical': 0}
    return {'score': sum(item.score for item in results) / len(results),
            'passed': sum(item.passed for item in results),
            'failed': sum(not item.passed for item in results),
            'critical': sum(item.severity == 'critical' for item in results)}
