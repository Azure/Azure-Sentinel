from __future__ import annotations

from pathlib import Path
from typing import Any

from solution_manager.reporting.pr_qualification_report import (
    HTML_REPORT_FILENAME,
    MARKDOWN_SUMMARY_FILENAME,
    render_pr_qualification_html,
    render_pr_qualification_markdown,
    write_pr_qualification_reports,
)


def _sample_check(
    check_id: str = "VAL-PKG-001",
    *,
    checklist: str = "validation",
    title: str = "Package Version Validation",
    original_criterion: str = "Solution version in SolutionMetadata.json and Data file must increment and match Package zip.",
    content_type: str = "Package",
    category: str = "validation",
    source_checklist: str = "PR Validation Checklist",
    applicable: bool = True,
    applicability_reason: str = "Solution contains a Package folder.",
    status: str = "PASS",
    what_we_checked: str = "Compared SolutionMetadata.json, Data/Solution_AKS.json, and Package/3.2.2.zip.",
    what_we_observed: str = "All package version references equal 3.2.2 (previous 2.0.2).",
    why_passed_or_failed: str = "Version bump is consistent across metadata, data input, and zip artifact.",
    evidence_refs: list[dict[str, Any]] | None = None,
    author_exception: dict[str, Any] | None = None,
    reviewer_action_required: bool = False,
    reviewer_action_prompt: str | None = None,
) -> dict[str, Any]:
    return {
        "id": check_id,
        "checklist": checklist,
        "title": title,
        "originalCriterion": original_criterion,
        "contentType": content_type,
        "category": category,
        "sourceChecklist": source_checklist,
        "applicable": applicable,
        "applicabilityReason": applicability_reason,
        "status": status,
        "whatWeChecked": what_we_checked,
        "whatWeObserved": what_we_observed,
        "whyPassedOrFailed": why_passed_or_failed,
        "evidenceRefs": evidence_refs
        if evidence_refs is not None
        else [
            {
                "label": "SolutionMetadata.json",
                "path": "Solutions/Azure kubernetes Service/SolutionMetadata.json",
                "line": 4,
                "kind": "file",
            },
            {
                "label": "Decision Manifest",
                "path": "Solutions/Azure kubernetes Service/Evidence/decision-manifest.json",
                "line": None,
                "kind": "manifest",
            },
        ],
        "authorException": author_exception,
        "reviewerActionRequired": reviewer_action_required,
        "reviewerActionPrompt": reviewer_action_prompt,
    }


def _sample_report_data(**overrides: Any) -> dict[str, Any]:
    checks = [
        _sample_check(),
        _sample_check(
            "QUAL-WB-001",
            checklist="qualification",
            title="Workbook Runtime Query Qualification",
            original_criterion="All workbook KQL queries must execute cleanly against live or mock telemetry.",
            content_type="Workbook",
            category="qualification",
            source_checklist="Solution Qualification Guide",
            what_we_checked="Executed 27 workbook KQL queries against AKS qualification workspace.",
            what_we_observed="27/27 queries returned valid schemas and expected rows.",
            why_passed_or_failed="All workbook queries succeeded with zero runtime errors.",
            evidence_refs=[
                {
                    "label": "AksSecurity.json",
                    "path": "Solutions/Azure kubernetes Service/XDR Workbooks/AksSecurity.json",
                    "line": 120,
                    "kind": "workbook",
                }
            ],
        ),
        _sample_check(
            "MIG-WB-001",
            checklist="migration",
            title="Defender XDR Workbook Migration Parity",
            original_criterion="Migrated XDR workbook must replace legacy SecurityAlert unions with AlertInfo/AlertEvidence.",
            content_type="XDR Workbook",
            category="qualification",
            source_checklist="XDR Migration Checklist",
            what_we_checked="Inspected XDR Workbooks/AksSecurity.json for legacy SecurityAlert dependencies.",
            what_we_observed="SecurityAlert replaced with AlertInfo and AlertEvidence joins.",
            why_passed_or_failed="XDR workbook queries conform to Defender XDR schema.",
        ),
    ]
    base: dict[str, Any] = {
        "schemaVersion": "pr-qualification-report-v1",
        "solutionName": "Azure kubernetes Service",
        "solutionVersion": "3.2.2",
        "previousVersion": "2.0.2",
        "isMigration": True,
        "generatedAtUtc": "2026-10-19T15:00:00Z",
        "validationStatus": "Validated",
        "qualificationStatus": "Qualified",
        "migrationStatus": "Migration Verified",
        "detectedContentTypes": ["Workbook", "XDR Workbook", "Package"],
        "summaryCounts": {
            "total": 3,
            "applicable": 3,
            "pass": 3,
            "fail": 0,
            "skipped": 0,
            "waivedWithAuthorEvidence": 0,
            "humanReviewRequired": 0,
            "notApplicable": 0,
        },
        "checks": checks,
    }
    base.update(overrides)
    return base


