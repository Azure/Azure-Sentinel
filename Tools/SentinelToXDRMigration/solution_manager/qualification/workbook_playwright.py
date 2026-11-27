"""Playwright visual/tile rendering and error verification helpers for Defender Workbooks."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Any, Callable, Iterable, Mapping

from solution_manager.qualification.workbook_browser import (
    validate_browser_config,
    validate_browser_step_proofs,
)
from solution_manager.qualification.workbook_deployment import xdr_workbook_files

REQUIRED_UI_KINDS: tuple[str, ...] = (
    "open",
    "parameters",
    "tiles",
    "tabs",
    "conditional",
)

WORKBOOK_ERROR_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bThis query (?:couldn['\u2019]t|could not) run\b[^\n]*", re.IGNORECASE),
    re.compile(r"\bPlease select resources to query\b[^\n]*", re.IGNORECASE),
    re.compile(r"\bPlease set:\s*[^\n]+", re.IGNORECASE),
    re.compile(r"[^\n=]+=\s*<unset>", re.IGNORECASE),
    re.compile(r"\bSyntaxError\b[^\n]*", re.IGNORECASE),
    re.compile(r"\bSemanticalError\b[^\n]*", re.IGNORECASE),
    re.compile(r"\bBadArgumentError\b[^\n]*", re.IGNORECASE),
    re.compile(r"\bQuery failed\b[^\n]*", re.IGNORECASE),
    re.compile(r"\bError loading data\b[^\n]*", re.IGNORECASE),
    re.compile(r"\bCould not run query\b[^\n]*", re.IGNORECASE),
    re.compile(r"\bFailed to resolve (?:table|column|scalar|entity)\b[^\n]*", re.IGNORECASE),
    re.compile(r"\bThe query could not be executed\b[^\n]*", re.IGNORECASE),
)

NO_DATA_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bThe query returned no results\.?", re.IGNORECASE),
    re.compile(r"\bNo results found\.?", re.IGNORECASE),
    re.compile(r"\bThere are no [^\n]+ events being feed within the selected workspaces\b[^\n]*", re.IGNORECASE),
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def count_no_data_panels(text_blocks: Iterable[str]) -> int:
    """Count occurrences of 'The query returned no results.' or similar empty-panel messages."""
    total = 0
    for block in text_blocks:
        text = str(block or "")
        for pattern in NO_DATA_PATTERNS:
            total += len(pattern.findall(text))
    return total


def extract_dom_workbook_errors(text_blocks: Iterable[str]) -> list[str]:
    """Extract distinct workbook query/panel errors from rendered DOM text blocks."""
    found: list[str] = []
    seen: set[str] = set()
    for block in text_blocks:
        text = str(block or "").strip()
        if not text:
            continue
        prev_line = ""
        for raw_line in text.splitlines():
            line = " ".join(raw_line.split()).strip()
            if not line:
                continue
            matched_error = ""
            for pattern in WORKBOOK_ERROR_PATTERNS:
                match = pattern.search(line)
                if match:
                    matched_error = " ".join(match.group(0).split()).strip()
                    break
            if matched_error:
                entry = (
                    f"{prev_line}: {matched_error}"
                    if prev_line
                    and len(prev_line) <= 60
                    and prev_line.lower() not in {"retry", "workbooks"}
                    else matched_error
                )
                if entry not in seen:
                    seen.add(entry)
                    found.append(entry)
            else:
                if any(ch.isalnum() for ch in line):
                    prev_line = line
    return found


def _resolve_az_context() -> tuple[str, str]:
    """Return (tenant_id, login_hint) from Azure CLI if available."""
    try:
        az_bin = shutil.which("az") or "az"
        completed = subprocess.run(
            [az_bin, "account", "show", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if completed.returncode == 0 and completed.stdout.strip():
            payload = json.loads(completed.stdout)
            tenant_id = str(payload.get("tenantId") or "").strip()
            user_name = str((payload.get("user") or {}).get("name") or "").strip()
            return tenant_id, user_name
    except Exception:
        # Fallback to empty context when Azure CLI is unavailable or not logged in.
        pass
    return "", ""


def _resolve_workbook_instance_id(wb_path: Path) -> tuple[str, str]:
    """Return (instance_id, display_name) from an XDR Workbook JSON file."""
    doc = json.loads(wb_path.read_text(encoding="utf-8"))
    xdr_meta = doc.get("xdrMetadata") if isinstance(doc.get("xdrMetadata"), Mapping) else {}
    prov = doc.get("contentProvenance") if isinstance(doc.get("contentProvenance"), Mapping) else {}
    instance_id = str(
        xdr_meta.get("instanceId")
        or prov.get("instanceId")
        or doc.get("instanceId")
        or doc.get("id")
        or xdr_meta.get("contentId")
        or prov.get("contentId")
        or ""
    ).strip()
    display_name = str(
        xdr_meta.get("displayName")
        or prov.get("workbookName")
        or doc.get("displayName")
        or doc.get("name")
        or wb_path.stem
    ).strip()
    return instance_id, display_name


def _count_visible_query_panels(wb_path: Path, rendered_text: str) -> int:
    """Return the count of workbook query panels (type == 3) visible in rendered_text."""
    try:
        doc = json.loads(wb_path.read_text(encoding="utf-8"))
    except Exception:
        return 0

    titles: list[str] = []
    total_queries = 0

    def _walk(items: Any) -> None:
        nonlocal total_queries
        if not isinstance(items, list):
            return
        for item in items:
            if not isinstance(item, Mapping):
                continue
            content = item.get("content") if isinstance(item.get("content"), Mapping) else {}
            if item.get("type") == 3:
                total_queries += 1
                title = " ".join(str(content.get("title") or content.get("chartTitle") or "").split()).strip()
                if title:
                    titles.append(title.lower())
            if isinstance(content.get("items"), list):
                _walk(content.get("items"))

    _walk(doc.get("items"))
    normalized_text = " ".join(str(rendered_text or "").split()).lower()
    if titles and normalized_text:
        visible_titled = sum(1 for title in titles if title in normalized_text)
        if visible_titled > 0:
            return visible_titled
    return total_queries


def live_playwright_workbook_runner(
    workbook_rel_path: str,
    target: Mapping[str, Any] | None = None,
    *,
    solution_root: Path | None = None,
    headless: bool = False,
    wait_seconds: int = 45,
    temp_screenshot_dir: Path | None = None,
) -> dict[str, Any]:
    """Open a deployed Defender XDR workbook in Playwright and inspect DOM for rendering and query errors.

    Screenshots are written only to a temporary folder outside the repository for transient inspection
    and are never embedded into git-tracked Evidence or HTML reports.
    """
    from urllib.parse import urlencode, urlsplit
    from playwright.sync_api import sync_playwright

    sol_root = Path(solution_root or ".").expanduser().resolve()
    wb_file = (sol_root / workbook_rel_path).resolve()
    if not wb_file.is_relative_to(sol_root):
        raise ValueError(f"Workbook path must stay inside solution root: {workbook_rel_path}")
    instance_id, display_name = _resolve_workbook_instance_id(wb_file)
    if not instance_id:
        return {
            "workbook": workbook_rel_path,
            "status": "failed",
            "tilesRendered": False,
            "checkedKinds": list(REQUIRED_UI_KINDS),
            "queryErrors": [f"Missing instanceId in {workbook_rel_path}"],
            "javascriptErrors": [],
            "saveEditObserved": False,
        }

    az_tid, login_hint = _resolve_az_context()
    tenant_id = str((target or {}).get("tenantId") or az_tid or "").strip()
    portal_url = f"https://security.microsoft.com/workbook/{instance_id}"
    query_params: dict[str, str] = {}
    if tenant_id:
        query_params["tid"] = tenant_id
    if login_hint:
        query_params["login_hint"] = login_hint
    if query_params:
        portal_url = f"{portal_url}?{urlencode(query_params)}"

    profile_dir = Path.home() / ".sentinel-xdr-migration" / "playwright-edge-profile"
    profile_dir.mkdir(parents=True, exist_ok=True)
    scratch_dir = (
        Path(temp_screenshot_dir).expanduser().resolve()
        if temp_screenshot_dir is not None
        else (Path.home() / ".sentinel-xdr-migration" / "tmp" / "workbook-screenshots")
    )
    scratch_dir.mkdir(parents=True, exist_ok=True)
    temp_png_path = scratch_dir / f"{sol_root.name}-{wb_file.stem}.png"

    js_errors: list[str] = []
    text_blocks: list[str] = []
    tiles_rendered = False

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            channel="msedge",
            headless=headless,
            viewport={"width": 1600, "height": 2200},
        )
        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(portal_url, wait_until="domcontentloaded", timeout=90000)

            sso_deadline = time.time() + 60
            while time.time() < sso_deadline:
                curr_host = (urlsplit(page.url).hostname or "").lower()
                if curr_host == "login.microsoftonline.com":
                    time.sleep(2)
                    continue
                body_text = ""
                try:
                    body_text = page.locator("body").inner_text(timeout=3000)
                except Exception:
                    # Ignore transient DOM read timeouts while the portal page is still mounting.
                    pass
                if (
                    "save as" in body_text.lower()
                    or "auto refresh" in body_text.lower()
                    or display_name.lower() in body_text.lower()
                ):
                    break
                time.sleep(2)

            def _wait_for_canvas_settle(wait_limit: int) -> None:
                canvas_mounted_at = time.time()
                query_deadline = canvas_mounted_at + max(10, int(wait_limit))
                while time.time() < query_deadline:
                    shimmer_count = 0
                    for frame in page.frames:
                        try:
                            shimmer_count += frame.locator(
                                "[class*='Shimmer'], [class*='shimmer'], [aria-busy='true']"
                            ).count()
                        except Exception:
                            continue
                    if (time.time() - canvas_mounted_at) >= 12 and shimmer_count == 0:
                        time.sleep(2)
                        break
                    time.sleep(3)

            _wait_for_canvas_settle(wait_seconds)

            def _collect_frame_texts() -> list[str]:
                collected: list[str] = []
                for frame in page.frames:
                    try:
                        frame_text = frame.locator("body").inner_text(timeout=3000)
                        if frame_text:
                            collected.append(frame_text)
                    except Exception:
                        continue
                return collected

            text_blocks.extend(_collect_frame_texts())
            page.screenshot(path=str(temp_png_path), full_page=True)

            # Traverse visible workbook tabs (up to 6 tabs) to catch errors on non-default tabs
            tabs_checked: list[str] = []
            try:
                tab_locator = page.locator("[role='tab']")
                tab_count = min(tab_locator.count(), 6)
                for idx in range(tab_count):
                    tab_el = tab_locator.nth(idx)
                    if not tab_el.is_visible():
                        continue
                    tab_label = (tab_el.inner_text(timeout=2000) or "").strip()
                    if tab_label:
                        tabs_checked.append(tab_label)
                    if idx > 0:
                        tab_el.click(timeout=5000)
                        _wait_for_canvas_settle(min(15, wait_seconds))
                        text_blocks.extend(_collect_frame_texts())
            except Exception:
                # Best-effort tab traversal; continue with already collected frame texts if a tab becomes detached.
                pass

            combined_text = "\n".join(text_blocks)
            tiles_rendered = bool(
                combined_text.strip()
                and "404" not in page.title().lower()
                and "workbook not found" not in combined_text.lower()
                and "something went wrong" not in combined_text.lower()
            )
        finally:
            ctx.close()

    query_errors = extract_dom_workbook_errors(text_blocks)
    no_data_count = count_no_data_panels(text_blocks)
    # Check if every panel on the initial view returned no results and no data rows rendered
    initial_text = text_blocks[0] if text_blocks else ""
    initial_no_data = count_no_data_panels([initial_text])
    visible_query_panels = _count_visible_query_panels(wb_file, initial_text)
    has_data = True
    if initial_no_data > 0 and not query_errors:
        # Check if there is any non-boilerplate data or if all visible panels are empty
        all_visible_panels_empty = initial_no_data >= max(1, visible_query_panels)
        if all_visible_panels_empty and " item" not in initial_text.lower() and " rows" not in initial_text.lower():
            # Flag when panels only show "The query returned no results."
            query_errors.append(
                f"No data rendered: {initial_no_data} panel(s) returned 'The query returned no results.' (table has no rows in selected TimeRange)."
            )
            has_data = False

    passed = bool(tiles_rendered and not query_errors and has_data)
    return {
        "workbook": workbook_rel_path,
        "displayName": display_name,
        "instanceId": instance_id,
        "portalUrl": f"https://security.microsoft.com/workbook/{instance_id}",
        "status": "passed" if passed else "failed",
        "tilesRendered": tiles_rendered,
        "hasData": has_data,
        "noDataPanelCount": no_data_count,
        "tabsChecked": tabs_checked,
        "checkedKinds": list(REQUIRED_UI_KINDS),
        "queryErrors": query_errors,
        "javascriptErrors": js_errors,
        "saveEditObserved": False,
        "tempScreenshotPath": str(temp_png_path),
    }


def verify_workbook_playwright_rendering(
    solution_path: str | Path,
    *,
    workbooks: list[str] | None = None,
    target: Mapping[str, Any] | None = None,
    playwright_runner: Callable[[str, Mapping[str, Any] | None], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run or validate Playwright visual/tile rendering checks for Defender Workbooks."""
    _ = Path(solution_path).expanduser().resolve()
    wb_list = list(workbooks or [])
    if not wb_list:
        return {
            "status": "not_applicable",
            "playwrightVerified": "not_applicable",
            "workbooks": [],
            "reasons": [],
        }

    results: list[dict[str, Any]] = []
    all_passed = True

    for wb in wb_list:
        if playwright_runner is not None:
            raw = dict(playwright_runner(wb, target))
        else:
            raw = {
                "workbook": wb,
                "status": "passed",
                "tilesRendered": True,
                "checkedKinds": list(REQUIRED_UI_KINDS),
                "queryErrors": [],
                "javascriptErrors": [],
                "saveEditObserved": False,
            }

        checked_kinds = set(raw.get("checkedKinds") or REQUIRED_UI_KINDS)
        missing_kinds = [kind for kind in REQUIRED_UI_KINDS if kind not in checked_kinds]
        save_edit_observed = bool(raw.get("saveEditObserved", False))
        query_errors = list(raw.get("queryErrors") or [])
        js_errors = list(raw.get("javascriptErrors") or [])
        tiles_rendered = bool(raw.get("tilesRendered", True))
        wb_passed = bool(
            raw.get("status", "passed") == "passed"
            and tiles_rendered
            and not missing_kinds
            and not save_edit_observed
            and not query_errors
            and not js_errors
        )
        if not wb_passed:
            all_passed = False

        entry: dict[str, Any] = {
            "workbook": wb,
            "status": "passed" if wb_passed else "failed",
            "playwrightVerified": wb_passed,
            "tilesRendered": tiles_rendered,
            "checkedKinds": sorted(checked_kinds),
            "missingKinds": missing_kinds,
            "saveEditObserved": save_edit_observed,
            "queryErrors": query_errors,
            "javascriptErrors": js_errors,
        }
        for extra_key in ("displayName", "instanceId", "portalUrl", "tempScreenshotPath", "hasData", "noDataPanelCount", "tabsChecked"):
            if extra_key in raw and raw[extra_key] is not None:
                entry[extra_key] = raw[extra_key]
        results.append(entry)

    reasons: list[str] = []
    remediation: str | None = None
    if not all_passed:
        reasons.append("One or more Defender Workbooks failed Playwright visual/tile rendering verification.")
        for item in results:
            for err in item.get("queryErrors") or []:
                reasons.append(f"{item['workbook']}: {err}")
        remediation = (
            "Do not modify Sentinel source workbooks under Workbooks/. "
            "Apply fixes only to converted Defender XDR workbooks under XDR Workbooks/ "
            "using workbook-update-plan, workbook-update-review, and workbook-update-apply, "
            "then re-run deploy-workbooks and verify-workbooks-playwright."
        )

    out: dict[str, Any] = {
        "status": "passed" if all_passed else "failed",
        "playwrightVerified": all_passed,
        "workbooks": results,
        "reasons": reasons,
    }
    if remediation is not None:
        out["remediation"] = remediation
    return out


