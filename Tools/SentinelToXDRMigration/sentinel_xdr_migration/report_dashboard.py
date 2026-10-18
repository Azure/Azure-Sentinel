"""Offline presentation of recorded migration facts; never changes workflow gates."""

from __future__ import annotations

from collections import Counter
from difflib import unified_diff
from html import escape
import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from .report_review import BULK_SCRIPT, render_bulk_review, review_candidates


THEME_SCRIPT = """
  (() => {
    const param = new URLSearchParams(window.location.search).get("scoutTheme");
    const theme =
      param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", theme);
  })();
"""

STYLE = """
:root {
  color-scheme: light;
  --cp-bg: #f7f4ef;
  --cp-bg-elevated: #fcfbf8;
  --cp-surface: #ffffff;
  --cp-surface-soft: #f5f5f5;
  --cp-border: #dedede;
  --cp-border-strong: #919191;
  --cp-text: #242424;
  --cp-text-muted: #5c5c5c;
  --cp-text-soft: #6f6f6f;
  --cp-accent: #b11f4b;
  --cp-accent-hover: #9a1a41;
  --cp-accent-soft: rgba(177, 31, 75, 0.08);
  --cp-accent-fg: #ffffff;
  --cp-success: #16a34a;
  --cp-danger: #dc2626;
  --cp-warning: #f59e0b;
  --cp-link: #0078d4;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.12);
  --cp-overlay: rgba(255, 255, 255, 0.8);
  --cp-panel: rgba(255, 255, 255, 0.86);
  --cp-panel-strong: rgba(255, 255, 255, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.55);
  --cp-highlight: rgba(177, 31, 75, 0.12);
}
html[data-theme="dark"] {
  color-scheme: dark;
  --cp-bg: #3d3b3a;
  --cp-bg-elevated: #343231;
  --cp-surface: #292929;
  --cp-surface-soft: #2e2e2e;
  --cp-border: #474747;
  --cp-border-strong: #5f5f5f;
  --cp-text: #dedede;
  --cp-text-muted: #919191;
  --cp-text-soft: #b0b0b0;
  --cp-accent: #fd8ea1;
  --cp-accent-hover: #fb7b91;
  --cp-accent-soft: rgba(253, 142, 161, 0.14);
  --cp-accent-fg: #1a1a1a;
  --cp-success: #4ade80;
  --cp-danger: #f87171;
  --cp-warning: #fbbf24;
  --cp-link: #4da6ff;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
  --cp-overlay: rgba(41, 41, 41, 0.88);
  --cp-panel: rgba(41, 41, 41, 0.72);
  --cp-panel-strong: rgba(41, 41, 41, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.04);
  --cp-highlight: rgba(253, 142, 161, 0.12);
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--cp-bg); color: var(--cp-text);
  font-family: "Segoe UI", Aptos, Calibri, -apple-system, BlinkMacSystemFont, sans-serif; }
main { max-width: 1560px; margin: auto; padding: 24px; }
h1 { margin: 8px 0; } h2 { font-size: 1.2rem; }
a { color: var(--cp-link); } .muted { color: var(--cp-text-muted); }
.panel { background: var(--cp-surface); border: 1px solid var(--cp-border);
  border-radius: 16px; padding: 20px; margin: 16px 0; }
.stages, .chips, .categories, .metrics { display: flex; flex-wrap: wrap; gap: 8px; }
.stages { list-style: none; padding: 0; }
.stage, .badge { border: 1px solid var(--cp-border); padding: 4px 8px; border-radius: .625rem; }
.badge { display: inline-block; margin: 4px 0; font-size: .85rem; }
.failed { border-left: 4px solid var(--cp-danger); }
.review, .unconfirmed, .blocked { border-left: 4px solid var(--cp-warning); }
.ready, .passed { border-left: 4px solid var(--cp-success); }
.finding-error { border-left: 4px solid var(--cp-danger); }
.finding-review { border-left: 4px solid var(--cp-accent); }
.finding-warning { border-left: 4px solid var(--cp-link); }
.finding-blocked { border-left: 4px solid var(--cp-warning); }
.finding-info { border-left: 4px solid var(--cp-border-strong); }
.metrics span { padding: 8px 12px; background: var(--cp-surface-soft); border-radius: .625rem; }
fieldset { border: 0; padding: 0; margin: 16px 0; }
legend { font-weight: 600; margin-bottom: 8px; }
label.chip { border: 1px solid var(--cp-border); padding: 8px 12px;
  border-radius: .625rem; cursor: pointer; background: var(--cp-surface); }
label.chip:has(input:checked) { border-color: var(--cp-accent); background: var(--cp-accent-soft); }
input { accent-color: var(--cp-accent); }
input[type=search] { display: block; margin-top: 8px; width: min(100%, 640px); }
input[type=search], button { font: inherit; padding: 8px 12px; border: 1px solid var(--cp-border-strong);
  border-radius: .625rem; background: var(--cp-surface); color: var(--cp-text); }
select { font: inherit; padding: 8px; max-width: 100%; background: var(--cp-surface); color: var(--cp-text);
  border: 1px solid var(--cp-border-strong); border-radius: .625rem; }
button:disabled { color: var(--cp-text-muted); cursor: not-allowed; }
.chart-layout { display: flex; flex-wrap: wrap; align-items: center; gap: 24px; }
.donut { width: 220px; max-width: 100%; height: 220px; }
.donut circle { fill: none; stroke-width: 5; }
.donut-track { stroke: var(--cp-border); }
.donut-green { stroke: var(--cp-success); }
.donut-yellow { stroke: var(--cp-warning); }
.donut-red { stroke: var(--cp-danger); }
.donut-gray { stroke: var(--cp-text-muted); }
.donut text { text-anchor: middle; fill: var(--cp-text); font-size: 3px; }
.donut .chart-total { font-size: 6px; font-weight: 600; }
.chart-legend { display: grid; gap: 8px; }
.chart-legend button { text-align: left; }
[data-chart-filter][aria-pressed=true] { outline: 2px solid var(--cp-accent); outline-offset: 2px; }
.swatch { display: inline-block; width: 12px; height: 12px; margin-right: 8px; border-radius: 50%; }
.swatch-green { background: var(--cp-success); }
.swatch-yellow { background: var(--cp-warning); }
.swatch-red { background: var(--cp-danger); }
.swatch-gray { background: var(--cp-text-muted); }
.findings-pie { width: 160px; height: 160px; max-width: 100%; }
.pie-error { fill: var(--cp-danger); }
.pie-attention { fill: var(--cp-warning); }
.pie-info { fill: var(--cp-link); }
.pie-empty { fill: var(--cp-border); }
.swatch-info { background: var(--cp-link); }
[data-findings-chart-filter][aria-pressed=true] { outline: 2px solid var(--cp-accent); outline-offset: 2px; }
button, summary { cursor: pointer; } button:hover { border-color: var(--cp-accent); }
:focus-visible { outline: 3px solid var(--cp-accent); outline-offset: 3px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; background: var(--cp-surface); }
th, td { text-align: left; vertical-align: top; padding: 12px; border-bottom: 1px solid var(--cp-border); }
thead th { position: sticky; top: 0; background: var(--cp-bg-elevated); z-index: 1; }
th:first-child { min-width: 220px; } td { overflow-wrap: anywhere; }
tbody.rule > tr:first-child > th { font-weight: normal; width: 30%; }
.detail-cell { background: var(--cp-bg-elevated); }
summary { padding: 8px 0; font-weight: 600; }
pre, code { font-family: Consolas, "Courier New", Courier, monospace; }
code { overflow-wrap: anywhere; word-break: normal; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; max-height: 420px; overflow: auto;
  background: var(--cp-surface-soft); border: 1px solid var(--cp-border); padding: 12px; border-radius: .625rem; }
.query-pair { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.issue-list { padding-left: 24px; } .issue-list li { padding: 8px 0; }
.flow-scroll { overflow-x: auto; padding: 8px 0 12px; }
.subway { display: block; width: 100%; min-width: 1160px; height: auto; }
.subway.qualification { min-width: 2110px; }
.subway .route { fill: none; stroke: var(--cp-border-strong); stroke-width: 4; }
.subway .route-prefix.active { stroke: var(--cp-accent); }
.subway .route-authoring.active { stroke: var(--cp-accent); }
.subway .route-qualification { stroke-dasharray: 8 7; }
.subway .route-qualification.active { stroke: var(--cp-accent); stroke-dasharray: none; }
.subway .route-external { stroke-dasharray: 3 8; }
.subway .route-label { fill: var(--cp-text-muted); font-size: 14px; }
.subway .station-marker { fill: var(--cp-surface); stroke: var(--cp-border-strong); stroke-width: 4; }
.subway .station-glyph { fill: var(--cp-text); font-size: 13px; font-weight: 700; text-anchor: middle; }
.subway .station-name { fill: var(--cp-text); font-size: 15px; font-weight: 600; text-anchor: middle; }
.subway .station-status { fill: var(--cp-text-muted); font-size: 12px; text-anchor: middle; }
.subway .branch-heading { fill: var(--cp-text); font-size: 14px; font-weight: 600; }
.subway .flow-link { cursor: pointer; }
.subway .flow-link .station-name { text-decoration: underline; text-decoration-style: dotted; text-underline-offset: 3px; }
.subway .flow-link:hover .station-name,
.subway .flow-link:focus-visible .station-name { text-decoration-style: solid; fill: var(--cp-accent); }
.subway .flow-link:hover .station-marker,
.subway .flow-link:focus-visible .station-marker { stroke: var(--cp-accent); stroke-width: 6; }
.subway .flow-link:focus { outline: none; }
.flow-evidence-entry { border-top: 1px solid var(--cp-border); padding: 12px 0; scroll-margin-top: 16px; }
.flow-evidence-entry h3 { margin: 4px 0 8px; }
.flow-evidence-entry:target { border-left: 4px solid var(--cp-accent); padding-left: 12px; }
.flow-evidence-entry ul { overflow-wrap: anywhere; }
.flow-artifact-links { display: flex; flex-wrap: wrap; gap: 8px 16px; padding-left: 20px; }
.flow-artifact-links a { overflow-wrap: anywhere; }
.subway.compact { min-width: 1160px; }
.subway .flow-station.state-completed .station-marker { stroke: var(--cp-success); }
.subway .flow-station.state-running .station-marker { stroke: var(--cp-accent); }
.subway .flow-station.state-blocked .station-marker,
.subway .flow-station.state-failed .station-marker { stroke: var(--cp-danger); }
.subway .flow-station.state-stale .station-marker { stroke: var(--cp-warning); stroke-dasharray: 5 3; }
.subway .flow-station.state-unknown .station-marker,
.subway .flow-station.state-pending .station-marker,
.subway .flow-station.state-not-required .station-marker { stroke: var(--cp-border-strong); stroke-dasharray: 5 3; }
.subway .state-completed .station-glyph { fill: var(--cp-success); }
.subway .state-running .station-glyph { fill: var(--cp-accent); }
.subway .state-blocked .station-glyph, .subway .state-failed .station-glyph { fill: var(--cp-danger); }
.subway .state-stale .station-glyph { fill: var(--cp-warning); }
.subway .flow-link:hover .station-marker,
.subway .flow-link:focus-visible .station-marker { stroke: var(--cp-accent); stroke-width: 6; }
.flow-legend { display: flex; flex-wrap: wrap; gap: 8px 16px; padding: 0; list-style: none; }
.flow-legend li { display: inline-flex; align-items: center; gap: 6px; }
.flow-key { width: 12px; height: 12px; border: 2px solid var(--cp-border-strong); border-radius: 50%; }
.flow-key.completed { border-color: var(--cp-success); }
.flow-key.running { border-color: var(--cp-accent); }
.flow-key.blocked, .flow-key.failed { border-color: var(--cp-danger); }
.flow-key.stale { border-color: var(--cp-warning); border-style: dashed; }
.flow-key.pending, .flow-key.not-required, .flow-key.unknown { border-style: dashed; }
.flow-mode { display: inline-block; border: 1px solid var(--cp-border-strong); border-radius: .625rem; padding: 4px 8px; }
.planning-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
.planning-card { min-width: 0; align-self: start; background: var(--cp-bg-elevated); border: 1px solid var(--cp-border); border-radius: .625rem; padding: 12px; }
.planning-card h3 { margin-top: 0; }
.planning-summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr)); align-items: start; gap: 10px; margin: 16px 0; }
.planning-summary-card { min-width: 0; align-self: start; display: grid; gap: 6px; padding: 12px; background: var(--cp-bg-elevated); border: 1px solid var(--cp-border); border-radius: .625rem; }
.planning-summary-card span { overflow-wrap: anywhere; word-break: normal; }
.planning-layout { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 320px), 1fr)); align-items: start; gap: 12px; }
.target-data { display: grid; gap: 8px; margin: 8px 0; }
.target-data > div { min-width: 0; }
.target-data dt { font-weight: 600; }
.target-data dd { margin: 2px 0 0; overflow-wrap: anywhere; word-break: normal; }
.planning-inventory { width: 100%; margin-top: 12px; }
.component-plan-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr)); align-items: start; gap: 10px; }
.component-coverage-summary { margin: 8px 0; padding-left: 20px; overflow-wrap: anywhere; }
.planning-table-scroll { max-width: 100%; overflow-x: auto; overscroll-behavior-inline: contain; }
.resource-inventory { width: 100%; min-width: 940px; table-layout: fixed; border-collapse: collapse; }
.resource-inventory th, .resource-inventory td { border-bottom: 1px solid var(--cp-border); padding: 8px; text-align: left; vertical-align: top; }
.resource-inventory th { white-space: nowrap; }
.resource-inventory th:nth-child(1) { width: 34%; }
.resource-inventory th:nth-child(2) { width: 20%; }
.resource-inventory th:nth-child(3) { width: 9%; }
.resource-inventory th:nth-child(4) { width: 24%; }
.resource-inventory th:nth-child(5) { width: 13%; }
.resource-inventory td:first-child code { overflow-wrap: break-word; word-break: normal; }
.resource-inventory td:nth-child(2), .resource-inventory td:nth-child(3), .resource-inventory td:nth-child(5) { white-space: nowrap; }
[hidden] { display: none !important; }
@media(max-width: 760px) { .planning-layout, .planning-summary-grid { grid-template-columns: 1fr; } }
@media(max-width: 760px) { main { padding: 12px; } .panel { padding: 12px; }
  .query-pair { grid-template-columns: 1fr; } }
"""