def test_full_validated_and_qualified_run_renders_html_and_markdown() -> None:
    report_data = _sample_report_data()

    html_out = render_pr_qualification_html(report_data)
    md_out = render_pr_qualification_markdown(report_data)

    assert "<!DOCTYPE html>" in html_out
    assert "Azure kubernetes Service" in html_out
    assert "3.2.2" in html_out
    assert "2.0.2" in html_out
    assert "Migration + Qualification" in html_out
    assert "Validated" in html_out
    assert "Qualified" in html_out
    assert "Migration Verified" in html_out
    assert "0 Actions Required" in html_out
    assert "1. Validation Checklist" in html_out
    assert "2. Qualification Checklist" in html_out
    assert "3. Migration Checklist" in html_out
    assert 'href="Solutions/Azure kubernetes Service/SolutionMetadata.json"' in html_out
    assert "Solutions/Azure kubernetes Service/SolutionMetadata.json:4" in html_out
    assert 'data-filter-checklist="validation"' in html_out
    assert 'data-filter-status="WAIVED_WITH_AUTHOR_EVIDENCE"' in html_out

    assert "# PR Qualification & Validation Summary" in md_out
    assert "**PASS - Package Version Validation**" in md_out
    assert "[SolutionMetadata.json:4](Solutions/Azure%20kubernetes%20Service/SolutionMetadata.json)" in md_out
    assert f"[{HTML_REPORT_FILENAME}]({HTML_REPORT_FILENAME})" in md_out


def test_partially_validated_and_conditionally_qualified_with_waiver_and_human_review() -> None:
    waived_check = _sample_check(
        "VAL-ARM-002",
        checklist="validation",
        title="ARM-TTK Embedded Workbook ResourceID Check",
        original_criterion="mainTemplate.json must pass ARM-TTK without ResourceID or blank property errors.",
        content_type="Package",
        category="validation",
        status="WAIVED_WITH_AUTHOR_EVIDENCE",
        what_we_checked="Ran ARM-TTK against Package/mainTemplate.json.",
        what_we_observed="Upstream generator emits empty string parameter defaults in workbook resource.",
        why_passed_or_failed="Waived with live Azure lab deployment evidence in decision-manifest.json.",
        author_exception={
            "checkId": "VAL-ARM-002",
            "originalStatus": "FAIL",
            "authorJustification": "Verified via live Azure lab ARM deployment and GET readback.",
            "supportingEvidenceRef": "Solutions/Azure kubernetes Service/Evidence/decision-manifest.json",
            "author": "contoso-author",
        },
        reviewer_action_required=True,
    )
    human_review_check = _sample_check(
        "QUAL-UI-001",
        checklist="qualification",
        title="Workbook Visual Layout Confirmation",
        original_criterion="Reviewer confirms workbook tabs and charts render without overlap.",
        content_type="Workbook",
        category="human-review",
        status="HUMAN_REVIEW_REQUIRED",
        what_we_checked="Extracted workbook layout metadata and screenshot references.",
        what_we_observed="3 tabs and 27 visualizations configured.",
        why_passed_or_failed="Visual inspection requires human reviewer confirmation.",
        evidence_refs=[
            {
                "label": "Workbook Screenshot",
                "path": "Solutions/Azure kubernetes Service/Evidence/workbook-preview.png",
                "line": None,
                "kind": "screenshot",
            }
        ],
        reviewer_action_required=True,
        reviewer_action_prompt="Inspect workbook-preview.png and confirm visual layout.",
    )

    report_data = _sample_report_data(
        validationStatus="Partially Validated",
        qualificationStatus="Conditionally Qualified",
        migrationStatus="Conditionally Migrated",
        summaryCounts=None,
        checks=[_sample_check(), waived_check, human_review_check],
    )

    html_out = render_pr_qualification_html(report_data)
    md_out = render_pr_qualification_markdown(report_data)

    assert "Partially Validated" in html_out
    assert "Conditionally Qualified" in html_out
    assert "Conditionally Migrated" in html_out
    assert "2 Item(s) Require Reviewer Attention" in html_out
    assert "WAIVED WITH AUTHOR EVIDENCE - ARM-TTK Embedded Workbook ResourceID Check" in html_out
    assert "HUMAN REVIEW REQUIRED - Workbook Visual Layout Confirmation" in html_out
    assert "Verified via live Azure lab ARM deployment and GET readback." in html_out
    assert (
        'href="Solutions/Azure kubernetes Service/Evidence/decision-manifest.json"'
        in html_out
    )
    assert (
        "Confirm author exception evidence to approve Partially Validated / Conditionally Qualified status"
        in html_out
    )
    assert "Inspect workbook-preview.png and confirm visual layout." in html_out

    assert "**WAIVED WITH AUTHOR EVIDENCE - ARM-TTK Embedded Workbook ResourceID Check**" in md_out
    assert "**HUMAN REVIEW REQUIRED - Workbook Visual Layout Confirmation**" in md_out
    assert (
        "[Solutions/Azure kubernetes Service/Evidence/decision-manifest.json]"
        "(Solutions/Azure%20kubernetes%20Service/Evidence/decision-manifest.json)"
        in md_out
    )
    assert (
        "Confirm author exception evidence to approve Partially Validated / Conditionally Qualified status"
        in md_out
    )


