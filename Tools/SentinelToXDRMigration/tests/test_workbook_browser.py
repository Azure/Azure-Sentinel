from __future__ import annotations

from copy import deepcopy
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import sys
import threading
from types import ModuleType
from unittest import mock
from uuid import uuid4

import pytest

from sentinel_xdr_migration import workbook_browser as browser
from sentinel_xdr_migration import workbook_qualification as qualification
from sentinel_xdr_migration.artifacts import report_directory
from test_workbook_qualification import qualified_source, ui_plan, consent, cli_run


def text(selector, expected):
    return {"selector": selector, "kind": "text", "expected": expected}


def attr(selector, attribute, expected):
    return {"selector": selector, "kind": "attribute", "attribute": attribute, "expected": expected}


def value(selector, expected):
    return {"selector": selector, "kind": "value", "expected": expected}


def reviewed_browser(plan):
    panel = text("#panel", "ok")
    steps = [
        {"id": "pickers", "kind": "pickers", "action": "select", "selector": "#picker", "value": "one",
         "assertions": [value("#picker", "one"), panel]},
        {"id": "dependent-refresh", "kind": "dependent-refresh", "action": "select",
         "selector": "#picker", "value": "two", "before": [text("#dependent", "before")],
         "assertions": [value("#picker", "two"), text("#dependent", "after")]},
        {"id": "filters", "kind": "filters", "action": "select", "selector": "#filter", "value": "one",
         "assertions": [value("#filter", "one"), panel]},
        {"id": "drill-down", "kind": "drill-down", "action": "drill-down", "selector": "#details",
         "expectedUrl": plan["url"], "assertions": [text("#drill", "opened")]},
        {"id": "reload", "kind": "reload", "action": "reload", "assertions": [text("#drill", "closed"), panel]},
        {"id": "layout", "kind": "layout", "action": "observe", "assertions": [{
            "selector": "#panel", "kind": "layout",
            "bounds": {"x": [0, 100], "y": [0, 300], "width": [50, 1000], "height": [5, 100]},
        }]},
        {"id": "conditional-visibility", "kind": "conditional-visibility", "action": "observe",
         "assertions": [{"selector": "#conditional", "kind": "hidden"}, panel]},
    ]
    config = {
        "schemaVersion": "1.0.0", "storageStateSha256": "0" * 64,
        "readiness": {
            "tenantId": attr("#tenant", "data-tenant", plan["target"]["tenantId"]),
            "contentId": attr("#workbook", "data-content", plan["contentId"]),
            "instanceId": attr("#workbook", "data-instance", plan["instanceId"]),
            "ready": attr("#ready", "data-ready", "true"),
        },
        "sessionAssertions": [text("#session", "signed in")],
        "guards": {"queryErrors": ["#query-error"], "prohibitedControls": ["#edit", "#save"], "signedOut": ["#login"]},
        "network": {
            "requests": [{"url": plan["url"], "methods": ["GET"], "purpose": "asset"}],
            "navigationUrls": [plan["url"]],
        },
        "timeoutMs": 100, "familyTimeoutSeconds": 30, "settleMs": 100,
        "viewport": {"width": 1024, "height": 768},
    }
    return steps, config


def standalone_plan():
    plan = {
        "target": {"tenantId": "tenant-observed"}, "contentId": "canonical-observed",
        "instanceId": "installed-observed", "url": "https://security.microsoft.com/workbooks/fixture",
        "readinessSelectors": {"tenant": "#tenant", "workbook": "#workbook", "ready": "#ready"},
        "backgroundActivityReview": "Explicit exact background request review.", "saveEditAllowed": False,
    }
    plan["steps"], plan["browserConfig"] = reviewed_browser(plan)
    return plan


