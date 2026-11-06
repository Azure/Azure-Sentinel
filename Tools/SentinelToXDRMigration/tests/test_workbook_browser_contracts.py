"""Offline portal contracts: no credentials, cloud calls or browser launch."""
from contextlib import nullcontext
from copy import deepcopy
from pathlib import Path
from unittest import mock

import pytest

from solution_manager.qualification import orchestrator
from solution_manager.qualification.workbook_playwright import verify_workbook_playwright_rendering
from sentinel_xdr_migration import workbook_browser as browser
from sentinel_xdr_migration import workbook_qualification as qualification
from test_workbook_browser import Locator, Page, attr, standalone_plan, text, value
from test_workbook_qualification import qualified_source, ui_plan


@pytest.mark.parametrize("url,host", [
    ("https://security.microsoft.com/workbooks/fixture", "security.microsoft.com"),
    ("https://security.microsoft.com:443/sentinel/workbooks", "security.microsoft.com"),
    ("https://portal.azure.com/#view/reviewed-workbook", "portal.azure.com"),
])
def test_exact_portal_hosts(url, host):
    assert browser.validate_portal_url(url) == host


@pytest.mark.parametrize("url", [
    "http://security.microsoft.com/workbooks",
    "https://security.microsoft.com.evil.test/workbooks",
    "https://evilsecurity.microsoft.com/workbooks",
    "https://security.microsoft.com@evil.test/workbooks",
    "https://user@security.microsoft.com/workbooks",
    "https://security.microsoft.com:444/workbooks",
    "https://security.microsoft.com:invalid/workbooks",
    "https://security.microsoft.com./workbooks",
    "https://portal.azure.com.evil.test/#view/workbook",
    "https://security.microsoft.com/workbooks?access_token=PRIVATE",
    "https://security.microsoft.com/workbooks#view?client-secret=PRIVATE",
    "https://portal.azure.com/#view?%74oken=PRIVATE",
    "https://security.microsoft.com\\@evil.test/workbooks",
    "https://security.microsoft.com/workbooks\n",
    "https://security.microsoft.com/workbooks/*",
    "https://security.microsoft.com",
])
def test_portal_urls_fail_closed_and_sanitized(url):
    with pytest.raises(browser.BrowserQualificationError) as failure:
        browser.validate_portal_url(url)
    assert url not in str(failure.value)
    assert "PRIVATE" not in str(failure.value)


def azure_plan():
    plan = standalone_plan()
    plan["url"] = "https://portal.azure.com/#view/reviewed-workbook"
    plan["steps"][3]["expectedUrl"] = plan["url"]
    plan["target"]["workspaceResourceId"] = "/subscriptions/fixture/resourceGroups/lab/providers/Microsoft.OperationalInsights/workspaces/fixture"
    plan["target"]["workspaceCustomerId"] = "workspace-customer-fixture"
    plan["readinessSelectors"]["workspace"] = "#workspace"
    config = plan["browserConfig"]
    config["network"]["navigationUrls"] = [plan["url"]]
    config["network"]["requests"][0]["url"] = plan["url"]
    for key in ("workspaceResourceId", "workspaceCustomerId"):
        config["readiness"][key] = attr("#workspace", f"data-{key}", plan["target"][key])
    return plan


def test_azure_fallback_requires_scoped_observed_workspace_not_url_claims():
    plan = azure_plan()
    browser.validate_browser_config(plan, plan["browserConfig"])
    page = Page(plan)
    page.nodes["#workspace"] = {f"data-{key}": plan["target"][key] for key in ("workspaceResourceId", "workspaceCustomerId")}
    capture = browser._DOMRun(plan, lambda: None).run(mock.Mock(), page)
    qualification._validate_ui_capture(plan, capture)
    capture["readiness"]["workspaceResourceId"] = "wrong-workspace"
    with pytest.raises(ValueError, match="workspace"):
        qualification._validate_ui_capture(plan, capture)
    del plan["browserConfig"]["readiness"]["workspaceResourceId"]
    with pytest.raises(ValueError, match="workspace"):
        browser.validate_browser_config(plan, plan["browserConfig"])


