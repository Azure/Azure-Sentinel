from __future__ import annotations

import html
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .decision_manifest import sanitize_decision_text

SCHEMA_VERSION = "pr-qualification-report-v1"
HTML_REPORT_FILENAME = "qualification-report.html"
MARKDOWN_SUMMARY_FILENAME = "qualification-summary.md"

DEFAULT_WAIVER_REVIEWER_PROMPT = (
    "Confirm author exception evidence to approve Partially Validated / Conditionally Qualified status"
)
DEFAULT_HUMAN_REVIEW_PROMPT = (
    "Review gathered supporting evidence and confirm the criterion is satisfied before approving the PR"
)
DEFAULT_FAILURE_REVIEW_PROMPT = (
    "Resolve the failing check or provide an approved author exception with supporting evidence"
)

ACTION_QUEUE_STATUSES = frozenset({
    "WAIVED_WITH_AUTHOR_EVIDENCE",
    "HUMAN_REVIEW_REQUIRED",
    "FAIL",
})

CHECKLIST_DEFINITIONS: tuple[tuple[str, str, str], ...] = (
    (
        "validation",
        "1. Validation Checklist",
        "Structural, schema, metadata, version, and ARM template checks.",
    ),
    (
        "qualification",
        "2. Qualification Checklist",
        "Runtime deployment, ingestion, query execution, connector, and content qualification checks.",
    ),
    (
        "migration",
        "3. Migration Checklist",
        "Sentinel-to-Defender-XDR conversion, dual-target parity, and hybrid packaging checks.",
    ),
)

STATUS_DISPLAY_LABELS: dict[str, str] = {
    "PASS": "PASS",
    "FAIL": "FAIL",
    "SKIPPED": "SKIPPED",
    "WAIVED_WITH_AUTHOR_EVIDENCE": "WAIVED WITH AUTHOR EVIDENCE",
    "HUMAN_REVIEW_REQUIRED": "HUMAN REVIEW REQUIRED",
    "NOT_APPLICABLE": "NOT APPLICABLE",
}

STATUS_BADGE_TONES: dict[str, str] = {
    "PASS": "green",
    "FAIL": "red",
    "SKIPPED": "amber",
    "WAIVED_WITH_AUTHOR_EVIDENCE": "amber",
    "HUMAN_REVIEW_REQUIRED": "amber",
    "NOT_APPLICABLE": "gray",
}

ROLLUP_CARD_TONES: dict[str, str] = {
    "Validated": "green",
    "Partially Validated": "amber",
    "Validation Failed": "red",
    "Qualified": "green",
    "Conditionally Qualified": "amber",
    "Qualification Failed": "red",
    "Not Run": "gray",
    "Migration Verified": "green",
    "Conditionally Migrated": "amber",
    "Migration Failed": "red",
    "Not Applicable": "gray",
}

_UNSAFE_SCHEME_RE = re.compile(r"^\s*(javascript|data|vbscript|file)\s*:", re.IGNORECASE)


def _escape(value: Any, default: str = "") -> str:
    if value is None:
        return html.escape(default, quote=True)
    text = str(value)
    return html.escape(text if text else default, quote=True)


def _resolve_solution_root(
    solution_path: str | None,
    output_dir: Path | None,
    explicit_solution_root: Path | None = None,
) -> Path | None:
    if explicit_solution_root is not None:
        return Path(explicit_solution_root).expanduser().resolve()
    candidates: list[Path] = []
    if solution_path:
        raw_p = Path(solution_path).expanduser()
        candidates.append(raw_p)
        if output_dir is not None:
            candidates.extend([
                output_dir / raw_p,
                output_dir / "workspace" / raw_p,
                output_dir / "workspace" / raw_p.name,
                output_dir.parent.parent,
            ])
        candidates.append(Path("Solutions") / raw_p.name)
    elif output_dir is not None:
        candidates.append(output_dir.parent.parent)
    for cand in candidates:
        resolved = cand.resolve()
        if resolved.exists():
            return resolved
    return Path(solution_path).expanduser().resolve() if solution_path else None


def _rebase_evidence_url(
    candidate: str,
    *,
    output_dir: Path | None = None,
    solution_root: Path | None = None,
) -> str:
    if candidate == "qualification_evidence":
        if output_dir is not None:
            for ev_cand in (
                output_dir / "qualification-evidence.json",
                output_dir / "evidence" / "qualification-evidence.json",
                output_dir.parent / "qualification-evidence.json",
            ):
                if ev_cand.exists():
                    rel = os.path.relpath(ev_cand, output_dir).replace("\\", "/")
                    return rel if rel.startswith(".") else f"./{rel}"
        return "../qualification-evidence.json"
    if candidate.startswith("qualification_evidence.") or candidate.startswith("qualification_evidence:"):
        sep = "." if "." in candidate else ":"
        frag = candidate.split(sep, 1)[1]
        base = _rebase_evidence_url(
            "qualification_evidence",
            output_dir=output_dir,
            solution_root=solution_root,
        )
        return f"{base}#{frag}"
    if candidate == "validationStatus":
        return "./pr-qualification-result.json#validationStatus"
    if not candidate.startswith(("http://", "https://", "file://", "mailto:", "/", ".", "#", "Solutions/")):
        path_only, sep, frag = candidate.partition("#")
        suffix = f"#{frag}" if sep else ""
        if output_dir is not None:
            search_candidates: list[Path] = []
            if solution_root is not None:
                search_candidates.append(solution_root / path_only)
            if path_only.startswith("Evidence/pr-qualification/"):
                sub = path_only[len("Evidence/pr-qualification/"):]
                search_candidates.append(output_dir / sub)
            if path_only.startswith("Evidence/"):
                sub = path_only[len("Evidence/"):]
                search_candidates.extend([
                    output_dir / "evidence" / sub,
                    output_dir / sub,
                    output_dir.parent / sub,
                ])
                if solution_root is not None:
                    search_candidates.append(solution_root / "Evidence" / sub)
            search_candidates.extend([
                output_dir / path_only,
                output_dir / "workspace" / path_only,
            ])
            for cand_path in search_candidates:
                if cand_path.exists():
                    rel = os.path.relpath(cand_path, output_dir).replace("\\", "/")
                    if not rel.startswith("."):
                        rel = f"./{rel}"
                    return f"{rel}{suffix}"
            if path_only.startswith("Evidence/") and (output_dir / "evidence").exists():
                sub = path_only[len("Evidence/"):]
                rel = os.path.relpath(output_dir / "evidence" / sub, output_dir).replace("\\", "/")
                if not rel.startswith("."):
                    rel = f"./{rel}"
                return f"{rel}{suffix}"
            if solution_root is not None and not path_only.startswith(("Evidence/", "Logs/")):
                rel = os.path.relpath(solution_root / path_only, output_dir).replace("\\", "/")
                if not rel.startswith("."):
                    rel = f"./{rel}"
                return f"{rel}{suffix}"
        if candidate.startswith("Evidence/pr-qualification/"):
            return "./" + candidate[len("Evidence/pr-qualification/"):]
        if candidate.startswith("Evidence/"):
            return "../" + candidate[len("Evidence/"):]
        if candidate.startswith("Logs/"):
            return "../../../../" + candidate
        return "../../" + candidate
    return candidate


def _sanitize_href(
    raw_url: Any,
    *,
    output_dir: Path | None = None,
    solution_root: Path | None = None,
) -> str:
    if raw_url is None:
        return "#"
    candidate = str(raw_url).strip()
    if not candidate or _UNSAFE_SCHEME_RE.match(candidate):
        return "#"
    candidate = _rebase_evidence_url(
        candidate,
        output_dir=output_dir,
        solution_root=solution_root,
    )
    try:
        parsed = urlsplit(candidate)
    except ValueError:
        return "#"
    if parsed.scheme and parsed.scheme.lower() not in {"http", "https", "mailto"}:
        return "#"
    return html.escape(candidate, quote=True)


