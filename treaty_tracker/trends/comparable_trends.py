"""可比趋势分析。

设计约束（对应月度通报诉求）：

* 提交期间来自哈希链上的 ``record.saved`` 证据事件，而不是当前时钟，因此每个
  期间都能追溯到具体的 ``event_id``。
* 同一事项（``record_id``）在同一期间内可能存在多个补交/更正版本，期间内只
  采用最后一个版本，候选版本全部留痕，分母按去重后的事项数计算，绝不把不同
  版本重复计数。
* 相邻期间只在同一事项构成的匹配队列上比较；缺少可比证据（队列为空）时
  ``improvement_rate`` 取 ``None`` 并注明原因，不做任何推算。
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

from treaty_tracker.commitments.pledge import ContractError, stable_hash, utc_now
from treaty_tracker.progress_signal.commitment_health import commitment_health

SCHEMA_VERSION = "trend-analysis-v1"
PERIOD_GRAIN = "calendar-month-utc"
VERSION_ADOPTION = "latest-version-per-record-within-period"
PERIOD_SOURCE = "record.saved.event.created_at"
SCORE_EPSILON = 1e-9
GROUP_DIMENSIONS = ("member_code", "commitment_area")
UNKNOWN_GROUP = "unknown"


def period_key(timestamp: str) -> str:
    """把证据事件时间截断为 UTC 年月（YYYY-MM）。"""
    text = str(timestamp).strip()
    if len(text) < 7 or text[4] != "-":
        raise ContractError(f"cannot derive submission period from timestamp: {timestamp!r}")
    month = text[:7]
    year, separator, month_value = month.partition("-")
    if separator != "-" or not (year.isdigit() and month_value.isdigit()) or not 1 <= int(month_value) <= 12:
        raise ContractError(f"cannot derive submission period from timestamp: {timestamp!r}")
    return month


def _group_value(payload: Mapping[str, Any], dimension: str) -> str:
    value = payload.get(dimension)
    if value in (None, ""):
        return UNKNOWN_GROUP
    return str(value)


def build_observations(repository: Any) -> list[dict[str, Any]]:
    """把不可变版本表与证据事件对齐，形成带提交期间的版本观测。

    每条观测对应一个已提交版本；期间内采用哪个版本由
    :func:`build_trend_analysis` 进一步裁决。
    """
    saved_events = {
        (row["record_id"], row["version"]): row
        for row in repository.record_saved_events()
    }
    decision_index = repository.decision_event_index()
    observations: list[dict[str, Any]] = []
    for version in repository.version_rows():
        key = (version["record_id"], version["version"])
        event = saved_events.get(key)
        if event is not None:
            period = period_key(event["created_at"])
            period_source = "record.saved.event.created_at"
            event_id = event["event_id"]
            event_hash = event["event_hash"]
        else:
            # 兜底：版本存在但缺失证据事件时，退回到版本入库时间并明确标注。
            period = period_key(version["stored_at"])
            period_source = "record_versions.stored_at"
            event_id = None
            event_hash = None
        payload = version["payload"]
        signal = commitment_health(payload)
        decision_event = decision_index.get(key)
        decision_outcome = None
        decision_event_id = None
        if decision_event is not None:
            decision_outcome = decision_event["payload"].get("outcome")
        observations.append({
            "record_id": version["record_id"],
            "version": version["version"],
            "fingerprint": version["fingerprint"],
            "state": version["state"],
            "period": period,
            "period_source": period_source,
            "event_id": event_id,
            "event_hash": event_hash,
            "health_score": signal.score,
            "health_severity": signal.severity,
            "decision_outcome": decision_outcome,
            "groups": {dimension: _group_value(payload, dimension) for dimension in GROUP_DIMENSIONS},
        })
    return observations


def _adopt_versions(observations: Sequence[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    """同一事项同一期间只采用最后提交的版本，其余版本仅作为候选留痕。"""
    candidates: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for observation in observations:
        candidates[(observation["record_id"], observation["period"])].append(observation)
    adopted: dict[tuple[str, str], dict[str, Any]] = {}
    for key, rows in candidates.items():
        ordered = sorted(rows, key=lambda row: (row["version"], row["event_id"] is None, row["event_id"] or -1))
        adopted[key] = ordered[-1]
    return adopted


def _outcome_breakdown(rows: Sequence[dict[str, Any]]) -> dict[str, int]:
    outcomes: dict[str, int] = defaultdict(int)
    for row in rows:
        if row["decision_outcome"]:
            outcomes[row["decision_outcome"]] += 1
    return dict(sorted(outcomes.items()))


def _summarize_period(period: str, rows: Sequence[dict[str, Any]],
                      candidate_versions: int) -> dict[str, Any]:
    scores = [row["health_score"] for row in rows]
    return {
        "period": period,
        "denominator": len(rows),
        "candidate_version_count": candidate_versions,
        "distinct_record_count": len({row["record_id"] for row in rows}),
        "decided_count": sum(1 for row in rows if row["decision_outcome"]),
        "outcomes": _outcome_breakdown(rows),
        "average_health_score": sum(scores) / len(scores) if scores else None,
        "minimum_health_score": min(scores) if scores else None,
        "maximum_health_score": max(scores) if scores else None,
    }


def _group_period_rows(rows: Sequence[dict[str, Any]], dimension: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["groups"][dimension]].append(row)
    return grouped


def _comparison(scope: str, scope_value: str, prior_period: str, current_period: str,
                prior_rows: Sequence[dict[str, Any]], current_rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    prior_by_record = {row["record_id"]: row for row in prior_rows}
    current_by_record = {row["record_id"]: row for row in current_rows}
    matched_ids = sorted(set(prior_by_record) & set(current_by_record))
    added_ids = sorted(set(current_by_record) - set(prior_by_record))
    removed_ids = sorted(set(prior_by_record) - set(current_by_record))
    basis = {
        "scope": scope,
        "scope_value": scope_value,
        "prior_period": prior_period,
        "current_period": current_period,
        "prior_denominator": len(prior_rows),
        "current_denominator": len(current_rows),
        "matched_record_ids": matched_ids,
        "matched_denominator": len(matched_ids),
        "entered_record_ids": added_ids,
        "exited_record_ids": removed_ids,
    }
    if not matched_ids:
        return basis | {
            "comparable": False,
            "reason": "no shared record between periods; improvement rate is not estimated",
            "improved_count": None,
            "declined_count": None,
            "unchanged_count": None,
            "improvement_rate": None,
            "average_score_delta": None,
        }
    deltas = {
        record_id: current_by_record[record_id]["health_score"] - prior_by_record[record_id]["health_score"]
        for record_id in matched_ids
    }
    improved = sorted(record_id for record_id, delta in deltas.items() if delta > SCORE_EPSILON)
    declined = sorted(record_id for record_id, delta in deltas.items() if delta < -SCORE_EPSILON)
    unchanged = sorted(record_id for record_id, delta in deltas.items() if abs(delta) <= SCORE_EPSILON)
    return basis | {
        "comparable": True,
        "reason": None,
        "improved_count": len(improved),
        "declined_count": len(declined),
        "unchanged_count": len(unchanged),
        "improved_record_ids": improved,
        "declined_record_ids": declined,
        "unchanged_record_ids": unchanged,
        "improvement_rate": len(improved) / len(matched_ids),
        "average_score_delta": sum(deltas.values()) / len(matched_ids),
    }


def build_trend_analysis(repository: Any, generated_at: str | None = None) -> dict[str, Any]:
    """基于台账版本与证据事件生成冻结的可比趋势分析。"""
    observations = build_observations(repository)
    adopted = _adopt_versions(observations)

    period_to_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    period_candidate_counts: dict[str, int] = defaultdict(int)
    adopted_versions: list[dict[str, Any]] = []
    for observation in observations:
        period_candidate_counts[observation["period"]] += 1
    for (record_id, period), row in sorted(adopted.items()):
        period_to_rows[period].append(row)
        candidate_keys = sorted(
            (item["version"], item["event_id"])
            for item in observations
            if item["record_id"] == record_id and item["period"] == period
        )
        adopted_versions.append({
            "record_id": record_id,
            "period": period,
            "adopted_version": row["version"],
            "adopted_fingerprint": row["fingerprint"],
            "evidence_event_id": row["event_id"],
            "evidence_event_hash": row["event_hash"],
            "candidate_versions": [version for version, _ in candidate_keys],
        })

    periods = sorted(period_to_rows)
    period_series = [
        _summarize_period(period, sorted(period_to_rows[period], key=lambda row: row["record_id"]),
                          period_candidate_counts[period])
        for period in periods
    ]

    comparisons: list[dict[str, Any]] = []
    for prior_period, current_period in zip(periods, periods[1:]):
        prior_rows = period_to_rows[prior_period]
        current_rows = period_to_rows[current_period]
        comparisons.append(_comparison("portfolio", "all", prior_period, current_period, prior_rows, current_rows))
        for dimension in GROUP_DIMENSIONS:
            prior_groups = _group_period_rows(prior_rows, dimension)
            current_groups = _group_period_rows(current_rows, dimension)
            for group_value in sorted(set(prior_groups) | set(current_groups)):
                comparisons.append(_comparison(
                    dimension, group_value, prior_period, current_period,
                    prior_groups.get(group_value, []), current_groups.get(group_value, [])))

    evidence = {
        "event_chain": "events.record.saved",
        "version_store": "record_versions",
        "decision_store": "events.decision.saved",
        "record_saved_event_count": sum(1 for row in observations if row["period_source"] == PERIOD_SOURCE),
        "fallback_period_count": sum(1 for row in observations if row["period_source"] != PERIOD_SOURCE),
    }
    methodology = {
        "schema_version": SCHEMA_VERSION,
        "period_grain": PERIOD_GRAIN,
        "period_source": PERIOD_SOURCE,
        "version_adoption": VERSION_ADOPTION,
        "comparison_rule": "matched-record cohort between adjacent periods only",
        "no_estimation_rule": "improvement_rate is null when the matched cohort is empty",
        "score_identity": "treaty_tracker.progress_signal.commitment_health.commitment_health",
        "group_dimensions": list(GROUP_DIMENSIONS),
    }
    report = {
        "product": "人工智能合作组织成员承诺履约证据台",
        "entity": "commitment_case",
        "generated_at": generated_at or utc_now(),
        "methodology": methodology,
        "evidence": evidence,
        "periods": period_series,
        "adopted_versions": adopted_versions,
        "comparisons": comparisons,
    }
    report["report_hash"] = stable_hash({key: value for key, value in report.items() if key != "report_hash"})
    return report


def verify_trend_analysis(report: Mapping[str, Any], repository: Any) -> list[str]:
    """沿现有核验入口审查冻结报告：只核对台账证据，不重新计算或重写报告。"""
    errors: list[str]
    errors = []
    methodology = report.get("methodology") or {}
    if methodology.get("schema_version") != SCHEMA_VERSION:
        errors.append("trend-analysis: unsupported schema_version")
    if methodology.get("period_grain") != PERIOD_GRAIN:
        errors.append("trend-analysis: unsupported period_grain")
    if methodology.get("version_adoption") != VERSION_ADOPTION:
        errors.append("trend-analysis: unsupported version_adoption")

    expected_hash = report.get("report_hash")
    body = {key: value for key, value in report.items() if key != "report_hash"}
    if expected_hash != stable_hash(body):
        errors.append("trend-analysis: report hash mismatch")

    ledger = build_observations(repository)
    adopted = _adopt_versions(ledger)
    ledger_observations = {(row["record_id"], row["version"]): row for row in ledger}

    for entry in report.get("adopted_versions", []):
        key = (entry.get("record_id"), entry.get("period"))
        chosen = adopted.get(key)
        if chosen is None:
            errors.append(f"trend-analysis: adopted version has no ledger evidence: {key}")
            continue
        if entry.get("adopted_version") != chosen["version"]:
            errors.append(f"trend-analysis: adopted version disagrees with ledger for {key}")
        if entry.get("adopted_fingerprint") != chosen["fingerprint"]:
            errors.append(f"trend-analysis: adopted fingerprint disagrees with ledger for {key}")
        observation = ledger_observations.get((entry.get("record_id"), entry.get("adopted_version")))
        if observation is None:
            errors.append(f"trend-analysis: adopted version missing in record_versions: {key}")
        elif entry.get("evidence_event_id") != observation["event_id"]:
            errors.append(f"trend-analysis: evidence event id disagrees with ledger for {key}")

    period_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in adopted.values():
        period_rows[row["period"]].append(row)
    ledger_periods = {
        period: _summarize_period(period, rows, sum(1 for item in ledger if item["period"] == period))
        for period, rows in period_rows.items()
    }
    reported_periods = {item.get("period"): item for item in report.get("periods", [])}
    if set(reported_periods) != set(ledger_periods):
        errors.append("trend-analysis: period coverage disagrees with ledger")
    for period, expected in ledger_periods.items():
        actual = reported_periods.get(period)
        if actual is None:
            continue
        for field_name in ("denominator", "candidate_version_count", "distinct_record_count",
                           "decided_count", "average_health_score", "minimum_health_score",
                           "maximum_health_score"):
            if actual.get(field_name) != expected[field_name]:
                errors.append(f"trend-analysis: {field_name} disagrees with ledger for period {period}")
        if actual.get("outcomes") != expected["outcomes"]:
            errors.append(f"trend-analysis: outcome breakdown disagrees with ledger for period {period}")

    comparisons = report.get("comparisons", [])
    comparison_keys = {(item.get("scope"), item.get("scope_value"), item.get("prior_period"),
                        item.get("current_period")) for item in comparisons}
    expected_comparisons: set[tuple[str, str, str, str]] = set()
    ordered_periods = sorted(period_rows)
    for prior_period, current_period in zip(ordered_periods, ordered_periods[1:]):
        expected_comparisons.add(("portfolio", "all", prior_period, current_period))
        for dimension in GROUP_DIMENSIONS:
            values = {row["groups"][dimension] for row in period_rows[prior_period] + period_rows[current_period]}
            for value in values:
                expected_comparisons.add((dimension, value, prior_period, current_period))
    if comparison_keys != expected_comparisons:
        errors.append("trend-analysis: comparison coverage disagrees with ledger")

    for item in comparisons:
        if item.get("comparable") is False:
            if item.get("improvement_rate") is not None:
                errors.append("trend-analysis: improvement rate must stay null without matched evidence")
            continue
        matched = item.get("matched_record_ids") or []
        if not matched:
            errors.append("trend-analysis: comparable comparison without matched records")
            continue
        denominator = item.get("matched_denominator")
        if denominator != len(matched):
            errors.append("trend-analysis: matched denominator is not traceable to matched records")
        counted = (item.get("improved_count") or 0) + (item.get("declined_count") or 0) + (item.get("unchanged_count") or 0)
        if counted != len(matched):
            errors.append("trend-analysis: matched records are not classified exactly once")
        rate = item.get("improvement_rate")
        if rate is None or abs(rate - (item.get("improved_count") or 0) / len(matched)) > SCORE_EPSILON:
            errors.append("trend-analysis: improvement rate is not derived from the matched denominator")
    return errors
