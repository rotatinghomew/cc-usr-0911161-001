from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from treaty_tracker.commitments.pledge import ContractError, DomainRecord
from treaty_tracker.ledger.evidence_log import Repository
from treaty_tracker.trends.comparable_trends import (
    GROUP_DIMENSIONS,
    SCHEMA_VERSION,
    build_observations,
    build_trend_analysis,
    period_key,
    verify_trend_analysis,
)


def make_payload(progress: float, member: str = "m1", area: str = "safety") -> dict:
    return {"progress_pct": progress, "legal_readiness": 0.8, "evidence_count": 10,
            "commitment_area": area, "audit_findings": 1, "unresolved_gaps": 1,
            "beneficiary_share": 0.6, "member_code": member, "deadline_days": 180,
            "data_quality": 0.9, "review_score": 0.8, "public_status": "reported"}


class MutableClock:
    def __init__(self, stamp: str):
        self.stamp = stamp

    def __call__(self) -> str:
        return self.stamp


class TrendRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / "ledger.sqlite3"
        self.repository = Repository(self.database, clock=MutableClock("2026-09-10T00:00:00+00:00"))

    def test_period_key_uses_calendar_month(self):
        self.assertEqual(period_key("2026-09-10T08:30:00+00:00"), "2026-09")
        self.assertEqual(period_key("2026-10-01T00:00:00Z"), "2026-10")
        for invalid in ("", "2026/09/01", "2026-13-01T00:00:00+00:00", "not-a-timestamp"):
            with self.assertRaises(ContractError):
                period_key(invalid)

    def test_observations_are_anchored_to_record_saved_events(self):
        self.repository.save_record(DomainRecord("case-a", make_payload(40)))
        observations = build_observations(self.repository)
        self.assertEqual(len(observations), 1)
        observation = observations[0]
        self.assertEqual(observation["period_source"], "record.saved.event.created_at")
        self.assertIsNotNone(observation["event_id"])
        self.assertTrue(observation["event_hash"])
        self.assertEqual(observation["period"], "2026-09")
        self.assertEqual(observation["groups"], {"member_code": "m1", "commitment_area": "safety"})

    def test_clock_drives_submission_period_without_touching_chain(self):
        self.repository.save_record(DomainRecord("case-a", make_payload(40)))
        self.repository.clock.stamp = "2026-10-05T00:00:00+00:00"
        self.repository.save_record(DomainRecord("case-a", make_payload(70), version=2), expected_version=1)
        self.assertEqual(self.repository.verify_chain(), [])
        observations = build_observations(self.repository)
        self.assertEqual({row["period"] for row in observations}, {"2026-09", "2026-10"})

    def test_decision_event_carries_adopted_version_fingerprint(self):
        record = DomainRecord("case-a", make_payload(40))
        self.repository.save_record(record)
        from treaty_tracker.lifecycle.fulfillment import decide

        self.repository.save_decision(decide(record))
        index = self.repository.decision_event_index()
        self.assertIn(("case-a", 1), index)
        self.assertEqual(index[("case-a", 1)]["payload"]["record_version"], 1)
        self.assertEqual(index[("case-a", 1)]["payload"]["record_fingerprint"], record.fingerprint)


class MultiPeriodTrendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / "ledger.sqlite3"
        self.clock = MutableClock("2026-09-10T00:00:00+00:00")
        self.repository = Repository(self.database, clock=self.clock)
        self._seed()

    def _seed(self) -> None:
        self.repository.save_record(DomainRecord("case-a", make_payload(40, "m1", "safety")))
        self.repository.save_record(DomainRecord("case-b", make_payload(50, "m2", "governance")))
        self.clock.stamp = "2026-10-05T00:00:00+00:00"
        # 10 月：case-a 被补交/更正两次，case-b 更正一次，case-c 为新进入统计对象
        self.repository.save_record(DomainRecord("case-a", make_payload(70, "m1", "safety"), version=2),
                                    expected_version=1)
        self.repository.save_record(DomainRecord("case-a", make_payload(80, "m1", "safety"), version=3),
                                    expected_version=2)
        self.repository.save_record(DomainRecord("case-b", make_payload(55, "m2", "governance"), version=2),
                                    expected_version=1)
        self.repository.save_record(DomainRecord("case-c", make_payload(30, "m1", "safety")))

    def test_versions_within_same_period_are_counted_once(self):
        report = build_trend_analysis(self.repository)
        self.assertEqual([item["period"] for item in report["periods"]], ["2026-09", "2026-10"])
        october = next(item for item in report["periods"] if item["period"] == "2026-10")
        # 4 个候选版本只对应 3 个事项，分母按事项去重，版本不重复计数
        self.assertEqual(october["candidate_version_count"], 4)
        self.assertEqual(october["distinct_record_count"], 3)
        self.assertEqual(october["denominator"], 3)
        adopted_a = next(item for item in report["adopted_versions"]
                         if item["record_id"] == "case-a" and item["period"] == "2026-10")
        self.assertEqual(adopted_a["adopted_version"], 3)
        self.assertEqual(adopted_a["candidate_versions"], [2, 3])
        self.assertIsNotNone(adopted_a["evidence_event_id"])

    def test_comparison_uses_matched_cohort_and_excludes_new_entrants(self):
        report = build_trend_analysis(self.repository)
        portfolio = next(item for item in report["comparisons"]
                         if item["scope"] == "portfolio" and item["scope_value"] == "all")
        self.assertTrue(portfolio["comparable"])
        self.assertEqual(portfolio["matched_record_ids"], ["case-a", "case-b"])
        self.assertEqual(portfolio["matched_denominator"], 2)
        self.assertEqual(portfolio["entered_record_ids"], ["case-c"])
        self.assertEqual(portfolio["exited_record_ids"], [])
        self.assertEqual(portfolio["prior_denominator"], 2)
        self.assertEqual(portfolio["current_denominator"], 3)
        # 两个匹配事项分数均上升，改善率以匹配队列（而非 3）为分母
        self.assertEqual(portfolio["improved_count"], 2)
        self.assertEqual(portfolio["improvement_rate"], 1.0)
        self.assertEqual(
            portfolio["improved_count"] + portfolio["declined_count"] + portfolio["unchanged_count"],
            portfolio["matched_denominator"])

    def test_group_comparisons_cover_member_and_domain_dimensions(self):
        report = build_trend_analysis(self.repository)
        scopes = {(item["scope"], item["scope_value"]) for item in report["comparisons"]}
        self.assertIn(("member_code", "m1"), scopes)
        self.assertIn(("member_code", "m2"), scopes)
        self.assertIn(("commitment_area", "safety"), scopes)
        self.assertIn(("commitment_area", "governance"), scopes)
        member_m1 = next(item for item in report["comparisons"]
                         if item["scope"] == "member_code" and item["scope_value"] == "m1")
        # case-c 是新进入者，m1 的匹配队列仍只有 case-a
        self.assertEqual(member_m1["matched_record_ids"], ["case-a"])
        self.assertEqual(member_m1["entered_record_ids"], ["case-c"])
        self.assertEqual(member_m1["improvement_rate"], 1.0)

    def test_report_documents_methodology_and_freezing_hash(self):
        report = build_trend_analysis(self.repository)
        self.assertEqual(report["methodology"]["schema_version"], SCHEMA_VERSION)
        self.assertEqual(report["methodology"]["group_dimensions"], list(GROUP_DIMENSIONS))
        self.assertEqual(report["methodology"]["version_adoption"],
                         "latest-version-per-record-within-period")
        self.assertTrue(report["report_hash"])
        self.assertEqual(verify_trend_analysis(report, self.repository), [])
        # 时钟注入不破坏哈希链，证据事件本身仍可独立核验
        self.assertEqual(self.repository.verify_chain(), [])

    def test_missing_matched_evidence_blocks_improvement_estimation(self):
        # 让 case-b 在 10 月切换到新成员组，原成员组没有跨期共同事项
        self.clock.stamp = "2026-10-20T00:00:00+00:00"
        self.repository.save_record(DomainRecord("case-b", make_payload(55, "m3", "governance"), version=3),
                                    expected_version=2)
        report = build_trend_analysis(self.repository)
        m2 = next(item for item in report["comparisons"]
                  if item["scope"] == "member_code" and item["scope_value"] == "m2")
        self.assertFalse(m2["comparable"])
        self.assertEqual(m2["matched_denominator"], 0)
        self.assertIsNone(m2["improvement_rate"])
        self.assertIsNone(m2["average_score_delta"])
        self.assertIn("not estimated", m2["reason"])
        self.assertEqual(verify_trend_analysis(report, self.repository), [])

    def test_verification_detects_frozen_report_tampering(self):
        report = build_trend_analysis(self.repository)

        fabricated = json.loads(json.dumps(report))
        # 强行把可比比较改成不可比并虚构改善率，核验必须拒绝推算
        fabricated["comparisons"][0]["comparable"] = False
        fabricated["comparisons"][0]["improvement_rate"] = 0.5
        self.assertTrue(any("null" in error for error in verify_trend_analysis(fabricated, self.repository)))

        altered_denominator = json.loads(json.dumps(report))
        altered_denominator["periods"][0]["denominator"] = 99
        self.assertTrue(any("denominator disagrees" in error
                            for error in verify_trend_analysis(altered_denominator, self.repository)))

        wrong_adoption = json.loads(json.dumps(report))
        for item in wrong_adoption["adopted_versions"]:
            if item["record_id"] == "case-a" and item["period"] == "2026-10":
                item["adopted_version"] = 2
        self.assertTrue(any("adopted version disagrees" in error
                            for error in verify_trend_analysis(wrong_adoption, self.repository)))

        body_change = json.loads(json.dumps(report))
        body_change["periods"][0]["average_health_score"] = 0.999
        self.assertIn("trend-analysis: report hash mismatch",
                      verify_trend_analysis(body_change, self.repository))


class EmptyAndSinglePeriodTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / "ledger.sqlite3"
        self.repository = Repository(self.database)

    def test_empty_ledger_has_no_periods_or_estimations(self):
        report = build_trend_analysis(self.repository)
        self.assertEqual(report["periods"], [])
        self.assertEqual(report["comparisons"], [])
        self.assertEqual(report["adopted_versions"], [])
        self.assertEqual(verify_trend_analysis(report, self.repository), [])

    def test_single_period_carries_denominator_without_comparison(self):
        self.repository.save_record(DomainRecord("case-a", make_payload(40)))
        report = build_trend_analysis(self.repository)
        self.assertEqual(len(report["periods"]), 1)
        self.assertEqual(report["periods"][0]["denominator"], 1)
        self.assertEqual(report["comparisons"], [])
        self.assertEqual(verify_trend_analysis(report, self.repository), [])


if __name__ == "__main__":
    unittest.main()