def _sanitize_markdown_url(
    raw_url: Any,
    *,
    output_dir: Path | None = None,
    solution_root: Path | None = None,
) -> str:
    if raw_url is None:
        return "#"
    candidate = str(raw_url).strip()
    if not candidate or _UNSAFE_SCHEME_RE.match(candidate):
        return "#"
    candidate = _rebase_evidence_url(
        candidate,
        output_dir=output_dir,
        solution_root=solution_root,
    )
    try:
        parsed = urlsplit(candidate)
    except ValueError:
        return "#"
    if parsed.scheme and parsed.scheme.lower() not in {"http", "https", "mailto"}:
        return "#"
    return candidate.replace("(", "%28").replace(")", "%29").replace(" ", "%20")


def _escape_markdown_cell(value: Any, default: str = "—") -> str:
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    escaped = html.escape(text, quote=True)
    escaped = escaped.replace("|", "\\|").replace("\r\n", "<br>").replace("\n", "<br>")
    return escaped


def _normalize_status(status: Any, applicable: bool = True) -> str:
    if not applicable and not status:
        return "NOT_APPLICABLE"
    raw = str(status or ("PASS" if applicable else "NOT_APPLICABLE")).strip().upper()
    if raw in STATUS_DISPLAY_LABELS:
        return raw
    return "NOT_APPLICABLE" if not applicable else raw


def _compute_summary_counts(checks: list[dict[str, Any]], provided: Any) -> dict[str, int]:
    total = len(checks)
    applicable = 0
    passed = 0
    failed = 0
    skipped = 0
    waived = 0
    human_review = 0
    not_applicable = 0

    for check in checks:
        is_applicable = bool(check.get("applicable", True))
        status = _normalize_status(check.get("status"), is_applicable)
        if status == "NOT_APPLICABLE" or not is_applicable:
            not_applicable += 1
            continue
        applicable += 1
        if status == "PASS":
            passed += 1
        elif status == "FAIL":
            failed += 1
        elif status == "SKIPPED":
            skipped += 1
        elif status == "WAIVED_WITH_AUTHOR_EVIDENCE":
            waived += 1
        elif status == "HUMAN_REVIEW_REQUIRED":
            human_review += 1

    computed = {
        "total": total,
        "applicable": applicable,
        "pass": passed,
        "fail": failed,
        "skipped": skipped,
        "waivedWithAuthorEvidence": waived,
        "humanReviewRequired": human_review,
        "notApplicable": not_applicable,
    }
    if isinstance(provided, dict):
        for key, fallback in computed.items():
            raw_val = provided.get(key)
            if isinstance(raw_val, int):
                computed[key] = raw_val
    return computed


def _infer_validation_status(checks: list[dict[str, Any]], explicit: Any) -> str:
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    val_checks = [
        c for c in checks
        if str(c.get("checklist", "")).lower() == "validation"
        and bool(c.get("applicable", True))
        and _normalize_status(c.get("status"), True) != "NOT_APPLICABLE"
    ]
    statuses = {_normalize_status(c.get("status"), True) for c in val_checks}
    if "FAIL" in statuses:
        return "Validation Failed"
    if statuses & {"WAIVED_WITH_AUTHOR_EVIDENCE", "HUMAN_REVIEW_REQUIRED", "SKIPPED"}:
        return "Partially Validated"
    return "Validated"


def _infer_qualification_status(checks: list[dict[str, Any]], explicit: Any) -> str:
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    qual_checks = [
        c for c in checks
        if str(c.get("checklist", "")).lower() == "qualification"
        and bool(c.get("applicable", True))
        and _normalize_status(c.get("status"), True) != "NOT_APPLICABLE"
    ]
    if not qual_checks:
        return "Not Run"
    statuses = {_normalize_status(c.get("status"), True) for c in qual_checks}
    if "FAIL" in statuses:
        return "Qualification Failed"
    if statuses == {"SKIPPED"}:
        return "Not Run"
    if statuses & {"WAIVED_WITH_AUTHOR_EVIDENCE", "HUMAN_REVIEW_REQUIRED", "SKIPPED"}:
        return "Conditionally Qualified"
    return "Qualified"


def _infer_migration_status(checks: list[dict[str, Any]], is_migration: bool, explicit: Any) -> str:
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    if not is_migration:
        return "Not Applicable"
    mig_checks = [
        c for c in checks
        if str(c.get("checklist", "")).lower() == "migration"
        and bool(c.get("applicable", True))
        and _normalize_status(c.get("status"), True) != "NOT_APPLICABLE"
    ]
    if not mig_checks:
        return "Migration Verified"
    statuses = {_normalize_status(c.get("status"), True) for c in mig_checks}
    if "FAIL" in statuses:
        return "Migration Failed"
    if statuses & {"WAIVED_WITH_AUTHOR_EVIDENCE", "HUMAN_REVIEW_REQUIRED", "SKIPPED"}:
        return "Conditionally Migrated"
    return "Migration Verified"


def _sanitize_check_item(item: dict[str, Any]) -> dict[str, Any]:
    cleaned = dict(item)
    for text_field in (
        "whatWeChecked",
        "whatWeObserved",
        "whyPassedOrFailed",
        "applicabilityReason",
        "reviewerActionPrompt",
    ):
        val = cleaned.get(text_field)
        if isinstance(val, str) and val.strip():
            cleaned[text_field] = sanitize_decision_text(val)

    raw_refs = cleaned.get("evidenceRefs")
    if isinstance(raw_refs, list):
        safe_refs: list[Any] = []
        for ref in raw_refs:
            if isinstance(ref, dict):
                ref_copy = dict(ref)
                raw_path = str(ref_copy.get("path") or "")
                if _UNSAFE_SCHEME_RE.match(raw_path):
                    ref_copy["path"] = "#"
                elif raw_path.strip():
                    ref_copy["path"] = sanitize_decision_text(raw_path)
                if isinstance(ref_copy.get("label"), str) and ref_copy["label"].strip():
                    ref_copy["label"] = sanitize_decision_text(ref_copy["label"])
                safe_refs.append(ref_copy)
            else:
                safe_refs.append(ref)
        cleaned["evidenceRefs"] = safe_refs

    raw_exc = cleaned.get("authorException")
    if isinstance(raw_exc, dict):
        exc_copy = dict(raw_exc)
        for exc_field in ("authorJustification", "author"):
            if isinstance(exc_copy.get(exc_field), str) and exc_copy[exc_field].strip():
                exc_copy[exc_field] = sanitize_decision_text(exc_copy[exc_field])
        sup_ref = str(exc_copy.get("supportingEvidenceRef") or "")
        if _UNSAFE_SCHEME_RE.match(sup_ref):
            exc_copy["supportingEvidenceRef"] = "#"
        elif sup_ref.strip():
            exc_copy["supportingEvidenceRef"] = sanitize_decision_text(sup_ref)
        cleaned["authorException"] = exc_copy

    return cleaned