FILTER_SCRIPT = """
(() => {
  const form = document.getElementById("filters");
  const rows = [...document.querySelectorAll("tbody.rule")];
  const search = document.getElementById("search");
  const count = document.getElementById("result-count");
  const issueLabel = document.getElementById("issue-filter");
  let issue = "";
  let chart = "all";
  let findingChart = "all";
  function apply() {
    const status = form.querySelector('input[name="status"]:checked').value;
    const finding = form.querySelector('input[name="finding"]:checked').value;
    const categories = [...form.querySelectorAll('input[name="category"]:checked')].map(x => x.value);
    const text = search.value.trim().toLowerCase();
    let visible = 0;
    rows.forEach(row => {
      const matchesStatus = status === "all" ||
        (status === "attention" ? !["ready", "excluded"].includes(row.dataset.status) : row.dataset.status === status);
      const matchesCategory = !categories.length || categories.some(x => row.dataset.categories.split("|").includes(x));
      const matchesFinding = finding === "any" || row.dataset.findings.split("|").includes(finding);
      const kinds = row.dataset.findings.split("|");
      const matchesFindingChart = findingChart === "all" ||
        (findingChart === "attention" ? kinds.some(kind => ["warning", "review"].includes(kind)) : kinds.includes(findingChart));
      row.hidden = !(matchesStatus && matchesFinding && matchesCategory && row.dataset.search.includes(text) &&
        matchesFindingChart &&
        (chart === "all" || row.dataset.chart === chart) &&
        (!issue || row.dataset.issues.split("|").includes(issue)));
      if (!row.hidden) visible++;
    });
    count.textContent = `Showing ${visible} of ${rows.length} rules`;
    document.getElementById("empty").hidden = visible !== 0;
    issueLabel.textContent = issue ? `Filtering to shared issue ${issue.replace("issue-", "")}` : "";
    document.getElementById("clear-issue").hidden = !issue;
    document.querySelectorAll("[data-chart-filter]").forEach(control => control.setAttribute("aria-pressed", String(control.dataset.chartFilter === chart)));
    document.getElementById("chart-filter-label").textContent = chart === "all" ? "" :
      `Chart filter: ${document.querySelector('button[data-chart-filter="' + chart + '"]').dataset.chartLabel}`;
    document.querySelectorAll("[data-findings-chart-filter]").forEach(control => control.setAttribute("aria-pressed", String(control.dataset.findingsChartFilter === findingChart)));
    document.getElementById("finding-chart-filter-label").textContent = findingChart === "all" ? "" :
      `Findings chart filter: ${document.querySelector('button[data-findings-chart-filter="' + findingChart + '"]').dataset.findingLabel}`;
  }
  form.addEventListener("input", event => {
    if (event.target.name === "finding") form.querySelector('input[name="status"][value="all"]').checked = true;
    apply();
  });
  form.addEventListener("submit", event => event.preventDefault());
  document.getElementById("clear").addEventListener("click", () => {
    form.reset();
    form.querySelector('input[value="all"]').checked = true;
    issue = "";
    chart = "all";
    findingChart = "all";
    apply();
  });
  document.getElementById("clear-issue").addEventListener("click", () => { issue = ""; apply(); });
  document.querySelectorAll("[data-filter-issue]").forEach(button => button.addEventListener("click", () => {
    form.reset();
    form.querySelector('input[value="all"]').checked = true;
    issue = button.dataset.filterIssue;
    chart = "all";
    findingChart = "all";
    apply();
    document.getElementById("result-count").focus();
  }));
  document.querySelectorAll("[data-chart-filter]").forEach(control => {
    function select() {
      form.reset();
      form.querySelector('input[name="status"][value="all"]').checked = true;
      issue = "";
      chart = control.dataset.chartFilter;
      findingChart = "all";
      apply();
      document.getElementById("result-count").focus();
    }
    control.addEventListener("click", select);
    if (control.tagName.toLowerCase() === "circle") control.addEventListener("keydown", event => {
      if (event.key === "Enter" || event.key === " ") { event.preventDefault(); select(); }
    });
  });
  document.querySelectorAll("[data-findings-chart-filter]").forEach(control => {
    function select() {
      form.reset();
      form.querySelector('input[name="status"][value="all"]').checked = true;
      issue = "";
      chart = "all";
      findingChart = control.dataset.findingsChartFilter;
      apply();
      document.getElementById("result-count").focus();
    }
    control.addEventListener("click", select);
    if (["path", "circle"].includes(control.tagName.toLowerCase())) control.addEventListener("keydown", event => {
      if (event.key === "Enter" || event.key === " ") { event.preventDefault(); select(); }
    });
  });
  document.querySelectorAll("[data-toggle-detail]").forEach(button => button.addEventListener("click", () => {
    const detail = document.getElementById(button.getAttribute("aria-controls"));
    detail.hidden = !detail.hidden;
    button.setAttribute("aria-expanded", String(!detail.hidden));
  }));
  apply();
})();
"""

STATUS_LABELS = {
    "attention": "Needs attention",
    "all": "All",
    "ready": "Ready for validation",
    "review": "Needs review",
    "failed": "Blocked / Failed",
    "notstarted": "Not started",
    "unconfirmed": "Readiness unconfirmed",
    "excluded": "Excluded",
}

STAGE_LABELS = {
    "setup": "Necessary setup / initial preflight",
    "discovery": "Discovery", "conversion": "Conversion", "validation": "Validation",
    "packaging": "Packaging", "preflight": "Preflight", "deployment": "Deployment", "mockIngestion": "Mock ingestion",
    "alertParity": "Alert parity", "report": "Report",
}

FINDING_LABELS = {
    "error": ("Errors", "Error", "!"),
    "review": ("Reviews", "Review — decision required", "?"),
    "blocked": ("Blocked prerequisites", "Blocked — not an execution failure", "Ⅱ"),
    "warning": ("Warnings", "Warning — nonblocking", "i"),
    "info": ("Information", "Information — nonblocking", "ℹ"),
}


def _finding_badge(severity: str) -> str:
    _, label, icon = FINDING_LABELS[severity]
    return f'<span class="badge finding-{severity}"><span aria-hidden="true">{icon}</span> {label}</span>'


def _text(value: Any) -> str:
    return escape(str(value)) if value is not None else "Evidence unavailable"


def _safe_flow_message(value: Any) -> str:
    text = str(value or "")
    text = re.sub(
        r"(?<![\w:<])(?:[A-Za-z]:[\\/]|\\\\|/(?!/))[^\s<>\"']+",
        "[local path omitted]",
        text,
    )
    return _text(text)


def _status_label(value: Any) -> str:
    return {
        "notRequired": "Not required", "pending": "Not started",
        "not-run": "Not run (recorded)", "not-recorded": "Evidence unavailable",
        "needsReview": "Needs review", "not-generated": "Not generated",
    }.get(str(value), str(value).replace("-", " ").capitalize() if value else "Evidence unavailable")


def _category(message: str, stage: str = "") -> str:
    text = (stage + " " + message).lower()
    if any(word in text for word in ("runtime", "deployment", "parity", "authentication")):
        return "Execution"
    if any(word in text for word in ("tactic", "technique")):
        return "Tactics"
    if any(word in text for word in ("entity", "mapping", "account", "upn", "host.", "filehash")):
        return "Identity / entities"
    if any(word in text for word in ("timestamp", "timegenerated", "lookback", "queryperiod", "schedule")):
        return "Time / schedule"
    if any(word in text for word in ("query", "table", "union", "search", "kql")):
        return "Query compatibility"
    return "Other"


def _message_key(message: str, stage: str) -> str:
    if stage == "structural-validation" and message.startswith("conversion: "):
        return message[len("conversion: "):]
    return message


