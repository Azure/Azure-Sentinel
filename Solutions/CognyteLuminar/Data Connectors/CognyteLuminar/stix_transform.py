"""
stix_transform.py

Turns a batch of Luminar STIX 2.1 objects into the list of objects sent to the
Microsoft Sentinel upload API.

The upload API accepts exactly five STIX types (indicator, attack-pattern,
identity, threat-actor, relationship). Everything else Luminar publishes
(malware, report, vulnerability, software, campaign, location, incident,
user-account, ...) is never sent. Reports, malware and campaigns are read only
to enrich the indicators they reference.

All functions here are pure: no I/O, no global state, deterministic output for
a given input. That keeps them unit-testable with recorded fixtures.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

SUPPORTED_TYPES = frozenset(
    {"indicator", "attack-pattern", "identity", "threat-actor", "relationship"}
)
# Types we read for indicator enrichment but never send.
ENRICHMENT_TYPES = frozenset({"report", "malware", "campaign", "threat-actor"})

STIX_TS_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
MAX_LABEL_LEN = 256
MAX_DESCRIPTION_LEN = 4000
EXTERNAL_SOURCE_NAME = "Cognyte Luminar"


@dataclass
class TransformOptions:
    collection: str
    tlp_marking_ref: str
    default_validity_days: int = 90
    default_confidence: Optional[int] = 50
    enrich_from_reports: bool = True
    # Drop indicators whose final valid_until is already in the past.
    skip_expired: bool = True
    # Reference time for the expiry check (UTC, naive). None means "now";
    # tests pass a fixed value.
    now: Optional[datetime] = None


@dataclass
class TransformStats:
    received: int = 0
    duplicates_dropped: int = 0
    sent: int = 0
    by_type_sent: Dict[str, int] = field(default_factory=dict)
    by_type_skipped: Dict[str, int] = field(default_factory=dict)
    relationships_dropped: int = 0
    missing_required_dropped: int = 0
    enriched_indicators: int = 0
    expired_dropped: int = 0

    def _bump(self, bucket: Dict[str, int], key: str) -> None:
        bucket[key] = bucket.get(key, 0) + 1

    def as_dict(self) -> Dict[str, Any]:
        return {
            "received": self.received,
            "duplicates_dropped": self.duplicates_dropped,
            "sent": self.sent,
            "by_type_sent": dict(self.by_type_sent),
            "by_type_skipped": dict(self.by_type_skipped),
            "relationships_dropped": self.relationships_dropped,
            "missing_required_dropped": self.missing_required_dropped,
            "enriched_indicators": self.enriched_indicators,
            "expired_dropped": self.expired_dropped,
        }


# ----- small helpers ---------------------------------------------------------


def parse_stix_timestamp(value: Any) -> Optional[datetime]:
    """Parse a STIX timestamp (RFC 3339, UTC, optional fraction)."""
    if not isinstance(value, str) or not value:
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1]
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def format_stix_timestamp(value: datetime) -> str:
    # STIX requires millisecond-or-finer precision with a trailing Z.
    return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{value.microsecond // 1000:03d}Z"


def stix_type_of(ref: Any) -> str:
    if not isinstance(ref, str):
        return ""
    return ref.split("--", 1)[0]


def _clean_label(text: str) -> str:
    text = " ".join(str(text).split())
    return text[:MAX_LABEL_LEN]


def _add_unique(target: List[str], values: Iterable[str]) -> None:
    seen = set(target)
    for v in values:
        if v and v not in seen:
            target.append(v)
            seen.add(v)


# ----- batch indexing --------------------------------------------------------


def dedupe_by_id(
    objects: Iterable[Dict[str, Any]],
) -> Tuple[Dict[str, Dict[str, Any]], int]:
    """Index objects by id, keeping the most recently `modified` version.

    The Luminar manager attaches hydrated reference objects to every batch
    that references them, so duplicates within a batch are normal.
    """
    index: Dict[str, Dict[str, Any]] = {}
    dropped = 0
    for obj in objects:
        if not isinstance(obj, dict):
            continue
        oid = obj.get("id")
        if not isinstance(oid, str) or "--" not in oid:
            continue
        existing = index.get(oid)
        if existing is None:
            index[oid] = obj
            continue
        dropped += 1
        if (obj.get("modified") or "") > (existing.get("modified") or ""):
            index[oid] = obj
    return index, dropped


def build_report_context(
    index: Dict[str, Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    """Map each referenced object id -> the reports that reference it."""
    by_ref: Dict[str, List[Dict[str, Any]]] = {}
    for obj in index.values():
        if obj.get("type") != "report":
            continue
        refs = obj.get("object_refs")
        if not isinstance(refs, list):
            continue
        for ref in refs:
            if isinstance(ref, str):
                by_ref.setdefault(ref, []).append(obj)
    return by_ref


# ----- per-type transforms ---------------------------------------------------


def _common_decorations(obj: Dict[str, Any], opts: TransformOptions) -> Dict[str, Any]:
    out = dict(obj)
    out.setdefault("spec_version", "2.1")

    labels: List[str] = [
        _clean_label(x) for x in (out.get("labels") or []) if isinstance(x, str) and x
    ]
    _add_unique(labels, [f"luminar:{opts.collection}"])
    out["labels"] = labels

    markings: List[str] = [
        x for x in (out.get("object_marking_refs") or []) if isinstance(x, str)
    ]
    if not markings:
        markings = [opts.tlp_marking_ref]
    out["object_marking_refs"] = markings

    refs: List[Dict[str, Any]] = [
        r for r in (out.get("external_references") or []) if isinstance(r, dict)
    ]
    if not any(
        r.get("source_name") == EXTERNAL_SOURCE_NAME
        and r.get("external_id") == out["id"]
        for r in refs
    ):
        refs.append({"source_name": EXTERNAL_SOURCE_NAME, "external_id": out["id"]})
    out["external_references"] = refs
    return out


def _ensure_required_timestamps(obj: Dict[str, Any]) -> bool:
    """`created` and `modified` are mandatory for the upload API.

    Luminar SDOs carry both. If one is missing we fill it from the other or
    from `valid_from`; if none is available the object cannot be sent.
    """
    created = obj.get("created")
    modified = obj.get("modified")
    fallback = created or modified or obj.get("valid_from")
    if not isinstance(fallback, str) or parse_stix_timestamp(fallback) is None:
        return False
    if not created:
        obj["created"] = fallback
    if not modified:
        obj["modified"] = obj["created"]
    return True


def transform_indicator(
    obj: Dict[str, Any],
    opts: TransformOptions,
    index: Dict[str, Dict[str, Any]],
    reports_by_ref: Dict[str, List[Dict[str, Any]]],
) -> Tuple[Optional[Dict[str, Any]], bool]:
    """Return (indicator, enriched). `None` when the object is not sendable."""
    if not obj.get("pattern") or not obj.get("pattern_type"):
        return None, False
    out = _common_decorations(obj, opts)
    if not _ensure_required_timestamps(out):
        return None, False

    valid_from_dt = parse_stix_timestamp(out.get("valid_from"))
    if valid_from_dt is None:
        valid_from_dt = parse_stix_timestamp(out["created"])
        out["valid_from"] = out["created"]
    if valid_from_dt is None:
        return None, False

    valid_until_dt = parse_stix_timestamp(out.get("valid_until"))
    if valid_until_dt is None or valid_until_dt <= valid_from_dt:
        out["valid_until"] = format_stix_timestamp(
            valid_from_dt + timedelta(days=opts.default_validity_days)
        )

    if "confidence" not in out and opts.default_confidence is not None:
        out["confidence"] = opts.default_confidence
    if isinstance(out.get("confidence"), (int, float)):
        out["confidence"] = max(0, min(100, int(out["confidence"])))

    enriched = False
    if opts.enrich_from_reports:
        enriched = _enrich_indicator_from_reports(out, index, reports_by_ref)
    return out, enriched


def _enrich_indicator_from_reports(
    ind: Dict[str, Any],
    index: Dict[str, Dict[str, Any]],
    reports_by_ref: Dict[str, List[Dict[str, Any]]],
) -> bool:
    """Add report titles and related malware / actor / campaign names.

    In the `cyberfeeds` collection no relationship touches an indicator; the
    only link between an indicator and its context is `report.object_refs`.
    """
    reports = reports_by_ref.get(ind["id"]) or []
    if not reports:
        return False

    labels: List[str] = list(ind.get("labels") or [])
    ext_refs: List[Dict[str, Any]] = list(ind.get("external_references") or [])
    titles: List[str] = []
    prefix_by_type = {
        "malware": "malware",
        "threat-actor": "actor",
        "campaign": "campaign",
    }
    for report in reports:
        name = report.get("name")
        if isinstance(name, str) and name.strip():
            titles.append(name.strip())
        ext_refs.append(
            {
                "source_name": EXTERNAL_SOURCE_NAME,
                "description": (name or "Luminar report")[:MAX_LABEL_LEN],
                "external_id": report["id"],
            }
        )
        for ref in report.get("object_refs") or []:
            prefix = prefix_by_type.get(stix_type_of(ref))
            if not prefix:
                continue
            related = index.get(ref)
            rel_name = related.get("name") if isinstance(related, dict) else None
            if isinstance(rel_name, str) and rel_name.strip():
                _add_unique(labels, [_clean_label(f"{prefix}:{rel_name.strip()}")])

    if titles:
        existing = (ind.get("description") or "").strip()
        addition = "Luminar reports: " + "; ".join(dict.fromkeys(titles))
        if addition not in existing:
            desc = f"{existing}\n{addition}" if existing else addition
            ind["description"] = desc[:MAX_DESCRIPTION_LEN]
        if not ind.get("name"):
            ind["name"] = titles[0][:MAX_LABEL_LEN]

    ind["labels"] = labels
    ind["external_references"] = ext_refs
    return True


def transform_generic_sdo(
    obj: Dict[str, Any], opts: TransformOptions
) -> Optional[Dict[str, Any]]:
    """identity / threat-actor / attack-pattern: pass through with decorations."""
    out = _common_decorations(obj, opts)
    if not _ensure_required_timestamps(out):
        return None
    if not out.get("name"):
        # Sentinel displays these by name; an unnamed actor/identity is noise.
        return None
    return out


def transform_relationship(
    obj: Dict[str, Any], opts: TransformOptions, sendable_ids: Set[str]
) -> Optional[Dict[str, Any]]:
    """Keep a relationship only when both ends are types we send.

    `sendable_ids` holds the ids of supported-type objects seen in this batch;
    an end that is a supported *type* but absent from the batch is still
    allowed (it may have been sent in an earlier batch or run).
    """
    src, tgt = obj.get("source_ref"), obj.get("target_ref")
    if (
        stix_type_of(src) not in SUPPORTED_TYPES
        or stix_type_of(tgt) not in SUPPORTED_TYPES
    ):
        return None
    if not obj.get("relationship_type"):
        return None
    out = _common_decorations(obj, opts)
    if not _ensure_required_timestamps(out):
        return None
    return out


def is_expired(indicator: Dict[str, Any], now: datetime) -> bool:
    """True when the indicator's valid_until is at or before `now`.

    Checked after defaults are applied, so a `cyberfeeds` indicator without a
    Luminar valid_until is judged on valid_from + DefaultIndicatorValidityDays.
    An unparseable valid_until is treated as not expired (never silently
    dropped on a format quirk).
    """
    valid_until = parse_stix_timestamp(indicator.get("valid_until"))
    return valid_until is not None and valid_until <= now


# ----- batch entry point -----------------------------------------------------


def transform_batch(
    objects: Iterable[Dict[str, Any]], opts: TransformOptions
) -> Tuple[List[Dict[str, Any]], TransformStats]:
    """Transform one Luminar batch into upload-ready STIX objects.

    Output order: identities/threat-actors/attack-patterns first, then
    indicators, then relationships, so that within a run the ends of a
    relationship are uploaded no later than the relationship itself.
    """
    stats = TransformStats()
    objects = list(objects)
    stats.received = len(objects)

    index, dropped = dedupe_by_id(objects)
    stats.duplicates_dropped = dropped
    reports_by_ref = build_report_context(index) if opts.enrich_from_reports else {}

    now = opts.now or datetime.now(timezone.utc).replace(tzinfo=None)
    sdos: List[Dict[str, Any]] = []
    indicators: List[Dict[str, Any]] = []
    relationships_in: List[Dict[str, Any]] = []
    expired_ids: Set[str] = set()

    for obj in index.values():
        otype = obj.get("type")
        if otype == "indicator":
            out, enriched = transform_indicator(obj, opts, index, reports_by_ref)
            if out is None:
                stats.missing_required_dropped += 1
                continue
            if opts.skip_expired and is_expired(out, now):
                stats.expired_dropped += 1
                expired_ids.add(out["id"])
                continue
            indicators.append(out)
            if enriched:
                stats.enriched_indicators += 1
        elif otype == "relationship":
            relationships_in.append(obj)
        elif otype in SUPPORTED_TYPES:
            out = transform_generic_sdo(obj, opts)
            if out is None:
                stats.missing_required_dropped += 1
                continue
            sdos.append(out)
        else:
            stats._bump(stats.by_type_skipped, str(otype))

    sendable_ids: Set[str] = {o["id"] for o in sdos} | {o["id"] for o in indicators}
    relationships: List[Dict[str, Any]] = []
    for obj in relationships_in:
        if obj.get("source_ref") in expired_ids or obj.get("target_ref") in expired_ids:
            # Do not upload an edge whose indicator end was not uploaded.
            stats.relationships_dropped += 1
            continue
        out = transform_relationship(obj, opts, sendable_ids)
        if out is None:
            stats.relationships_dropped += 1
            continue
        relationships.append(out)

    result = sdos + indicators + relationships
    stats.sent = len(result)
    for obj in result:
        stats._bump(stats.by_type_sent, obj["type"])
    return result, stats