class Locator:
    def __init__(self, page, selector):
        self.page, self.selector = page, selector

    def count(self):
        return 1 if self.selector in self.page.nodes else 0

    def nth(self, index):
        return self

    def wait_for(self, **kwargs):
        if not self.count() or kwargs["state"] == "visible" and not self.is_visible():
            raise RuntimeError("synthetic missing selector; sensitive detail must not escape")

    def is_visible(self):
        return self.count() and self.page.nodes[self.selector].get("visible", True)

    def is_disabled(self, **kwargs):
        return not self.page.nodes[self.selector].get("enabled", True)

    def inner_text(self, **kwargs):
        return self.page.nodes[self.selector].get("text", "")

    def get_attribute(self, name, **kwargs):
        return self.page.nodes[self.selector].get(name)

    def input_value(self, **kwargs):
        return self.page.nodes[self.selector].get("value", "")

    def bounding_box(self, **kwargs):
        return {"x": 8, "y": 50, "width": 400, "height": 20}

    def select_option(self, value, **kwargs):
        self.page.actions.append("select")
        self.page.nodes[self.selector]["value"] = value
        if self.selector == "#picker" and value == "two":
            self.page.nodes["#dependent"]["text"] = "after"

    def click(self, **kwargs):
        self.page.actions.append("click")
        if self.selector == "#custom-filter":
            self.page.nodes["#custom-option"]["visible"] = True
        elif self.selector == "#custom-option":
            self.page.nodes["#custom-filter"]["data-value"] = "one"
            self.page.nodes["#custom-option"]["visible"] = False
        else:
            self.page.nodes["#drill"]["text"] = "opened"


class Page:
    def __init__(self, plan):
        self.url, self.actions, self.handlers = plan["url"], [], {}
        self.nodes = {
            "#tenant": {"data-tenant": plan["target"]["tenantId"]},
            "#workbook": {"data-content": plan["contentId"], "data-instance": plan["instanceId"]},
            "#ready": {"data-ready": "true"}, "#session": {"text": "signed in"},
            "#panel": {"text": "ok"}, "#picker": {"text": "Picker", "value": "initial"},
            "#filter": {"text": "Filter", "value": "initial"},
            "#dependent": {"text": "before"}, "#details": {"text": "Details"},
            "#drill": {"text": "closed"}, "#conditional": {"visible": False},
        }

    def locator(self, selector):
        return Locator(self, selector)

    def set_default_timeout(self, timeout):
        pass

    def set_default_navigation_timeout(self, timeout):
        pass

    def on(self, name, handler):
        self.handlers[name] = handler

    def goto(self, url, **kwargs):
        self.actions.append("goto")
        self.url = url

    def reload(self, **kwargs):
        self.actions.append("reload")
        self.nodes["#drill"]["text"] = "closed"

    def wait_for_url(self, url, **kwargs):
        assert self.url == url

    def wait_for_timeout(self, ms):
        pass


@pytest.fixture
def scratch():
    directory = Path.cwd() / f".workbook-browser-tests-{uuid4().hex}"
    directory.mkdir(mode=0o700)
    try:
        yield directory
    finally:
        shutil.rmtree(directory)


def test_real_dom_engine_exercises_every_check_without_copying_identity():
    plan = standalone_plan()
    browser.validate_browser_config(plan, plan["browserConfig"])
    guard = mock.Mock()
    page = Page(plan)
    capture = browser._DOMRun(plan, guard).run(mock.Mock(), page)
    assert len(capture["steps"]) == 7
    assert page.actions == ["goto", "select", "select", "select", "click", "reload"]
    assert capture["readiness"] == {
        "tenantId": "tenant-observed", "contentId": "canonical-observed",
        "instanceId": "installed-observed", "ready": True,
    }
    assert capture["browserWideNoWriteSandbox"] is False
    assert guard.call_count > 20
    assert "cookies" not in json.dumps(capture)


def custom_filter(plan):
    plan["steps"][2].update({
        "selector": "#custom-filter", "selectMode": "option", "optionSelector": "#custom-option",
        "assertions": [attr("#custom-filter", "data-value", "one"), text("#panel", "ok")],
    })


