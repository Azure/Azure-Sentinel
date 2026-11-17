"""Exact Kusto tick parsing and deterministic timestamp namespaces."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Sequence

TICKS_PER_SECOND = 10_000_000
TICKS_PER_MICROSECOND = 10
SAFETY_DELAY_SECONDS = 5 * 60
MAX_SAMPLE_SPAN_TICKS = 36 * 60 * 60 * TICKS_PER_SECOND
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
ISO_FRACTION_RE = re.compile(r"(?<=\d{2}:\d{2}:\d{2})\.(\d+)")
LEGACY_TIMESTAMP_FORMATS = (
    "%m/%d/%Y, %I:%M:%S.%f %p",
    "%m/%d/%Y, %I:%M:%S %p",
    "%m/%d/%Y %I:%M:%S.%f %p",
    "%m/%d/%Y %I:%M:%S %p",
    "%d/%m/%Y, %H:%M:%S.%f",
    "%d/%m/%Y, %H:%M:%S",
    "%d/%m/%Y",
    "%d-%m-%Y %H:%M",
    "%d-%m-%y %H:%M",
)

@dataclass(frozen=True)
class TimestampNamespace:
    target_id: str
    target_group: str
    slot: int
    quantum_ticks: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "targetId": self.target_id,
            "targetGroup": self.target_group,
            "slot": self.slot,
            "quantumTicks": self.quantum_ticks,
        }


def datetime_to_ticks(value: datetime) -> int:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    delta = value - EPOCH
    return (
        (delta.days * 86_400 + delta.seconds) * TICKS_PER_SECOND
        + delta.microseconds * TICKS_PER_MICROSECOND
    )


def ticks_to_kusto_datetime(ticks: int) -> str:
    seconds, fraction_ticks = divmod(ticks, TICKS_PER_SECOND)
    value = EPOCH + timedelta(seconds=seconds)
    return (
        f"{value:%Y-%m-%dT%H:%M:%S}."
        f"{fraction_ticks:07d}Z"
    )


def parse_kusto_datetime_ticks(value: Any) -> int:
    if isinstance(value, datetime):
        return datetime_to_ticks(value)
    normalized = str(value).strip()
    if not normalized:
        raise ValueError("Timestamp cannot be empty.")
    normalized = re.sub(r"^0(?=\d{2}/\d{2}/\d{4})", "", normalized)

    fraction_match = ISO_FRACTION_RE.search(normalized)
    fraction = fraction_match.group(1) if fraction_match else ""
    if len(fraction) > 7:
        raise ValueError(
            f"Timestamp exceeds Kusto 100ns precision: {value}"
        )
    parse_value = normalized.replace("Z", "+00:00")
    if fraction_match:
        parse_fraction = fraction[:6].ljust(6, "0")
        parse_value = (
            parse_value[: fraction_match.start(1)]
            + parse_fraction
            + parse_value[fraction_match.end(1) :]
        )
    try:
        parsed = datetime.fromisoformat(parse_value)
    except ValueError:
        parsed = None
    if parsed is not None:
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        else:
            parsed = parsed.astimezone(timezone.utc)
        base_ticks = datetime_to_ticks(parsed.replace(microsecond=0))
        fraction_ticks = int(fraction.ljust(7, "0") or "0")
        return base_ticks + fraction_ticks

    for timestamp_format in LEGACY_TIMESTAMP_FORMATS:
        try:
            parsed = datetime.strptime(normalized, timestamp_format)
            return datetime_to_ticks(parsed.replace(tzinfo=timezone.utc))
        except ValueError:
            continue
    raise ValueError(f"Unsupported timestamp value: {value}")


def timestamp_quantum_for_target_count(target_count: int) -> int:
    if target_count < 1:
        raise ValueError("target_count must be at least 1.")
    quantum = 1
    while quantum < target_count:
        quantum *= 10
    if quantum > TICKS_PER_SECOND:
        raise ValueError(
            f"Cannot allocate {target_count} parser timestamp slots in one second."
        )
    return quantum


def allocate_timestamp_namespaces(
    targets: Sequence[tuple[str, str]],
) -> dict[str, TimestampNamespace]:
    """Allocate non-overlapping low-order tick slots by target group."""
    grouped: dict[str, set[str]] = {}
    for target_id, target_group in targets:
        if not target_id or not target_group:
            raise ValueError("target_id and target_group must be non-empty.")
        grouped.setdefault(target_group, set()).add(target_id)

    namespaces: dict[str, TimestampNamespace] = {}
    for target_group, target_ids in sorted(grouped.items()):
        ordered_ids = sorted(target_ids)
        quantum = timestamp_quantum_for_target_count(len(ordered_ids))
        for slot, target_id in enumerate(ordered_ids):
            if target_id in namespaces:
                raise ValueError(
                    f"Target '{target_id}' appears in multiple timestamp groups."
                )
            namespaces[target_id] = TimestampNamespace(
                target_id=target_id,
                target_group=target_group,
                slot=slot,
                quantum_ticks=quantum,
            )
    return namespaces


def _hash_to_run_slot(run_key: str, quantum_ticks: int) -> int:
    available_slots = TICKS_PER_SECOND // quantum_ticks
    digest = hashlib.sha256(run_key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % available_slots


def build_run_key(
    repository: str,
    pull_request: str,
    run_id: str,
    run_attempt: int,
) -> str:
    if not repository or not run_id:
        raise ValueError("repository and run_id must be non-empty.")
    if run_attempt < 1:
        raise ValueError("run_attempt must be at least 1.")
    return "|".join(
        (repository, str(pull_request), str(run_id), str(run_attempt))
    )


def compute_latest_rebased_tick(
    now_ticks: int,
    run_key: str,
    namespace: TimestampNamespace,
    safety_delay_seconds: int = SAFETY_DELAY_SECONDS,
) -> tuple[int, int]:
    if namespace.slot < 0 or namespace.slot >= namespace.quantum_ticks:
        raise ValueError("Timestamp namespace slot is outside its quantum.")
    base_second = (
        now_ticks
        - (now_ticks % TICKS_PER_SECOND)
        - safety_delay_seconds * TICKS_PER_SECOND
    )
    run_slot = _hash_to_run_slot(run_key, namespace.quantum_ticks)
    latest_tick = (
        base_second
        + run_slot * namespace.quantum_ticks
        + namespace.slot
    )
    return latest_tick, run_slot


def rebase_time_generated(
    rows: Sequence[dict[str, Any]],
    run_key: str,
    namespace: TimestampNamespace,
    now_ticks: int,
    max_span_ticks: int = MAX_SAMPLE_SPAN_TICKS,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not rows:
        raise ValueError("Fixture must contain at least one row.")

    parsed_ticks: list[int | None] = []
    for row_index, row in enumerate(rows, start=1):
        if "TimeGenerated" not in row:
            raise ValueError(
                f"Fixture row {row_index} is missing TimeGenerated."
            )
        raw_value = row["TimeGenerated"]
        parsed_ticks.append(
            None
            if raw_value is None or not str(raw_value).strip()
            else parse_kusto_datetime_ticks(raw_value)
        )

    nonempty_ticks = [tick for tick in parsed_ticks if tick is not None]
    if not nonempty_ticks:
        raise ValueError("Fixture has no non-empty TimeGenerated values.")
    latest_source_tick = max(nonempty_ticks)
    earliest_source_tick = min(nonempty_ticks)
    source_span = latest_source_tick - earliest_source_tick
    compress_span = source_span > max_span_ticks

    latest_rebased_tick, run_slot = compute_latest_rebased_tick(
        now_ticks, run_key, namespace
    )
    timestamp_suffix_ticks = latest_rebased_tick % TICKS_PER_SECOND
    distance_by_source_tick: dict[int, int] = {}
    previous_units = -1
    distance_quantum = TICKS_PER_SECOND
    max_units = max_span_ticks // distance_quantum
    ordered_source_ticks = sorted(set(nonempty_ticks), reverse=True)
    if len(ordered_source_ticks) > max_units + 1:
        raise ValueError(
            "Fixture has too many distinct timestamps to preserve within "
            "the configured maximum span."
        )
    for index, source_tick in enumerate(ordered_source_ticks):
        distance = latest_source_tick - source_tick
        if compress_span:
            distance = distance * max_span_ticks // source_span
        desired_units = (
            distance + distance_quantum - 1
        ) // distance_quantum
        lower_bound = 0 if previous_units < 0 else previous_units + 1
        remaining_values = len(ordered_source_ticks) - index - 1
        upper_bound = max_units - remaining_values
        units = min(max(desired_units, lower_bound), upper_bound)
        distance_by_source_tick[source_tick] = (
            units * distance_quantum
        )
        previous_units = units

    prepared_rows: list[dict[str, Any]] = []
    timestamp_values: list[str] = []
    for row, source_tick in zip(rows, parsed_ticks):
        prepared_row = dict(row)
        rebased_tick = (
            latest_rebased_tick
            if source_tick is None
            else latest_rebased_tick - distance_by_source_tick[source_tick]
        )
        if rebased_tick % TICKS_PER_SECOND != timestamp_suffix_ticks:
            raise AssertionError("Rebased timestamp escaped its run suffix.")
        if rebased_tick % namespace.quantum_ticks != namespace.slot:
            raise AssertionError("Rebased timestamp escaped its target slot.")
        timestamp_value = ticks_to_kusto_datetime(rebased_tick)
        prepared_row["TimeGenerated"] = timestamp_value
        prepared_rows.append(prepared_row)
        timestamp_values.append(timestamp_value)

    unique_timestamps = sorted(set(timestamp_values))
    timestamp_hash = hashlib.sha256(
        "\n".join(unique_timestamps).encode("utf-8")
    ).hexdigest()
    return prepared_rows, {
        "latestTick": latest_rebased_tick,
        "latestTimeGenerated": ticks_to_kusto_datetime(
            latest_rebased_tick
        ),
        "runSlot": run_slot,
        "timestampSuffixTicks": timestamp_suffix_ticks,
        "sourceSpanTicks": source_span,
        "rebasedSpanTicks": (
            max(parse_kusto_datetime_ticks(value) for value in timestamp_values)
            - min(
                parse_kusto_datetime_ticks(value)
                for value in timestamp_values
            )
        ),
        "compressed": compress_span,
        "timestampValues": unique_timestamps,
        "timestampSetHash": f"sha256:{timestamp_hash}",
    }