def _normalize_report_data(report_data: dict[str, Any] | None) -> dict[str, Any]:
    raw = dict(report_data or {})
    raw_checks = raw.get("checks")
    checks: list[dict[str, Any]] = [
        _sanitize_check_item(item) for item in raw_checks if isinstance(item, dict)
    ] if isinstance(raw_checks, list) else []

    is_migration = bool(raw.get("isMigration", False))
    summary_counts = _compute_summary_counts(checks, raw.get("summaryCounts"))
    validation_status = _infer_validation_status(checks, raw.get("validationStatus"))
    qualification_status = _infer_qualification_status(checks, raw.get("qualificationStatus"))
    migration_status = _infer_migration_status(checks, is_migration, raw.get("migrationStatus"))

    detected_types_raw = raw.get("detectedContentTypes")
    detected_content_types = (
        [str(t) for t in detected_types_raw if t is not None and str(t).strip()]
        if isinstance(detected_types_raw, list)
        else []
    )

    generated_at = str(raw.get("generatedAtUtc") or "").strip()
    if not generated_at:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    previous_version_raw = raw.get("previousVersion")
    previous_version = (
        str(previous_version_raw).strip()
        if previous_version_raw is not None and str(previous_version_raw).strip()
        else None
    )

    solution_path_raw = raw.get("solutionPath")
    solution_path = (
        str(solution_path_raw).strip()
        if solution_path_raw is not None and str(solution_path_raw).strip()
        else None
    )

    return {
        "schemaVersion": str(raw.get("schemaVersion") or SCHEMA_VERSION),
        "solutionName": str(raw.get("solutionName") or "Unknown Solution"),
        "solutionPath": solution_path,
        "solutionVersion": str(raw.get("solutionVersion") or "0.0.0"),
        "previousVersion": previous_version,
        "isMigration": is_migration,
        "generatedAtUtc": generated_at,
        "validationStatus": validation_status,
        "qualificationStatus": qualification_status,
        "migrationStatus": migration_status,
        "detectedContentTypes": detected_content_types,
        "summaryCounts": summary_counts,
        "checks": checks,
    }


def _is_reviewer_action_check(check: dict[str, Any]) -> bool:
    status = _normalize_status(check.get("status"), bool(check.get("applicable", True)))
    return status in ACTION_QUEUE_STATUSES or bool(check.get("reviewerActionRequired", False))


def _format_evidence_ref_html(
    ref: dict[str, Any],
    *,
    output_dir: Path | None = None,
    solution_root: Path | None = None,
) -> str:
    raw_path = str(ref.get("path") or "").strip()
    raw_label = str(ref.get("label") or raw_path or "Evidence").strip()
    raw_kind = str(ref.get("kind") or "").strip()
    line = ref.get("line")
    has_line = isinstance(line, int) and not isinstance(line, bool)

    href = _sanitize_href(raw_path, output_dir=output_dir, solution_root=solution_root)
    escaped_label = _escape(raw_label)
    escaped_path = _escape(raw_path)
    line_suffix = f":{line}" if has_line else ""
    path_with_line = f"{escaped_path}{line_suffix}" if escaped_path else ""
    kind_badge = (
        f' <span class="evidence-kind">[{_escape(raw_kind)}]</span>'
        if raw_kind
        else ""
    )
    line_attr = f' data-line="{line}"' if has_line else ""

    if path_with_line and raw_label != f"{raw_path}{line_suffix}":
        display_html = f'{escaped_label} <code class="evidence-path">{path_with_line}</code>'
    elif path_with_line:
        display_html = f'<code class="evidence-path">{path_with_line}</code>'
    else:
        display_html = escaped_label

    return (
        f'<a class="evidence-link" href="{href}" target="_blank" rel="noopener noreferrer"{line_attr}>{display_html}</a>{kind_badge}'
    )


def _render_evidence_links_list_html(
    check: dict[str, Any],
    *,
    output_dir: Path | None = None,
    solution_root: Path | None = None,
) -> str:
    items: list[str] = []
    evidence_refs = check.get("evidenceRefs")
    if isinstance(evidence_refs, list):
        for ref in evidence_refs:
            if isinstance(ref, dict) and (ref.get("path") or ref.get("label")):
                items.append(
                    f"<li>{_format_evidence_ref_html(ref, output_dir=output_dir, solution_root=solution_root)}</li>"
                )

    author_exc = check.get("authorException")
    if isinstance(author_exc, dict):
        supporting_ref = str(author_exc.get("supportingEvidenceRef") or "").strip()
        if supporting_ref:
            href = _sanitize_href(supporting_ref, output_dir=output_dir, solution_root=solution_root)
            escaped_ref = _escape(supporting_ref)
            items.append(
                "<li>"
                f'<a class="evidence-link supporting-evidence-link" href="{href}" target="_blank" rel="noopener noreferrer">'
                f"Author Supporting Evidence: <code>{escaped_ref}</code>"
                "</a>"
                ' <span class="evidence-kind">[author-exception]</span>'
                "</li>"
            )

    if not items:
        return '<span class="muted">No evidence files attached</span>'
    return f'<ul class="evidence-list">{"".join(items)}</ul>'


def _format_evidence_links_markdown(
    check: dict[str, Any],
    *,
    output_dir: Path | None = None,
    solution_root: Path | None = None,
) -> str:
    links: list[str] = []
    evidence_refs = check.get("evidenceRefs")
    if isinstance(evidence_refs, list):
        for ref in evidence_refs:
            if not isinstance(ref, dict):
                continue
            raw_path = str(ref.get("path") or "").strip()
            raw_label = str(ref.get("label") or raw_path or "Evidence").strip()
            line = ref.get("line")
            has_line = isinstance(line, int) and not isinstance(line, bool)
            if not raw_path and not raw_label:
                continue
            label_with_line = f"{raw_label}:{line}" if has_line else raw_label
            safe_label = _escape_markdown_cell(label_with_line)
            safe_url = _sanitize_markdown_url(raw_path, output_dir=output_dir, solution_root=solution_root)
            links.append(f"[{safe_label}]({safe_url})")

    author_exc = check.get("authorException")
    if isinstance(author_exc, dict):
        supporting_ref = str(author_exc.get("supportingEvidenceRef") or "").strip()
        if supporting_ref:
            safe_ref_label = _escape_markdown_cell(supporting_ref)
            safe_ref_url = _sanitize_markdown_url(
                supporting_ref, output_dir=output_dir, solution_root=solution_root
            )
            links.append(f"[Author Evidence: {safe_ref_label}]({safe_ref_url})")

    return ", ".join(links) if links else "—"


def _reviewer_prompt_for_check(check: dict[str, Any]) -> str:
    status = _normalize_status(check.get("status"), bool(check.get("applicable", True)))
    custom_prompt = str(check.get("reviewerActionPrompt") or "").strip()
    if status == "WAIVED_WITH_AUTHOR_EVIDENCE":
        if custom_prompt and DEFAULT_WAIVER_REVIEWER_PROMPT.lower() not in custom_prompt.lower():
            return f"{DEFAULT_WAIVER_REVIEWER_PROMPT} ({custom_prompt})"
        return custom_prompt or DEFAULT_WAIVER_REVIEWER_PROMPT
    if custom_prompt:
        return custom_prompt
    if status == "HUMAN_REVIEW_REQUIRED":
        return DEFAULT_HUMAN_REVIEW_PROMPT
    if status == "FAIL":
        return DEFAULT_FAILURE_REVIEW_PROMPT
    return "Review check details and confirm qualification sign-off."


def _render_author_exception_box_html(
    author_exc: dict[str, Any] | None,
    reviewer_prompt: str,
    *,
    output_dir: Path | None = None,
    solution_root: Path | None = None,
) -> str:
    if not isinstance(author_exc, dict):
        return ""
    original_status = _escape(author_exc.get("originalStatus") or "FAIL")
    justification = _escape(author_exc.get("authorJustification") or "No justification provided.")
    supporting_ref = str(author_exc.get("supportingEvidenceRef") or "").strip()
    author = str(author_exc.get("author") or "").strip()

    supporting_link_html = (
        f'<a class="evidence-link supporting-evidence-link" href="{_sanitize_href(supporting_ref, output_dir=output_dir, solution_root=solution_root)}" target="_blank" rel="noopener noreferrer">'
        f"{_escape(supporting_ref)}</a>"
        if supporting_ref
        else '<span class="muted">None provided</span>'
    )
    author_line = (
        f'<div class="waiver-meta"><strong>Author:</strong> {_escape(author)}</div>'
        if author
        else ""
    )

    return (
        '<div class="author-waiver-box">'
        '<div class="waiver-header">Author Exception / Waiver Evidence</div>'
        f'<div class="waiver-meta"><strong>Original Status:</strong> <span class="badge tone-red">{original_status}</span></div>'
        f"{author_line}"
        f'<div class="waiver-meta"><strong>Author Justification:</strong> {justification}</div>'
        f'<div class="waiver-meta"><strong>Supporting Evidence File:</strong> {supporting_link_html}</div>'
        f'<div class="waiver-prompt"><strong>Reviewer Action:</strong> {_escape(reviewer_prompt)}</div>'
        "</div>"
    )