def test_custom_dropdown_uses_only_reviewed_option_and_observed_value():
    plan = standalone_plan()
    custom_filter(plan)
    browser.validate_browser_config(plan, plan["browserConfig"])
    page = Page(plan)
    page.nodes.update({
        "#custom-filter": {"text": "Filter", "data-value": "initial"},
        "#custom-option": {"text": "One", "visible": False},
    })
    capture = browser._DOMRun(plan, lambda: None).run(mock.Mock(), page)
    assert len(capture["steps"]) == 7
    assert page.actions == ["goto", "select", "select", "click", "click", "click", "reload"]
    del plan["steps"][2]["optionSelector"]
    with pytest.raises(ValueError, match="selector"):
        browser.validate_browser_config(plan, plan["browserConfig"])


@pytest.mark.parametrize("field", ["tenantId", "contentId", "instanceId", "ready"])
def test_unobserved_or_wrong_identity_never_passes(field):
    plan = standalone_plan()
    page = Page(plan)
    assertion = plan["browserConfig"]["readiness"][field]
    page.nodes[assertion["selector"]][assertion["attribute"]] = "wrong"
    with pytest.raises(ValueError, match="observed DOM"):
        browser._DOMRun(plan, lambda: None).run(mock.Mock(), page)
    assert page.actions == ["goto"]


@pytest.mark.parametrize("fault", [
    "missing-panel", "query-error", "edit", "signed-out", "wrong-session",
    "ambiguous", "disabled", "unsafe-label", "wrong-layout", "deadline",
])
def test_dom_safety_failures_block_actions(fault):
    plan = standalone_plan()
    page = Page(plan)
    engine = browser._DOMRun(plan, lambda: None)
    if fault == "missing-panel":
        del page.nodes["#panel"]
    elif fault in {"query-error", "edit", "signed-out"}:
        page.nodes[{"query-error": "#query-error", "edit": "#edit", "signed-out": "#login"}[fault]] = {}
    elif fault == "wrong-session":
        page.nodes["#session"]["text"] = "signed out"
    elif fault == "ambiguous":
        page.locator = lambda _: mock.Mock(count=lambda: 2, wait_for=lambda **kw: None, nth=lambda i: mock.Mock(is_visible=lambda: False))
    elif fault == "disabled":
        page.nodes["#picker"]["enabled"] = False
    elif fault == "unsafe-label":
        page.nodes["#picker"]["aria-label"] = "Save workbook"
    elif fault == "wrong-layout":
        plan["steps"][5]["assertions"][0]["bounds"]["width"] = [1, 2]
    else:
        engine.deadline = 0
    with pytest.raises((ValueError, RuntimeError)):
        engine.run(mock.Mock(), page)
    if fault in {"query-error", "edit", "signed-out", "wrong-session", "disabled", "unsafe-label", "deadline"}:
        assert "select" not in page.actions


@pytest.mark.parametrize("event", [
    "pageerror", "console", "response", "requestfailed", "websocket", "download", "dialog", "framenavigated",
])
def test_error_events_are_fail_closed_and_sanitized(event):
    plan = standalone_plan()
    page, context = Page(plan), mock.Mock()
    engine = browser._DOMRun(plan, lambda: None)
    engine.attach(context, page)
    message = mock.Mock(type="error", status=500, url="https://attacker.invalid/token=secret")
    page.handlers[event](message)
    with pytest.raises(ValueError) as failure:
        engine.check()
    assert "secret" not in str(failure.value)
    assert "attacker" not in str(failure.value)


def test_network_and_popups_are_rejected_without_retaining_headers_or_urls():
    plan = standalone_plan()
    page, context = Page(plan), mock.Mock()
    engine = browser._DOMRun(plan, lambda: None)
    engine.attach(context, page)
    route = mock.Mock(request=mock.Mock(url=plan["url"], method="GET"))
    handler = context.route.call_args.args[1]
    handler(route)
    route.continue_.assert_called_once()
    route = mock.Mock(request=mock.Mock(url="https://unreviewed.invalid/?token=secret", method="POST"))
    handler(route)
    route.abort.assert_called_once()
    route.continue_.assert_not_called()
    with pytest.raises(ValueError, match="unreviewed-request"):
        engine.check()
    assert "secret" not in json.dumps(engine.events)
    for event in ("page", "serviceworker"):
        callback = next(call.args[1] for call in context.on.call_args_list if call.args[0] == event)
        callback(mock.Mock())
    socket = mock.Mock()
    context.route_web_socket.call_args.args[1](socket)
    socket.close.assert_called_once()
    assert {"unexpected-page", "unexpected-service-worker", "unreviewed-websocket"} <= engine.faults