def test_non_migration_run_renders_general_solution_qualification_mode() -> None:
    non_mig_check = _sample_check(
        "MIG-001",
        checklist="migration",
        title="XDR Detection Conversion",
        applicable=False,
        applicability_reason="PR is a general Sentinel solution update without XDR migration scope.",
        status="NOT_APPLICABLE",
    )
    report_data = _sample_report_data(
        isMigration=False,
        previousVersion=None,
        migrationStatus="Not Applicable",
        checks=[_sample_check(), non_mig_check],
    )

    html_out = render_pr_qualification_html(report_data)
    md_out = render_pr_qualification_markdown(report_data)

    assert "General Solution Qualification" in html_out
    assert "Migration + Qualification" not in html_out
    assert "Not Applicable" in html_out
    assert "NOT_APPLICABLE" in html_out

    assert "General Solution Qualification" in md_out
    assert "| **Migration** | **Not Applicable** |" in md_out


def test_xss_and_html_escaping_in_observed_justification_and_evidence_refs() -> None:
    malicious_check = _sample_check(
        "VAL-XSS-001",
        title='Check <script>alert("title")</script>',
        what_we_observed='<img src=x onerror="alert(1)"> & "quoted"',
        why_passed_or_failed="Failed because <script>bad()</script>",
        status="WAIVED_WITH_AUTHOR_EVIDENCE",
        evidence_refs=[
            {
                "label": '<b>Evil Label</b>',
                "path": 'javascript:alert("xss")',
                "line": 10,
                "kind": '<script>evil</script>',
            },
            {
                "label": "Safe Evidence",
                "path": 'Solutions/Test/file"onclick="alert(1).json',
                "line": 25,
                "kind": "json",
            },
        ],
        author_exception={
            "checkId": "VAL-XSS-001",
            "originalStatus": "FAIL",
            "authorJustification": '<script>alert("waiver")</script>',
            "supportingEvidenceRef": "javascript:evil()",
            "author": '<svg onload="alert(2)">',
        },
        reviewer_action_required=True,
    )
    report_data = _sample_report_data(
        solutionName='<script>alert("sol")</script>',
        checks=[malicious_check],
    )

    html_out = render_pr_qualification_html(report_data)
    md_out = render_pr_qualification_markdown(report_data)

    assert '<script>alert("sol")</script>' not in html_out
    assert '<script>alert("title")</script>' not in html_out
    assert '<img src=x onerror="alert(1)">' not in html_out
    assert '<script>alert("waiver")</script>' not in html_out
    assert '<b>Evil Label</b>' not in html_out
    assert '<svg onload="alert(2)">' not in html_out
    assert 'href="javascript:' not in html_out

    assert "&lt;script&gt;alert(&quot;waiver&quot;)&lt;/script&gt;" in html_out
    assert "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;" in html_out
    assert "&lt;b&gt;Evil Label&lt;/b&gt;" in html_out

    assert "(javascript:" not in md_out
    assert "&lt;script&gt;alert(&quot;waiver&quot;)&lt;/script&gt;" in md_out


