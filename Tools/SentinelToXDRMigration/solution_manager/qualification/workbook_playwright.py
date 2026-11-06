"""Playwright visual/tile rendering verification helpers for Defender Workbooks."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping

from solution_manager.qualification.workbook_browser import (
    REQUIRED_CHECK_KINDS,
    validate_browser_config,
    validate_browser_step_proofs,
    validate_portal_url,
)

REQUIRED_UI_KINDS: tuple[str, ...] = tuple(sorted(REQUIRED_CHECK_KINDS))


def verify_workbook_playwright_rendering(
    solution_path: str | Path,
    *,
    workbooks: list[str] | None = None,
    target: Mapping[str, Any] | None = None,
    playwright_runner: Callable[[str, Mapping[str, Any] | None], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Validate runner-produced, reviewed DOM captures; never synthesize UI evidence.

    A runner returns ``{"plan": <versioned UI plan>, "capture": <DOM capture>}``.
    The existing workbook-ui-execute CLI owns browser execution and consent.
    """
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
        wb_passed = False
        checked_kinds: list[str] = []
        reason = "browser-provider-missing"
        if playwright_runner is not None:
            try:
                from solution_manager.qualification.workbook_qualification import _validate_ui_capture

                raw = playwright_runner(wb, target)
                plan, capture = raw["plan"], raw["capture"]
                if (
                    plan["workbook"] != wb or target is None or plan["target"] != dict(target)
                    or capture.get("producer") != "playwright-dom-v1"
                ):
                    raise ValueError("browser capture identity or producer is not verified")
                validate_portal_url(plan["url"])
                validate_browser_config(plan, plan["browserConfig"])
                _validate_ui_capture(plan, capture)
                checked_kinds = sorted({step["kind"] for step in capture["steps"]})
                wb_passed = True
            except Exception:
                # Provider exceptions, DOM text and URLs can contain credentials.
                reason = "browser-provider-failed-or-evidence-incomplete"
        if not wb_passed:
            all_passed = False

        results.append(
            {
                "workbook": wb,
                "status": "passed" if wb_passed else "failed",
                "playwrightVerified": wb_passed,
                "tilesRendered": wb_passed,
                "checkedKinds": checked_kinds,
                "reasons": [] if wb_passed else [reason],
            }
        )

    return {
        "status": "passed" if all_passed else "failed",
        "playwrightVerified": all_passed,
        "workbooks": results,
        "reasons": [] if all_passed else ["One or more Defender Workbooks failed Playwright visual/tile rendering verification."],
    }


__all__ = [
    "REQUIRED_UI_KINDS",
    "validate_browser_config",
    "validate_browser_step_proofs",
    "verify_workbook_playwright_rendering",
]