@pytest.mark.parametrize("mutation", [
    "missing-readiness", "wrong-identity", "same-identities", "empty-session", "negative-session",
    "empty-guards", "wildcard-url", "write-method", "post-asset", "unapproved-navigation",
    "arbitrary-code", "empty-assertions", "incomplete-refresh", "unobserved-selection",
    "unexercised-reload", "missing-layout", "missing-visibility", "unbounded", "unknown-action",
])
def test_configuration_requires_complete_exact_reviewed_contract(mutation):
    plan = standalone_plan()
    config = plan["browserConfig"]
    if mutation == "missing-readiness":
        del config["readiness"]["instanceId"]
    elif mutation == "wrong-identity":
        config["readiness"]["tenantId"]["expected"] = "other"
    elif mutation == "same-identities":
        config["readiness"]["instanceId"] = config["readiness"]["contentId"]
    elif mutation == "empty-session":
        config["sessionAssertions"] = []
    elif mutation == "negative-session":
        config["sessionAssertions"] = [{"selector": "#login", "kind": "hidden"}]
    elif mutation == "empty-guards":
        config["guards"]["queryErrors"] = []
    elif mutation == "wildcard-url":
        config["network"]["navigationUrls"] = ["https://*.microsoft.com/*"]
    elif mutation == "write-method":
        config["network"]["requests"][0]["methods"] = ["PUT"]
    elif mutation == "post-asset":
        config["network"]["requests"][0]["methods"] = ["POST"]
    elif mutation == "unapproved-navigation":
        plan["steps"][3]["expectedUrl"] = "https://security.microsoft.com/other"
    elif mutation == "arbitrary-code":
        config["eval"] = "window.secret"
    elif mutation == "empty-assertions":
        plan["steps"][0]["assertions"] = []
    elif mutation == "incomplete-refresh":
        plan["steps"][1]["before"] = []
    elif mutation == "unobserved-selection":
        plan["steps"][0]["assertions"] = [text("#panel", "ok")]
    elif mutation == "unexercised-reload":
        plan["steps"][4]["action"] = "observe"
    elif mutation == "missing-layout":
        plan["steps"][5]["assertions"] = [text("#panel", "ok")]
    elif mutation == "missing-visibility":
        plan["steps"][6]["assertions"] = [text("#panel", "ok")]
    elif mutation == "unbounded":
        config["familyTimeoutSeconds"] = 999999
    else:
        plan["steps"][5]["action"] = "execute-python"
    with pytest.raises(ValueError):
        browser.validate_browser_config(plan, config)


def test_private_storage_is_hash_bound_owner_only_and_never_exported(scratch):
    path = scratch / "auth.json"
    raw = json.dumps({"cookies": [{"value": "PRIVATE"}], "origins": []}).encode()
    path.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    path.chmod(0o600)
    assert browser._private_storage(path, digest)["cookies"][0]["value"] == "PRIVATE"
    for mode, expected in ((0o644, digest), (0o600, "0" * 64)):
        path.chmod(mode)
        with pytest.raises(ValueError) as failure:
            browser._private_storage(path, expected)
        assert "PRIVATE" not in str(failure.value)
    link = scratch / "linked.json"
    link.symlink_to(path)
    with pytest.raises(ValueError, match="symbolic"):
        browser._private_storage(link, digest)
    path.write_text('{"cookies":[],"origins":[]}')
    with pytest.raises(ValueError, match="authenticated"):
        browser._private_storage(path, hashlib.sha256(path.read_bytes()).hexdigest())