def test_write_pr_qualification_reports_writes_both_files(tmp_path: Path) -> None:
    report_data = _sample_report_data()
    output_dir = tmp_path / "pr-qualification-output"

    written = write_pr_qualification_reports(report_data, output_dir)

    assert set(written.keys()) == {"html", "markdown"}
    assert written["html"] == output_dir / HTML_REPORT_FILENAME
    assert written["markdown"] == output_dir / MARKDOWN_SUMMARY_FILENAME
    assert written["html"].is_file()
    assert written["markdown"].is_file()

    html_text = written["html"].read_text(encoding="utf-8")
    md_text = written["markdown"].read_text(encoding="utf-8")
    assert "Azure kubernetes Service" in html_text
    assert "PR Qualification & Validation Summary" in md_text


def test_defensive_defaults_when_optional_keys_are_missing() -> None:
    minimal_data: dict[str, Any] = {
        "solutionName": "MinimalSolution",
        "checks": [
            {
                "id": "VAL-001",
                "checklist": "validation",
                "title": "Metadata Check",
                "status": "FAIL",
            }
        ],
    }

    html_out = render_pr_qualification_html(minimal_data)
    md_out = render_pr_qualification_markdown(minimal_data)

    assert "MinimalSolution" in html_out
    assert "Validation Failed" in html_out
    assert "Not Run" in html_out
    assert "Not Applicable" in html_out
    assert "FAIL - Metadata Check" in html_out
    assert "**FAIL - Metadata Check**" in md_out


def test_report_redacts_file_urls_local_paths_and_emails() -> None:
    leaky_check = _sample_check(
        check_id="QUAL-PRIV-001",
        checklist="qualification",
        what_we_observed="Observed at /Users/secadmin/private/lab.json by analyst@contoso.com with tenantId: 11111111-2222-3333-4444-555555555555",
        evidence_refs=[
            {
                "label": "Local File URL",
                "path": "file:///Users/secadmin/secret/evidence.json",
                "kind": "json",
            }
        ],
    )
    report_data = _sample_report_data(checks=[leaky_check])
    html_out = render_pr_qualification_html(report_data)
    md_out = render_pr_qualification_markdown(report_data)

    for rendered in (html_out, md_out):
        assert "file://" not in rendered
        assert "/Users/secadmin" not in rendered
        assert "analyst@contoso.com" not in rendered
        assert "11111111-2222-3333-4444-555555555555" not in rendered
        assert "[REDACTED_PATH]" in rendered
        assert "[REDACTED_EMAIL]" in rendered
        assert "[REDACTED_ID]" in rendered