def _render_reviewer_action_queue_html(
    checks: list[dict[str, Any]],
    *,
    output_dir: Path | None = None,
    solution_root: Path | None = None,
) -> str:
    action_checks = [c for c in checks if _is_reviewer_action_check(c)]
    if not action_checks:
        return (
            '<section class="section-card action-queue-section" id="reviewer-action-queue">'
            '<div class="section-header">'
            "<h2>Reviewer Action Queue</h2>"
            '<span class="badge tone-green">0 Actions Required</span>'
            "</div>"
            '<p class="queue-empty">All applicable checks passed automatically without exceptions or manual review gates.</p>'
            "</section>"
        )

    cards_html: list[str] = []
    for check in action_checks:
        check_id = _escape(check.get("id") or "CHECK")
        title = _escape(check.get("title") or check.get("id") or "Untitled Check")
        checklist = _escape(str(check.get("checklist") or "validation").title())
        content_type = _escape(check.get("contentType") or "Solution")
        status = _normalize_status(check.get("status"), bool(check.get("applicable", True)))
        status_label = STATUS_DISPLAY_LABELS.get(status, status)
        tone = STATUS_BADGE_TONES.get(status, "amber")
        prompt = _reviewer_prompt_for_check(check)
        what_checked = _escape(check.get("whatWeChecked") or "—")
        what_observed = _escape(check.get("whatWeObserved") or "—")
        why_result = _escape(check.get("whyPassedOrFailed") or "—")

        author_exc = check.get("authorException") if isinstance(check.get("authorException"), dict) else None
        waiver_html = _render_author_exception_box_html(
            author_exc, prompt, output_dir=output_dir, solution_root=solution_root
        )
        evidence_list_html = _render_evidence_links_list_html(
            check, output_dir=output_dir, solution_root=solution_root
        )

        human_review_block = ""
        if status != "WAIVED_WITH_AUTHOR_EVIDENCE" or not waiver_html:
            human_review_block = (
                '<div class="reviewer-prompt-box">'
                f"<strong>Reviewer Confirmation Required:</strong> {_escape(prompt)}"
                "</div>"
            )

        cards_html.append(
            f'<article class="action-queue-card tone-border-{tone}" data-check-id="{check_id}" data-status="{_escape(status)}">'
            '<div class="action-card-top">'
            f'<span class="badge tone-{tone}">{_escape(status_label)}</span>'
            f'<span class="check-id-pill">{check_id}</span>'
            f'<span class="meta-pill">{checklist}</span>'
            f'<span class="meta-pill">{content_type}</span>'
            "</div>"
            f'<h3 class="action-card-title">{_escape(status_label)} - {title}</h3>'
            f'<div class="action-card-details">'
            f"<div><strong>What We Checked:</strong> {what_checked}</div>"
            f"<div><strong>What We Observed:</strong> {what_observed}</div>"
            f"<div><strong>Why:</strong> {why_result}</div>"
            "</div>"
            f"{waiver_html}"
            f"{human_review_block}"
            '<div class="action-card-evidence">'
            "<strong>Gathered Supporting Evidence:</strong>"
            f"{evidence_list_html}"
            "</div>"
            "</article>"
        )

    return (
        '<section class="section-card action-queue-section" id="reviewer-action-queue">'
        '<div class="section-header">'
        "<h2>Reviewer Action Queue</h2>"
        f'<span class="badge tone-amber">{len(action_checks)} Item(s) Require Reviewer Attention</span>'
        "</div>"
        '<p class="section-subtitle">'
        "Items below require human reviewer verification, author exception sign-off, or remediation before final approval."
        "</p>"
        f'<div class="action-queue-grid">{"".join(cards_html)}</div>'
        "</section>"
    )


def _render_checklist_row_html(
    check: dict[str, Any],
    *,
    output_dir: Path | None = None,
    solution_root: Path | None = None,
) -> str:
    check_id = _escape(check.get("id") or "CHECK")
    checklist = str(check.get("checklist") or "validation").strip().lower()
    title = _escape(check.get("title") or check.get("id") or "Untitled Check")
    original_criterion = _escape(check.get("originalCriterion") or "")
    content_type = _escape(check.get("contentType") or "Solution")
    category = _escape(check.get("category") or checklist)
    source_checklist = _escape(check.get("sourceChecklist") or checklist.title())
    applicable = bool(check.get("applicable", True))
    applicability_reason = _escape(check.get("applicabilityReason") or "")
    status = _normalize_status(check.get("status"), applicable)
    status_label = STATUS_DISPLAY_LABELS.get(status, status)
    tone = STATUS_BADGE_TONES.get(status, "gray")
    action_required = "true" if _is_reviewer_action_check(check) else "false"

    what_checked = _escape(check.get("whatWeChecked") or "—")
    what_observed = _escape(check.get("whatWeObserved") or "—")
    why_result = _escape(check.get("whyPassedOrFailed") or "—")

    prompt = _reviewer_prompt_for_check(check)
    author_exc = check.get("authorException") if isinstance(check.get("authorException"), dict) else None
    waiver_box_html = _render_author_exception_box_html(
        author_exc, prompt, output_dir=output_dir, solution_root=solution_root
    )

    reviewer_prompt_inline = ""
    if _is_reviewer_action_check(check) and not waiver_box_html:
        reviewer_prompt_inline = (
            '<div class="reviewer-prompt-box">'
            f"<strong>Reviewer Action:</strong> {_escape(prompt)}"
            "</div>"
        )

    applicability_html = (
        f'<div class="applicability-note"><strong>Applicability:</strong> {applicability_reason}</div>'
        if applicability_reason
        else ""
    )

    criterion_subtext = (
        f'<div class="criterion-text">{original_criterion}</div>'
        if original_criterion
        else ""
    )

    evidence_links_html = _render_evidence_links_list_html(
        check, output_dir=output_dir, solution_root=solution_root
    )

    return (
        f'<tr class="check-row" '
        f'data-checklist="{_escape(checklist)}" '
        f'data-status="{_escape(status)}" '
        f'data-action-required="{action_required}" '
        f'data-check-id="{check_id}">'
        '<td class="col-id">'
        f'<div class="check-id-code">{check_id}</div>'
        f'<div class="check-meta-badges">'
        f'<span class="meta-pill">{content_type}</span>'
        f'<span class="source-badge">{source_checklist}</span>'
        "</div>"
        "</td>"
        '<td class="col-criterion">'
        f'<div class="criterion-title"><strong>{title}</strong></div>'
        f"{criterion_subtext}"
        "</td>"
        f'<td class="col-category"><span class="category-pill">{category}</span></td>'
        '<td class="col-status">'
        f'<span class="badge tone-{tone}">{_escape(status_label)}</span>'
        f'<div class="status-code-raw">{_escape(status)}</div>'
        f"{applicability_html}"
        "</td>"
        '<td class="col-details">'
        f'<div class="detail-item"><strong>What We Checked:</strong> {what_checked}</div>'
        f'<div class="detail-item"><strong>What We Observed:</strong> {what_observed}</div>'
        f'<div class="detail-item"><strong>Why:</strong> {why_result}</div>'
        f"{waiver_box_html}"
        f"{reviewer_prompt_inline}"
        "</td>"
        f'<td class="col-evidence">{evidence_links_html}</td>'
        "</tr>"
    )