def test_wrong_observed_workspace_blocks_before_selection():
    plan = azure_plan()
    page = Page(plan)
    page.nodes["#workspace"] = {"data-workspaceResourceId": "wrong", "data-workspaceCustomerId": "wrong"}
    with pytest.raises(ValueError, match="observed DOM"):
        browser._DOMRun(plan, lambda: None).run(mock.Mock(), page)
    assert page.actions == ["goto"]


def test_defender_portal_also_requires_observed_locked_workspace():
    plan = standalone_plan()
    plan["target"]["workspaceResourceId"] = "/reviewed/locked/workspace"
    with pytest.raises(ValueError, match="workspace"):
        browser.validate_browser_config(plan, plan["browserConfig"])
    plan["readinessSelectors"]["workspace"] = "#workspace"
    plan["browserConfig"]["readiness"]["workspaceResourceId"] = attr(
        "#workspace", "data-workspace", plan["target"]["workspaceResourceId"],
    )
    browser.validate_browser_config(plan, plan["browserConfig"])
    page = Page(plan)
    capture = browser._DOMRun(plan, lambda: None).run(mock.Mock(), page)
    qualification._validate_ui_capture(plan, capture)
    capture["readiness"].pop("workspaceResourceId")
    with pytest.raises(ValueError, match="workspace"):
        qualification._validate_ui_capture(plan, capture)


def test_azure_ui_plan_uses_existing_selected_run_and_provenance_contract(qualified_source):
    root, state = qualified_source
    legacy = ui_plan(root)
    plan = azure_plan()
    plan["target"], plan["contentId"], plan["instanceId"] = legacy["target"], legacy["contentId"], legacy["instanceId"]
    for key in ("tenantId", "contentId", "instanceId", "workspaceResourceId", "workspaceCustomerId"):
        plan["browserConfig"]["readiness"][key]["expected"] = plan["target"][key] if key in plan["target"] else plan[key]
    planned = qualification.plan_workbook_ui(
        root, workbook=legacy["workbook"], url=plan["url"], readiness_selectors=plan["readinessSelectors"],
        steps=plan["steps"], background_activity_review=plan["backgroundActivityReview"],
        browser_config=plan["browserConfig"],
    )
    assert planned["runId"] == state["runId"] and planned["schemaVersion"] == "1.1.0"
    assert len(planned["sourceSha256"]) == 64
    assert qualification.current_workbook_ui_plan(root, planned) == planned
    with pytest.raises(ValueError, match="browser configuration"):
        qualification.plan_workbook_ui(
            root, workbook=legacy["workbook"], url=plan["url"], readiness_selectors=plan["readinessSelectors"],
            steps=plan["steps"], background_activity_review=plan["backgroundActivityReview"],
        )
    with pytest.raises(ValueError, match="selected Defender workbook"):
        qualification.plan_workbook_ui(
            root, workbook="Workbooks/LinuxMachines.json", url=plan["url"], readiness_selectors=plan["readinessSelectors"],
            steps=plan["steps"], background_activity_review=plan["backgroundActivityReview"],
            browser_config=plan["browserConfig"],
        )


def extended_plan():
    plan = standalone_plan()
    plan["steps"].extend([
        {"id": "exact-data", "kind": "data", "action": "observe", "assertions": [
            {"selector": "#panel", "kind": "texts", "expected": ["ok"]},
            {"selector": "#panel", "kind": "count", "expected": 1},
        ]},
        {"id": "tab-details", "kind": "tabs", "action": "click", "selector": "#tab", "assertions": [
            attr("#tab", "aria-selected", "true"), text("#panel", "ok"),
        ]},
        {"id": "reset-filter", "kind": "reset", "action": "select", "selector": "#filter", "value": "initial",
         "before": [value("#filter", "one")], "assertions": [value("#filter", "initial"), text("#panel", "ok")]},
    ])
    return plan