def _findings(rule: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    statuses = []
    for side_key, label in (("analyticRule", "Sentinel"), ("customDetection", "XDR")):
        side = rule.get(side_key) or {}
        prefix = "analytic-rule" if side_key == "analyticRule" else "custom-detection"
        for item in side.get("runtime") or []:
            statuses.append((f"{prefix}-runtime-validation", f"{label} runtime", item))
        statuses.append((f"{prefix}-deployment", f"{label} deployment", {"status": side.get("deploymentStatus")}))
    custom = rule["customDetection"]
    alert_statuses = [custom.get("alertStatus"), (rule.get("analyticRule") or {}).get("alertStatus")]
    statuses.extend([
        ("conversion", "Conversion", {"status": custom.get("conversionStatus")}),
        ("structural-validation", "Local structural check", {"status": custom.get("structuralStatus")}),
        ("query-result-parity", "Query parity", rule.get("queryParity") or {}),
        ("alert-parity", "Alert parity", {
            "status": "failed" if "failed" in alert_statuses else "blocked" if "blocked" in alert_statuses else custom.get("alertStatus"),
            "analyticRuleStatus": alert_statuses[1], "customDetectionStatus": alert_statuses[0],
        }),
    ])

    def diagnostic_severity(item: dict[str, Any]) -> str:
        matches = [
            value.get("status") for stage, _, value in statuses
            if stage == item.get("stage") and (
                not item.get("provider") or not value.get("provider") or item["provider"] == value["provider"]
            )
        ]
        return "blocked" if "blocked" in matches and not any(value in {"failed", "conflict"} for value in matches) else "error"

    items = [
        (diagnostic_severity(item), item.get("stage", "unknown"), str(item.get("message", "")), item)
        for item in rule.get("errors") or []
    ]
    for stage, label, value in statuses:
        status = value.get("status")
        if status not in {"failed", "blocked", "conflict"}:
            continue
        if any(
            raw.get("stage") == stage and (
                not value.get("provider") or not raw.get("provider") or raw["provider"] == value["provider"]
            )
            for raw in rule.get("errors") or []
        ):
            continue
        items.append(("blocked" if status == "blocked" else "error", stage,
                      f"{label}: {_status_label(status)}", value))
    items += [
        (
            "review",
            "conversion-review",
            str(message),
            {
                "message": message,
                "reviewScope": custom.get("reviewScope"),
                "reviewDecisions": [
                    decision for decision in custom.get("reviewDecisions") or []
                    if isinstance(decision, dict) and decision.get("reason") == message
                ],
            },
        )
        for message in rule["customDetection"].get("reviewReasons") or []
    ]
    if (custom.get("reviewRequired") or custom.get("conversionStatus") == "needsReview") and not custom.get("reviewReasons"):
        items.append(("review", "conversion-review", "Review required; detailed reason not recorded.",
                      {"reviewRequired": custom.get("reviewRequired"), "conversionStatus": custom.get("conversionStatus")}))
    items += [
        ("warning", "conversion-warning", str(message), {"message": message})
        for message in rule.get("warnings") or []
    ]
    items += [
        ("info", "conversion-information", str(message), {"message": message})
        for message in rule.get("informational") or []
    ]
    for side_key in ("analyticRule", "customDetection"):
        for runtime in (rule.get(side_key) or {}).get("runtime") or []:
            fallback = runtime.get("providerFallback")
            if fallback:
                items.append((
                    "info",
                    "runtime-provider-fallback",
                    "Triage MCP provider gap recorded; complete query family rerun through "
                    f"{fallback.get('fallbackProvider')}: {fallback.get('reason')}",
                    {"provider": runtime.get("provider"), "providerFallback": fallback},
                ))
    for severity, stage, message, raw in items:
        key = _message_key(message, stage)
        # Only the inherited conversion/structural pair shares an error identity.
        scope = "conversion" if stage in {"conversion", "structural-validation"} else stage
        identity = (
            f"{scope}:{key}" if severity in {"error", "blocked"}
            else f"information:{key}" if severity == "info" else f"advisory:{key}"
        )
        if identity not in grouped:
            grouped[identity] = {
                "message": key, "severity": severity, "stages": [],
                "category": _category(key, stage), "evidence": [],
            }
        finding = grouped[identity]
        if stage not in finding["stages"]:
            finding["stages"].append(stage)
        finding["evidence"].append({"stage": stage, **raw})
    return sorted(grouped.values(), key=lambda finding: list(FINDING_LABELS).index(finding["severity"]))


def _rule_status(rule: dict[str, Any], workflow: dict[str, Any]) -> str:
    custom = rule["customDetection"]
    sides = [rule.get("analyticRule") or {}, custom]
    result_statuses = [
        runtime.get("status")
        for side in sides for runtime in side.get("runtime") or []
    ] + [
        side.get(field) for side in sides for field in ("alertStatus", "deploymentStatus")
    ] + [
        (rule.get("queryParity") or {}).get("status"),
        custom.get("structuralStatus"),
        custom.get("conversionStatus"),
    ]
    if rule.get("errors") or any(value in {"failed", "blocked", "conflict"} for value in result_statuses):
        return "failed"
    if custom.get("reviewRequired") or custom.get("reviewReasons") or custom.get("conversionStatus") == "needsReview":
        return "review"
    if custom.get("conversionStatus") == "excluded":
        return "excluded"
    if custom.get("conversionStatus") in {None, "not-run", "pending"}:
        return "notstarted"
    conversion = (workflow.get("stages") or {}).get("conversion") or {}
    if custom.get("conversionStatus") == "converted" and custom.get("structuralStatus") == "passed" and conversion.get("status") == "passed":
        return "ready"
    return "unconfirmed"


CHART_LABELS = {
    "green": "Automated checks passed",
    "yellow": "Warnings or review required",
    "red": "Errors",
    "gray": "Readiness unconfirmed",
}


def _chart_bucket(rule: dict[str, Any]) -> str:
    kinds = {finding["severity"] for finding in _findings(rule)}
    if "error" in kinds:
        return "red"
    if kinds.intersection({"review", "warning"}):
        return "yellow"
    custom = rule["customDetection"]
    if "blocked" not in kinds and custom.get("conversionStatus") == "converted" and custom.get("structuralStatus") == "passed":
        return "green"
    return "gray"


def _chart_html(rules: list[dict[str, Any]]) -> str:
    counts = Counter(_chart_bucket(rule) for rule in rules)
    total = len(rules)
    offset = 0.0
    arcs, legend = [], []
    for color, label in CHART_LABELS.items():
        count = counts[color]
        percentage = count * 100 / total if total else 0
        text = f"{label}: {count} rules ({percentage:.1f}%)"
        if count:
            arcs.append(
                f'<circle class="donut-{color}" cx="21" cy="21" r="15.9155" pathLength="100" '
                f'stroke-dasharray="{percentage:.6f} {100-percentage:.6f}" stroke-dashoffset="{-offset:.6f}" '
                f'transform="rotate(-90 21 21)" tabindex="0" role="button" aria-pressed="false" '
                f'aria-label="{text}" data-chart-filter="{color}"><title>{text}</title></circle>'
            )
        offset += percentage
        legend.append(
            f'<button type="button" data-chart-filter="{color}" data-chart-label="{label}" aria-pressed="false">'
            f'<span class="swatch swatch-{color}" aria-hidden="true"></span>{text}</button>'
        )
    return (
        '<section class="panel" aria-labelledby="chart-heading"><h2 id="chart-heading">Automated check overview — not deployment readiness</h2>'
        '<div class="chart-layout"><svg class="donut" viewBox="0 0 42 42" role="group" aria-label="Rule counts by automated-check outcome">'
        '<circle class="donut-track" cx="21" cy="21" r="15.9155"></circle>'
        + "".join(arcs) + f'<text class="chart-total" x="21" y="21">{total}</text><text x="21" y="26">rules</text></svg>'
        '<div class="chart-legend">' + "".join(legend)
        + '<button type="button" data-chart-filter="all" aria-pressed="true">Show all chart groups</button></div></div>'
        '<p>Each rule is counted once: errors take priority, then warnings/reviews, then passed automated conversion '
        'and local structural checks; insufficient evidence or a remaining per-rule prerequisite block is gray. '
        'Information alone is nonblocking and belongs in green when both automated checks passed. Missing results are never green.</p>'
        '<p class="muted">Green is not semantic approval or deployment readiness. A green rule can still have '
        'Readiness unconfirmed in the status filter while run-level conversion review remains incomplete. '
        'Chart selections reset other filters; further filters narrow the selected group.</p></section>'
    )


def _findings_chart_html(rules: list[dict[str, Any]]) -> str:
    counts = Counter(finding["severity"] for rule in rules for finding in _findings(rule))
    buckets = [
        ("error", "Errors", counts["error"], "red"),
        ("attention", "Warnings / reviews", counts["warning"] + counts["review"], "yellow"),
        ("info", "Informational", counts["info"], "info"),
    ]
    total = sum(count for _, _, count, _ in buckets)
    passed_rules = sum(_chart_bucket(rule) == "green" for rule in rules)
    angle = -math.pi / 2
    segments, legend = [], []
    for key, label, count, swatch in buckets:
        proportion = count / total if total else 0
        text = f"{label}: {count} findings ({proportion * 100:.1f}%)"
        attributes = (
            f'class="pie-{key}" tabindex="0" role="button" aria-pressed="false" '
            f'aria-label="{text}" data-findings-chart-filter="{key}"'
        )
        if count == total and total:
            segments.append(f'<circle cx="21" cy="21" r="18" {attributes}><title>{text}</title></circle>')
        elif count:
            end = angle + proportion * math.tau
            start_x, start_y = 21 + 18 * math.cos(angle), 21 + 18 * math.sin(angle)
            end_x, end_y = 21 + 18 * math.cos(end), 21 + 18 * math.sin(end)
            path = f"M21 21 L{start_x:.6f} {start_y:.6f} A18 18 0 {int(proportion > .5)} 1 {end_x:.6f} {end_y:.6f} Z"
            segments.append(f'<path d="{path}" {attributes}><title>{text}</title></path>')
        angle += proportion * math.tau
        legend.append(
            f'<button type="button" data-findings-chart-filter="{key}" data-finding-label="{label}" aria-pressed="false">'
            f'<span class="swatch swatch-{swatch}" aria-hidden="true"></span>{text}</button>'
        )
    if not total:
        segments.append('<circle class="pie-empty" cx="21" cy="21" r="18"><title>No charted findings</title></circle>')
    return (
        '<section class="panel" aria-labelledby="findings-chart-heading">'
        f'<h2 id="findings-chart-heading">High-level findings — {total} distinct findings</h2>'
        '<div class="chart-layout"><svg class="findings-pie" viewBox="0 0 42 42" role="group" aria-label="Findings by type">'
        + "".join(segments) + '</svg><div class="chart-legend">' + "".join(legend)
        + '<button type="button" data-findings-chart-filter="all" aria-pressed="true">Show all finding types</button></div>'
        f'<div class="badge ready"><strong>{passed_rules} rules</strong> passed automated checks with no actionable findings'
        '<br><span class="muted">Separate rule metric; not a pie slice. Informational notes are allowed.</span></div></div>'
        '<p class="muted">Pie counts are deduplicated per-rule findings, not unique rules; one rule may contribute several. '
        f'Yellow combines {counts["warning"]} warnings and {counts["review"]} reviews. '
        f'Blocked prerequisite findings ({counts["blocked"]}) are tracked separately, not counted as errors or included in this pie. '
        'Select a slice or legend to show matching rules; the rule-list count may differ from the finding count.</p></section>'
    )


def _next_action(status: str, findings: list[dict[str, Any]]) -> str:
    if status == "failed":
        return "Inspect failed or blocked check evidence; resolve its cause before retrying."
    if status == "notstarted":
        return "Start conversion after the run prerequisites are satisfied."
    if status == "unconfirmed":
        return "See the run-level conversion review caution; no per-rule review decision is inferred."
    if status == "ready":
        return "Proceed to the workflow validation stage; deployment is not approved."
    if status == "excluded":
        return "Inspect the recorded exclusion before changing scope."
    categories = {item["category"] for item in findings if item["severity"] in {"error", "review", "blocked"}}
    if "Tactics" in categories:
        return "Review invalid or incompatible classification metadata. Authoring preserves all source tactics; regenerate historical single-tactic drafts after review."
    if "Identity / entities" in categories:
        return "Confirm the output identity mapping against source evidence."
    return "Review the recorded reasons and resolve the rule-specific decision."


def _is_tactic_review(finding: dict[str, Any]) -> bool:
    return finding["severity"] == "review" and "one tactic" in finding["message"].lower()


def _tactic_guide() -> str:
    return (
        '<details id="tactic-selection-guide-panel"><summary>Preserve source tactics; review historical single-tactic findings</summary>'
        '<section id="tactic-selection-guide" aria-label="Source tactic preservation guidance" tabindex="-1">'
        '<p><strong>Historical finding:</strong> authoring now preserves all source tactics in source order, '
        'with documented compatible techniques. Multiple tactics alone no longer require review. '
        'Regenerate older drafts explicitly; this report does not clear historical findings.</p>'
        '<p>V3.1 ARM packaging carries only the first tactic and its compatible techniques, without modifying YAML. '
        'This classification loss is not validated parity. Direct Graph deployment remains <strong>one tactic, '
        'with multiple compatible techniques and subtechniques under it</strong> — not one technique only.</p>'
        '<p>Do not pair the source lists by position or copy every technique into every tactic. '
        'Legacy overrides replace techniques only for their named source tactic; they cannot narrow or reorder the source tactics. '
        'Unknown or incompatible classifications still require correction.</p>'
        '<p><strong>Verified scope (2026-10-07):</strong> an isolated Microsoft Graph beta create request with '
        'multiple tactics returned HTTP 400: <q>Multiple MITRE tactics are not supported. Specify a single tactic..</q> '
        'The Defender UI was confirmed to allow one tactic with multiple techniques; a read-back of a UI-created '
        'rule also confirmed the nested technique/subtechnique shape. This is not a claim that the multi-tactic '
        'request succeeded, that ARM was tested, or that every future API version has the same restriction.</p>'
        '<p>The public <a href="https://learn.microsoft.com/en-us/graph/api/resources/security-alerttemplate?view=graph-rest-beta" '
        'rel="noreferrer">Graph beta alertTemplate reference</a> describes <code>tactics</code> as a collection. '
        'A collection-shaped property alone does not establish acceptance of multiple tactics. '
        'The <a href="https://learn.microsoft.com/en-us/graph/api/resources/security-mitretactic?view=graph-rest-beta" '
        'rel="noreferrer">mitreTactic reference</a> documents the techniques collection within a tactic.</p>'
        '<p>The converter preserves the original classification in '
        '<code>contentProvenance.conversion.originalTactics</code> and <code>originalTechniques</code>. '
        'Each affected rule below shows source lists, preserved provenance, the current draft, and a rule-specific '
        '<code>ruleOverrides</code> example. Missing metadata is reported rather than reconstructed. '
        'No selection is automatically approved, and this report changes no query, configuration, or workflow gate.</p></section></details>'
    )


def _tactic_details(rule: dict[str, Any], findings: list[dict[str, Any]]) -> str:
    if not any(_is_tactic_review(finding) for finding in findings):
        return ""
    classification = rule.get("attackClassification") or {}
    sections = []
    for label, key in (
        ("Sentinel source tactics (independent list)", "sourceTactics"),
        ("Sentinel source techniques (independent list)", "sourceTechniques"),
        ("Original tactics preserved in draft provenance", "originalTactics"),
        ("Original techniques preserved in draft provenance", "originalTechniques"),
        ("Current draft tactics, techniques and subtechniques (exact recorded shape)", "draftTactics"),
    ):
        value = classification.get(key)
        text = json.dumps(value, indent=2, ensure_ascii=False) if value is not None else "Classification metadata not recorded."
        sections.append(f"<h5>{label}</h5><pre>{escape(text)}</pre>")
    original = classification.get("originalTactics")
    draft = classification.get("draftTactics")
    fallback = (
        isinstance(original, list) and len(original) > 1
        and isinstance(draft, list) and len(draft) == 1 and isinstance(draft[0], dict)
        and draft[0].get("tactic") == original[0] and not draft[0].get("techniques")
    )
    rule_id = (rule.get("analyticRule") or {}).get("id")
    example = {"ruleOverrides": {str(rule_id or "<source-rule-id>"): {
        "tactic": "<existing source tactic whose techniques need correction>",
        "techniques": ["<compatible technique ID>", "<additional compatible technique or subtechnique ID, if applicable>"],
    }}}
    return (
        '<section class="tactic-review"><h4>Historical tactic finding and retained classification</h4>'
        '<p><a href="#tactic-selection-guide">Authored YAML preserves all source tactics; deployment contracts differ.</a></p>'
        '<p>Source lists are independent; their positions do not establish tactic/technique pairings. '
        'Source metadata reflects the current file; provenance records the original conversion classification.</p>'
        + "".join(sections)
        + (
            '<p><strong>Unapproved fallback shape:</strong> this draft retains the first original tactic '
            f'({_text(original[0])}) with techniques omitted. It matches the converter fallback for an unresolved '
            'multi-tactic source; it is not an approved classification. Explicitly regenerate to preserve all source tactics '
            'and their documented compatible techniques/subtechniques.</p>' if fallback else
            '<p>The draft shape is not treated as proof that a selection was approved. Resolve the recorded review reason explicitly.</p>'
        )
        + '<h5>Rule-specific override example — illustrative, not ready to apply</h5>'
        f'<pre>{escape(json.dumps(example, indent=2, ensure_ascii=False))}</pre>'
        '<p>Replace every placeholder with reviewed values and remove unused optional entries. '
        'Use technique IDs, including dotted subtechnique IDs where appropriate, in the existing '
        '<code>techniques</code> list. Merge this rule entry into the existing migration configuration; '
        'do not replace other rules. No tactic or technique is selected by this example. '
        'An override is optional for technique corrections, not required merely for multiple tactics. '
        'It does not remove or reorder source tactics. Subsequent workflow checks remain required.</p></section>'
    )


def _query_html(rule: dict[str, Any]) -> str:
    queries = rule.get("queries") or {}
    source, converted = queries.get("source"), queries.get("converted")
    if source is None and converted is None:
        return (
            '<section class="query-review"><h4>Sentinel and XDR queries</h4>'
            '<p class="muted">Source and converted queries were not recorded in this report.</p></section>'
        )
    pair = (
        '<div class="query-pair">'
        f'<section><h4>Source Sentinel KQL</h4><pre>{_text(source)}</pre></section>'
        f'<section><h4>Converted XDR KQL</h4><pre>{_text(converted)}</pre></section></div>'
    )
    if source is None or converted is None:
        diff = "<p>Comparison unavailable: one query was not recorded.</p>"
    elif source == converted:
        diff = "<p>Query unchanged.</p>"
    else:
        lines = unified_diff(
            str(source).splitlines(), str(converted).splitlines(),
            fromfile="Source Sentinel", tofile="Converted XDR", lineterm="",
        )
        diff = "<h4>Unified text diff</h4><pre>" + escape("\n".join(lines)) + "</pre>"
    return (
        '<section class="query-review"><h4>Sentinel and XDR queries</h4>'
        '<p class="muted">Current file snapshot at report generation; textual comparison is not proof of semantic equivalence.</p>'
        + pair + diff + "</section>"
    )


def _result_html(rule: dict[str, Any]) -> str:
    lines = []
    custom = rule["customDetection"]
    lines.append(f"<li>Conversion: {_text(_status_label(custom.get('conversionStatus')))}; "
                 f"local structural checks: {_text(_status_label(custom.get('structuralStatus')))}</li>")
    for name, side in (("Sentinel", rule.get("analyticRule") or {}), ("XDR", custom)):
        for runtime in side.get("runtime") or []:
            count = runtime.get("rowCount")
            measurement = f"{_text(count)} rows" if count is not None else "Row count unavailable"
            lines.append(
                f"<li>{name} runtime — {_text(runtime.get('provider'))}: "
                f"{_text(_status_label(runtime.get('status')))} · {measurement}</li>"
            )
            whitelist = runtime.get("sourceWhitelist")
            if isinstance(whitelist, dict):
                lines.append(
                    f"<li>Source table whitelist — {_text(whitelist.get('table'))}: "
                    f"{_text(whitelist.get('status'))}; raw result "
                    f"{_text((whitelist.get('rawFailure') or {}).get('status'))}; "
                    f"{_text(whitelist.get('reason'))}</li>"
                )
        for field, label in (("deploymentStatus", "deployment"), ("alertStatus", "alerts")):
            value = side.get(field)
            if value not in {None, "not-run", "not-recorded"}:
                lines.append(f"<li>{name} {label}: {_text(_status_label(value))}</li>")
    parity = rule.get("queryParity") or {}
    if parity.get("status") not in {None, "not-run", "not-recorded"}:
        lines.append(f"<li>Query parity: {_text(_status_label(parity['status']))}")
        for field, label in (("analyticRuleRows", "Sentinel rows"), ("customDetectionRows", "XDR rows"), ("matchKey", "Match key")):
            if parity.get(field) is not None:
                lines.append(f" · {label}: {_text(parity[field])}")
        lines.append("</li>")
    return "<h4>Recorded checks</h4><ul>" + "".join(lines) + "</ul>"


def _run_html(report: dict[str, Any]) -> str:
    workflow = report.get("workflow") or {}
    stages = workflow.get("stages") or {}
    profile = workflow.get("profile")
    stage_html, evidence = [], []
    for name, stage in stages.items():
        label = STAGE_LABELS.get(name, name)
        status = stage.get("status")
        runtime_status = (
            (stage.get("artifacts") or {}).get("runtimeStatus")
            if isinstance(stage.get("artifacts"), dict)
            else None
        )
        display_status = (
            "Pending" if status == "pending" and stage.get("attempts") != 0
            else "Source waived — not fully runtime-qualified"
            if name == "validation" and runtime_status == "source-waived"
            else "Passed — offline Authoring; runtime not run"
            if name == "validation"
            and runtime_status == "not-run"
            and (stage.get("artifacts") or {}).get("validationMode") == "offline-authoring"
            and status == "passed"
            else _status_label(status)
        )
        stage_html.append(f'<li class="stage {_text(status)}">{_text(label)}: {_text(display_status)}</li>')
        if stage.get("message") or stage.get("evidence"):
            evidence_links = _flow_links(report, name)
            evidence.append(
                f"<details><summary>{_text(label)} — recorded context</summary>"
                f"<p>{_safe_flow_message(stage['message']) if stage.get('message') else ''}</p>"
                + evidence_links + "</details>"
            )
    if not stages:
        stage_html.append("<li>Workflow stage evidence unavailable.</li>")
    runtime_rules = sum(
        bool(rule.get("analyticRule", {}).get("runtime") or rule["customDetection"].get("runtime"))
        for rule in report["rules"]
    )
    runtime_assessment = (
        report.get("runtimeAssessment")
        if isinstance(report.get("runtimeAssessment"), dict)
        else {}
    )
    whitelist_entries = (
        runtime_assessment.get("sourceWhitelist")
        if isinstance(runtime_assessment.get("sourceWhitelist"), list)
        else []
    )
    whitelist_summary = ""
    if whitelist_entries:
        whitelist_summary = (
            f"<p>Source runtime whitelist: {len(whitelist_entries)} IdentityInfo "
            "missing-table result(s) classified; raw query results remain failed. "
            "This does not indicate XDR runtime qualification.</p>"
        )
    workspace = "Configured in run context" if workflow.get("workspaceConfigured") else "Not recorded in run context"
    return (
        '<section class="panel" aria-labelledby="run-heading"><h2 id="run-heading">Run context</h2>'
        f"<p><strong>{_text(str(profile).capitalize() if profile else 'Profile unavailable')}</strong>"
        f" · Run {_text(workflow.get('runId'))} · {_text(_status_label(workflow.get('status')))}</p>"
        '<ol class="stages">' + "".join(stage_html) + "</ol>"
        f"<p>Workspace: {workspace}. Runtime evidence available for {runtime_rules} of {len(report['rules'])} rules.</p>"
        + whitelist_summary
        + "<p class=\"muted\">Shared stage status does not override individual results. Missing evidence is not proof "
        "a check was skipped. Optional stages are marked Not required only when recorded by the workflow.</p>"
        "<details><summary>Run messages, environment reasons and historical evidence</summary>"
        "<p class=\"muted\">Recorded text may contain historical counts; current artifact counts appear below.</p>"
        + "".join(evidence) + "</details></section>"
    )


FLOW_STATIONS = (
    ("setup", "Necessary setup / initial preflight"),
    ("discovery", "Discovery"),
    ("conversion", "Conversion"),
    ("validation", "Validation"),
    ("packaging", "Packaging"),
    ("preflight", "Preflight"),
    ("validationSuite", "Official validation rerun"),
    ("deployment", "Deployment"),
    ("mockIngestion", "Mock ingestion"),
    ("queryValidation", "Semantic/query validation"),
    ("alertParity", "Alert parity"),
    ("packageAcceptance", "Full package deployment"),
)
FLOW_DESCRIPTIONS = {
    "setup": "Display-only startup summary of persisted local tool/runtime, selected profile, explicit run ID, and locked target metadata. It never runs doctor or authentication. A separate fresh read-only preflight remains immediately before Qualification deployment.",
    "discovery": "Identify the source solution and inventory its content. Source/target details appear only when recorded.",
    "conversion": "Convert source rules into XDR detection drafts. Mapping choices remain reviewable; untracked subtasks are not marked complete.",
    "validation": "Mandatory structural validation and recorded runtime checks. Query execution alone is not alert parity.",
    "packaging": "Record the release action and build the V3.1 package. A passed historical build is not current unless package freshness is verified.",
    "preflight": "Qualification only: inspect persisted cached-auth, scope, exact GET, DCR and query-permission evidence. Readiness is diagnostic, not write approval.",
    "validationSuite": "Qualification prerequisite: current full official local validation is distinct from the canonical source-query/schema validation stage. No current suite result is inferred when absent.",
    "deployment": "Qualification only: after validation and fresh exact-scope approval, deploy the approved AR/CD testing pairs disabled in the locked target environment.",
    "mockIngestion": "Qualification only: ingest reviewed shared fixtures after a separate exact-scope write approval; prepared hypotheses are not runtime proof.",
    "queryValidation": "Qualification only: validate semantic/query behavior against observed telemetry. Query-permission checks and zero-row query success are not semantic matches.",
    "alertParity": "Qualification only: compare observed alerts and preserve separate approval and cleanup evidence.",
    "packageAcceptance": "Separate later full-package deployment/read-back. Pair deployment does not prove package acceptance; this full-package action is not a canonical tracked stage here.",
    "report": "Generate an offline snapshot from recorded workflow and rule evidence.",
    "publication": "External to this workflow. A package artifact does not prove publication.",
}


def _flow_stage(stage: Any, *, freshness: Any = None) -> dict[str, Any]:
    if not isinstance(stage, dict):
        stage = {}
    raw = stage.get("status") if isinstance(stage.get("status"), str) else None
    normalized = {
        "passed": ("completed", "Passed"),
        "completed": ("completed", "Completed"),
        "running": ("running", "In progress"),
        "inProgress": ("running", "In progress"),
        "blocked": ("blocked", "Blocked"),
        "failed": ("failed", "Failed"),
        "pending": ("pending", "Pending"),
        "notRequired": ("not-required", "Not required"),
        "stale": ("stale", "Stale"),
    }.get(raw, ("unknown", "Evidence unavailable" if raw is None else "Unknown status"))
    artifacts = stage.get("artifacts") if isinstance(stage.get("artifacts"), dict) else {}
    freshness_status = None
    if isinstance(freshness, dict):
        freshness_status = freshness.get("status") if isinstance(freshness.get("status"), str) else None
    if raw in {"passed", "completed"}:
        if freshness_status == "stale":
            normalized = ("stale", "Stale package")
        elif freshness_status != "current":
            normalized = ("unknown", "Freshness unverified")
    if artifacts.get("runtimeStatus") == "source-waived":
        display = "Source waived — not fully runtime-qualified"
    else:
        display = normalized[1]
    message = stage.get("message") if isinstance(stage.get("message"), str) else ""
    evidence = stage.get("evidence") if isinstance(stage.get("evidence"), list) else []
    return {
        "state": normalized[0],
        "display": display,
        "raw": raw or "",
        "freshness": freshness_status or "",
        "freshnessReason": (
            freshness.get("reason")
            if isinstance(freshness, dict) and isinstance(freshness.get("reason"), str)
            else ""
        ),
        "message": message,
        "evidence": [item for item in evidence if isinstance(item, str)],
        "updated": stage.get("updatedAt") if isinstance(stage.get("updatedAt"), str) else "",
        "timing": " · ".join(
            value for value in (
                f"Started: {stage.get('startedAt')}" if isinstance(stage.get("startedAt"), str) else "",
                f"Completed: {stage.get('completedAt')}" if isinstance(stage.get("completedAt"), str) else "",
                _flow_duration(stage.get("startedAt"), stage.get("completedAt")),
            ) if value
        ),
        "attempts": (
            str(stage.get("attempts"))
            if isinstance(stage.get("attempts"), int) and not isinstance(stage.get("attempts"), bool)
            else ""
        ),
    }


FLOW_GLYPHS = {
    "completed": "OK", "running": ">>", "blocked": "!!", "failed": "X",
    "pending": "..", "not-required": "--", "stale": "~", "unknown": "?",
}


def _flow_duration(started: Any, completed: Any) -> str:
    if not isinstance(started, str) or not isinstance(completed, str):
        return ""
    try:
        start = datetime.fromisoformat(started.replace("Z", "+00:00"))
        end = datetime.fromisoformat(completed.replace("Z", "+00:00"))
        seconds = (end - start).total_seconds()
    except (OverflowError, TypeError, ValueError):
        return ""
    return f"Elapsed: {seconds:.1f} seconds" if seconds >= 0 else ""


def _setup_station_value(report: dict[str, Any]) -> dict[str, Any]:
    setup = report.get("startupSetup")
    setup = setup if isinstance(setup, dict) else {}
    return {
        "state": "unknown",
        "display": setup.get("display") if isinstance(setup.get("display"), str) else "Setup checks not recorded",
        "raw": "not-checked",
        "message": (
            "This informational station reads persisted run/profile/target records only. "
            "It does not run doctor, inspect authentication caches, authenticate, or probe network access."
        ),
        "updated": "",
        "timing": "",
        "attempts": "",
    }


def _preflight_station_value(preflight: dict[str, Any]) -> dict[str, Any]:
    if preflight.get("graphRecorded") is not True:
        return {
            "state": "unknown",
            "display": "Graph preflight not recorded",
            "raw": "",
            "message": "DCR/workspace permission evidence, when present, is partial and does not replace the Graph preflight.",
        }
    raw = preflight.get("deploymentReadiness") if isinstance(preflight.get("deploymentReadiness"), str) else "unknown"
    states = {
        "ready": ("unknown", "Readiness unconfirmed"),
        "blocked": ("blocked", "Blocked"),
        "action-required": ("blocked", "Action required"),
        "readiness-unconfirmed": ("unknown", "Readiness unconfirmed"),
        "unknown": ("unknown", "Unknown"),
    }
    state, display = states.get(raw, ("unknown", "Unknown preflight status"))
    return {
        "state": state,
        "display": display,
        "raw": raw,
        "message": "Management permission grant, read access, GET checks, and deployment readiness are separate. A read-only GET does not prove effective write authorization; it is not deployment or write approval.",
    }


def _query_validation_value(report: dict[str, Any]) -> dict[str, Any]:
    rules = report.get("rules") if isinstance(report.get("rules"), list) else []
    results = []
    for rule in rules:
        if isinstance(rule, dict) and isinstance(rule.get("queryParity"), dict):
            results.append(rule["queryParity"])
    if not results:
        return {"state": "unknown", "display": "Not run", "raw": "not-run"}
    if any(item.get("status") == "failed" for item in results):
        return {"state": "failed", "display": "Failed", "raw": "failed"}
    if any(item.get("status") == "blocked" for item in results):
        return {"state": "blocked", "display": "Blocked", "raw": "blocked"}
    if all(item.get("status") == "passed" for item in results):
        if any(
            not isinstance(item.get("analyticRuleRows"), int)
            or not isinstance(item.get("customDetectionRows"), int)
            or item.get("analyticRuleRows") <= 0
            or item.get("customDetectionRows") <= 0
            for item in results
        ):
            return {
                "state": "unknown",
                "display": "Zero / unknown rows · no semantic pass",
                "raw": "passed-without-positive-rows",
            }
        return {"state": "completed", "display": "Query parity recorded", "raw": "passed"}
    return {"state": "unknown", "display": "Not run / incomplete", "raw": "unknown"}


def _package_acceptance_value(report: dict[str, Any]) -> dict[str, Any]:
    plan = report.get("deploymentPlanning")
    plan = plan.get("packageAcceptancePlan") if isinstance(plan, dict) else {}
    plan = plan if isinstance(plan, dict) else {}
    return {
        "state": "unknown",
        "display": "Not tracked · not run",
        "raw": "not-tracked",
        "message": (
            "Full-package deployment and read-back are separate from the V3.1 package build "
            "and from direct AR/CD pair results. No full-package execution evidence is recorded."
        ),
        "plan": plan,
    }


def _validation_suite_value(report: dict[str, Any]) -> dict[str, Any]:
    workflow = report.get("workflow") if isinstance(report.get("workflow"), dict) else {}
    stages = workflow.get("stages") if isinstance(workflow.get("stages"), dict) else {}
    validation = stages.get("validation") if isinstance(stages.get("validation"), dict) else {}
    current_suite = stages.get("validationSuite")
    if isinstance(current_suite, dict) and isinstance(current_suite.get("status"), str):
        value = _flow_stage(current_suite)
        return {
            **value,
            "canonicalStatus": validation.get("status"),
            "message": current_suite.get("message")
            if isinstance(current_suite.get("message"), str)
            else "Current official local validation status comes from the selected run's validationSuite stage evidence.",
        }
    return {
        "state": "unknown",
        "display": "Current full-suite result not recorded",
        "raw": "not-recorded",
        "message": (
            "The canonical Validation stage records structural/query evidence. "
            "Its historical pass does not prove that the current full official local validation rerun passed."
        ),
        "canonicalStatus": validation.get("status"),
    }


def _flow_station(
    key: str,
    title: str,
    lines: tuple[str, ...],
    x: int,
    y: int,
    value: dict[str, Any],
    *,
    branch: bool = False,
    compact: bool = False,
) -> str:
    label_y = y + (48 if branch else 42 if compact else 45)
    line_markup = "".join(
        f'<tspan x="{x}" dy="{18 if index else 0}">{escape(line)}</tspan>'
        for index, line in enumerate(lines)
    )
    status_y = label_y + len(lines) * 18 + 6
    return (
        f'<a class="flow-link" href="#flow-evidence-{escape(key, quote=True)}" '
        f'tabindex="0" focusable="true" aria-label="{escape(title + ": " + value["display"] + ". Open recorded stage evidence.", quote=True)}" '
        f'title="Open {escape(title, quote=True)} evidence">'
        f'<g class="flow-station state-{value["state"]}" data-flow-station="{escape(key, quote=True)}" '
        f'data-flow-status="{escape(value["display"], quote=True)}">'
        f'<circle class="station-marker" cx="{x}" cy="{y}" r="21"/>'
        f'<text class="station-glyph" x="{x}" y="{y + 5}" aria-hidden="true">{FLOW_GLYPHS[value["state"]]}</text>'
        f'<text class="station-name" x="{x}" y="{label_y}">{line_markup}</text>'
        f'<text class="station-status" x="{x}" y="{status_y}">{escape(value["display"])}</text>'
        f'<title>{escape(title)} — {escape(value["display"])}</title></g></a>'
    )


def _safe_local_href(value: Any) -> str | None:
    if not isinstance(value, str) or not value or any(ord(char) < 32 for char in value):
        return None
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        return None
    if value.startswith(("/", "\\", "//")) or "\\" in value:
        return None
    decoded_path = unquote(parsed.path)
    segments = decoded_path.split("/")
    if (
        "\\" in decoded_path
        or any(ord(char) < 32 for char in decoded_path)
        or any(segment in {"", ".", ".."} for segment in segments)
    ):
        return None
    if any(":" in segment for segment in segments):
        return None
    return value


def _flow_links(report: dict[str, Any], stage_name: str) -> str:
    evidence = report.get("flowEvidence")
    references = evidence.get(stage_name) if isinstance(evidence, dict) else None
    safe_links = []
    workflow = report.get("workflow") if isinstance(report.get("workflow"), dict) else {}
    stages = workflow.get("stages") if isinstance(workflow.get("stages"), dict) else {}
    recorded = stages.get(stage_name) if isinstance(stages.get(stage_name), dict) else {}
    unavailable = bool(recorded.get("evidence"))
    for item in references if isinstance(references, list) else []:
        if not isinstance(item, dict):
            unavailable = True
            continue
        if item.get("available") is not True:
            unavailable = True
            continue
        href = _safe_local_href(item.get("href"))
        label = item.get("label")
        if href is None or not isinstance(label, str) or not label:
            unavailable = True
            continue
        label = label.replace("\\", "/").rsplit("/", 1)[-1]
        if label in {"", ".", ".."}:
            unavailable = True
            continue
        safe_links.append(
            f'<li><a href="{escape(href, quote=True)}">{_text(label)}</a></li>'
        )
    if not safe_links:
        message = (
            "Evidence is recorded but unavailable or non-portable."
            if unavailable else "No linked stage evidence is recorded in this snapshot."
        )
        return f'<p class="muted">{message}</p>'
    if unavailable:
        safe_links.append('<li class="muted">Some recorded evidence is unavailable or non-portable.</li>')
    return '<ul class="flow-artifact-links">' + "".join(safe_links) + "</ul>"


def _flow_rule_detail_link(index: int, name: Any) -> str:
    return f'<a href="#rule-detail-{index}">{_text(name)}</a>'


def _flow_stage_detail(stage_name: str, report: dict[str, Any]) -> str:
    workflow = report.get("workflow") if isinstance(report.get("workflow"), dict) else {}
    stages = workflow.get("stages") if isinstance(workflow.get("stages"), dict) else {}
    stage = stages.get(stage_name)
    preflight = report.get("qualificationPreflight") if isinstance(report.get("qualificationPreflight"), dict) else {}
    preflight_value: dict[str, Any] = {}
    suite_value: dict[str, Any] = {}
    package_value: dict[str, Any] = {}
    if stage_name == "setup":
        setup_value = _setup_station_value(report)
        stage = {"status": "unknown", "message": setup_value["message"]}
    elif stage_name == "preflight":
        preflight_value = _preflight_station_value(preflight)
        stage = {
            "status": preflight_value["raw"] or "unknown",
            "message": preflight_value["message"],
        }
        if isinstance(preflight.get("checkedAt"), str):
            stage["updatedAt"] = preflight["checkedAt"]
    elif stage_name == "validationSuite":
        suite_value = _validation_suite_value(report)
        stage = {
            "status": "unknown",
            "message": suite_value["message"],
        }
    elif stage_name == "queryValidation":
        query_value = _query_validation_value(report)
        stage = {
            "status": query_value["raw"],
            "message": "Status is derived only from recorded semantic query-parity evidence; zero or missing row counts are not a pass.",
        }
    elif stage_name == "packageAcceptance":
        package_value = _package_acceptance_value(report)
        stage = {
            "status": "unknown",
            "message": package_value["message"],
        }
    freshness = workflow.get("packageFreshness") if stage_name == "packaging" else None
    value = _flow_stage(stage, freshness=freshness)
    if stage_name == "preflight":
        value = {**value, **preflight_value}
    elif stage_name == "validationSuite":
        value = {**value, **suite_value}
    elif stage_name == "queryValidation":
        value = {**value, **_query_validation_value(report)}
    elif stage_name == "packageAcceptance":
        value = {**value, **package_value}
    label = {
        "validationSuite": "Official full-suite validation rerun",
        "deployment": "Direct AR/CD testing-pair deployment",
        "queryValidation": "Semantic/query validation",
        "packageAcceptance": "Full-package deployment and read-back",
    }.get(stage_name, STAGE_LABELS.get(stage_name, "Publication"))
    description = FLOW_DESCRIPTIONS.get(stage_name, FLOW_DESCRIPTIONS["publication"])
    stage_status = (
        f'<p><strong>Recorded stage status:</strong> {_text(value["raw"] or "Evidence unavailable")} '
        f'· {_text(value["display"])}</p>'
    )
    freshness_status = ""
    if stage_name == "packaging":
        fresh_value = (
            freshness.get("status")
            if isinstance(freshness, dict) and isinstance(freshness.get("status"), str)
            else "Evidence unavailable"
        )
        freshness_status = f'<p><strong>Package freshness:</strong> {_text(fresh_value)}</p>'
        if value["freshnessReason"]:
            freshness_status += f'<p>{_text(value["freshnessReason"])}</p>'
    if value["message"]:
        message = f'<p><strong>Recorded remarks:</strong> {_safe_flow_message(value["message"])}</p>'
    elif stage is None:
        message = '<p class="muted">No recorded stage status or remarks.</p>'
    else:
        message = '<p class="muted">No stage remarks recorded.</p>'
    timestamps = []
    if value["updated"]:
        timestamps.append(f'Updated: {_text(value["updated"])}')
    if value["timing"]:
        timestamps.append(_text(value["timing"]))
    if value["attempts"]:
        timestamps.append(f'Attempts: {_text(value["attempts"])}')
    timing = f'<p class="muted">{" · ".join(timestamps)}</p>' if timestamps else ""
    stage_evidence = _flow_links(report, stage_name)
    rules = report.get("rules") if isinstance(report.get("rules"), list) else []
    rule_proof = ""
    if stage_name == "setup":
        setup = report.get("startupSetup") if isinstance(report.get("startupSetup"), dict) else {}
        setup_target = setup.get("target") if isinstance(setup.get("target"), dict) else {}
        auth = setup.get("authentication") if isinstance(setup.get("authentication"), dict) else {}
        consent = (
            report.get("deploymentPlanning", {}).get("deploymentPlan", {}).get("planningConsent", {})
            if isinstance(report.get("deploymentPlanning"), dict)
            and isinstance(report.get("deploymentPlanning", {}).get("deploymentPlan"), dict)
            else {}
        )
        runtime_consent = (
            report.get("workflow", {}).get("runtimeQueryConsent", {})
            if isinstance(report.get("workflow"), dict)
            else {}
        )
        runtime_families = (
            runtime_consent.get("families", {})
            if isinstance(runtime_consent.get("families"), dict)
            else {}
        )
        details = [
            f'<li>Explicit migration run ID: {_text(setup.get("runId") or "Not recorded")}</li>',
            f'<li>Confirmed workflow profile: {_text(setup.get("profile") or "Not recorded")}</li>',
            f'<li>Local Python/CLI/tool checks: {_text(setup.get("localToolChecks") or "Not recorded")}</li>',
            f'<li>Locked target record: {_text("Confirmed" if setup.get("targetLocked") else "Not confirmed")} · source: {_text(setup.get("targetSource") or "Not recorded")}</li>',
            f'<li>Cached authentication evidence: {_text(auth.get("status") or "Not checked in this run")}</li>',
            f'<li>Advance read-only runtime-query consent: {_text(runtime_consent.get("status") or "Not recorded")} · scope: {_text(runtime_consent.get("consentScope") or "Not recorded")} · latest decision: {_text((runtime_consent.get("latestDecision") or {}).get("status") or "unanswered")} · run snapshot: {_text((runtime_consent.get("runSnapshot") or {}).get("status") or "not-current")} · Sentinel source: {_text((runtime_families.get("sentinelSourceQueryFamily") or {}).get("status") or "Not recorded")} / {_text((runtime_families.get("sentinelSourceQueryFamily") or {}).get("executionStatus") or "not-run")} · Defender XDR: {_text((runtime_families.get("defenderXdrQueryFamily") or {}).get("status") or "Not recorded")} / {_text((runtime_families.get("defenderXdrQueryFamily") or {}).get("executionStatus") or "not-run")}</li>',
            '<li>Exact-scope write approval: Not recorded. A recorded target or cached auth does not authorize any write.</li>',
        ]
        consent_value = consent.get("status")
        if isinstance(consent_value, str) and consent_value.casefold().replace("_", "-") not in {
            "not-recorded", "unknown", "unrecorded", "not-checked",
        }:
            details.insert(
                5,
                f'<li>Advance planning consent: {_text(consent_value)} · hash: '
                f'<code>{_text(consent.get("planSha256") or "Not recorded")}</code></li>',
            )
        if setup_target:
            details.extend(
                f'<li>{_text(key)}: {_text(value)}</li>'
                for key, value in setup_target.items()
            )
        if isinstance(auth.get("checkedAt"), str):
            details.append(
                f'<li>Last recorded scoped preflight: {_text(auth["checkedAt"])}; '
                'this is later-stage evidence, not an initial setup pass.</li>'
            )
        notes = setup.get("notes") if isinstance(setup.get("notes"), list) else []
        details.extend(f'<li>{_safe_flow_message(note)}</li>' for note in notes if isinstance(note, str))
        rule_proof = (
            '<h4>Persisted setup/configuration facts</h4><ul>'
            + "".join(details)
            + '</ul><p class="muted">The .env target keys are configuration only; they do not prove Graph/ARM authentication, scoped read access, management permission, effective RBAC, or deployment approval. The report does not run doctor, authenticate, or make provider/network calls. Runtime-query consent status may inspect only local cached-account selection to detect stale authentication bindings.</p>'
            + ('<p>Qualification still requires a fresh read-only preflight immediately before each deployment phase.</p>' if setup.get("profile") == "qualification" else "")
        )
    elif stage_name in {"discovery", "conversion"}:
        entries = []
        for index, rule in enumerate(rules):
            if not isinstance(rule, dict):
                continue
            custom = rule.get("customDetection") if isinstance(rule.get("customDetection"), dict) else {}
            findings = []
            if stage_name == "conversion":
                findings.extend(str(item) for item in custom.get("reviewReasons") or [])
                findings.extend(
                    str(item.get("message") or item.get("stage") or "Recorded conversion error")
                    for item in rule.get("errors") or [] if isinstance(item, dict)
                )
                status = custom.get("conversionStatus") or "not recorded"
                text = f'Conversion: {_text(status)}'
                if findings:
                    text += " · " + _text("; ".join(findings))
            else:
                text = (
                    f'Source file: {_text(Path(str(rule.get("sourceFile") or "")).name or "Not recorded")} · '
                    f'Conversion: {_text(custom.get("conversionStatus") or "not recorded")}'
                )
            entries.append(f'<li>{_flow_rule_detail_link(index, rule.get("name"))} — {text}</li>')
        if entries:
            rule_proof = '<details><summary>Rule-level evidence</summary><ul>' + "".join(entries) + "</ul></details>"
        elif stage_name == "discovery":
            rule_proof = '<p class="muted">No source-rule inventory is recorded in this report.</p>'
    elif stage_name == "validation":
        entries = []
        for index, rule in enumerate(rules):
            if not isinstance(rule, dict):
                continue
            custom = rule.get("customDetection") if isinstance(rule.get("customDetection"), dict) else {}
            analytic = rule.get("analyticRule") if isinstance(rule.get("analyticRule"), dict) else {}
            results = [
                f'Local structure: {_status_label(custom.get("structuralStatus"))}'
            ]
            for side_name, side in (("Source query", analytic), ("Converted query", custom)):
                for runtime in side.get("runtime") or []:
                    row_count = runtime.get("rowCount")
                    rows_text = f'{_text(row_count)} rows' if row_count is not None else "row count unavailable"
                    results.append(
                        f'{side_name} ({_text(runtime.get("provider") or "provider unavailable")}): '
                        f'{_status_label(runtime.get("status"))}, {rows_text}'
                    )
            entries.append(
                f'<li>{_flow_rule_detail_link(index, rule.get("name"))} — {_text("; ".join(results))}</li>'
            )
        rule_proof = (
            '<details><summary>Structural and query-provider results</summary><ul>' + "".join(entries) + "</ul></details>"
            if entries else '<p class="muted">No per-rule structural or query-provider results are recorded.</p>'
        )
    elif stage_name in {"deployment", "mockIngestion", "alertParity"}:
        if stage_name == "deployment":
            entries = []
            for index, rule in enumerate(rules):
                if not isinstance(rule, dict):
                    continue
                custom = rule.get("customDetection") if isinstance(rule.get("customDetection"), dict) else {}
                analytic = rule.get("analyticRule") if isinstance(rule.get("analyticRule"), dict) else {}
                entries.append(
                    f'<li>{_flow_rule_detail_link(index, rule.get("name"))} — '
                    f'Source: {_status_label(analytic.get("deploymentStatus"))}; '
                    f'XDR: {_status_label(custom.get("deploymentStatus"))}</li>'
                )
        elif stage_name == "alertParity":
            entries = []
            for index, rule in enumerate(rules):
                if isinstance(rule, dict):
                    custom = rule.get("customDetection") if isinstance(rule.get("customDetection"), dict) else {}
                    entries.append(
                        f'<li>{_flow_rule_detail_link(index, rule.get("name"))} — '
                        f'Strict alert parity: {_status_label(custom.get("alertStatus"))}</li>'
                    )
        else:
            entries = []
        if entries:
            rule_proof = '<details><summary>Recorded per-rule outcomes</summary><ul>' + "".join(entries) + "</ul></details>"
        elif stage_name == "mockIngestion":
            ingestion = report.get("ingestion")
            record_count = len(ingestion) if isinstance(ingestion, list) else 0
            rule_proof = (
                f'<p>{record_count} ingestion report(s) were included in this snapshot.</p>'
                if record_count else '<p class="muted">No ingestion reports are recorded in this snapshot.</p>'
            )
    elif stage_name == "preflight":
        auth = preflight.get("authentication") if isinstance(preflight.get("authentication"), dict) else {}
        permissions = preflight.get("permissions") if isinstance(preflight.get("permissions"), dict) else {}
        read_checks = preflight.get("readChecks") if isinstance(preflight.get("readChecks"), list) else []
        dcr = preflight.get("dcr") if isinstance(preflight.get("dcr"), dict) else {}
        checks = []
        for field, label in (
            ("status", "Overall Graph preflight"),
            ("method", "Selected cached-auth method"),
            ("selectedMethod", "Selected cached-auth method"),
            ("requestedScope", "Requested scope"),
            ("tenantMatch", "Tenant match"),
            ("graphAudience", "Graph audience"),
        ):
            if auth.get(field) is not None:
                checks.append(f'<li>{label}: {_text(auth[field])}</li>')
        for field, label in (
            ("readAccess", "Read access"),
            ("writeScopeInToken", "Write scope in token"),
            ("consent", "Consent"),
            ("writeAuthorization", "Write authorization"),
        ):
            if permissions.get(field) is not None:
                checks.append(f'<li>{label}: {_text(permissions[field])}</li>')
        grant = preflight.get("managementPermissionGrant")
        grant = grant if isinstance(grant, dict) else {}
        required_permission = preflight.get("requiredManagementPermission")
        if required_permission:
            checks.append(f'<li>Required management permission: {_text(required_permission)}</li>')
        if grant:
            checks.append(
                f'<li>Required write-grant status: {_text(grant.get("status"))}; '
                f'grant type: {_text(grant.get("grantType"))}; claim type: {_text(grant.get("claimType"))}</li>'
            )
            checks.append(
                f'<li>Grant evidence permission: {_text(grant.get("permission"))}; '
                f'credential request scope: {_text(grant.get("credentialRequestScope"))}</li>'
            )
            if grant.get("reason"):
                checks.append(f'<li>Grant assessment: {_safe_flow_message(grant["reason"])}</li>')
        if preflight.get("deploymentReadiness") is not None:
            checks.append(f'<li>Deployment readiness assessment: {_text(preflight.get("deploymentReadiness"))}</li>')
        checks.append(f'<li>Effective management role: {_text(preflight.get("effectiveRoleStatus"))}</li>')
        claims = preflight.get("tokenPermissionClaims")
        claims = claims if isinstance(claims, dict) else {}
        if claims:
            checks.append(
                f'<li>Token permission-claim inspection: {_text(claims.get("status"))}; '
                f'claim type: {_text(claims.get("claimType"))}</li>'
            )
        if read_checks:
            checks.append(
                '<li>Exact-rule GET checks: '
                + "; ".join(
                    _text(" · ".join(
                        str(check[key]) for key in ("status", "httpStatus") if check.get(key) is not None
                    )) for check in read_checks if isinstance(check, dict)
                )
                + '</li>'
            )
        if dcr:
            checks.extend([
                f'<li>DCR preflight: {_text(dcr.get("status"))}; authentication: {_text(dcr.get("authenticationStatus"))}</li>',
                f'<li>Locked-target verification: {_text(dcr.get("targetVerificationStatus"))}; local contract readiness: {_text(dcr.get("localReadinessStatus"))}</li>',
                f'<li>Workspace query permission: {_text(dcr.get("workspaceQueryPermissionStatus"))}; contracts recorded: {_text(dcr.get("contractCount"))}</li>',
            ])
        if not checks:
            rule_proof = '<p class="muted">No persisted Graph authentication, scope, GET, DCR, or workspace-query preflight details are available.</p>'
        else:
            checks.extend([
                '<li>Required CustomDetection.ReadWrite.All grant is distinct from read grant, successful GET, effective RBAC, and write authorization.</li>',
                '<li>Preflight is diagnostic only; it does not prove effective write authorization or approve a write.</li>',
                '<li>Query-permission preflight is not semantic query parity, telemetry ingestion, or alert parity.</li>',
            ])
            rule_proof = '<h4>Recorded read-only checks</h4><ul>' + "".join(checks) + "</ul>"
    elif stage_name == "packageAcceptance":
        plan = package_value.get("plan") if isinstance(package_value.get("plan"), dict) else {}
        plan_types = plan.get("resourceTypes") if isinstance(plan.get("resourceTypes"), list) else []
        plan_identity = plan.get("packageIdentity") if isinstance(plan.get("packageIdentity"), dict) else {}
        type_list = (
            '<ul>' + "".join(f'<li><code>{_text(item)}</code></li>' for item in plan_types) + '</ul>'
            if plan_types else '<p class="muted">No recorded package-acceptance resource list.</p>'
        )
        identity_text = " · ".join(
            f'{_text(key)}: {_text(value)}' for key, value in plan_identity.items()
        ) or "Package identity not recorded in acceptance plan."
        rule_proof = (
            f'<p><strong>Recorded proposal status:</strong> {_text(plan.get("status"))}</p>'
            f'<p><strong>Proposal package identity:</strong> {identity_text}</p>'
            f'<p><strong>Proposal execution status:</strong> {_text(plan.get("executionStatus"))}</p>'
            f'<p><strong>Proposal approval status:</strong> {_text(plan.get("approvalStatus"))}</p>'
            + type_list
            + '<p>Proposal/planning metadata is not final exact-scope approval, execution, or package acceptance evidence.</p>'
        )
    elif stage_name == "validationSuite":
        canonical_status = suite_value.get("canonicalStatus")
        rule_proof = (
            f'<p>Recorded canonical structural/query Validation status: {_text(canonical_status)}</p>'
            '<p>A prior structural or source-query pass does not prove the current full official local validation rerun.</p>'
        )
    elif stage_name == "queryValidation":
        counts = report.get("summary") if isinstance(report.get("summary"), dict) else {}
        rule_proof = (
            f'<p>Recorded query parity passed: {_text(counts.get("queryParityPassed"))} of {_text(counts.get("rules"))} rules.</p>'
            '<p>Missing checks, zero-row results, and query-permission checks are not semantic validation passes.</p>'
        )
    if stage_name == "publication":
        message = '<p class="muted">Publication is external and not tracked. No publication link or completion status is available here.</p>'
        stage_evidence = '<p class="muted">No publication evidence is recorded.</p>'
    if stage_name == "report" and report.get("generatedAt"):
        stage_status = (
            f'<p><strong>Report snapshot:</strong> Generated {_text(report["generatedAt"])}</p>'
            + (f'<p><strong>Recorded report-stage status:</strong> {_text(value["raw"])} · {_text(value["display"])}</p>' if value["raw"] else "")
        )
    return (
        f'<section class="flow-evidence-entry" id="flow-evidence-{escape(stage_name, quote=True)}" '
        f'aria-labelledby="flow-evidence-heading-{escape(stage_name, quote=True)}">'
        f'<h3 id="flow-evidence-heading-{escape(stage_name, quote=True)}">{_text(label)} evidence</h3>'
        + f'<p class="muted">{_text(description)}</p>'
        + stage_status + freshness_status + message + timing + rule_proof
        + '<h4>Evidence artifacts</h4>' + stage_evidence + '</section>'
    )


def _flow_evidence_html(report: dict[str, Any], show_qualification: bool) -> str:
    stages = ["setup", "discovery", "conversion", "validation", "packaging"]
    if show_qualification:
        stages.extend([
            "validationSuite", "preflight", "deployment", "mockIngestion",
            "queryValidation", "alertParity", "packageAcceptance",
        ])
    stages.extend(["report", "publication"])
    return (
        '<section class="panel" aria-labelledby="flow-evidence-heading">'
        '<h2 id="flow-evidence-heading">Migration evidence</h2>'
        '<p class="muted">Each station links here to its recorded evidence. Artifact links are limited to files inside this selected migration run; unavailable or non-portable references are stated without exposing local paths.</p>'
        + "".join(_flow_stage_detail(name, report) for name in stages)
        + '</section>'
    )


def _flow_html(report: dict[str, Any]) -> str:
    workflow = report.get("workflow") if isinstance(report.get("workflow"), dict) else {}
    stages = workflow.get("stages") if isinstance(workflow.get("stages"), dict) else {}
    recorded_profile = workflow.get("profile")
    profile = recorded_profile if isinstance(recorded_profile, str) and recorded_profile in {"authoring", "qualification"} else None
    mode = profile if workflow.get("profileSelectionConfirmed") is True else None
    freshness = workflow.get("packageFreshness")
    values = {
        name: _flow_stage(stage, freshness=freshness if name == "packaging" else None)
        for name, stage in stages.items()
    }
    for name, _ in FLOW_STATIONS:
        values.setdefault(name, _flow_stage(None))
    qualification_evidence = any(
        isinstance(stages.get(name), dict)
        and (
            (
                stages[name].get("status") is not None
                and stages[name].get("status") != "notRequired"
            )
            or (
                stages[name].get("attempts") is not None
                and stages[name].get("attempts") != 0
            )
            or bool(stages[name].get("evidence"))
            or bool(stages[name].get("message"))
        )
        for name in ("deployment", "mockIngestion", "alertParity")
    )
    qualification_evidence = qualification_evidence or any(
        isinstance(rule, dict)
        and isinstance(rule.get("queryParity"), dict)
        and rule["queryParity"].get("status") not in {None, "not-run", "not-recorded"}
        for rule in report.get("rules", [])
    )
    planning = report.get("deploymentPlanning")
    package_acceptance_plan = (
        planning.get("packageAcceptancePlan")
        if isinstance(planning, dict) and isinstance(planning.get("packageAcceptancePlan"), dict)
        else {}
    )
    qualification_evidence = qualification_evidence or package_acceptance_plan.get("recorded") is True
    show_qualification = mode == "qualification" or qualification_evidence
    preflight_evidence = bool(
        (report.get("qualificationPreflight") or {}).get("graphRecorded") is True
        or (report.get("qualificationPreflight") or {}).get("dcrRecorded") is True
    )
    show_qualification = show_qualification or preflight_evidence
    compact = mode == "authoring" and not show_qualification
    setup_value = _setup_station_value(report)
    report_value = _flow_stage(stages.get("report"))
    if report.get("generatedAt"):
        report_value = {
            **report_value,
            "state": "completed" if report_value["raw"] in {"", "passed"} else report_value["state"],
            "display": "Snapshot generated" if report_value["raw"] in {"", "passed"} else report_value["display"],
            "message": report_value["message"] or "This offline JSON/HTML snapshot was generated at the timestamp shown above.",
            "updated": report_value["updated"] or str(report["generatedAt"]),
        }
    coordinates = (
        {"setup": 70, "discovery": 250, "conversion": 430, "validation": 610, "packaging": 790, "report": 980, "publication": 1120}
        if compact else
        {"setup": 80, "discovery": 260, "conversion": 440, "validation": 620, "packaging": 800, "report": 1880, "publication": 2040}
    )
    y = 92 if compact else 105
    station_specs = [
        ("setup", "Necessary setup / initial preflight", ("Necessary setup", "initial preflight"), coordinates["setup"], setup_value),
        ("discovery", "Discovery", ("Discovery",), coordinates["discovery"], values["discovery"]),
        ("conversion", "Conversion", ("Conversion",), coordinates["conversion"], values["conversion"]),
        ("validation", "Validation", ("Validation",), coordinates["validation"], values["validation"]),
        ("packaging", "Packaging", ("Packaging",), coordinates["packaging"], values["packaging"]),
    ]
    if show_qualification:
        station_specs.extend([
            ("validationSuite", "Official validation rerun", ("Official", "validation rerun"), 930, _validation_suite_value(report)),
            ("preflight", "Just-in-time preflight", ("Fresh", "preflight"), 1080, _preflight_station_value(
                report.get("qualificationPreflight")
                if isinstance(report.get("qualificationPreflight"), dict) else {}
            )),
            ("deployment", "Direct AR/CD pair deployment", ("Direct AR/CD", "pair deployment"), 1230, values["deployment"]),
            ("mockIngestion", "Mock ingestion", ("Shared mock", "ingestion"), 1380, values["mockIngestion"]),
            ("queryValidation", "Semantic/query validation", ("Semantic/query", "validation"), 1530, _query_validation_value(report)),
            ("alertParity", "Alert parity", ("Alert", "parity"), 1680, values["alertParity"]),
            ("packageAcceptance", "Full package deployment", ("Full package", "deployment"), 1830, _package_acceptance_value(report)),
        ])
    station_specs.extend([
        ("report", "Report", ("Report", "snapshot"), coordinates["report"], report_value),
        ("publication", "External publication (optional)", ("External", "publish (optional)"), coordinates["publication"], {
            "state": "unknown", "display": "Not tracked", "raw": "", "freshness": "",
            "freshnessReason": "",
            "message": "Optional publication is external to the canonical workflow and has no recorded status here. A package artifact does not prove publication.",
            "evidence": [], "updated": "", "timing": "", "attempts": "",
        }),
    ])
    lines = [
        _flow_station(
            key, title, title_lines, x,
            288 if key in {
                "validationSuite", "preflight", "deployment", "mockIngestion",
                "queryValidation", "alertParity", "packageAcceptance",
            } else y,
            value,
            branch=key in {
                "validationSuite", "preflight", "deployment", "mockIngestion",
                "queryValidation", "alertParity", "packageAcceptance",
            },
            compact=compact,
        )
        for key, title, title_lines, x, value in station_specs
    ]
    route_authoring = "active" if mode == "authoring" else ""
    route_qualification = "active" if mode == "qualification" else ""
    branch_label = (
        "Lab qualification selected"
        if mode == "qualification"
        else "Lab evidence recorded · authoring"
        if mode == "authoring"
        else "Lab evidence present · mode unknown"
    )
    if mode == "qualification":
        mode_label = "Qualification · lab validation"
        mode_note = "The selected qualification route follows Packaging, then rejoins at Report. Mandatory structural validation remains on the main route."
    elif compact:
        mode_label = "Authoring · no lab qualification"
        mode_note = "Lab qualification was not selected. The optional branch is omitted; mandatory structural validation and packaging remain on this route."
    elif mode == "authoring":
        mode_label = "Authoring · qualification evidence recorded"
        mode_note = "The authoring profile is recorded, and existing lab-stage evidence remains visible rather than being hidden."
    elif show_qualification:
        mode_label = "Mode not recorded · qualification evidence present"
        mode_note = "The selected mode is unavailable in this legacy report. Qualification-stage evidence is shown without inferring profile selection."
    else:
        mode_label = "Mode not recorded"
        mode_note = "The selected mode is unavailable. No authoring or qualification profile is inferred; statuses remain unknown unless recorded."
    workflow_status = workflow.get("status") if isinstance(workflow.get("status"), str) else None
    overall_status = _status_label(workflow_status) if workflow_status else "Evidence unavailable"
    description = (
        "Necessary setup and initial preflight, discovery, conversion, mandatory validation, packaging and report, followed by optional external publication."
        if compact else
        "Necessary setup and initial preflight, discovery, conversion, mandatory validation and V3.1 packaging continue to Report. The optional qualification branch illustrates a separate local validation rerun, a fresh read-only preflight, direct AR/CD pairs, fixture ingestion and semantic checks, alert parity, then separately approved full-package deployment before Report. These display-only planned steps do not alter the canonical workflow."
    )
    svg_viewbox = "0 0 1160 245" if compact else "0 0 2110 420"
    route_markup = (
        f'<path class="route route-prefix active" d="M{coordinates["setup"]} {y} H{coordinates["packaging"]}"/>'
        f'<path class="route route-authoring {_text(route_authoring)}" d="M{coordinates["packaging"]} {y} H{coordinates["report"]}"/>'
        f'<path class="route route-external" d="M{coordinates["report"] + 21} {y} H{coordinates["publication"] - 21}"/>'
    )
    if show_qualification:
        route_markup += (
            f'<path class="route route-qualification {_text(route_qualification)}" d="M800 126 V267 H1830"/>'
            f'<path class="route route-qualification {_text(route_qualification)}" d="M1830 267 C1850 220 1865 158 1880 126"/>'
        )
    return (
        '<section class="panel subway-panel" aria-labelledby="flow-heading">'
        f'<h2 id="flow-heading">Migration flow <span class="flow-mode">{_text(mode_label)}</span></h2>'
        f'<p><strong>Recorded workflow status:</strong> {_text(overall_status)}</p>'
        '<p class="muted">A snapshot of recorded workflow state, generated at the timestamp above; this diagram does not poll or change stages. Each clickable station opens its stage-specific evidence below.</p>'
        f'<p class="muted">{_text(mode_note)}</p>'
        '<div class="flow-scroll" role="region" aria-label="Scrollable migration flow diagram" tabindex="0">'
        f'<svg class="subway{" compact" if compact else " qualification" if show_qualification else ""}" viewBox="{svg_viewbox}" role="group" aria-labelledby="flow-svg-title flow-svg-desc">'
        '<title id="flow-svg-title">Migration workflow subway schematic</title>'
        f'<desc id="flow-svg-desc">{escape(description)}</desc>'
        + route_markup
        + (f'<text class="route-label" x="{(coordinates["packaging"] + coordinates["report"]) // 2}" y="{y - 24}">Authoring route</text>' if compact else "")
        + (f'<text class="branch-heading" x="810" y="225">{escape(branch_label)}</text>' if show_qualification else "")
        + "".join(lines)
        + '</svg></div>'
        '<p class="muted">Tab moves between stations; press Enter to open that station’s recorded evidence. Underlined labels, hover and focus cues identify links. Status words and symbols supplement color.</p>'
        '<ul class="flow-legend" aria-label="Station status legend">'
        '<li><span class="flow-key completed" aria-hidden="true"></span>Completed / snapshot</li>'
        '<li><span class="flow-key running" aria-hidden="true"></span>In progress</li>'
        '<li><span class="flow-key blocked" aria-hidden="true"></span>Blocked or failed</li>'
        '<li><span class="flow-key stale" aria-hidden="true"></span>Stale</li>'
        '<li><span class="flow-key pending" aria-hidden="true"></span>Pending</li>'
        '<li><span class="flow-key not-required" aria-hidden="true"></span>Not required</li>'
        '<li><span class="flow-key unknown" aria-hidden="true"></span>Unknown / not tracked</li>'
        '</ul>'
        '</section>'
        + _flow_evidence_html(report, show_qualification)
    )


def _deployment_planning_html(report: dict[str, Any]) -> str:
    plan = report.get("deploymentPlanning")
    plan = plan if isinstance(plan, dict) else {}
    contract = plan.get("deploymentPlan")
    contract = contract if isinstance(contract, dict) else {}
    profile = plan.get("profile")
    selected_profile = contract.get("selectedProfile")
    profile_label = selected_profile if isinstance(selected_profile, str) else {
        "authoring": "Authoring",
        "qualification": "Qualification",
        "unknown": "Mode not recorded",
    }.get(profile, "Mode not recorded")
    inventory = contract.get("packageResourceInventory")
    if not isinstance(inventory, list) or not inventory:
        inventory = plan.get("resourceInventory")
    rows = []
    if isinstance(inventory, list):
        for item in inventory:
            if not isinstance(item, dict):
                continue
            if not any(
                item.get(name) not in (None, "", [], {})
                for name in ("type", "typeAtVersion", "apiVersion", "count", "sourceForms", "extensionResource")
            ):
                continue
            forms = item.get("sourceForms")
            form_text = ", ".join(str(value) for value in forms) if isinstance(forms, list) else "not recorded"
            resource_type = item.get("type") or item.get("typeAtVersion") or "Not recorded"
            api_version = item.get("apiVersion")
            if not api_version and isinstance(item.get("typeAtVersion"), str) and "@" in item["typeAtVersion"]:
                resource_type, api_version = item["typeAtVersion"].rsplit("@", 1)
            extension = "Yes" if item.get("extensionResource") is True else "No / not recorded"
            rows.append(
                "<tr>"
                f'<td><code>{_text(resource_type)}</code></td>'
                f'<td>{_text(api_version or "Not recorded")}</td>'
                f'<td>{_text(item.get("count"))}</td>'
                f'<td>{_text(form_text)}</td>'
                f'<td>{extension}</td>'
                "</tr>"
            )
    inventory_markup = (
        '<section class="planning-card planning-inventory" aria-labelledby="package-resource-inventory">'
        '<h3 id="package-resource-inventory">Package resource inventory</h3>'
        '<p class="muted">Candidate package contents are inventory, not a selected or approved deployment scope. Resource type/API columns retain readable widths; scroll this table horizontally on narrow screens.</p>'
        '<div class="planning-table-scroll" role="region" aria-label="Horizontally scrollable package resource inventory" tabindex="0">'
        '<table class="resource-inventory"><thead><tr><th scope="col">Resource type</th><th scope="col">API version</th><th scope="col">Count</th><th scope="col">Source form</th><th scope="col">Extension</th></tr></thead><tbody>'
        + "".join(rows)
        + '</tbody></table></div></section>'
        if rows else ""
    )
    defaults = plan.get("deploymentDefaults")
    if isinstance(defaults, list):
        default_lines = [
            f'<li>{_safe_flow_message(item.get("name"))}: {_text(item.get("value"))}</li>'
            for item in defaults
            if isinstance(item, dict) and isinstance(item.get("value"), bool)
        ]
    else:
        default_lines = []
    template_hash = plan.get("templateSha256")
    recorded_hash = plan.get("recordedTemplateSha256")
    package_hash = plan.get("packageArtifactsSha256")
    input_hash = plan.get("packageInputSha256")
    hash_markup = (
        f'<p>Current template SHA-256: <code>{_text(template_hash)}</code></p>'
        if isinstance(template_hash, str) and re.fullmatch(r"[0-9a-fA-F]{64}", template_hash)
        else '<p>Current template SHA-256: unavailable.</p>'
    )
    if isinstance(recorded_hash, str) and re.fullmatch(r"[0-9a-fA-F]{64}", recorded_hash):
        hash_markup += f'<p>Package-recorded template SHA-256: <code>{_text(recorded_hash)}</code></p>'
    if isinstance(package_hash, str) and re.fullmatch(r"[0-9a-fA-F]{64}", package_hash):
        hash_markup += f'<p>Package artifacts SHA-256: <code>{_text(package_hash)}</code></p>'
    if isinstance(input_hash, str) and re.fullmatch(r"[0-9a-fA-F]{64}", input_hash):
        hash_markup += f'<p>Package input identity SHA-256: <code>{_text(input_hash)}</code></p>'
    freshness = plan.get("packageFreshness")
    identity = plan.get("packageIdentity")
    startup = report.get("startupSetup")
    startup = startup if isinstance(startup, dict) else {}
    target = (
        contract.get("target")
        if isinstance(contract.get("target"), dict) and contract.get("target")
        else startup.get("target")
    )
    target = target if isinstance(target, dict) else {}
    target_source = (
        "Hash-bound plan target"
        if contract.get("target")
        else startup.get("targetSource") or "Not recorded"
    )
    target_html = (
        f'<p class="muted">{_text(target_source)} · '
        f'{"locked" if startup.get("targetLocked") or contract.get("target") else "lock not recorded"}</p>'
        + "<dl class=\"target-data\">" + "".join(
            f'<div><dt>{_text(key)}</dt><dd>{_text(value)}</dd></div>'
            for key, value in target.items()
        ) + "</dl>"
        if target else '<p class="muted">No target is recorded in this run; a formal deployment plan is also not recorded.</p>'
    )
    source_inventory = contract.get("sourceInventory")
    source_inventory_html = (
        "<ul>" + "".join(
            f'<li>{_text(key)}: {_text(value)}</li>'
            for key, value in source_inventory.items()
        ) + "</ul>"
        if isinstance(source_inventory, dict) and source_inventory
        else (
            f'<p class="muted">No plan-bound source inventory recorded. This report includes '
            f'{_text(len(report.get("rules", [])))} source rule(s); this count is not an approved deployment scope.</p>'
        )
    )
    detection_scope = contract.get("detectionScope")
    detection_scope_items = (
        [
            f'{_text(key)}: {_text(value)}'
            for key, value in detection_scope.items()
        ]
        if isinstance(detection_scope, dict)
        else []
    )
    id_lists = []
    if isinstance(detection_scope, dict):
        for key in (
            "currentReviewedDraftIds", "eligibleAdditionalRuleIds",
            "excludedRuleIds", "ineligibleRuleIds", "duplicateSourceRuleIds",
        ):
            values = detection_scope.get(key)
            if isinstance(values, list) and values:
                id_lists.append(
                    f'<details><summary>{_text(key)} ({len(values)})</summary><ul>'
                    + "".join(f'<li><code>{_text(value)}</code></li>' for value in values if isinstance(value, str))
                    + '</ul></details>'
                )
    eligible_ids_html = "".join(id_lists)
    caps = contract.get("scopeCaps")
    cap_html = (
        "<dl class=\"compact-data\">" + "".join(
            f'<div><dt>{_text(key)}</dt><dd>{_text(value)}</dd></div>' for key, value in caps.items()
        ) + "</dl>"
        if isinstance(caps, dict) and caps
        else ""
    )
    consent = contract.get("planningConsent")
    consent = consent if isinstance(consent, dict) else {}
    consent_status = consent.get("status") if isinstance(consent.get("status"), str) else "not-recorded"
    consent_recorded = consent_status.casefold().replace("_", "-") not in {
        "not-recorded", "not-recorded-or-unknown", "unknown", "unrecorded", "not-checked",
    }
    consent_status_label = "Not recorded" if consent_status == "not-recorded" else consent_status
    consent_keys = consent.get("componentKeys") if isinstance(consent.get("componentKeys"), list) else []
    consent_types = consent.get("resourceTypes") if isinstance(consent.get("resourceTypes"), list) else []
    consent_flags = consent.get("selectedFlags") if isinstance(consent.get("selectedFlags"), dict) else {}
    consent_max_additional = consent.get("maxAdditionalCustomDetections")
    component_markup = []
    components = contract.get("components")
    if isinstance(components, dict):
        for key, component in components.items():
            if not isinstance(component, dict):
                continue
            has_component_evidence = any(
                value is not None
                and value not in ("", [], {})
                and not (
                    name in {"status", "planningConsent"}
                    and isinstance(value, str)
                    and value.casefold().replace("_", "-") in {
                        "not-recorded", "unknown", "unrecorded", "not-checked",
                    }
                )
                for name, value in component.items()
            )
            if not has_component_evidence:
                continue
            non_consentable = (
                component.get("consentable") is False
                or key in {"controlledAlertParity", "ownedResourceCleanup"}
            )
            resource_types = component.get("resourceTypes")
            types_html = (
                "<ul class=\"component-types\">" + "".join(f'<li><code>{_text(item)}</code></li>' for item in resource_types) + "</ul>"
                if isinstance(resource_types, list) and resource_types else ""
            )
            selected_flags = component.get("selectedFlags")
            flags_html = (
                "<ul>" + "".join(f'<li>{_text(name)}: {_text(value)}</li>' for name, value in selected_flags.items()) + "</ul>"
                if isinstance(selected_flags, dict) and selected_flags
                else '<p class="muted">Selected flags not recorded.</p>'
            )
            component_status = component.get("planningConsent")
            component_status = component_status if isinstance(component_status, str) else "not-recorded"
            component_fields = {
                name: value for name, value in component.items()
                if name not in {"resourceTypes", "planningConsent"}
            }
            component_plan_status = component.get("status") or "not-recorded"
            component_reason = component.get("reason")
            if non_consentable:
                status_markup = (
                    f'<p><strong>Coverage status:</strong> {_text(component_plan_status)} · '
                    'not consentable and not deployment approval.</p>'
                    '<p><strong>Advance consent support:</strong> No.</p>'
                )
            elif component_status.casefold().replace("_", "-") in {
                "not-recorded", "unknown", "unrecorded", "not-checked",
            }:
                status_markup = (
                    f'<p><strong>Plan status:</strong> {_text(component_plan_status)}</p>'
                )
            else:
                status_markup = (
                    f'<p><strong>Plan status:</strong> {_text(component_plan_status)} · '
                    f'<strong>Advance consent:</strong> {_text(component_status)}</p>'
                )
            coverage_fields = (
                (
                    "eligiblePairRuleIds", "maximumRulePairCount",
                    "maximumEnableWriteRequests", "maximumRestoreWriteRequests",
                    "maximumWriteRequestsForOneBoundedRun", "timeWindow",
                    "restoreDisabledAfterRun", "abortOnRestoreFailure",
                    "repeatedRunsAllowed", "maximumRepeatedRuns",
                    "deleteCap", "maximumDeleteResourceCount",
                    "resources", "resourceIds", "resourceTypes", "ownershipEvidence",
                    "existingResourceDeletionAllowed", "unownedResourceDeletionAllowed",
                )
                if non_consentable else ()
            )
            if non_consentable:
                coverage_fields += tuple(
                    name for name in component
                    if isinstance(name, str)
                    and any(token in name.casefold() for token in ("restore", "abort", "repeat"))
                    and name not in coverage_fields
                )
            coverage_summary_items = []
            for name in coverage_fields:
                if name not in component:
                    continue
                value = component[name]
                if name in {"eligiblePairRuleIds", "resources", "resourceTypes"} and isinstance(value, list):
                    rendered_value = f"{len(value)} recorded" + (
                        ": " + ", ".join(str(item) for item in value)
                        if name == "eligiblePairRuleIds" and value else ""
                    )
                else:
                    rendered_value = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
                coverage_summary_items.append(
                    f'<li><strong>{_text(name)}:</strong> {_text(rendered_value)}</li>'
                )
            coverage_summary = (
                '<ul class="component-coverage-summary">'
                + "".join(coverage_summary_items) + '</ul>'
                if coverage_summary_items else ""
            )
            component_markup.append(
                f'<section class="planning-card"><h4>{_text(key)}</h4>'
                + status_markup
                + (f'<p><strong>Recorded reason:</strong> {_safe_flow_message(component_reason)}</p>' if isinstance(component_reason, str) and component_reason else "")
                + coverage_summary
                + types_html
                + (flags_html if selected_flags else "")
                + (f'<details><summary>Recorded component evidence</summary><pre>{_text(json.dumps(component_fields, indent=2, sort_keys=True))}</pre></details>' if component_fields else "")
                + '</section>'
            )
    plan_fingerprint = contract.get("planSha256")
    plan_fingerprint_html = (
        f'<p>Plan SHA-256: <code>{_text(plan_fingerprint)}</code></p>'
        if isinstance(plan_fingerprint, str) and re.fullmatch(r"[0-9a-fA-F]{64}", plan_fingerprint)
        else '<p>Plan fingerprint: unavailable.</p>'
    )
    contract_artifact_hashes = contract.get("packageArtifactHashes")
    if isinstance(contract_artifact_hashes, dict):
        plan_fingerprint_html += "".join(
            f'<p>Planned { _text(name) } SHA-256: <code>{_text(value)}</code></p>'
            for name, value in contract_artifact_hashes.items()
            if isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value)
        )
    dcr_resolver = contract.get("dcrResolver")
    dcr_resolver_html = (
        "<ul>" + "".join(f'<li>{_text(key)}: {_text(value)}</li>' for key, value in dcr_resolver.items()) + "</ul>"
        if isinstance(dcr_resolver, dict) and dcr_resolver
        else '<p class="muted">DCR resolver restrictions not recorded.</p>'
    )
    package_acceptance = contract.get("packageAcceptancePlan")
    if not isinstance(package_acceptance, dict) or not package_acceptance:
        package_acceptance = plan.get("packageAcceptancePlan")
    package_acceptance = package_acceptance if isinstance(package_acceptance, dict) else {}
    package_input_hash = contract.get("packageInputSha256")
    if isinstance(package_input_hash, str) and re.fullmatch(r"[0-9a-fA-F]{64}", package_input_hash):
        plan_fingerprint_html += f'<p>Package input SHA-256: <code>{_text(package_input_hash)}</code></p>'
    recorded_artifact_hashes = contract.get("recordedPackageArtifactHashes")
    if isinstance(recorded_artifact_hashes, dict):
        plan_fingerprint_html += "".join(
            f'<p>Recorded { _text(name) } SHA-256: <code>{_text(value)}</code></p>'
            for name, value in recorded_artifact_hashes.items()
            if isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value)
        )
    dcr_evidence = contract.get("dcrEvidence") if isinstance(contract.get("dcrEvidence"), dict) else {}
    dcr_resolver = contract.get("dcrResolver") if isinstance(contract.get("dcrResolver"), dict) else {}
    workflow = report.get("workflow") if isinstance(report.get("workflow"), dict) else {}
    workflow_stages = workflow.get("stages") if isinstance(workflow.get("stages"), dict) else {}
    validation_stage = workflow_stages.get("validationSuite")
    validation_stage = validation_stage if isinstance(validation_stage, dict) else {}
    deployment_stage = workflow_stages.get("deployment")
    deployment_stage = deployment_stage if isinstance(deployment_stage, dict) else {}
    validation_summary = _validation_suite_value(report)
    package_acceptance_summary = package_acceptance
    target_json = _text(json.dumps(target, sort_keys=True, indent=2)) if target else ""
    source_json = _text(json.dumps(source_inventory, sort_keys=True, indent=2)) if isinstance(source_inventory, dict) and source_inventory else ""
    detection_json = _text(json.dumps(detection_scope, sort_keys=True, indent=2)) if isinstance(detection_scope, dict) and detection_scope else ""
    component_consent_note = (
        "Advance consent applies only to the listed persisted component scope."
        if consent_status == "approved" and consent_keys
        else "No approved component scope is recorded; conditional resource plans are not consent."
    )
    current_package_status = plan.get("packageIdentity")
    current_package_status = (
        current_package_status.get("status")
        if isinstance(current_package_status, dict)
        else plan.get("packageIdentity")
    )
    version = plan.get("packageVersion") or (
        current_package_status.get("version")
        if isinstance(current_package_status, dict)
        else None
    )
    if not version:
        version = "Not recorded"
    deployment_message = deployment_stage.get("message")
    deployment_summary = (
        f'<p><strong>Current deployment blocker:</strong> {_safe_flow_message(deployment_message)}</p>'
        if deployment_stage.get("status") in {"blocked", "failed"} and deployment_message
        else ""
    )
    consent_blocked_stage = next(
        (
            name for name, stage in workflow_stages.items()
            if isinstance(stage, dict)
            and stage.get("status") in {"blocked", "failed"}
            and isinstance(stage.get("message"), str)
            and "consent" in stage["message"].casefold()
        ),
        None,
    )
    target_summary = (
        target.get("workspaceName")
        or target.get("workspaceResourceId")
        or target.get("resourceGroup")
        or "Not recorded"
    )
    if profile_label == "qualification" and contract.get("executionMode") == "pairs":
        route_summary = "Qualification · direct AR/CD pairs first"
    elif profile_label == "qualification" and contract.get("executionMode") == "package":
        route_summary = "Qualification · full-package acceptance selected"
    elif profile_label == "qualification" and contract.get("executionMode") == "both":
        route_summary = "Qualification · selected components"
    else:
        route_summary = f'{profile_label} · {contract.get("executionMode") or "selection not recorded"}'
    target_fallback_text = (
        "Recorded run target; not bound to a formal deployment plan."
        if target and not contract.get("target")
        else "Target is hash-bound to the persisted plan."
        if target and contract.get("target")
        else "Target details are not available in this selected run."
    )
    consent_scope_text = (
        " · ".join(_text(value) for value in consent_keys)
        if consent_keys
        else "No approved component scope recorded"
    )
    if consent_status != "approved":
        consent_scope_text = "No approved component scope recorded"
    consent_summary = (
        f'<div class="planning-summary-card"><strong>Advance planning consent</strong>'
        f'<span>{_text(consent_status_label)} · {_text(consent_scope_text)}</span></div>'
        if consent_recorded
        else (
            '<div class="planning-summary-card"><strong>Advance planning consent</strong>'
            f'<span>Not recorded · blocking at {_text(consent_blocked_stage)} stage</span></div>'
            if consent_blocked_stage else ""
        )
    )
    inventory_status = (
        "Plan-bound source inventory recorded"
        if isinstance(source_inventory, dict) and source_inventory
        else f'{len(report.get("rules", []))} source rule(s) in this report only'
    )
    hash_details = (
        f'<details class="planning-details"><summary>Package hashes and plan provenance</summary>'
        + hash_markup + plan_fingerprint_html
        + (
            f'<p>Current package input SHA-256: <code>{_text(plan.get("currentPackageInputSha256"))}</code></p>'
            if isinstance(plan.get("currentPackageInputSha256"), str)
            and re.fullmatch(r"[0-9a-fA-F]{64}", plan["currentPackageInputSha256"])
            else '<p>Current package input identity: unavailable.</p>'
        )
        + (f'<p>Package content SHA-256: <code>{_text(contract.get("packageContentSha256"))}</code></p>' if contract.get("packageContentSha256") else "")
        + (f'<p>Source inventory SHA-256: <code>{_text(contract.get("sourceInventorySha256"))}</code></p>' if contract.get("sourceInventorySha256") else "")
        + '</details>'
    )
    package_default_details = (
        f'<details class="planning-details"><summary>Recorded package defaults ({len(default_lines)})</summary>'
        + (f'<ul>{"".join(default_lines)}</ul>' if default_lines else '<p class="muted">No package defaults recorded.</p>')
        + '</details>'
    )
    scope_details = (
        f'<details class="planning-details"><summary>Detailed source/scope inventory</summary>'
        + (f'<pre>{source_json}</pre>' if source_json else '<p>No plan-bound source inventory.</p>')
        + (f'<pre>{detection_json}</pre>' if detection_json else '<p>No plan-bound detection scope.</p>')
        + (f'<pre>{_text(json.dumps(caps, sort_keys=True, indent=2))}</pre>' if isinstance(caps, dict) and caps else "")
        + eligible_ids_html
        + '</details>'
    )
    dcr_details = (
        f'<details class="planning-details"><summary>Preflight DCR evidence and resolver limits</summary>'
        + (
            f'<p><strong>Resolver:</strong> {_text(dcr_resolver.get("kind") or "not recorded")} · '
            f'arbitrary solution-owned DCR discovery: {_text(dcr_resolver.get("arbitrarySolutionOwnedDcrDiscovery", "unknown"))}</p>'
            if dcr_resolver else '<p class="muted">DCR resolver restrictions are not recorded.</p>'
        )
        + (f'<pre>{_text(json.dumps(dcr_evidence, sort_keys=True, indent=2))}</pre>' if dcr_evidence else "")
        + (f'<pre>{_text(json.dumps(dcr_resolver, sort_keys=True, indent=2))}</pre>' if dcr_resolver else "")
        + f'<p><strong>Bicep extensibility / what-if:</strong> {_text(contract.get("whatIfSupport") or "not-evaluated")}</p>'
        + '</details>'
    )
    package_acceptance_details = (
        f'<details class="planning-details"><summary>Full-package acceptance proposal</summary>'
        + (f'<pre>{_text(json.dumps(package_acceptance_summary, sort_keys=True, indent=2))}</pre>' if package_acceptance_summary else '<p class="muted">No package acceptance plan recorded.</p>')
        + '<p>V3.1 package creation is separate from later full-package deployment. AR/CD pair results do not establish package acceptance.</p>'
        + '</details>'
    )
    return (
        '<section class="panel" id="deployment-planning" aria-labelledby="deployment-planning-heading">'
        '<h2 id="deployment-planning-heading">Deployment scope and approval status '
        '<span class="flow-mode">Informational snapshot · no write authorization</span></h2>'
        '<div class="planning-summary-grid">'
        f'<div class="planning-summary-card"><strong>Profile / route</strong><span>{_text(route_summary)}</span></div>'
        f'<div class="planning-summary-card"><strong>Recorded target</strong><span>{_text(target_summary)}</span></div>'
        f'<div class="planning-summary-card"><strong>Formal scope plan</strong><span>{_text(contract.get("status") or "not-recorded")}</span></div>'
        f'<div class="planning-summary-card"><strong>Current package</strong><span>{_text(version)} · freshness {_text(freshness or "unknown")} · identity {_text(current_package_status or "unknown")}</span></div>'
        f'<div class="planning-summary-card"><strong>Official local validation</strong><span>{_text(validation_summary.get("display") or "Not recorded")}</span></div>'
        + consent_summary
        + '<div class="planning-summary-card"><strong>Exact-scope write approval</strong><span>Not recorded. Required immediately before each environment write.</span></div>'
        '</div>'
        + deployment_summary
        + '<p class="muted">A missing formal plan is not evidence that no run target exists. The setup station shows only persisted target/profile data; it never runs doctor, authentication, discovery, or network checks.</p>'
        + '<div class="planning-layout">'
        + '<section class="planning-card" aria-labelledby="planning-target">'
        + '<h3 id="planning-target">Target and run context</h3>'
        + f'<p class="muted">{_text(target_fallback_text)}</p>'
        + (f'<dl class="target-data">{"".join(f"<div><dt>{_text(key)}</dt><dd>{_text(value)}</dd></div>" for key, value in target.items())}</dl>' if target else '<p class="muted">No target details are recorded.</p>')
        + f'<p><strong>Target source:</strong> {_text(target_source or "not recorded")}</p>'
        + f'<p><strong>Plan status:</strong> {_text(contract.get("status") or "No formal plan recorded")}</p>'
        + (f'<p><strong>Planning consent fingerprint:</strong> <code>{_text(consent.get("planSha256"))}</code></p>' if consent.get("planSha256") else "")
        + '</section>'
        + '<section class="planning-card" aria-labelledby="planning-source-summary">'
        + '<h3 id="planning-source-summary">Source and selected scope</h3>'
        + f'<p>{_text(inventory_status)}</p>'
        + (source_inventory_html if isinstance(source_inventory, dict) and source_inventory else "")
        + (f'<p><strong>Detection scope:</strong> {_text(" · ".join(detection_scope_items))}</p>' if detection_scope_items else "")
        + (cap_html if cap_html else "")
        + scope_details
        + '</section></div>'
        + inventory_markup
        + (
            '<section class="planning-card" aria-labelledby="deployment-components-heading">'
            + f'<h3 id="deployment-components-heading">{"Component plans and advance consent" if consent_recorded else "Component plans"}</h3>'
            + (f'<p>{_text(component_consent_note)}</p>' if consent_recorded else "")
            + '<div class="component-plan-grid">' + "".join(component_markup) + '</div>'
            + (f'<p><strong>Consent resource types:</strong> {_text(", ".join(consent_types))}</p>' if consent_status == "approved" and consent_types else "")
            + (f'<p><strong>Approved max additional detections:</strong> {_text(consent_max_additional)}</p>' if consent_status == "approved" and consent_max_additional is not None else "")
            + (f'<details class="planning-details"><summary>Approved package flags and conditional selections</summary><pre>{_text(json.dumps({"packageFlags": consent_flags, "conditionalSelections": consent.get("conditionalSelections")}, sort_keys=True, indent=2))}</pre></details>' if consent_status == "approved" else "")
            + '</section>'
            if component_markup or consent_recorded else ""
        )
        + package_default_details + dcr_details + package_acceptance_details
        + '<p class="muted">No cleanup, deletion, retention change, RBAC assignment, enablement, or recurring job is implied by these plans. Exact-scope approval and readiness are separate from advance consent.</p>'
        + '</section>'
        + hash_details
        + '</section>'
    )
