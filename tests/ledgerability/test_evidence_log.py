from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path

from treaty_tracker.commitments.pledge import ContractError, DomainRecord, RuleResult, bounded, stable_hash
from treaty_tracker.assurance.compliance_rules import RULE_INDEX, evaluate, summarize
from treaty_tracker.quality.calibration import METRICS, compare, grouped_metrics, metric_vector, portfolio, record_score

FIELDS = ['progress_pct', 'legal_readiness', 'evidence_count', 'commitment_area', 'audit_findings', 'unresolved_gaps', 'beneficiary_share', 'member_code', 'deadline_days', 'data_quality', 'review_score', 'public_status']

def make_record(seed: int = 1, state: str | None = None) -> DomainRecord:
    payload = {}
    for index, field in enumerate(FIELDS):
        selector = (seed + index) % 4
        if selector == 0:
            payload[field] = seed * 9.5 + index * 1.25
        elif selector == 1:
            payload[field] = f'{field}-{seed % 5}'
        elif selector == 2:
            payload[field] = (seed + index) / 10.0
        else:
            payload[field] = (seed + index) % 2 == 0
    return DomainRecord(f'commitment_case-{seed:03d}', payload, state or 'pledged')

class RuleGroup2Tests(unittest.TestCase):
    def test_evaluate_returns_complete_catalog(self):
        record = make_record()
        results = evaluate(record, {})
        self.assertEqual(len(results), len(RULE_INDEX))
        self.assertTrue(all(isinstance(item, RuleResult) for item in results))
        self.assertTrue(all(0.0 <= item.score <= 1.0 for item in results))

    def test_summary_is_conservative_and_counted(self):
        results = evaluate(make_record(2), {'risk_weight': 0.8})
        summary = summarize(results)
        self.assertEqual(summary['passed'] + summary['failed'], len(results))
        self.assertGreaterEqual(summary['critical'], 0)
        self.assertGreaterEqual(summary['score'], 0.0)
        self.assertLessEqual(summary['score'], 1.0)

    def test_check_commitment_area_presence_02_01(self):
        record = make_record(4)
        result = RULE_INDEX['check_commitment_area_presence'](record, {'check_commitment_area_presence_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_commitment_area_presence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_commitment_area_range_02_02(self):
        record = make_record(5)
        result = RULE_INDEX['check_commitment_area_range'](record, {'check_commitment_area_range_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_commitment_area_range')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_commitment_area_stability_02_03(self):
        record = make_record(6)
        result = RULE_INDEX['check_commitment_area_stability'](record, {'check_commitment_area_stability_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_commitment_area_stability')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_commitment_area_freshness_02_04(self):
        record = make_record(7)
        result = RULE_INDEX['check_commitment_area_freshness'](record, {'check_commitment_area_freshness_threshold': 4.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_commitment_area_freshness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_commitment_area_coverage_02_05(self):
        record = make_record(8)
        result = RULE_INDEX['check_commitment_area_coverage'](record, {'check_commitment_area_coverage_threshold': 5.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_commitment_area_coverage')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_commitment_area_consistency_02_06(self):
        record = make_record(9)
        result = RULE_INDEX['check_commitment_area_consistency'](record, {'check_commitment_area_consistency_threshold': 6.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_commitment_area_consistency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_commitment_area_risk_02_07(self):
        record = make_record(10)
        result = RULE_INDEX['check_commitment_area_risk'](record, {'check_commitment_area_risk_threshold': 7.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_commitment_area_risk')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_commitment_area_confidence_02_08(self):
        record = make_record(11)
        result = RULE_INDEX['check_commitment_area_confidence'](record, {'check_commitment_area_confidence_threshold': 8.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_commitment_area_confidence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_commitment_area_dependency_02_09(self):
        record = make_record(12)
        result = RULE_INDEX['check_commitment_area_dependency'](record, {'check_commitment_area_dependency_threshold': 9.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_commitment_area_dependency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_commitment_area_readiness_02_10(self):
        record = make_record(13)
        result = RULE_INDEX['check_commitment_area_readiness'](record, {'check_commitment_area_readiness_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_commitment_area_readiness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_audit_findings_presence_02_11(self):
        record = make_record(14)
        result = RULE_INDEX['check_audit_findings_presence'](record, {'check_audit_findings_presence_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_audit_findings_presence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_audit_findings_range_02_12(self):
        record = make_record(15)
        result = RULE_INDEX['check_audit_findings_range'](record, {'check_audit_findings_range_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_audit_findings_range')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_audit_findings_stability_02_13(self):
        record = make_record(16)
        result = RULE_INDEX['check_audit_findings_stability'](record, {'check_audit_findings_stability_threshold': 4.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_audit_findings_stability')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_audit_findings_freshness_02_14(self):
        record = make_record(17)
        result = RULE_INDEX['check_audit_findings_freshness'](record, {'check_audit_findings_freshness_threshold': 5.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_audit_findings_freshness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_audit_findings_coverage_02_15(self):
        record = make_record(18)
        result = RULE_INDEX['check_audit_findings_coverage'](record, {'check_audit_findings_coverage_threshold': 6.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_audit_findings_coverage')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_audit_findings_consistency_02_16(self):
        record = make_record(19)
        result = RULE_INDEX['check_audit_findings_consistency'](record, {'check_audit_findings_consistency_threshold': 7.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_audit_findings_consistency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_audit_findings_risk_02_17(self):
        record = make_record(20)
        result = RULE_INDEX['check_audit_findings_risk'](record, {'check_audit_findings_risk_threshold': 8.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_audit_findings_risk')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_audit_findings_confidence_02_18(self):
        record = make_record(21)
        result = RULE_INDEX['check_audit_findings_confidence'](record, {'check_audit_findings_confidence_threshold': 9.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_audit_findings_confidence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_audit_findings_dependency_02_19(self):
        record = make_record(22)
        result = RULE_INDEX['check_audit_findings_dependency'](record, {'check_audit_findings_dependency_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_audit_findings_dependency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_audit_findings_readiness_02_20(self):
        record = make_record(23)
        result = RULE_INDEX['check_audit_findings_readiness'](record, {'check_audit_findings_readiness_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_audit_findings_readiness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unresolved_gaps_presence_02_21(self):
        record = make_record(24)
        result = RULE_INDEX['check_unresolved_gaps_presence'](record, {'check_unresolved_gaps_presence_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unresolved_gaps_presence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unresolved_gaps_range_02_22(self):
        record = make_record(25)
        result = RULE_INDEX['check_unresolved_gaps_range'](record, {'check_unresolved_gaps_range_threshold': 4.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unresolved_gaps_range')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unresolved_gaps_stability_02_23(self):
        record = make_record(26)
        result = RULE_INDEX['check_unresolved_gaps_stability'](record, {'check_unresolved_gaps_stability_threshold': 5.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unresolved_gaps_stability')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unresolved_gaps_freshness_02_24(self):
        record = make_record(27)
        result = RULE_INDEX['check_unresolved_gaps_freshness'](record, {'check_unresolved_gaps_freshness_threshold': 6.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unresolved_gaps_freshness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unresolved_gaps_coverage_02_25(self):
        record = make_record(28)
        result = RULE_INDEX['check_unresolved_gaps_coverage'](record, {'check_unresolved_gaps_coverage_threshold': 7.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unresolved_gaps_coverage')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unresolved_gaps_consistency_02_26(self):
        record = make_record(29)
        result = RULE_INDEX['check_unresolved_gaps_consistency'](record, {'check_unresolved_gaps_consistency_threshold': 8.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unresolved_gaps_consistency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unresolved_gaps_risk_02_27(self):
        record = make_record(30)
        result = RULE_INDEX['check_unresolved_gaps_risk'](record, {'check_unresolved_gaps_risk_threshold': 9.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unresolved_gaps_risk')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unresolved_gaps_confidence_02_28(self):
        record = make_record(31)
        result = RULE_INDEX['check_unresolved_gaps_confidence'](record, {'check_unresolved_gaps_confidence_threshold': 1.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unresolved_gaps_confidence')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unresolved_gaps_dependency_02_29(self):
        record = make_record(32)
        result = RULE_INDEX['check_unresolved_gaps_dependency'](record, {'check_unresolved_gaps_dependency_threshold': 2.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unresolved_gaps_dependency')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

    def test_check_unresolved_gaps_readiness_02_30(self):
        record = make_record(33)
        result = RULE_INDEX['check_unresolved_gaps_readiness'](record, {'check_unresolved_gaps_readiness_threshold': 3.0})
        self.assertIsInstance(result, RuleResult)
        self.assertEqual(result.code, 'check_unresolved_gaps_readiness')
        self.assertIn(result.severity, {'info', 'warning', 'error', 'critical'})
        self.assertTrue(math.isfinite(result.score))
        self.assertIn('field', result.evidence)
        self.assertIn('threshold', result.evidence)

class MetricGroup2Tests(unittest.TestCase):
    def test_metric_vector_is_deterministic(self):
        record = make_record(11)
        first = metric_vector(record, {})
        second = metric_vector(record, {})
        self.assertEqual(first, second)
        self.assertEqual(set(first), set(METRICS))
        self.assertTrue(all(0.0 <= value <= 1.0 for value in first.values()))

    def test_grouped_metrics_match_business_catalog(self):
        grouped = grouped_metrics(make_record(4), {})
        self.assertEqual(set(grouped), {'member_drift', 'false_release_risk', 'recall_exposure', 'calibration_need', 'inspection_coverage', 'feedback_latency', 'lot_value', 'grade_consistency'})
        self.assertTrue(all(math.isfinite(value) for value in grouped.values()))

    def test_portfolio_orders_by_descending_score(self):
        result = portfolio([make_record(2), make_record(3), make_record(4)])
        scores = [row['score'] for row in result['rows']]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(result['count'], 3)
        self.assertGreaterEqual(result['maximum'], result['minimum'])

    def test_compare_has_all_metric_deltas(self):
        result = compare(make_record(5), make_record(6))
        self.assertEqual(set(result['delta']), {'member_drift', 'false_release_risk', 'recall_exposure', 'calibration_need', 'inspection_coverage', 'feedback_latency', 'lot_value', 'grade_consistency'})
        self.assertIn(result['winner'], {make_record(5).record_id, make_record(6).record_id})

    def test_score_fingerprint_changes_with_payload(self):
        left = record_score(make_record(7))
        right = record_score(make_record(8))
        self.assertNotEqual(left['fingerprint'], right['fingerprint'])
        self.assertNotEqual(stable_hash(left['metrics']), stable_hash(right['metrics']))

if __name__ == '__main__':
    unittest.main()