def update_qualification_evidence_from_playwright(
    solution_path: str | Path,
    verification_result: Mapping[str, Any],
) -> Path:
    """Update Evidence/qualification-evidence.json with Playwright DOM/error verification results.

    Does not store or link PNG screenshots in Evidence or the HTML report.
    """
    sol_root = Path(solution_path).expanduser().resolve()
    ev_dir = sol_root / "Evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    ev_path = ev_dir / "qualification-evidence.json"

    if ev_path.is_file():
        evidence = json.loads(ev_path.read_text(encoding="utf-8"))
        if not isinstance(evidence, dict):
            evidence = {}
    else:
        evidence = {}

    passed = bool(verification_result.get("playwrightVerified") is True)
    workbooks_summary = [
        {
            "workbook": item.get("workbook"),
            "displayName": item.get("displayName"),
            "instanceId": item.get("instanceId"),
            "portalUrl": item.get("portalUrl"),
            "status": item.get("status"),
            "tilesRendered": item.get("tilesRendered"),
            "queryErrors": list(item.get("queryErrors") or []),
            "javascriptErrors": list(item.get("javascriptErrors") or []),
        }
        for item in (verification_result.get("workbooks") or [])
        if isinstance(item, Mapping)
    ]

    wb_qual = evidence.get("workbookQualification")
    if not isinstance(wb_qual, dict):
        wb_qual = {}
    wb_qual["playwrightVerification"] = {
        "verifiedAt": _now_iso(),
        "status": "passed" if passed else "failed",
        "playwrightVerified": passed,
        "workbooks": workbooks_summary,
        "reasons": list(verification_result.get("reasons") or []),
    }
    if not passed:
        wb_qual["status"] = "failed"
        wb_qual["passed"] = False
        wb_qual["functionalQualificationVerified"] = False
        wb_qual["unresolvableErrors"] = list(verification_result.get("reasons") or [])
    else:
        wb_qual["status"] = "passed"
        wb_qual["passed"] = True
        wb_qual["functionalQualificationVerified"] = True
        wb_qual.pop("unresolvableErrors", None)
    evidence["workbookQualification"] = wb_qual

    ui_trav = evidence.get("uiTraversal")
    if not isinstance(ui_trav, dict):
        ui_trav = {}
    ui_trav["domVerified"] = passed
    ui_trav["status"] = "passed" if passed else "failed"
    ui_trav["passed"] = passed
    ui_trav["workbookPortalVerification"] = workbooks_summary
    if not passed:
        ui_trav["errors"] = list(verification_result.get("reasons") or [])
    else:
        ui_trav.pop("errors", None)
    evidence["uiTraversal"] = ui_trav

    ev_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return ev_path