def _workbooks_html(report: dict[str, Any]) -> str:
    workbooks = report.get("workbooks")
    if not isinstance(workbooks, dict):
        return ""
    excluded = {row["path"]: row["reason"] for row in workbooks.get("excluded") or []}
    rows = []
    for source in workbooks.get("sources") or []:
        reasons = [excluded[source["path"]]] if source["path"] in excluded else []
        reasons.extend(
            item.get("message", item.get("code", "Recorded finding")) if isinstance(item, dict) else str(item)
            for item in source.get("issues") or []
        )
        rows.append("<tr>" + "".join(
            f"<td>{_text(value)}</td>" for value in (
                source["path"], "Selected" if source["selected"] else "Excluded",
                source["status"], "; ".join(reasons),
            )
        ) + "</tr>")
    return (
        '<section class="panel" aria-labelledby="workbooks-heading"><h2 id="workbooks-heading">Defender workbooks</h2>'
        f'<p>{_text(workbooks.get("inventoryCount"))} frozen sources · {_text(workbooks.get("selectedCount"))} selected. '
        'Workbook panels do not count toward detection coverage.</p>'
        f'<p>ARM method: {_text(workbooks.get("armValidationMethod"))}. '
        f'Installation/registration contract: {_text(workbooks.get("contractSupport"))}. '
        'Query/UI Qualification is independent of ARM acceptance and detection alert parity.</p>'
        + "".join(f"<p>{_text(issue)}</p>" for issue in workbooks.get("issues") or [])
        + '<div class="table-wrap"><table><thead><tr><th>Original workbook</th><th>Selection</th>'
        '<th>Conversion</th><th>Recorded reasons</th></tr></thead><tbody>'
        + "".join(rows) + "</tbody></table></div></section>"
    )