def test_producer_closes_fresh_context_and_sanitizes_playwright_failures(scratch):
    plan = standalone_plan()
    path = scratch / "auth.json"
    path.write_text('{"cookies":[{"name":"private","value":"PRIVATE"}],"origins":[]}')
    path.chmod(0o600)
    plan["browserConfig"]["storageStateSha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    playwright = mock.MagicMock()
    context = playwright.chromium.launch.return_value.new_context.return_value
    page = Page(plan)
    context.new_page.return_value = page
    entry = mock.MagicMock()
    entry.__enter__.return_value = playwright
    api = ModuleType("playwright.sync_api")
    api.sync_playwright = mock.Mock(return_value=entry)
    package = ModuleType("playwright")
    with mock.patch.dict(sys.modules, {"playwright": package, "playwright.sync_api": api}):
        result = browser.capture_workbook_browser(plan, storage_state=path, before_action=lambda: None)
    assert result["producer"] == "playwright-dom-v1"
    context.close.assert_called_once()
    playwright.chromium.launch.return_value.close.assert_called_once()
    assert playwright.chromium.launch.return_value.new_context.call_args.kwargs["service_workers"] == "block"
    page.goto = mock.Mock(side_effect=RuntimeError("Authorization: PRIVATE"))
    with mock.patch.dict(sys.modules, {"playwright": package, "playwright.sync_api": api}):
        with pytest.raises(ValueError) as failure:
            browser.capture_workbook_browser(plan, storage_state=path, before_action=lambda: None)
    assert "PRIVATE" not in str(failure.value)
    assert failure.value.diagnostic_events[-1]["status"] == "failed"
    assert "PRIVATE" not in json.dumps(failure.value.diagnostic_events)


def test_optional_dependency_missing_is_a_clean_failure(scratch):
    plan = standalone_plan()
    path = scratch / "auth.json"
    path.write_text('{"cookies":[{"value":"PRIVATE"}],"origins":[]}')
    path.chmod(0o600)
    plan["browserConfig"]["storageStateSha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    original = __import__

    def import_without_browser(name, *args, **kwargs):
        if name.startswith("playwright"):
            raise ImportError("not installed")
        return original(name, *args, **kwargs)

    with mock.patch("builtins.__import__", side_effect=import_without_browser):
        with pytest.raises(ValueError, match="optional browser dependency"):
            browser.capture_workbook_browser(plan, storage_state=path, before_action=lambda: None)


@pytest.mark.parametrize("change", ["withdrawn", "input"])
def test_latest_guard_is_checked_between_browser_actions(change):
    plan, approval = standalone_plan(), {"approved": True}
    page = Page(plan)
    changed = False
    original = Locator.select_option

    def guarded():
        if not approval["approved"]:
            raise ValueError("withdrawn")
        if changed:
            raise ValueError("changed input")

    def select(locator, *args, **kwargs):
        nonlocal changed
        original(locator, *args, **kwargs)
        if change == "withdrawn":
            approval["approved"] = False
        else:
            changed = True

    with mock.patch.object(Locator, "select_option", select):
        with pytest.raises(ValueError):
            browser._DOMRun(plan, guarded).run(mock.Mock(), page)
    assert page.actions == ["goto", "select"]


def test_assertions_must_remain_true_after_settling():
    plan = standalone_plan()
    page = Page(plan)
    page.wait_for_timeout = lambda _: page.nodes["#panel"].update(text="query failed")
    with pytest.raises(ValueError, match="observed DOM"):
        browser._DOMRun(plan, lambda: None).run(mock.Mock(), page)


@pytest.mark.parametrize("change", ["missing", "identity", "value", "layout"])
def test_versioned_capture_cannot_omit_or_forge_assertion_proofs(change):
    plan = standalone_plan()
    capture = browser._DOMRun(plan, lambda: None).run(mock.Mock(), Page(plan))
    if change == "layout":
        index = 5
        capture["steps"][index]["assertions"][0]["measurement"]["width"] = 200000
    else:
        index = 0
        if change == "missing":
            capture["steps"][index].pop("assertions")
        elif change == "identity":
            capture["steps"][index]["assertions"][0]["assertionSha256"] = "0" * 64
        else:
            capture["steps"][index]["assertions"][0]["actualSha256"] = "0" * 64
    with pytest.raises(ValueError):
        browser.validate_browser_step_proofs(plan["steps"][index], capture["steps"][index])


def test_evidence_must_be_ignored_untracked_and_private(qualified_source):
    root, _ = qualified_source
    with mock.patch.object(browser.subprocess, "run", return_value=mock.Mock(returncode=1, stdout=b"")):
        with pytest.raises(ValueError, match="Git-ignored"):
            browser.prepare_private_browser_evidence(root)
    with mock.patch.object(browser.subprocess, "run", side_effect=[
        mock.Mock(returncode=0), mock.Mock(returncode=0, stdout=b"tracked evidence"),
    ]):
        with pytest.raises(ValueError, match="untracked"):
            browser.prepare_private_browser_evidence(root)
    browser.prepare_private_browser_evidence(root)
    assert report_directory(root).stat().st_mode & 0o077 == 0


def test_no_import_time_browser_dependency_and_legacy_plan_cannot_dispatch():
    plan = standalone_plan()
    del plan["browserConfig"]
    with mock.patch("builtins.__import__", side_effect=AssertionError("must not import")):
        with pytest.raises(ValueError, match="reviewed versioned"):
            browser.capture_workbook_browser(plan, storage_state="missing", before_action=lambda: None)


def test_browser_plan_is_versioned_and_bound_to_source_config_and_expected_values(qualified_source):
    root, _ = qualified_source
    legacy = ui_plan(root)
    steps, config = reviewed_browser(legacy)
    plan = qualification.plan_workbook_ui(
        root, workbook=legacy["workbook"], url=legacy["url"], readiness_selectors=legacy["readinessSelectors"],
        steps=steps, background_activity_review=legacy["backgroundActivityReview"], browser_config=config,
    )
    assert legacy["schemaVersion"] == "1.0.0"
    assert "browserConfig" not in legacy
    assert plan["schemaVersion"] == "1.1.0" and len(plan["sourceSha256"]) == 64
    assert qualification.current_workbook_ui_plan(root, plan) == plan
    changed = deepcopy(plan)
    changed["browserConfig"]["viewport"]["width"] += 1
    assert qualification.current_workbook_ui_plan(root, changed)["planSha256"] != plan["planSha256"]
    called = mock.Mock()
    with pytest.raises(ValueError, match="stale"):
        qualification.execute_workbook_ui(root, changed, read_consent=lambda: consent(plan), browser_runner=called)
    called.assert_not_called()


@pytest.mark.parametrize("change", ["withdrawn", "source", "target", "revoked-after-capture"])
def test_execution_rechecks_live_consent_and_inputs_and_persists_failure(qualified_source, change):
    root, _ = qualified_source
    legacy = ui_plan(root)
    steps, config = reviewed_browser(legacy)
    plan = qualification.plan_workbook_ui(
        root, workbook=legacy["workbook"], url=legacy["url"], readiness_selectors=legacy["readinessSelectors"],
        steps=steps, background_activity_review=legacy["backgroundActivityReview"], browser_config=config,
    )
    approval = consent(plan)

    def capture(current, *, before_action, **kwargs):
        page = Page(current)
        engine = browser._DOMRun(current, before_action)
        if change == "withdrawn":
            approval["withdrawn"] = True
        elif change == "source":
            source = root / "Workbooks/LinuxMachines.json"
            source.write_bytes(source.read_bytes() + b"\n")
        elif change == "target":
            output = root / current["workbook"]
            output.write_bytes(output.read_bytes() + b"\n")
        result = engine.run(mock.Mock(), page)
        if change == "revoked-after-capture":
            approval["withdrawn"] = True
        return result

    with mock.patch.object(browser, "capture_workbook_browser", side_effect=capture):
        with pytest.raises(ValueError):
            browser.execute_workbook_browser(root, plan, read_consent=lambda: approval, storage_state="unused")
    report = report_directory(root) / f"workbook-ui.{plan['contentId']}.json"
    assert json.loads(report.read_bytes())["status"] == "failed"
    assert report_directory(root).stat().st_mode & 0o077 == 0


def test_execute_cli_uses_current_hash_and_explicit_run_and_preserves_import(qualified_source):
    root, state = qualified_source
    legacy = ui_plan(root)
    steps, config = reviewed_browser(legacy)
    paths = {}
    for name, content in (("selectors", legacy["readinessSelectors"]), ("steps", steps), ("browser", config)):
        path = report_directory(root) / f"reviewed-{name}.json"
        path.write_text(json.dumps(content))
        paths[name] = path.relative_to(root).as_posix()
    common = ["--solution", str(root), "--run-id", state["runId"]]
    code, planned, error = cli_run([
        "workbook-ui-plan", *common, "--workbook", legacy["workbook"], "--url", legacy["url"],
        "--readiness-selectors", paths["selectors"], "--steps", paths["steps"], "--browser-config", paths["browser"],
        "--background-activity-review", legacy["backgroundActivityReview"],
    ])
    assert code == 0, error
    binding = ["--plan", planned["planPath"], "--plan-sha256", planned["planSha256"]]
    code, _, error = cli_run([
        "workbook-ui-review", *common, *binding, "--actor", "reviewer",
        "--reference", "explicit-browser-read-approval", "--decision", "approved",
    ])
    assert code == 0, error

    def capture(current, *, before_action, **kwargs):
        return browser._DOMRun(current, before_action).run(mock.Mock(), Page(current))

    with mock.patch.object(browser, "capture_workbook_browser", side_effect=capture):
        code, result, error = cli_run(["workbook-ui-execute", *common, *binding, "--storage-state", "unused"])
    assert code == 0, error
    assert result["browserExecution"] == "playwright-dom-v1"
    assert result["queryQualification"] == "separate"
    code, _, error = cli_run([
        "workbook-ui-execute", *common, "--plan", planned["planPath"], "--plan-sha256", "0" * 64,
        "--storage-state", "unused",
    ])
    assert code == 2 and "exact reviewed" in error
    with pytest.raises(SystemExit):
        cli_run(["workbook-ui-execute", "--solution", str(root), *binding, "--storage-state", "unused"])


def test_local_loopback_browser_smoke():
    api = pytest.importorskip("playwright.sync_api")
    with api.sync_playwright() as playwright:
        if not Path(playwright.chromium.executable_path).is_file():
            pytest.skip("local Chromium is not installed")
        plan = standalone_plan()
        html = b"""<!doctype html><meta charset="utf-8">
<div id="tenant" data-tenant="tenant-observed">Tenant</div>
<div id="workbook" data-content="canonical-observed" data-instance="installed-observed">Workbook</div>
<div id="ready" data-ready="true">Ready</div><div id="session">signed in</div>
<select id="picker" onchange="document.getElementById('dependent').textContent=this.value==='two'?'after':'before'">
<option value="initial">Initial</option><option value="one">One</option><option value="two">Two</option></select>
<select id="filter"><option value="initial">Initial</option><option value="one">One</option></select>
<button id="custom-filter" data-value="initial" onclick="document.getElementById('custom-option').style.display='inline'">Filter</button>
<button id="custom-option" style="display:none" onclick="document.getElementById('custom-filter').dataset.value='one';this.style.display='none'">One</button>
<div id="dependent">before</div><button id="details" onclick="document.getElementById('drill').textContent='opened'">Details</button>
<div id="drill">closed</div><div id="panel" style="width:400px;height:20px">ok</div>
<div id="conditional" style="display:none">Conditional</div>"""

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(html)

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            plan["url"] = f"http://127.0.0.1:{server.server_port}/"
            plan["steps"], plan["browserConfig"] = reviewed_browser(plan)
            custom_filter(plan)
            plan["browserConfig"]["timeoutMs"] = 3000
            browser.validate_browser_config(plan, plan["browserConfig"])
            instance = playwright.chromium.launch(headless=True)
            try:
                context = instance.new_context(service_workers="block", accept_downloads=False, viewport=plan["browserConfig"]["viewport"])
                try:
                    result = browser._DOMRun(plan, lambda: None).run(context, context.new_page())
                finally:
                    context.close()
            finally:
                instance.close()
            assert len(result["steps"]) == 7
            assert result["readiness"]["instanceId"] == "installed-observed"
            assert result["queryErrors"] == result["javascriptErrors"] == []
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
