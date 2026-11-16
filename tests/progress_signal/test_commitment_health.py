from __future__ import annotations
import unittest
from treaty_tracker.progress_signal.commitment_health import commitment_health, peer_distribution
class Record:
    def __init__(self, payload): self.payload = payload
class SignalTests(unittest.TestCase):
    def setUp(self): self.payload = {'progress_pct': 75, 'legal_readiness': 0.8, 'evidence_count': 10, 'commitment_area': 'safety', 'audit_findings': 1, 'unresolved_gaps': 1, 'beneficiary_share': 0.65, 'member_code': 'member-a', 'deadline_days': 180, 'data_quality': 0.9, 'review_score': 0.85, 'public_status': 'reported'}
    def test_signal_is_bounded_and_explainable(self):
        signal = commitment_health(self.payload)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)
        self.assertIn(signal.severity, {'info', 'warning', 'critical'})
        self.assertTrue({'legal', 'deadline_days', 'progress'}.issubset(signal.evidence))
    def test_peer_distribution_uses_business_group(self):
        other = dict(self.payload); other['member_code'] = 'group-b'
        result = peer_distribution([Record(self.payload), Record(other)])
        self.assertEqual(result['count'], 2)
        self.assertIn('members', result)
    def test_material_business_change_is_observable(self):
        changed = dict(self.payload); changed['deadline_days'] = -1
        self.assertNotEqual(commitment_health(changed).score, commitment_health(self.payload).score)
    def test_business_variant_1(self):
        changed = dict(self.payload)
        changed['evidence_count'] = self.payload['evidence_count']
        signal = commitment_health(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_2(self):
        changed = dict(self.payload)
        changed['commitment_area'] = self.payload['commitment_area']
        signal = commitment_health(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_3(self):
        changed = dict(self.payload)
        changed['audit_findings'] = self.payload['audit_findings']
        signal = commitment_health(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_4(self):
        changed = dict(self.payload)
        changed['unresolved_gaps'] = self.payload['unresolved_gaps']
        signal = commitment_health(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_5(self):
        changed = dict(self.payload)
        changed['beneficiary_share'] = self.payload['beneficiary_share']
        signal = commitment_health(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

if __name__ == '__main__': unittest.main()