def render_dashboard(report: dict[str, Any]) -> str:
    workflow = report.get("workflow") or {}
    candidates = review_candidates(report)
    candidates_by_index = {candidate["index"]: candidate for candidate in candidates}
    prepared = []
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for index, rule in enumerate(report["rules"]):
        findings = _findings(rule)
        status = _rule_status(rule, workflow)
        for finding in findings:
            message = re.sub(
                r"ruleOverrides\.[0-9a-fA-F-]{36}\.", "ruleOverrides.<rule-id>.", finding["message"]
            )
            key = (finding["severity"], message)
            group = groups.setdefault(key, {"id": f"issue-{len(groups) + 1}", "message": message,
                                            "severity": finding["severity"], "rules": set()})
            group["rules"].add(index)
            finding["group"] = group
        prepared.append((rule, status, findings))
    counts = Counter(status for _, status, _ in prepared)
    counts["all"] = len(prepared)
    counts["attention"] = sum(status not in {"ready", "excluded"} for _, status, _ in prepared)
    finding_counts = Counter(finding["severity"] for _, _, findings in prepared for finding in findings)
    affected_counts = Counter(kind for _, _, findings in prepared for kind in {finding["severity"] for finding in findings})
    categories = sorted({finding["category"] for _, _, findings in prepared for finding in findings})
    chips = "".join(
        f'<label class="chip"><input type="radio" name="status" value="{key}"'
        f'{" checked" if key == "attention" else ""}> {label} ({counts[key]})</label>'
        for key, label in STATUS_LABELS.items() if key != "excluded" or counts[key]
    )
    category_html = "".join(
        f'<label class="chip"><input type="checkbox" name="category" value="{_text(category)}"> {_text(category)}</label>'
        for category in categories
    )
    finding_chips = (
        '<label class="chip"><input type="radio" name="finding" value="any" checked> Any finding</label>'
        + "".join(
            f'<label class="chip"><input type="radio" name="finding" value="{kind}"> {labels[0]} ({affected_counts[kind]} rules)</label>'
            for kind, labels in FINDING_LABELS.items()
        )
    )
    shared_groups = sorted(
        (group for group in groups.values() if len(group["rules"]) > 1),
        key=lambda group: (list(FINDING_LABELS).index(group["severity"]), -len(group["rules"])),
    )
    has_tactic_review = any(_is_tactic_review(finding) for _, _, findings in prepared for finding in findings)
    shared = ""
    for kind, labels in FINDING_LABELS.items():
        section = "".join(
            f'<li id="{group["id"]}">{_finding_badge(kind)} — '
            + ('<a href="#tactic-selection-guide">Historical single-tactic finding; preserve source tactics</a> '
               if _is_tactic_review(group) else _text(group["message"]) + " ")
            + f'<button type="button" data-filter-issue="{group["id"]}">Show {len(group["rules"])} affected rules'
            f'<span class="muted"> · Issue {group["id"].split("-")[1]}</span></button></li>'
            for group in shared_groups if group["severity"] == kind
        )
        if section:
            shared += f'<section data-finding-group="{kind}"><h3>{labels[0]}</h3><ul class="issue-list">{section}</ul></section>'
    rows = []
    order = {"failed": 0, "review": 1, "unconfirmed": 2, "notstarted": 3, "ready": 4, "excluded": 5}
    for index, (rule, status, findings) in sorted(enumerate(prepared), key=lambda item: (order[item[1][1]], str(item[1][0]["name"]).casefold())):
        reasons, advisories, information = [], [], []
        evidence: dict[str, list[str]] = {kind: [] for kind in FINDING_LABELS}
        for finding in findings:
            group = finding["group"]
            if _is_tactic_review(finding):
                reason = '<a href="#tactic-selection-guide">Historical single-tactic finding; preserve source tactics</a>'
            elif len(group["rules"]) > 1:
                reason = f'<a href="#{group["id"]}">{_text(finding["category"])} · Issue {group["id"].split("-")[1]}</a>'
            else:
                reason = _text(finding["message"])
            kind = finding["severity"]
            (advisories if kind == "warning" else information if kind == "info" else reasons).append(
                f"<li>{_finding_badge(kind)} {reason}</li>"
            )
            evidence[kind].append(
                f"<details><summary>{_finding_badge(kind)} — {_text(finding['message'])}</summary>"
                f"<p>Observed in: {_text(', '.join(finding['stages']))}</p>"
                f"<pre>{escape(json.dumps(finding['evidence'], indent=2, ensure_ascii=False))}</pre></details>"
            )
        if not reasons:
            reasons.append("<li>" + {
                "unconfirmed": "Automated conversion passed; semantic review completion is unconfirmed.",
                "ready": "Recorded conversion stage and local checks passed.",
                "notstarted": "No conversion result recorded.",
                "review": "Review required; no detailed reason recorded.",
                "failed": "A recorded check failed or is blocked; see evidence.",
                "excluded": "Excluded from conversion.",
            }[status] + "</li>")
        search = " ".join(
            str(value or "") for value in [
                rule["name"], rule.get("sourceFile"), rule.get("outputFile"),
                rule.get("analyticRule", {}).get("id"), rule["customDetection"].get("id"),
                *(finding["message"] for finding in findings),
            ]
        ).lower()
        detail_id = f"rule-detail-{index}"
        recommendation = rule.get("entityRecommendation")
        advisory_html = (
            f'<details class="advisories"><summary>Warnings ({len(advisories)}) — nonblocking advisories</summary>'
            f'<ul class="issue-list">{"".join(advisories)}</ul></details>' if advisories else ""
        )
        if information:
            advisory_html += (
                f'<details class="information"><summary>Information ({len(information)}) — nonblocking notes</summary>'
                f'<ul class="issue-list">{"".join(information)}</ul></details>'
            )
        selection_html = ""
        candidate = candidates_by_index.get(index)
        if candidate:
            selection_html = (
                '<br><label>'
                f'<input type="checkbox" class="review-select" data-review-id="{_text(candidate["id"])}" '
                f'{"disabled " if not candidate["eligible"] else ""}'
                f'title="{_text(candidate["reason"])}"> Select for reviewed override</label>'
            )
            if not candidate["eligible"]:
                selection_html += f'<p class="muted">{_text(candidate["reason"])}</p>'
        evidence_html = "".join(
            f'<section data-evidence-kind="{kind}"><h4>{FINDING_LABELS[kind][0]}</h4>{"".join(values)}</section>'
            for kind, values in evidence.items() if values
        )
        rows.append(
            f'<tbody class="rule" data-status="{status}" data-chart="{_chart_bucket(rule)}" data-search="{_text(search)}" '
            f'data-categories="{_text("|".join(sorted({finding["category"] for finding in findings})))}" '
            f'data-findings="{_text("|".join(sorted({finding["severity"] for finding in findings})))}" '
            f'data-issues="{_text("|".join(finding["group"]["id"] for finding in findings))}">'
            f'<tr><th scope="row"><strong>{_text(rule["name"])}</strong><br>'
            f'<span class="badge {status}">{STATUS_LABELS[status]}</span>{selection_html}</th>'
            f'<td><ul class="issue-list">{"".join(reasons)}</ul>{advisory_html}</td>'
            f'<td>{_text(_next_action(status, findings))}</td>'
            f'<td><button type="button" data-toggle-detail aria-expanded="false" aria-controls="{detail_id}"'
            f' aria-label="Details for {_text(rule["name"])}">Details</button></td></tr>'
            f'<tr id="{detail_id}" hidden><td colspan="4" class="detail-cell">'
            f'<p>Source: <code>{_text(rule.get("sourceFile"))}</code><br>'
            f'Output: <code>{_text(rule.get("outputFile"))}</code><br>'
            f'Sentinel ID: <code>{_text(rule.get("analyticRule", {}).get("id"))}</code> · '
            f'XDR ID: <code>{_text(rule["customDetection"].get("id"))}</code></p>'
            + _query_html(rule)
            + (f"<p><strong>Entity recommendation:</strong> {_text(recommendation)}</p>" if recommendation else "")
            + _result_html(rule)
            + _tactic_details(rule, findings)
            + "<h4>Findings and original evidence</h4>"
            + (evidence_html if evidence_html else "<p>No rule-level findings recorded.</p>")
            + "</td></tr></tbody>"
        )
    summary = report.get("summary") or {}
    scope = summary.get("conversionScope") or {}
    scope_notice = (
        '<section class="panel"><h2>Rule-scoped conversion only</h2>'
        f'<p>Selected source ID: {_text(", ".join(scope.get("ruleIds") or []))}. '
        'Unselected drafts were not converted in this attempt. Local structural passes '
        'do not establish full-solution conversion or packaging readiness.</p></section>'
        if scope.get("kind") == "rule" else ""
    )
    structural = sum(rule["customDetection"].get("structuralStatus") == "passed" for rule, _, _ in prepared)
    distinct_errors = sum(finding["severity"] == "error" for _, _, findings in prepared for finding in findings)
    occurrences = sum(
        len(finding["evidence"]) for _, _, findings in prepared
        for finding in findings if finding["severity"] == "error"
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{_text(report["solution"])} migration report</title>'
        f"<script>{THEME_SCRIPT}</script><style>{STYLE}</style></head><body><main>"
        f'<h1>{_text(report["solution"])} migration report</h1>'
        f'<p class="muted">Generated {_text(report.get("generatedAt"))} · Offline report · No environment writes</p>'
        + _flow_html(report)
        + scope_notice
        + _deployment_planning_html(report)
        + _findings_chart_html(report["rules"])
        + _run_html(report)
        + _workbooks_html(report)
        + '<section class="panel" aria-labelledby="overview"><h2 id="overview">Current artifact overview</h2>'
        f'<div class="metrics"><span>{len(prepared)} rules</span><span>{_text(summary.get("converted"))} automated conversions</span>'
        f'<span>{_text(summary.get("needsReview"))} converter review flags</span><span>{structural} local structural passes</span>'
        f'<span>{distinct_errors} distinct rule errors · {occurrences} diagnostic occurrences</span></div>'
        '<h3>Finding types — separate from readiness</h3><div class="metrics">'
        + "".join(
            f'<span>{_finding_badge(kind)} <strong>{finding_counts[kind]}</strong> findings across {affected_counts[kind]} rules</span>'
            for kind in FINDING_LABELS
        )
        + '</div><p>Errors are failed checks/executions or recorded hard errors. Reviews are explicit unresolved human decisions. '
        'Warnings are nonblocking advisories: a time/schedule warning is not automatically a review or failure. '
        'Information records explicit backend informational notes; it is not a warning and does not by itself require attention. '
        'Blocked prerequisites are tracked separately from execution failures. Counts are deduplicated per rule; types may overlap.</p>'
        '<p>Ready for validation means automated checks and the recorded conversion stage passed. '
        'It does not mean deployment approval or proven semantic equivalence. When conversion review is incomplete, '
        'automated successes remain <strong>Readiness unconfirmed</strong>. '
        '<strong>Run-level caution:</strong> any historical semantic findings without structured rule mappings remain a run-level caution; '
        'they do not create per-rule Needs review flags. Warnings do not change readiness.</p></section>'
        + _chart_html(report["rules"])
        + ('<section class="panel"><details id="shared-findings"><summary>Shared findings — '
           f'{len(shared_groups)} repeated patterns</summary><p class="muted">Each explanation appears once here. '
           'Counts are affected rules, not diagnostic occurrences. Original per-rule evidence is preserved in Details.</p>'
           + (_tactic_guide() if has_tactic_review else "")
           + f'{shared}</details></section>' if shared or has_tactic_review else "")
        + render_bulk_review(report, candidates)
        + '<section class="panel"><h2>Rules</h2><form id="filters">'
        '<fieldset><legend>Status — select one; counts cover the entire run</legend><div class="chips">'
        + chips + '</div></fieldset><fieldset><legend>Finding type — counts are affected rules</legend><div class="chips">'
        + finding_chips + '</div><p class="muted">Choosing a finding type shows all statuses; refine status afterward. '
        'Warnings remain advisories even on a ready rule.</p></fieldset><label for="search">Search rule name, path, ID or finding</label>'
        '<input type="search" id="search" name="search" placeholder="Search this run">'
        '<fieldset><legend>Issue categories — any selected category</legend><div class="categories">'
        + category_html + '</div></fieldset><p class="muted">Status, search and categories are combined. '
        'Multiple categories match any selected category.</p>'
        '<button type="button" id="clear">Clear filters / show all</button></form>'
        '<p><span id="issue-filter"></span> <button type="button" id="clear-issue" hidden>Clear issue filter</button></p>'
        '<p id="chart-filter-label" role="status" aria-live="polite"></p>'
        '<p id="finding-chart-filter-label" role="status" aria-live="polite"></p>'
        '<p id="result-count" role="status" aria-live="polite" tabindex="-1"></p>'
        '<p id="empty" hidden>No matching rules. Change your filters or choose Clear filters / show all.</p>'
        '<noscript><p>Enable JavaScript for filters and expandable rule details. Original evidence remains in migration-report.json.</p></noscript>'
        '<div class="table-wrap"><table><caption class="muted">Actionable issues first; individual results remain authoritative.</caption>'
        '<thead><tr><th scope="col">Rule</th><th scope="col">Problem / review reason</th><th scope="col">Next action</th>'
        '<th scope="col">Details</th></tr></thead>' + "".join(rows)
        + f"</table></div></section></main><script>{FILTER_SCRIPT}</script><script>{BULK_SCRIPT}</script></body></html>"
    )