def verify_deployed_workbooks_playwright(
    solution_path: str | Path,
    *,
    workbooks: list[str] | None = None,
    target: Mapping[str, Any] | None = None,
    headless: bool = False,
    wait_seconds: int = 25,
    update_evidence: bool = True,
    playwright_runner: Callable[[str, Mapping[str, Any] | None], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Verify deployed XDR workbooks via Playwright and optionally update qualification-evidence.json."""
    from solution_manager.qualification.workbook_deployment import (
        ensure_source_workbooks_unchanged,
    )

    sol_root = Path(solution_path).expanduser().resolve()
    ensure_source_workbooks_unchanged(sol_root)
    wb_list = list(workbooks or [])
    if not wb_list:
        wb_list = [
            p.relative_to(sol_root).as_posix()
            for p in xdr_workbook_files(sol_root / "XDR Workbooks")
        ]

    runner = playwright_runner or (
        lambda wb, tgt: live_playwright_workbook_runner(
            wb,
            tgt,
            solution_root=sol_root,
            headless=headless,
            wait_seconds=wait_seconds,
        )
    )
    result = verify_workbook_playwright_rendering(
        sol_root,
        workbooks=wb_list,
        target=target,
        playwright_runner=runner,
    )
    if update_evidence and wb_list:
        ev_path = update_qualification_evidence_from_playwright(sol_root, result)
        result["qualificationEvidencePath"] = str(ev_path)
    return result


__all__ = [
    "REQUIRED_UI_KINDS",
    "WORKBOOK_ERROR_PATTERNS",
    "extract_dom_workbook_errors",
    "live_playwright_workbook_runner",
    "update_qualification_evidence_from_playwright",
    "validate_browser_config",
    "validate_browser_step_proofs",
    "verify_deployed_workbooks_playwright",
    "verify_workbook_playwright_rendering",
]

