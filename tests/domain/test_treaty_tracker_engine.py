from __future__ import annotations

import unittest
from treaty_tracker.commitments.pledge import DomainRecord
from treaty_tracker.harmonization.progress_model import commitment_calibration, derive_context, fulfillment_probability, member_drift


class Repo:
    def __init__(self, rows): self.rows = rows
    def list_records(self): return self.rows


class FusionTests(unittest.TestCase):
    def record(self, key, origin="gx"):
        return DomainRecord(key, {"progress_pct": 82, "legal_readiness": 74, "evidence_count": 10, "commitment_area": "governance",
            "audit_findings": 1, "unresolved_gaps": 0.5, "beneficiary_share": 0.8, "member_code": origin,
            "deadline_days": 18, "data_quality": 0.98, "review_score": 0.94, "public_status": "reviewed"})

    def test_probabilities_sum_to_one(self):
        values = fulfillment_probability(self.record("a"))
        self.assertAlmostEqual(sum(values.values()), 1.0)
        self.assertGreater(values["fulfilled"], values["at_risk"])

    def test_batch_and_member_drift(self):
        rows = [self.record("a", "north"), self.record("b", "south")]
        self.assertEqual(commitment_calibration(rows)["sample_count"], 2.0)
        self.assertEqual(member_drift(rows)["origin_count"], 2.0)
        self.assertIn("calibration_need_weight", derive_context(rows[0], Repo(rows)))