def test_data_tabs_and_reset_produce_reusable_exact_proofs():
    plan = extended_plan()
    browser.validate_browser_config(plan, plan["browserConfig"])
    page = Page(plan)
    page.nodes["#tab"] = {"text": "Details", "aria-selected": "false"}
    original = Locator.click

    def click(locator, **kwargs):
        if locator.selector == "#tab":
            locator.page.actions.append("click-tab")
            locator.page.nodes["#tab"]["aria-selected"] = "true"
        else:
            original(locator, **kwargs)

    with mock.patch.object(Locator, "click", click):
        capture = browser._DOMRun(plan, lambda: None).run(mock.Mock(), page)
    qualification._validate_ui_capture(plan, capture)
    assert len(capture["steps"]) == 10
    assert page.nodes["#filter"]["value"] == "initial"
    capture["steps"][7]["assertions"][0]["actualSha256"] = "0" * 64
    with pytest.raises(ValueError, match="exact expectations"):
        qualification._validate_ui_capture(plan, capture)


@pytest.mark.parametrize("mutation", ["missing-before", "no-change", "unselected-tab", "missing-tab-panel", "missing-reset-panel", "missing-data", "bool-count", "empty-texts"])
def test_extended_checks_need_real_assertions(mutation):
    plan = extended_plan()
    if mutation == "missing-before":
        plan["steps"][-1].pop("before")
    elif mutation == "no-change":
        plan["steps"][-1]["before"] = [value("#filter", "initial")]
    elif mutation == "unselected-tab":
        plan["steps"][-2]["assertions"] = [text("#panel", "ok")]
    elif mutation == "missing-tab-panel":
        plan["steps"][-2]["assertions"] = [attr("#tab", "aria-selected", "true")]
    elif mutation == "missing-reset-panel":
        plan["steps"][-1]["assertions"] = [value("#filter", "initial")]
    elif mutation == "missing-data":
        plan["steps"][-3]["assertions"] = [attr("#panel", "data-ready", "true")]
    elif mutation == "bool-count":
        plan["steps"][-3]["assertions"][1]["expected"] = True
    else:
        plan["steps"][-3]["assertions"][0]["expected"] = []
    with pytest.raises(ValueError):
        browser.validate_browser_config(plan, plan["browserConfig"])


def test_rows_assert_order_and_visibility_and_zero_count_is_explicit():
    plan = standalone_plan()
    engine = browser._DOMRun(plan, lambda: None)
    locator = mock.Mock()
    rows = [mock.Mock(), mock.Mock()]
    for row, content in zip(rows, ["alpha", "beta"], strict=True):
        row.is_visible.return_value = True
        row.inner_text.return_value = content
    locator.count.return_value = 2
    locator.nth.side_effect = rows.__getitem__
    page = mock.Mock()
    page.locator.return_value = locator
    assertion = {"selector": "#reviewed-rows", "kind": "texts", "expected": ["alpha", "beta"]}
    assert engine.observe(page, assertion) == ["alpha", "beta"]
    assertion["expected"].reverse()
    with pytest.raises(ValueError, match="observed DOM"):
        engine.observe(page, assertion)
    assertion["expected"].reverse()
    rows[0].is_visible.return_value = False
    with pytest.raises(ValueError, match="observed DOM"):
        engine.observe(page, assertion)
    locator.count.return_value = 0
    assert engine.observe(page, {"selector": "#reviewed-rows", "kind": "count", "expected": 0}) == 0


def runner_evidence(workbook="XDR Workbooks/fixture.json"):
    plan = standalone_plan()
    plan["workbook"] = workbook
    capture = browser._DOMRun(plan, lambda: None).run(mock.Mock(), Page(plan))
    return {"plan": plan, "capture": capture}


@pytest.mark.parametrize("evidence", [None, {}, {"status": "passed"}, {
    "status": "passed", "tilesRendered": True, "checkedKinds": ["open", "parameters", "tiles", "tabs", "conditional"],
    "queryErrors": [], "javascriptErrors": [], "saveEditObserved": False,
}])
def test_legacy_helper_never_qualifies_missing_runner_or_boolean_claims(evidence):
    result = verify_workbook_playwright_rendering(
        Path.cwd(), workbooks=["XDR Workbooks/fixture.json"], target={"tenantId": "tenant-observed"},
        playwright_runner=None if evidence is None else lambda *_: evidence,
    )
    assert result["status"] == "failed"
    assert result["playwrightVerified"] is False


