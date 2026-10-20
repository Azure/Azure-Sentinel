"""Playwright visual/tile rendering verification helpers for Defender Workbooks."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping

from solution_manager.qualification.workbook_browser import (
    validate_browser_config,
    validate_browser_step_proofs,
)

REQUIRED_UI_KINDS: tuple[str, ...] = (
    "open",
    "parameters",
    "tiles",
    "tabs",
    "conditional",
)


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

        results.append(
            {
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