def test_filter_button_counters_render_accurate_checklist_and_status_counts() -> None:
    waived_check = _sample_check(
        "VAL-WAIV-001",
        checklist="validation",
        status="WAIVED_WITH_AUTHOR_EVIDENCE",
        reviewer_action_required=True,
    )
    human_check = _sample_check(
        "QUAL-HUM-001",
        checklist="qualification",
        status="HUMAN_REVIEW_REQUIRED",
        reviewer_action_required=True,
    )
    na_check = _sample_check(
        "MIG-NA-001",
        checklist="migration",
        applicable=False,
        status="NOT_APPLICABLE",
    )
    report_data = _sample_report_data(
        summaryCounts=None,
        checks=[
            _sample_check("VAL-PASS-001", checklist="validation", status="PASS"),
            waived_check,
            _sample_check("QUAL-PASS-001", checklist="qualification", status="PASS"),
            human_check,
            na_check,
        ],
    )

    html_out = render_pr_qualification_html(report_data)

    assert 'data-filter-checklist="all">All <span class="filter-count">5</span>' in html_out
    assert 'data-filter-checklist="validation">Validation <span class="filter-count">2</span>' in html_out
    assert 'data-filter-checklist="qualification">Qualification <span class="filter-count">2</span>' in html_out
    assert 'data-filter-checklist="migration">Migration <span class="filter-count">1</span>' in html_out

    assert 'data-filter-status="ALL">All Statuses <span class="filter-count">5</span>' in html_out
    assert 'data-filter-status="ACTION_REQUIRED">Action Required <span class="filter-count">2</span>' in html_out
    assert 'data-filter-status="PASS">PASS <span class="filter-count">2</span>' in html_out
    assert (
        'data-filter-status="WAIVED_WITH_AUTHOR_EVIDENCE">'
        'WAIVED_WITH_AUTHOR_EVIDENCE <span class="filter-count">1</span>'
    ) in html_out
    assert (
        'data-filter-status="HUMAN_REVIEW_REQUIRED">'
        'HUMAN_REVIEW_REQUIRED <span class="filter-count">1</span>'
    ) in html_out
    assert 'data-filter-status="FAIL">FAIL <span class="filter-count">0</span>' in html_out
    assert (
        'data-filter-status="NOT_APPLICABLE">'
        'NOT_APPLICABLE <span class="filter-count">1</span>'
    ) in html_out


def test_relative_path_rebasing_with_output_dir_and_solution_root(tmp_path: Path) -> None:
    output_dir = tmp_path / "Reports" / "ddos-pr-qualification"
    evidence_dir = output_dir / "evidence"
    screenshots_dir = evidence_dir / "screenshots"
    solution_root = output_dir / "workspace" / "Azure DDoS Protection"
    (solution_root / "Data").mkdir(parents=True, exist_ok=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    (solution_root / "SolutionMetadata.json").write_text("{}", encoding="utf-8")
    (evidence_dir / "qualification-evidence.json").write_text("{}", encoding="utf-8")
    (evidence_dir / "workbook-arg-sku-limitation.md").write_text("# Waiver", encoding="utf-8")
    (screenshots_dir / "ddos-workbook-overview.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    check_with_links = _sample_check(
        "QUAL-WB-001",
        checklist="qualification",
        status="WAIVED_WITH_AUTHOR_EVIDENCE",
        evidence_refs=[
            {"label": "SolutionMetadata.json", "path": "SolutionMetadata.json", "kind": "file"},
            {"label": "Qualification Evidence", "path": "qualification_evidence.workbookQualification", "kind": "json"},
            {"label": "Screenshot", "path": "Evidence/screenshots/ddos-workbook-overview.png", "kind": "screenshot"},
            {"label": "Validation Status", "path": "validationStatus", "kind": "json"},
        ],
        author_exception={
            "checkId": "QUAL-WB-001",
            "originalStatus": "FAIL",
            "authorJustification": "Lab subscription SKU limitation.",
            "supportingEvidenceRef": "Evidence/workbook-arg-sku-limitation.md",
            "author": "@maintainer",
        },
        reviewer_action_required=True,
    )
    report_data = _sample_report_data(
        solutionName="Azure DDoS Protection",
        checks=[check_with_links],
    )

    html_out = render_pr_qualification_html(
        report_data,
        output_dir=output_dir,
        solution_root=solution_root,
    )
    md_out = render_pr_qualification_markdown(
        report_data,
        output_dir=output_dir,
        solution_root=solution_root,
    )

    assert 'href="./workspace/Azure DDoS Protection/SolutionMetadata.json"' in html_out
    assert 'href="./evidence/qualification-evidence.json#workbookQualification"' in html_out
    assert 'href="./evidence/screenshots/ddos-workbook-overview.png"' in html_out
    assert 'href="./pr-qualification-result.json#validationStatus"' in html_out
    assert 'href="./evidence/workbook-arg-sku-limitation.md"' in html_out

    assert "(./workspace/Azure%20DDoS%20Protection/SolutionMetadata.json)" in md_out
    assert "(./evidence/workbook-arg-sku-limitation.md)" in md_out