def test_legacy_helper_requires_matching_capture_and_exact_proofs():
    evidence = runner_evidence()
    target = evidence["plan"]["target"]
    def verify(item):
        return verify_workbook_playwright_rendering(
            Path.cwd(), workbooks=[evidence["plan"]["workbook"]], target=target, playwright_runner=lambda *_: item,
        )
    assert verify(evidence)["playwrightVerified"] is True
    for mutate in (
        lambda item: item["capture"]["steps"][0].pop("assertions"),
        lambda item: item["capture"].update(producer="synthetic"),
        lambda item: item["plan"]["target"].update(tenantId="wrong"),
        lambda item: item["plan"].update(workbook="wrong"),
    ):
        changed = deepcopy(evidence)
        mutate(changed)
        assert verify(changed)["playwrightVerified"] is False


def test_provider_exception_is_sanitized_and_no_workbooks_stays_not_applicable():
    def failure(*_):
        raise RuntimeError("Authorization: PRIVATE")
    result = verify_workbook_playwright_rendering(
        Path.cwd(), workbooks=["fixture"], target={}, playwright_runner=failure,
    )
    assert "PRIVATE" not in str(result) and result["playwrightVerified"] is False
    assert verify_workbook_playwright_rendering(Path.cwd())["playwrightVerified"] == "not_applicable"


@pytest.mark.parametrize("mode", ["missing-query", "missing-browser", "browser-skipped", "empty-inventory", "query-incomplete", "query-failed", "query-bool-count"])
def test_orchestrator_cannot_promote_missing_skipped_or_incomplete_workbook_evidence(mode):
    instance = orchestrator.QualificationOrchestrator.__new__(orchestrator.QualificationOrchestrator)
    wb = "XDR Workbooks/fixture.json"
    instance.solution_root, instance.run_id = Path.cwd(), "offline-contract-fixture"
    instance.plan = {
        "target": {"tenantId": "tenant-observed"}, "expectedContentCounts": {"workbooksCount": 1},
        "inventory": {"defenderWorkbookPaths": [] if mode == "empty-inventory" else [wb]},
    }
    instance.state = {
        "qualificationStages": {"workbook_qualification": {}, "rule_parity": {"status": "passed"}},
        "mockIngestionVerified": True, "ruleParityVerified": True,
    }
    query = {"workbook": wb, "status": "passed", "executedQueryCount": 1, "failedQueryCount": 0}
    if mode == "query-incomplete":
        del query["failedQueryCount"]
    if mode == "query-bool-count":
        query["executedQueryCount"] = True
    if mode == "query-failed":
        query["status"] = "failed"
    instance.workbook_query_runner = None if mode == "missing-query" else lambda *_: query
    instance.playwright_runner = None if mode == "missing-browser" else lambda *_: runner_evidence(wb)
    instance.enable_playwright = mode != "browser-skipped"
    instance._persist_state = lambda state: state
    instance._validate_runtime_query_consent = lambda: (True, [])
    with mock.patch.object(orchestrator, "using_run", return_value=nullcontext()), mock.patch.object(
        orchestrator, "audit_private_config_and_support_export", return_value={"status": "isolated", "supportExportsRedacted": True},
    ):
        result = instance.run_workbook_qualification()
    assert result["workbookQualificationVerified"] is False
    assert result["workbookContractResult"]["accepted"] is False
    assert result["qualificationStages"]["workbook_qualification"]["status"] == "failed"


@pytest.mark.parametrize("evidence", [
    {"workbookQualificationVerified": "not_applicable"},
    {"qualificationStages": {"workbook_qualification": {"status": "notRequired"}}},
    {"workbookQualificationVerified": True, "workbookContractResult": {
        "accepted": True, "status": "passed", "playwrightVerification": {"status": "skipped", "playwrightVerified": True},
    }},
])
def test_promotion_cannot_reuse_skipped_or_inapplicable_evidence_for_nonempty_inventory(evidence):
    result = orchestrator.evaluate_qualification_promotion_gate({
        "expectedContentCounts": {"workbooksCount": 1, "sentinelRulesCount": 0, "customDetectionsCount": 0},
        **evidence,
    })
    assert result["workbookQualificationVerified"] is False
    assert result["passed"] is False