def _render_checklist_tables_html(
    checks: list[dict[str, Any]],
    *,
    output_dir: Path | None = None,
    solution_root: Path | None = None,
) -> str:
    sections_html: list[str] = []
    for checklist_key, heading, description in CHECKLIST_DEFINITIONS:
        section_checks = [
            c for c in checks
            if str(c.get("checklist") or "validation").strip().lower() == checklist_key
        ]
        rows_html = (
            "".join(
                _render_checklist_row_html(c, output_dir=output_dir, solution_root=solution_root)
                for c in section_checks
            )
            if section_checks
            else (
                '<tr class="empty-checklist-row">'
                '<td colspan="6" class="muted">No checks recorded for this checklist.</td>'
                "</tr>"
            )
        )
        sections_html.append(
            f'<section class="section-card checklist-section" data-checklist-section="{_escape(checklist_key)}">'
            '<div class="section-header">'
            f"<h2>{_escape(heading)}</h2>"
            f'<span class="meta-pill">{len(section_checks)} Check(s)</span>'
            "</div>"
            f'<p class="section-subtitle">{_escape(description)}</p>'
            '<div class="table-wrapper">'
            '<table class="checklist-table">'
            "<thead>"
            "<tr>"
            "<th>Check ID &amp; Source</th>"
            "<th>Reviewer Criterion</th>"
            "<th>Category</th>"
            "<th>Status</th>"
            "<th>Evidence Details (What We Checked / Observed / Why)</th>"
            "<th>Detailed Evidence Files</th>"
            "</tr>"
            "</thead>"
            f"<tbody>{rows_html}</tbody>"
            "</table>"
            "</div>"
            "</section>"
        )
    return "".join(sections_html)


