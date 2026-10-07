from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


def _messages(values: list[str], empty: str) -> str:
    if not values:
        return f'<span class="muted">{escape(empty)}</span>'
    return "<ul>" + "".join(f"<li>{escape(value)}</li>" for value in values) + "</ul>"


def render_transformation_report(summary: dict[str, Any]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    rows: list[str] = []
    for result in summary["results"]:
        status = str(result["status"])
        review_required = bool(result.get("reviewRequired"))
        display_name = str(result.get("displayName") or Path(result["source"]).stem)
        source_name = Path(result["source"]).name
        output_name = Path(result["output"]).name
        warnings = list(result.get("warnings") or [])
        errors = list(result.get("errors") or [])
        rows.append(
            f"""
            <tr>
              <td><strong>{escape(display_name)}</strong><br><span class="muted">{escape(source_name)} -&gt; {escape(output_name)}</span></td>
              <td><span class="status {escape(status)}">{escape(status)}</span>
              {'<br><span class="muted">Review required</span>' if review_required else ''}</td>
              <td>{_messages(warnings, "None")}</td>
              <td>{_messages(errors, "None")}</td>
            </tr>
            """
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sentinel to XDR transformation report</title>
  <style>
    :root {{ color-scheme: light dark; font-family: Segoe UI, Arial, sans-serif; }}
    body {{ margin: 0; background: #0f172a; color: #e2e8f0; }}
    main {{ max-width: 1400px; margin: auto; padding: 32px; }}
    h1 {{ margin-bottom: 6px; }}
    .muted {{ color: #94a3b8; font-size: 0.9rem; }}
    .cards {{ display: grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap: 14px; margin: 24px 0; }}
    .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 18px; }}
    .card strong {{ display: block; font-size: 2rem; margin-top: 5px; }}
    .table-wrap {{ overflow-x: auto; border: 1px solid #334155; border-radius: 10px; }}
    table {{ width: 100%; border-collapse: collapse; background: #111827; }}
    th, td {{ padding: 14px; border-bottom: 1px solid #334155; text-align: left; vertical-align: top; }}
    th {{ background: #1e293b; position: sticky; top: 0; }}
    tr:last-child td {{ border-bottom: 0; }}
    ul {{ margin: 0; padding-left: 20px; }}
    .status {{ display: inline-block; border-radius: 999px; padding: 4px 10px; font-weight: 600; }}
    .converted {{ background: #14532d; color: #bbf7d0; }}
    .excluded {{ background: #334155; color: #e2e8f0; }}
    .needsReview {{ background: #78350f; color: #fde68a; }}
    .conflict {{ background: #7f1d1d; color: #fecaca; }}
    @media (max-width: 760px) {{ .cards {{ grid-template-columns: repeat(2, 1fr); }} main {{ padding: 18px; }} }}
  </style>
</head>
<body>
<main>
  <h1>Sentinel to XDR transformation report</h1>
  <div class="muted">{escape(str(summary["solution"]))} - Generated {generated_at}</div>
  <section class="cards">
    <div class="card">Rules attempted<strong>{summary["total"]}</strong></div>
    <div class="card">Converted<strong>{summary["converted"]}</strong></div>
    <div class="card">Excluded<strong>{summary.get("excluded", 0)}</strong></div>
    <div class="card">Review required<strong>{summary.get("reviewRequired", summary["needsReview"])}</strong></div>
    <div class="card">Conflicts<strong>{summary["conflicts"]}</strong></div>
  </section>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Rule</th><th>Status</th><th>Warnings</th><th>Errors</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
</main>
</body>
</html>
"""


def write_transformation_report(summary: dict[str, Any], path: Path) -> None:
    path.write_text(render_transformation_report(summary), encoding="utf-8", newline="\n")


def render_runtime_validation_report(summary: dict[str, Any]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    rows: list[str] = []
    for result in summary["results"]:
        status = str(result["status"])
        error = str(result.get("error") or "")
        rows.append(
            f"""
            <tr>
              <td><strong>{escape(str(result["detection"]))}</strong></td>
              <td><span class="status {escape(status)}">{escape(status)}</span></td>
              <td>{result.get("rowCount", 0)}</td>
              <td>{result.get("schemaColumnCount", 0)}</td>
              <td>{escape(error) if error else '<span class="muted">None</span>'}</td>
            </tr>
            """
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(str(summary["platform"]))} runtime validation report</title>
  <style>
    :root {{ color-scheme: light dark; font-family: Segoe UI, Arial, sans-serif; }}
    body {{ margin: 0; background: #0f172a; color: #e2e8f0; }}
    main {{ max-width: 1400px; margin: auto; padding: 32px; }}
    h1 {{ margin-bottom: 6px; }}
    .muted {{ color: #94a3b8; font-size: 0.9rem; }}
    .cards {{ display: grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap: 14px; margin: 24px 0; }}
    .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 18px; }}
    .card strong {{ display: block; font-size: 2rem; margin-top: 5px; }}
    .table-wrap {{ overflow-x: auto; border: 1px solid #334155; border-radius: 10px; }}
    table {{ width: 100%; border-collapse: collapse; background: #111827; }}
    th, td {{ padding: 14px; border-bottom: 1px solid #334155; text-align: left; vertical-align: top; }}
    th {{ background: #1e293b; }}
    .status {{ display: inline-block; border-radius: 999px; padding: 4px 10px; font-weight: 600; }}
    .passed {{ background: #14532d; color: #bbf7d0; }}
    .failed {{ background: #7f1d1d; color: #fecaca; }}
    .blocked {{ background: #78350f; color: #fde68a; }}
    .not-run {{ background: #334155; color: #cbd5e1; }}
    @media (max-width: 760px) {{ .cards {{ grid-template-columns: repeat(2, 1fr); }} main {{ padding: 18px; }} }}
  </style>
</head>
<body>
<main>
  <h1>{escape(str(summary["platform"]))} runtime validation</h1>
  <div class="muted">{escape(str(summary["solution"]))} - Provider: {escape(str(summary["provider"]))} - Generated {generated_at}</div>
  <section class="cards">
    <div class="card">Rules tested<strong>{summary["total"]}</strong></div>
    <div class="card">Passed<strong>{summary["valid"]}</strong></div>
    <div class="card">Failed<strong>{summary["invalid"]}</strong></div>
    <div class="card">Blocked<strong>{summary["blocked"]}</strong></div>
    <div class="card">Not run<strong>{summary.get("notRun", 0)}</strong></div>
  </section>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Detection</th><th>Status</th><th>Rows</th><th>Schema columns</th><th>Error</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
</main>
</body>
</html>
"""


def write_runtime_validation_report(summary: dict[str, Any], path: Path) -> None:
    path.write_text(
        render_runtime_validation_report(summary), encoding="utf-8", newline="\n"
    )