def render_pr_qualification_html(
    report_data: dict[str, Any],
    *,
    output_dir: Path | None = None,
    solution_root: Path | None = None,
) -> str:
    """Render a self-contained HTML5 PR Qualification & Validation report."""
    data = _normalize_report_data(report_data)
    resolved_output_dir = Path(output_dir).expanduser().resolve() if output_dir else None
    resolved_solution_root = _resolve_solution_root(
        data.get("solutionPath"),
        resolved_output_dir,
        solution_root,
    )
    solution_name = _escape(data["solutionName"])
    solution_version = _escape(data["solutionVersion"])
    previous_version = data["previousVersion"]
    version_display = (
        f"{solution_version} <span class=\"version-prev\">(previous: {_escape(previous_version)})</span>"
        if previous_version
        else f"{solution_version} <span class=\"version-prev\">(new / no prior version)</span>"
    )
    mode_label = (
        "Migration + Qualification"
        if data["isMigration"]
        else "General Solution Qualification"
    )
    mode_tone = "blue" if data["isMigration"] else "slate"
    generated_at = _escape(data["generatedAtUtc"])

    val_status = data["validationStatus"]
    qual_status = data["qualificationStatus"]
    mig_status = data["migrationStatus"]

    val_tone = ROLLUP_CARD_TONES.get(val_status, "amber")
    qual_tone = ROLLUP_CARD_TONES.get(qual_status, "gray")
    mig_tone = ROLLUP_CARD_TONES.get(mig_status, "gray")

    counts = data["summaryCounts"]
    checklist_counts = {
        "all": len(data["checks"]),
        "validation": sum(
            1 for c in data["checks"]
            if str(c.get("checklist") or "validation").strip().lower() == "validation"
        ),
        "qualification": sum(
            1 for c in data["checks"]
            if str(c.get("checklist") or "validation").strip().lower() == "qualification"
        ),
        "migration": sum(
            1 for c in data["checks"]
            if str(c.get("checklist") or "validation").strip().lower() == "migration"
        ),
    }
    action_required_count = sum(1 for c in data["checks"] if _is_reviewer_action_check(c))
    detected_types = data["detectedContentTypes"]
    detected_pills = (
        "".join(f'<span class="content-type-pill">{_escape(t)}</span>' for t in detected_types)
        if detected_types
        else '<span class="content-type-pill">None Detected</span>'
    )

    action_queue_html = _render_reviewer_action_queue_html(
        data["checks"],
        output_dir=resolved_output_dir,
        solution_root=resolved_solution_root,
    )
    checklists_html = _render_checklist_tables_html(
        data["checks"],
        output_dir=resolved_output_dir,
        solution_root=resolved_solution_root,
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PR Qualification Report — {solution_name} ({solution_version})</title>
  <style>
    :root {{
      --bg: #f8fafc;
      --surface: #ffffff;
      --border: #e2e8f0;
      --text: #0f172a;
      --muted: #475569;
      --green-bg: #dcfce7;
      --green-fg: #166534;
      --green-border: #22c55e;
      --amber-bg: #fef3c7;
      --amber-fg: #92400e;
      --amber-border: #f59e0b;
      --red-bg: #fee2e2;
      --red-fg: #991b1b;
      --red-border: #ef4444;
      --gray-bg: #f1f5f9;
      --gray-fg: #334155;
      --gray-border: #94a3b8;
      --blue-bg: #dbeafe;
      --blue-fg: #1e40af;
      --blue-border: #3b82f6;
      --accent: #2563eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 24px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    .container {{
      max-width: 1480px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}
    .exec-header, .section-card, .filter-bar {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px 24px;
      box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }}
    .exec-top {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 16px;
    }}
    .exec-title {{
      margin: 0 0 6px 0;
      font-size: 1.6rem;
      font-weight: 700;
    }}
    .exec-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
      font-size: 0.92rem;
      color: var(--muted);
      align-items: center;
    }}
    .version-prev {{
      color: var(--muted);
      font-weight: 400;
    }}
    .content-types-bar {{
      margin-top: 12px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      font-size: 0.85rem;
    }}
    .content-type-pill, .meta-pill, .category-pill, .source-badge, .check-id-pill {{
      display: inline-block;
      padding: 2px 10px;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 600;
      background: var(--gray-bg);
      color: var(--gray-fg);
      border: 1px solid var(--border);
    }}
    .source-badge {{
      background: var(--blue-bg);
      color: var(--blue-fg);
    }}
    .rollup-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
      margin-top: 18px;
    }}
    .rollup-card {{
      padding: 16px 18px;
      border-radius: 10px;
      border: 1px solid var(--border);
      border-left-width: 6px;
      background: var(--surface);
    }}
    .rollup-card.tone-green {{ border-left-color: var(--green-border); background: #f0fdf4; }}
    .rollup-card.tone-amber {{ border-left-color: var(--amber-border); background: #fffbeb; }}
    .rollup-card.tone-red {{ border-left-color: var(--red-border); background: #fef2f2; }}
    .rollup-card.tone-gray {{ border-left-color: var(--gray-border); background: var(--gray-bg); }}
    .rollup-label {{
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
      font-weight: 600;
    }}
    .rollup-value {{
      font-size: 1.25rem;
      font-weight: 700;
      margin-top: 6px;
    }}
    .summary-pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 18px;
      padding-top: 14px;
      border-top: 1px solid var(--border);
    }}
    .metric-pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      border-radius: 999px;
      font-size: 0.85rem;
      font-weight: 600;
      border: 1px solid var(--border);
      background: var(--gray-bg);
    }}
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.02em;
    }}
    .tone-green {{ background: var(--green-bg); color: var(--green-fg); border: 1px solid var(--green-border); }}
    .tone-amber {{ background: var(--amber-bg); color: var(--amber-fg); border: 1px solid var(--amber-border); }}
    .tone-red {{ background: var(--red-bg); color: var(--red-fg); border: 1px solid var(--red-border); }}
    .tone-gray, .tone-slate {{ background: var(--gray-bg); color: var(--gray-fg); border: 1px solid var(--gray-border); }}
    .tone-blue {{ background: var(--blue-bg); color: var(--blue-fg); border: 1px solid var(--blue-border); }}
    .section-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;
    }}
    .section-header h2 {{
      margin: 0;
      font-size: 1.2rem;
    }}
    .section-subtitle {{
      margin: 0 0 16px 0;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .action-queue-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
      gap: 16px;
    }}
    .action-queue-card {{
      border: 1px solid var(--border);
      border-left-width: 5px;
      border-radius: 10px;
      padding: 16px;
      background: #fffdf9;
    }}
    .tone-border-amber {{ border-left-color: var(--amber-border); }}
    .tone-border-red {{ border-left-color: var(--red-border); background: #fffafa; }}
    .tone-border-green {{ border-left-color: var(--green-border); }}
    .action-card-top {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin-bottom: 8px;
    }}
    .action-card-title {{
      margin: 0 0 10px 0;
      font-size: 1.02rem;
    }}
    .action-card-details {{
      font-size: 0.88rem;
      display: flex;
      flex-direction: column;
      gap: 4px;
      margin-bottom: 10px;
    }}
    .author-waiver-box {{
      margin-top: 10px;
      padding: 12px;
      border-radius: 8px;
      background: var(--amber-bg);
      border: 1px solid var(--amber-border);
      font-size: 0.86rem;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .waiver-header {{
      font-weight: 700;
      color: var(--amber-fg);
      text-transform: uppercase;
      font-size: 0.76rem;
      letter-spacing: 0.04em;
    }}
    .waiver-prompt, .reviewer-prompt-box {{
      margin-top: 8px;
      padding: 8px 10px;
      border-radius: 6px;
      background: #eff6ff;
      border: 1px solid #93c5fd;
      color: #1e3a8a;
      font-size: 0.85rem;
    }}
    .filter-controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      align-items: center;
      justify-content: space-between;
    }}
    .filter-group {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
    }}
    .filter-group-label {{
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--muted);
      margin-right: 4px;
    }}
    .filter-btn {{
      padding: 6px 12px;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: var(--gray-bg);
      color: var(--text);
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .filter-btn.active {{
      background: var(--accent);
      color: #ffffff;
      border-color: var(--accent);
    }}
    .filter-count {{
      display: inline-block;
      padding: 1px 6px;
      border-radius: 999px;
      font-size: 0.74rem;
      font-weight: 700;
      background: rgba(15, 23, 42, 0.08);
      color: inherit;
    }}
    .filter-btn.active .filter-count {{
      background: rgba(255, 255, 255, 0.22);
      color: #ffffff;
    }}
    .search-input {{
      padding: 7px 12px;
      border-radius: 6px;
      border: 1px solid var(--border);
      font-size: 0.88rem;
      min-width: 260px;
    }}
    .table-wrapper {{
      overflow-x: auto;
    }}
    .checklist-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
    }}
    .checklist-table th, .checklist-table td {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
      text-align: left;
    }}
    .checklist-table th {{
      background: var(--gray-bg);
      font-weight: 700;
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: var(--muted);
    }}
    .check-id-code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-weight: 700;
      margin-bottom: 6px;
    }}
    .check-meta-badges {{
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
    }}
    .criterion-title {{
      margin-bottom: 4px;
    }}
    .criterion-text {{
      color: var(--muted);
      font-size: 0.84rem;
    }}
    .status-code-raw {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.72rem;
      color: var(--muted);
      margin-top: 4px;
    }}
    .applicability-note {{
      margin-top: 6px;
      font-size: 0.78rem;
      color: var(--muted);
    }}
    .detail-item {{
      margin-bottom: 6px;
    }}
    .evidence-list {{
      margin: 4px 0 0 0;
      padding-left: 18px;
    }}
    .evidence-list li {{
      margin-bottom: 4px;
    }}
    .evidence-link {{
      color: var(--accent);
      text-decoration: none;
      font-weight: 500;
    }}
    .evidence-link:hover {{
      text-decoration: underline;
    }}
    .evidence-kind {{
      font-size: 0.75rem;
      color: var(--muted);
    }}
    .muted {{
      color: var(--muted);
    }}
    .hidden-by-filter {{
      display: none !important;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header class="exec-header" id="executive-header">
      <div class="exec-top">
        <div>
          <h1 class="exec-title">{solution_name}</h1>
          <div class="exec-meta">
            <span><strong>Version:</strong> {version_display}</span>
            <span><strong>Generated (UTC):</strong> {generated_at}</span>
            <span><strong>Schema:</strong> <code>{_escape(data["schemaVersion"])}</code></span>
          </div>
          <div class="content-types-bar">
            <strong>Detected Content Types:</strong> {detected_pills}
          </div>
        </div>
        <div>
          <span class="badge tone-{mode_tone}" id="mode-badge">{_escape(mode_label)}</span>
        </div>
      </div>

      <div class="rollup-grid" id="rollup-status-cards">
        <div class="rollup-card tone-{val_tone}" data-rollup="validation">
          <div class="rollup-label">1. Validation Checklist</div>
          <div class="rollup-value">{_escape(val_status)}</div>
        </div>
        <div class="rollup-card tone-{qual_tone}" data-rollup="qualification">
          <div class="rollup-label">2. Qualification Checklist</div>
          <div class="rollup-value">{_escape(qual_status)}</div>
        </div>
        <div class="rollup-card tone-{mig_tone}" data-rollup="migration">
          <div class="rollup-label">3. Migration Overlay</div>
          <div class="rollup-value">{_escape(mig_status)}</div>
        </div>
      </div>

      <div class="summary-pills" id="summary-metric-pills">
        <span class="metric-pill tone-green">Passed: <strong>{counts["pass"]}</strong></span>
        <span class="metric-pill tone-amber">Waived with Author Evidence: <strong>{counts["waivedWithAuthorEvidence"]}</strong></span>
        <span class="metric-pill tone-amber">Human Review Required: <strong>{counts["humanReviewRequired"]}</strong></span>
        <span class="metric-pill tone-red">Failed: <strong>{counts["fail"]}</strong></span>
        <span class="metric-pill tone-gray">Not Applicable: <strong>{counts["notApplicable"]}</strong></span>
        <span class="metric-pill tone-gray">Skipped: <strong>{counts["skipped"]}</strong></span>
        <span class="metric-pill">Applicable / Total: <strong>{counts["applicable"]} / {counts["total"]}</strong></span>
      </div>
    </header>

    {action_queue_html}

    <section class="filter-bar" id="interactive-filter-bar" aria-label="Checklist Filters">
      <div class="filter-controls">
        <div class="filter-group" role="group" aria-label="Filter by Checklist">
          <span class="filter-group-label">Checklist:</span>
          <button type="button" class="filter-btn active" data-filter-checklist="all">All <span class="filter-count">{checklist_counts["all"]}</span></button>
          <button type="button" class="filter-btn" data-filter-checklist="validation">Validation <span class="filter-count">{checklist_counts["validation"]}</span></button>
          <button type="button" class="filter-btn" data-filter-checklist="qualification">Qualification <span class="filter-count">{checklist_counts["qualification"]}</span></button>
          <button type="button" class="filter-btn" data-filter-checklist="migration">Migration <span class="filter-count">{checklist_counts["migration"]}</span></button>
        </div>
        <div class="filter-group" role="group" aria-label="Filter by Status">
          <span class="filter-group-label">Status:</span>
          <button type="button" class="filter-btn active" data-filter-status="ALL">All Statuses <span class="filter-count">{counts["total"]}</span></button>
          <button type="button" class="filter-btn" data-filter-status="ACTION_REQUIRED">Action Required <span class="filter-count">{action_required_count}</span></button>
          <button type="button" class="filter-btn" data-filter-status="PASS">PASS <span class="filter-count">{counts["pass"]}</span></button>
          <button type="button" class="filter-btn" data-filter-status="WAIVED_WITH_AUTHOR_EVIDENCE">WAIVED_WITH_AUTHOR_EVIDENCE <span class="filter-count">{counts["waivedWithAuthorEvidence"]}</span></button>
          <button type="button" class="filter-btn" data-filter-status="HUMAN_REVIEW_REQUIRED">HUMAN_REVIEW_REQUIRED <span class="filter-count">{counts["humanReviewRequired"]}</span></button>
          <button type="button" class="filter-btn" data-filter-status="FAIL">FAIL <span class="filter-count">{counts["fail"]}</span></button>
          <button type="button" class="filter-btn" data-filter-status="NOT_APPLICABLE">NOT_APPLICABLE <span class="filter-count">{counts["notApplicable"]}</span></button>
        </div>
        <div class="filter-group">
          <input type="search" id="check-search-input" class="search-input" placeholder="Search checks, criteria, evidence..." aria-label="Search checks">
        </div>
      </div>
    </section>

    <main id="checklist-tables-container">
      {checklists_html}
    </main>
  </div>

  <script>
    (function () {{
      var activeChecklist = "all";
      var activeStatus = "ALL";
      var searchQuery = "";

      var checklistButtons = document.querySelectorAll("[data-filter-checklist]");
      var statusButtons = document.querySelectorAll("[data-filter-status]");
      var searchInput = document.getElementById("check-search-input");
      var rows = document.querySelectorAll("tr.check-row");
      var sections = document.querySelectorAll("[data-checklist-section]");

      function matchesStatus(rowStatus, rowAction, targetStatus) {{
        if (targetStatus === "ALL") {{
          return true;
        }}
        if (targetStatus === "ACTION_REQUIRED") {{
          return rowAction;
        }}
        return rowStatus === targetStatus;
      }}

      function updateFilterCounts() {{
        var q = searchQuery.toLowerCase();
        var cCounts = {{ all: 0, validation: 0, qualification: 0, migration: 0 }};
        var sCounts = {{
          ALL: 0,
          ACTION_REQUIRED: 0,
          PASS: 0,
          WAIVED_WITH_AUTHOR_EVIDENCE: 0,
          HUMAN_REVIEW_REQUIRED: 0,
          FAIL: 0,
          NOT_APPLICABLE: 0
        }};

        rows.forEach(function (row) {{
          var rowChecklist = (row.getAttribute("data-checklist") || "").toLowerCase();
          var rowStatus = row.getAttribute("data-status") || "";
          var rowAction = row.getAttribute("data-action-required") === "true";
          var text = (row.textContent || "").toLowerCase();
          var matchSearch = !q || text.indexOf(q) !== -1;
          if (!matchSearch) {{
            return;
          }}

          if (matchesStatus(rowStatus, rowAction, activeStatus)) {{
            cCounts.all += 1;
            if (cCounts.hasOwnProperty(rowChecklist)) {{
              cCounts[rowChecklist] += 1;
            }}
          }}

          if (activeChecklist === "all" || rowChecklist === activeChecklist) {{
            sCounts.ALL += 1;
            if (rowAction) {{
              sCounts.ACTION_REQUIRED += 1;
            }}
            if (sCounts.hasOwnProperty(rowStatus)) {{
              sCounts[rowStatus] += 1;
            }}
          }}
        }});

        checklistButtons.forEach(function (btn) {{
          var key = (btn.getAttribute("data-filter-checklist") || "all").toLowerCase();
          var badge = btn.querySelector(".filter-count");
          if (badge && cCounts.hasOwnProperty(key)) {{
            badge.textContent = String(cCounts[key]);
          }}
        }});

        statusButtons.forEach(function (btn) {{
          var key = btn.getAttribute("data-filter-status") || "ALL";
          var badge = btn.querySelector(".filter-count");
          if (badge && sCounts.hasOwnProperty(key)) {{
            badge.textContent = String(sCounts[key]);
          }}
        }});
      }}

      function applyFilters() {{
        var q = searchQuery.toLowerCase();
        rows.forEach(function (row) {{
          var rowChecklist = (row.getAttribute("data-checklist") || "").toLowerCase();
          var rowStatus = row.getAttribute("data-status") || "";
          var rowAction = row.getAttribute("data-action-required") === "true";
          var text = (row.textContent || "").toLowerCase();

          var matchChecklist = activeChecklist === "all" || rowChecklist === activeChecklist;
          var matchStatus = matchesStatus(rowStatus, rowAction, activeStatus);
          var matchSearch = !q || text.indexOf(q) !== -1;

          if (matchChecklist && matchStatus && matchSearch) {{
            row.classList.remove("hidden-by-filter");
          }} else {{
            row.classList.add("hidden-by-filter");
          }}
        }});

        sections.forEach(function (sec) {{
          var secName = (sec.getAttribute("data-checklist-section") || "").toLowerCase();
          if (activeChecklist !== "all" && secName !== activeChecklist) {{
            sec.classList.add("hidden-by-filter");
          }} else {{
            sec.classList.remove("hidden-by-filter");
          }}
        }});

        updateFilterCounts();
      }}

      checklistButtons.forEach(function (btn) {{
        btn.addEventListener("click", function () {{
          checklistButtons.forEach(function (b) {{ b.classList.remove("active"); }});
          btn.classList.add("active");
          activeChecklist = (btn.getAttribute("data-filter-checklist") || "all").toLowerCase();
          applyFilters();
        }});
      }});

      statusButtons.forEach(function (btn) {{
        btn.addEventListener("click", function () {{
          statusButtons.forEach(function (b) {{ b.classList.remove("active"); }});
          btn.classList.add("active");
          activeStatus = btn.getAttribute("data-filter-status") || "ALL";
          applyFilters();
        }});
      }});

      if (searchInput) {{
        searchInput.addEventListener("input", function (e) {{
          searchQuery = e.target.value || "";
          applyFilters();
        }});
      }}
    }})();
  </script>
</body>
</html>
"""


def render_pr_qualification_markdown(
    report_data: dict[str, Any],
    *,
    output_dir: Path | None = None,
    solution_root: Path | None = None,
) -> str:
    """Render the reviewer-facing Markdown qualification summary (`qualification-summary.md`)."""
    data = _normalize_report_data(report_data)
    resolved_output_dir = Path(output_dir).expanduser().resolve() if output_dir else None
    resolved_solution_root = _resolve_solution_root(
        data.get("solutionPath"),
        resolved_output_dir,
        solution_root,
    )
    solution_name = _escape_markdown_cell(data["solutionName"])
    solution_version = _escape_markdown_cell(data["solutionVersion"])
    previous_version = (
        _escape_markdown_cell(data["previousVersion"])
        if data["previousVersion"]
        else "None (new or baseline)"
    )
    mode_label = (
        "Migration + Qualification"
        if data["isMigration"]
        else "General Solution Qualification"
    )
    detected_types = (
        ", ".join(f"`{_escape_markdown_cell(t)}`" for t in data["detectedContentTypes"])
        if data["detectedContentTypes"]
        else "None"
    )
    counts = data["summaryCounts"]

    lines: list[str] = [
        f"# PR Qualification & Validation Summary — {solution_name} (`{solution_version}`)",
        "",
        f"- **Solution:** {solution_name}",
        f"- **Version:** `{solution_version}` (Previous: `{previous_version}`)",
        f"- **Qualification Mode:** {mode_label}",
        f"- **Detected Content Types:** {detected_types}",
        f"- **Generated (UTC):** `{_escape_markdown_cell(data['generatedAtUtc'])}`",
        f"- **Interactive Full Report:** [{HTML_REPORT_FILENAME}]({HTML_REPORT_FILENAME})",
        "",
        "## Executive Rollup Status",
        "",
        "| Checklist / Track | Rollup Status |",
        "| :--- | :--- |",
        f"| **Validation** | **{_escape_markdown_cell(data['validationStatus'])}** |",
        f"| **Qualification** | **{_escape_markdown_cell(data['qualificationStatus'])}** |",
        f"| **Migration** | **{_escape_markdown_cell(data['migrationStatus'])}** |",
        "",
        "### Summary Counts",
        "",
        "| Passed | Waived with Author Evidence | Human Review Required | Failed | Skipped | Not Applicable | Applicable / Total |",
        "| :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
        (
            f"| {counts['pass']} | {counts['waivedWithAuthorEvidence']} | "
            f"{counts['humanReviewRequired']} | {counts['fail']} | "
            f"{counts['skipped']} | {counts['notApplicable']} | "
            f"{counts['applicable']} / {counts['total']} |"
        ),
        "",
        "## Reviewer Action Queue",
        "",
    ]

    action_checks = [c for c in data["checks"] if _is_reviewer_action_check(c)]
    if not action_checks:
        lines.append("No reviewer actions, manual verifications, or author exception sign-offs are required.")
        lines.append("")
    else:
        for check in action_checks:
            status = _normalize_status(check.get("status"), bool(check.get("applicable", True)))
            status_label = STATUS_DISPLAY_LABELS.get(status, status)
            title = _escape_markdown_cell(check.get("title") or check.get("id") or "Untitled Check")
            check_id = _escape_markdown_cell(check.get("id") or "CHECK")
            checklist_name = _escape_markdown_cell(str(check.get("checklist") or "validation").title())
            content_type = _escape_markdown_cell(check.get("contentType") or "Solution")
            what_checked = _escape_markdown_cell(check.get("whatWeChecked") or "—")
            what_observed = _escape_markdown_cell(check.get("whatWeObserved") or "—")
            why_result = _escape_markdown_cell(check.get("whyPassedOrFailed") or "—")
            prompt = _escape_markdown_cell(_reviewer_prompt_for_check(check))
            evidence_md = _format_evidence_links_markdown(
                check,
                output_dir=resolved_output_dir,
                solution_root=resolved_solution_root,
            )

            lines.extend([
                f"### **{status_label} - {title}** (`{check_id}`)",
                f"- **Checklist / Content Type:** {checklist_name} / `{content_type}`",
                f"- **What We Checked:** {what_checked}",
                f"- **What We Observed:** {what_observed}",
                f"- **Why:** {why_result}",
            ])

            author_exc = check.get("authorException")
            if isinstance(author_exc, dict):
                orig_status = _escape_markdown_cell(author_exc.get("originalStatus") or "FAIL")
                justification = _escape_markdown_cell(author_exc.get("authorJustification") or "—")
                supporting_ref = str(author_exc.get("supportingEvidenceRef") or "").strip()
                author_name = str(author_exc.get("author") or "").strip()
                lines.append(f"- **Original Status:** `{orig_status}`")
                if author_name:
                    lines.append(f"- **Author:** `{_escape_markdown_cell(author_name)}`")
                lines.append(f"- **Author Justification:** {justification}")
                if supporting_ref:
                    safe_label = _escape_markdown_cell(supporting_ref)
                    safe_url = _sanitize_markdown_url(
                        supporting_ref,
                        output_dir=resolved_output_dir,
                        solution_root=resolved_solution_root,
                    )
                    lines.append(f"- **Supporting Evidence:** [{safe_label}]({safe_url})")

            lines.extend([
                f"- **Gathered Evidence Files:** {evidence_md}",
                f"- **Reviewer Action Required:** {prompt}",
                "",
            ])

    lines.extend([
        "## Detailed Check Highlights",
        "",
    ])
    for check in data["checks"]:
        status = _normalize_status(check.get("status"), bool(check.get("applicable", True)))
        status_label = STATUS_DISPLAY_LABELS.get(status, status)
        title = _escape_markdown_cell(check.get("title") or check.get("id") or "Untitled Check")
        check_id = _escape_markdown_cell(check.get("id") or "CHECK")
        why_result = _escape_markdown_cell(check.get("whyPassedOrFailed") or check.get("whatWeObserved") or "—")
        lines.append(f"- **{status_label} - {title}** (`{check_id}`): {why_result}")
    lines.append("")

    for checklist_key, heading, description in CHECKLIST_DEFINITIONS:
        section_checks = [
            c for c in data["checks"]
            if str(c.get("checklist") or "validation").strip().lower() == checklist_key
        ]
        lines.extend([
            f"## {heading}",
            "",
            description,
            "",
            "| Check ID & Source | Reviewer Criterion | Category | Status | Evidence Details (Checked / Observed / Why) | Detailed Evidence Files |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ])
        if not section_checks:
            lines.append("| — | No checks recorded for this checklist | — | — | — | — |")
        else:
            for check in section_checks:
                check_id = _escape_markdown_cell(check.get("id") or "CHECK")
                content_type = _escape_markdown_cell(check.get("contentType") or "Solution")
                source_checklist = _escape_markdown_cell(check.get("sourceChecklist") or checklist_key.title())
                title = _escape_markdown_cell(check.get("title") or check.get("id") or "Untitled Check")
                criterion = _escape_markdown_cell(check.get("originalCriterion") or "")
                category = _escape_markdown_cell(check.get("category") or checklist_key)
                status = _normalize_status(check.get("status"), bool(check.get("applicable", True)))
                status_label = STATUS_DISPLAY_LABELS.get(status, status)

                what_checked = _escape_markdown_cell(check.get("whatWeChecked") or "—")
                what_observed = _escape_markdown_cell(check.get("whatWeObserved") or "—")
                why_result = _escape_markdown_cell(check.get("whyPassedOrFailed") or "—")
                details_Parts = [
                    f"**Checked:** {what_checked}",
                    f"**Observed:** {what_observed}",
                    f"**Why:** {why_result}",
                ]
                author_exc = check.get("authorException")
                if isinstance(author_exc, dict):
                    orig_status = _escape_markdown_cell(author_exc.get("originalStatus") or "FAIL")
                    justification = _escape_markdown_cell(author_exc.get("authorJustification") or "—")
                    details_Parts.append(
                        f"**Author Waiver (was `{orig_status}`):** {justification}"
                    )

                criterion_cell = f"**{title}**" + (f"<br>{criterion}" if criterion and criterion != "—" else "")
                evidence_cell = _format_evidence_links_markdown(
                    check,
                    output_dir=resolved_output_dir,
                    solution_root=resolved_solution_root,
                )

                lines.append(
                    f"| `{check_id}` ({content_type} · {source_checklist}) "
                    f"| {criterion_cell} "
                    f"| `{category}` "
                    f"| **{status_label}** (`{status}`) "
                    f"| {'<br>'.join(details_Parts)} "
                    f"| {evidence_cell} |"
                )
        lines.append("")

    lines.extend([
        "---",
        f"Full interactive evidence report: [{HTML_REPORT_FILENAME}]({HTML_REPORT_FILENAME})",
        "",
    ])
    return "\n".join(lines)


def write_pr_qualification_reports(
    report_data: dict[str, Any],
    output_dir: Path,
    *,
    solution_root: Path | None = None,
) -> dict[str, Path]:
    """Write both `qualification-report.html` and `qualification-summary.md` to `output_dir`."""
    target_dir = Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    html_path = target_dir / HTML_REPORT_FILENAME
    markdown_path = target_dir / MARKDOWN_SUMMARY_FILENAME

    html_content = render_pr_qualification_html(
        report_data,
        output_dir=target_dir,
        solution_root=solution_root,
    )
    markdown_content = render_pr_qualification_markdown(
        report_data,
        output_dir=target_dir,
        solution_root=solution_root,
    )

    html_path.write_text(html_content, encoding="utf-8")
    markdown_path.write_text(markdown_content, encoding="utf-8")

    return {
        "html": html_path,
        "markdown": markdown_path,
    }
