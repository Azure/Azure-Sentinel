"""Reviewed, bounded DOM assertions; never an authentication or deployment client."""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
import time
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qsl, urlsplit


class BrowserQualificationError(ValueError):
    """Sanitized failure: browser exceptions can contain credentials and URLs."""


def _fail(message: str) -> None:
    raise BrowserQualificationError(message)


def observation_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _keys(value: Any, required: set[str], optional: set[str] | None = None) -> None:
    if not isinstance(value, dict) or not required <= value.keys() or value.keys() - required - (optional or set()):
        _fail("browser configuration has missing or unsupported fields")


def _selector(value: Any) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > 1024:
        _fail("an exact reviewed DOM selector is required")


def _assertion(value: Any) -> None:
    _keys(value, {"selector", "kind"}, {"expected", "attribute", "bounds"})
    _selector(value["selector"])
    kind = value["kind"]
    if kind in {"text", "attribute", "value"}:
        if not isinstance(value.get("expected"), str) or len(value["expected"]) > 4096:
            _fail("DOM text, attribute and value assertions need exact expected strings")
        if kind == "attribute":
            if not isinstance(value.get("attribute"), str) or not re.fullmatch(r"[A-Za-z_][\w:.-]*", value["attribute"]):
                _fail("attribute assertion needs an exact attribute name")
        elif "attribute" in value:
            _fail("attribute name is only permitted for attribute assertions")
        if "bounds" in value:
            _fail("bounds are only permitted for layout assertions")
    elif kind in {"visible", "hidden"}:
        if set(value) != {"selector", "kind"}:
            _fail("visibility assertions do not accept expected values")
    elif kind == "layout":
        if set(value) != {"selector", "kind", "bounds"}:
            _fail("layout assertion requires reviewed bounds")
        _keys(value["bounds"], {"x", "y", "width", "height"})
        for axis, bounds in value["bounds"].items():
            if (
                not isinstance(bounds, list) or len(bounds) != 2
                or any(isinstance(n, bool) or not isinstance(n, (int, float)) or not -100000 <= n <= 100000 for n in bounds)
                or bounds[0] > bounds[1]
                or axis in {"width", "height"} and bounds[0] <= 0
            ):
                _fail("layout bounds must be finite ordered ranges with positive dimensions")
    else:
        _fail("unsupported DOM assertion kind")


def _assertions(values: Any) -> None:
    if not isinstance(values, list) or not 1 <= len(values) <= 50:
        _fail("each browser check needs a bounded, nonempty assertion list")
    for value in values:
        _assertion(value)


def _url(value: Any, origin: str | None) -> None:
    if not isinstance(value, str):
        _fail("reviewed browser URL is required")
    parsed = urlsplit(value)
    if (
        (parsed.scheme + "://" + parsed.netloc != origin if origin else parsed.scheme != "https" or not parsed.hostname)
        or parsed.username or parsed.password
        or "*" in value
        or any(key.casefold().replace("_", "").replace("-", "") in {
            "accesstoken", "refreshtoken", "idtoken", "token", "code", "sig",
            "signature", "clientsecret", "authorization", "cookie", "apikey",
        } for key, _ in parse_qsl(parsed.query) + parse_qsl(parsed.fragment.split("?", 1)[-1]))
    ):
        _fail("browser URLs must be exact approved URLs without credentials or signatures")


def validate_browser_config(plan: dict[str, Any], config: dict[str, Any]) -> None:
    """Validate the versioned, hash-bound contract without importing Playwright."""
    _keys(config, {
        "schemaVersion", "storageStateSha256", "readiness", "sessionAssertions",
        "guards", "network", "timeoutMs", "familyTimeoutSeconds", "settleMs", "viewport",
    })
    if config["schemaVersion"] != "1.0.0" or not re.fullmatch(r"[0-9a-f]{64}", str(config["storageStateSha256"])):
        _fail("browser configuration version or private session hash is invalid")
    for key, low, high in (("timeoutMs", 100, 30000), ("familyTimeoutSeconds", 1, 600), ("settleMs", 100, 5000)):
        if type(config[key]) is not int or not low <= config[key] <= high:
            _fail("browser timeouts must be explicitly bounded integers")
    _keys(config["viewport"], {"width", "height"})
    if any(type(value) is not int or not 320 <= value <= 4096 for value in config["viewport"].values()):
        _fail("browser viewport must have bounded reviewed dimensions")
    _keys(config["readiness"], {"tenantId", "contentId", "instanceId", "ready"})
    identities = {
        "tenantId": plan["target"]["tenantId"], "contentId": plan["contentId"],
        "instanceId": plan["instanceId"], "ready": "true",
    }
    selectors = {"tenantId": "tenant", "contentId": "workbook", "instanceId": "workbook", "ready": "ready"}
    for key, expected in identities.items():
        assertion = config["readiness"][key]
        _assertion(assertion)
        if (
            assertion["kind"] not in {"text", "attribute"}
            or assertion["expected"] != expected
            or assertion["selector"] != plan["readinessSelectors"][selectors[key]]
        ):
            _fail("browser readiness must observe both exact identities, tenant, and ready state")
    if config["readiness"]["contentId"] == config["readiness"]["instanceId"]:
        _fail("canonical and installed workbook identities need independent observations")
    _assertions(config["sessionAssertions"])
    if not any(a["kind"] in {"text", "attribute"} and a.get("expected") for a in config["sessionAssertions"]):
        _fail("session readiness requires a positive visible authenticated-session assertion")
    _keys(config["guards"], {"queryErrors", "prohibitedControls", "signedOut"})
    for selectors in config["guards"].values():
        if not isinstance(selectors, list) or not 1 <= len(selectors) <= 50:
            _fail("reviewed query, edit and signed-out guards are mandatory")
        for selector in selectors:
            _selector(selector)
    _keys(config["network"], {"requests", "navigationUrls"})
    network = config["network"]
    origin_parts = urlsplit(plan["url"])
    origin = origin_parts.scheme + "://" + origin_parts.netloc
    if not isinstance(network["navigationUrls"], list) or not 1 <= len(network["navigationUrls"]) <= 25:
        _fail("exact reviewed navigation URL allowlist is required")
    for url in network["navigationUrls"]:
        _url(url, origin)
    if plan["url"] not in network["navigationUrls"]:
        _fail("initial workbook URL is not approved for navigation")
    if not isinstance(network["requests"], list) or not 1 <= len(network["requests"]) <= 100:
        _fail("exact reviewed background request allowlist is required")
    for rule in network["requests"]:
        _keys(rule, {"url", "methods", "purpose"})
        _url(rule["url"], origin if origin_parts.hostname in {"127.0.0.1", "localhost"} else None)
        if not isinstance(rule["methods"], list) or not rule["methods"] or set(rule["methods"]) - {"GET", "HEAD", "POST"}:
            _fail("only specifically reviewed GET, HEAD or read-query POST requests are permitted")
        if rule["purpose"] not in {"asset", "read-query"} or "POST" in rule["methods"] and rule["purpose"] != "read-query":
            _fail("POST requires an explicit reviewed read-query classification")
    if not any(rule["url"] == plan["url"] and "GET" in rule["methods"] for rule in network["requests"]):
        _fail("initial document request is not approved")
    if not plan.get("backgroundActivityReview", "").strip() or plan.get("saveEditAllowed") is not False:
        _fail("non-edit and background activity review are required")
    if not isinstance(plan["steps"], list) or not 7 <= len(plan["steps"]) <= 50:
        _fail("browser steps must be bounded and complete")
    if any(
        not isinstance(step, dict) or not isinstance(step.get("id"), str)
        or not step["id"].strip() or len(step["id"]) > 200
        or not isinstance(step.get("kind"), str)
        for step in plan["steps"]
    ):
        _fail("browser check identities and kinds must be explicit bounded strings")
    if (
        {step.get("kind") for step in plan["steps"]} != {
            "pickers", "dependent-refresh", "filters", "drill-down", "reload", "layout", "conditional-visibility",
        }
        or len({step.get("id") for step in plan["steps"]}) != len(plan["steps"])
    ):
        _fail("browser check kinds and identities must be complete and unique")
    for step in plan["steps"]:
        _keys(step, {"id", "kind", "action", "assertions"}, {
            "before", "selector", "value", "expectedUrl", "selectMode", "optionSelector",
        })
        _assertions(step["assertions"])
        if not any(a["kind"] in {"text", "attribute", "value", "layout"} for a in step["assertions"]):
            _fail("every step must assert visible panel content or layout")
        if "before" in step:
            _assertions(step["before"])
        action = step["action"]
        if action not in {"observe", "select", "reload", "drill-down"}:
            _fail("unsupported browser action")
        if action in {"select", "drill-down"}:
            _selector(step.get("selector"))
        if action == "select":
            if not isinstance(step.get("value"), str) or not step["value"]:
                _fail("select action requires an exact reviewed option value")
            mode = step.get("selectMode", "native")
            if mode not in {"native", "option"}:
                _fail("select mode must be native or an exact reviewed option locator")
            if mode == "option":
                _selector(step.get("optionSelector"))
            elif "optionSelector" in step:
                _fail("native selections do not accept an option locator")
            kinds = {"value"} if mode == "native" else {"text", "attribute", "value"}
            if not any(a["selector"] == step["selector"] and a["kind"] in kinds and a["expected"] == step["value"] for a in step["assertions"]):
                _fail("selection must be independently observed after the action")
        elif {"value", "selectMode", "optionSelector"} & step.keys():
            _fail("only select actions accept an option value")
        if action == "drill-down":
            if step.get("expectedUrl") not in network["navigationUrls"]:
                _fail("drill-down needs an exact reviewed destination URL")
        elif "expectedUrl" in step:
            _fail("only drill-down accepts a destination URL")
        if action not in {"select", "drill-down"} and "selector" in step:
            _fail("observation and reload do not accept action selectors")
        if step["kind"] in {"pickers", "filters", "dependent-refresh"} and action != "select":
            _fail("picker, filter and dependent refresh checks must exercise selection")
        if step["kind"] == "reload" and action != "reload" or step["kind"] == "drill-down" and action != "drill-down":
            _fail("reload and drill-down checks must exercise their reviewed action")
        if step["kind"] == "layout" and not any(a["kind"] == "layout" for a in step["assertions"]):
            _fail("layout check requires measured visible panel bounds")
        if step["kind"] == "conditional-visibility" and not any(a["kind"] in {"visible", "hidden"} for a in step["assertions"]):
            _fail("conditional visibility check needs an explicit visibility assertion")
        if step["kind"] == "dependent-refresh":
            if not any(
                before["kind"] in {"text", "attribute", "value"}
                and before["selector"] != step["selector"]
                and any(
                    after["selector"] == before["selector"] and after["kind"] == before["kind"]
                    and after.get("attribute") == before.get("attribute")
                    and after.get("expected") != before["expected"]
                    for after in step["assertions"]
                )
                for before in step.get("before", [])
            ):
                _fail("dependent refresh must prove an observed panel changed, not just a picker")


def _private_storage(path: str | Path, expected_hash: str) -> dict[str, Any]:
    if not hasattr(os, "getuid") or not hasattr(os, "O_NOFOLLOW"):
        _fail("private browser session ownership verification requires a supported POSIX host")
    path = Path(path).expanduser().absolute()
    if any(part.is_symlink() for part in (path, *path.parents)):
        _fail("private browser session must not use symbolic links")
    try:
        info = path.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            _fail("existing browser storage state must be owner-only and owned by this user")
        if info.st_size > 10_000_000:
            _fail("private browser session exceeds the bounded size")
        with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), "rb") as stream:
            opened = os.fstat(stream.fileno())
            if (
                (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino)
                or opened.st_uid != os.getuid() or opened.st_mode & 0o077
            ):
                _fail("private browser session changed while it was being opened")
            raw = stream.read(10_000_001)
        if hashlib.sha256(raw).hexdigest() != expected_hash:
            _fail("private browser session differs from the reviewed plan")
        state = json.loads(raw)
        if not isinstance(state, dict) or not isinstance(state.get("cookies"), list) or not isinstance(state.get("origins"), list):
            _fail("existing Playwright storage state is incomplete")
        if not state["cookies"] and not state["origins"]:
            _fail("an existing authenticated browser session is required")
        return state
    except BrowserQualificationError:
        raise
    except (OSError, ValueError):
        _fail("existing private browser session cannot be read")


def prepare_private_browser_evidence(solution: str | Path) -> None:
    from .artifacts import report_directory

    directory = report_directory(solution, create=True)
    if not hasattr(os, "getuid"):
        _fail("private browser evidence verification requires a supported POSIX host")
    if any(part.is_symlink() for part in (directory, *directory.parents)):
        _fail("browser evidence directory must not use symbolic links")
    try:
        ignored = subprocess.run(
            ["git", "-C", str(directory), "check-ignore", "--quiet", str(directory / "browser-evidence.json")],
            capture_output=True, timeout=5,
        )
        tracked = subprocess.run(
            ["git", "-C", str(directory), "ls-files", "--", str(directory)],
            capture_output=True, timeout=5,
        )
        if ignored.returncode != 0 or tracked.returncode != 0 or tracked.stdout:
            _fail("browser evidence must be Git-ignored and untracked before execution")
        directory.chmod(0o700)
    except (OSError, subprocess.SubprocessError):
        _fail("private local browser evidence destination cannot be verified")


class _DOMRun:
    def __init__(self, plan: dict[str, Any], guard: Callable[[], None]):
        self.plan, self.config, self.guard = plan, plan["browserConfig"], guard
        self.deadline = time.monotonic() + self.config["familyTimeoutSeconds"]
        self.faults: set[str] = set()
        self.events: list[dict[str, Any]] = []
        self.observed: dict[str, str | bool] = {}

    def check(self) -> None:
        self.guard()
        if time.monotonic() >= self.deadline:
            _fail("browser family deadline expired")
        if self.faults:
            _fail("browser safety or query monitor failed: " + ", ".join(sorted(self.faults)))

    def timeout(self) -> int:
        self.check()
        return max(1, min(self.config["timeoutMs"], int((self.deadline - time.monotonic()) * 1000)))

    def observe(self, page: Any, assertion: dict[str, Any]) -> str | bool | dict[str, float]:
        self.check()
        locator = page.locator(assertion["selector"])
        kind = assertion["kind"]
        locator.wait_for(state="attached", timeout=self.timeout())
        if locator.count() != 1:
            _fail("reviewed DOM assertion does not resolve exactly one element")
        locator.wait_for(state="hidden" if kind == "hidden" else "visible", timeout=self.timeout())
        until = time.monotonic() + self.timeout() / 1000
        while True:
            if kind == "text":
                actual = locator.inner_text(timeout=self.timeout())
            elif kind == "attribute":
                actual = locator.get_attribute(assertion["attribute"], timeout=self.timeout())
            elif kind == "value":
                actual = locator.input_value(timeout=self.timeout())
            elif kind == "layout":
                actual = locator.bounding_box(timeout=self.timeout())
            else:
                actual = kind == "visible"
            if kind == "layout":
                matched = actual is not None and all(
                    bounds[0] <= actual[axis] <= bounds[1] for axis, bounds in assertion["bounds"].items()
                )
            else:
                matched = kind not in {"text", "attribute", "value"} or actual == assertion["expected"]
            if matched:
                break
            if time.monotonic() >= until:
                _fail("observed DOM value or layout differs from the exact reviewed expectation")
            page.wait_for_timeout(min(50, self.timeout()))
        self.check()
        return actual

    def ready(self, page: Any) -> None:
        self.check()
        if page.url not in self.config["network"]["navigationUrls"]:
            _fail("browser navigation left the exact approved target")
        for group, selectors in self.config["guards"].items():
            for selector in selectors:
                matches = page.locator(selector)
                count = matches.count()
                if count > 100:
                    _fail("browser safety guard matched too many elements")
                if any(matches.nth(index).is_visible() for index in range(count)):
                    self.faults.add(group)
        self.check()
        for assertion in self.config["sessionAssertions"]:
            self.observe(page, assertion)
        observed = {
            key: self.observe(page, assertion)
            for key, assertion in self.config["readiness"].items()
        }
        observed["ready"] = observed["ready"] == "true"
        self.observed = observed

    def proof(self, page: Any, assertion: dict[str, Any]) -> dict[str, Any]:
        observed = self.observe(page, assertion)
        proof = {
            "assertionSha256": observation_digest(assertion),
            "actualSha256": observation_digest(observed), "kind": assertion["kind"],
        }
        if assertion["kind"] == "layout":
            proof["measurement"] = observed
        return proof

    def action_locator(self, page: Any, selector: str) -> Any:
        locator = page.locator(selector)
        locator.wait_for(state="visible", timeout=self.timeout())
        if locator.count() != 1 or locator.is_disabled(timeout=self.timeout()):
            _fail("action target is missing, ambiguous, or disabled")
        labels = " ".join(filter(None, (
            locator.inner_text(timeout=self.timeout()),
            locator.get_attribute("aria-label", timeout=self.timeout()),
            locator.get_attribute("title", timeout=self.timeout()),
            locator.get_attribute("name", timeout=self.timeout()),
        )))
        if re.search(r"\b(save|edit|delete|remove|publish|sign.?in|log.?in|consent|grant)\b", labels, re.I):
            _fail("prohibited edit or authentication action observed")
        return locator

    def attach(self, context: Any, page: Any) -> None:
        rules = {(rule["url"], method) for rule in self.config["network"]["requests"] for method in rule["methods"]}

        def route_request(route: Any) -> None:
            try:
                self.check()
                request = route.request
                if (request.url, request.method) not in rules:
                    self.faults.add("unreviewed-request")
                    route.abort()
                else:
                    route.continue_()
            except Exception:
                self.faults.add("request-guard")
                route.abort()

        context.route("**/*", route_request)
        context.route_web_socket(
            "**/*", lambda socket: (self.faults.add("unreviewed-websocket"), socket.close()),
        )
        context.on("page", lambda _: self.faults.add("unexpected-page"))
        page.on("pageerror", lambda _: self.faults.add("javascript-error"))
        page.on("console", lambda message: self.faults.add("console-error") if message.type == "error" else None)
        page.on("response", lambda response: self.faults.add("query-http-error") if response.status >= 400 else None)
        page.on("requestfailed", lambda _: self.faults.add("request-failed"))
        page.on("websocket", lambda _: self.faults.add("unreviewed-websocket"))
        page.on("download", lambda _: self.faults.add("unexpected-download"))
        page.on("dialog", lambda dialog: (self.faults.add("unexpected-dialog"), dialog.dismiss()))
        page.on("framenavigated", lambda frame: self.faults.add("unreviewed-navigation") if frame.url not in self.config["network"]["navigationUrls"] else None)
        context.on("serviceworker", lambda _: self.faults.add("unexpected-service-worker"))

    def run(self, context: Any, page: Any) -> dict[str, Any]:
        page.set_default_timeout(self.config["timeoutMs"])
        page.set_default_navigation_timeout(self.config["timeoutMs"])
        self.attach(context, page)
        self.check()
        page.goto(self.plan["url"], wait_until="domcontentloaded", timeout=self.timeout())
        self.ready(page)
        outcomes = []
        for step in self.plan["steps"]:
            self.events.append({"stepId": step["id"], "action": step["action"], "status": "running"})
            self.ready(page)
            before = [self.proof(page, assertion) for assertion in step.get("before", [])]
            self.check()
            action = step["action"]
            if action in {"select", "drill-down"}:
                locator = self.action_locator(page, step["selector"])
                self.check()
                if action == "select":
                    if step.get("selectMode", "native") == "native":
                        locator.select_option(value=step["value"], timeout=self.timeout())
                    else:
                        locator.click(timeout=self.timeout(), no_wait_after=True)
                        self.ready(page)
                        option = self.action_locator(page, step["optionSelector"])
                        self.check()
                        option.click(timeout=self.timeout(), no_wait_after=True)
                else:
                    locator.click(timeout=self.timeout(), no_wait_after=True)
                    page.wait_for_url(step["expectedUrl"], timeout=self.timeout())
                    if page.url != step["expectedUrl"]:
                        _fail("drill-down navigation did not match the reviewed URL")
            elif action == "reload":
                page.reload(wait_until="domcontentloaded", timeout=self.timeout())
            self.ready(page)
            for assertion in step["assertions"]:
                self.observe(page, assertion)
            page.wait_for_timeout(min(self.config["settleMs"], self.timeout()))
            self.ready(page)
            assertions = [self.proof(page, assertion) for assertion in step["assertions"]]
            outcomes.append({
                "id": step["id"], "kind": step["kind"], "status": "passed",
                "evidence": "Exact reviewed DOM assertions observed twice after the action.",
                "assertionCount": len(step["assertions"]),
                "assertions": assertions, "beforeAssertions": before,
            })
            self.events[-1]["status"] = "passed"
        self.ready(page)
        if page.url != self.plan["url"]:
            _fail("final browser URL differs from the approved workbook URL")
        return {
            "target": self.plan["target"], "url": page.url, "readiness": self.observed,
            "steps": outcomes, "queryErrors": [], "javascriptErrors": [],
            "saveEditObserved": False, "backgroundActivityReview": self.plan["backgroundActivityReview"],
            "producer": "playwright-dom-v1", "diagnosticEvents": self.events,
            "browserWideNoWriteSandbox": False,
        }


def capture_workbook_browser(
    plan: dict[str, Any], *, storage_state: str | Path,
    before_action: Callable[[], None],
) -> dict[str, Any]:
    """Use only an existing private session in a fresh, nonpersistent context.

    No traces, HAR, storage-state export, raw error messages or page content are
    retained. Exact request allowlists reduce risk; they are not a no-write sandbox.
    """
    config = plan.get("browserConfig")
    if config is None:
        _fail("real browser execution requires a reviewed versioned browser configuration")
    validate_browser_config(plan, config)
    before_action()
    state = _private_storage(storage_state, config["storageStateSha256"])
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        _fail("optional browser dependency is missing; install the toolkit browser extra")
    engine = None
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, timeout=config["timeoutMs"])
            try:
                context = browser.new_context(
                    storage_state=state, service_workers="block", accept_downloads=False,
                    viewport=config["viewport"],
                )
                try:
                    page = context.new_page()
                    engine = _DOMRun(plan, before_action)
                    return engine.run(context, page)
                finally:
                    context.close()
            finally:
                browser.close()
    except BrowserQualificationError as exc:
        exc.diagnostic_events = _failure_events(engine)
        raise
    except Exception:
        failure = BrowserQualificationError("browser execution failed; no raw browser exception was retained")
        failure.diagnostic_events = _failure_events(engine)
        raise failure from None


def _failure_events(engine: _DOMRun | None) -> list[dict[str, Any]]:
    events = [dict(event) for event in engine.events] if engine else []
    if events and events[-1]["status"] == "running":
        events[-1]["status"] = "failed"
    events.append({"status": "failed", "faultCodes": sorted(engine.faults) if engine else ["browser-startup"]})
    return events


def validate_browser_step_proofs(step: dict[str, Any], actual: dict[str, Any]) -> None:
    for field, expected in (("assertions", step["assertions"]), ("beforeAssertions", step.get("before", []))):
        proofs = actual.get(field)
        if not isinstance(proofs, list) or len(proofs) != len(expected):
            _fail("browser capture has incomplete DOM observation proofs")
        for assertion, proof in zip(expected, proofs, strict=True):
            if (
                not isinstance(proof, dict) or proof.get("kind") != assertion["kind"]
                or proof.get("assertionSha256") != observation_digest(assertion)
            ):
                _fail("browser capture DOM proofs differ from reviewed assertions")
            if assertion["kind"] == "layout":
                observed = proof.get("measurement")
                if (
                    not isinstance(observed, dict) or set(observed) != {"x", "y", "width", "height"}
                    or any(type(n) not in (int, float) for n in observed.values())
                    or any(not bounds[0] <= observed[axis] <= bounds[1] for axis, bounds in assertion["bounds"].items())
                ):
                    _fail("browser capture is missing reviewed visible panel measurements")
            else:
                observed = assertion.get("expected") if assertion["kind"] in {"text", "attribute", "value"} else assertion["kind"] == "visible"
            if proof.get("actualSha256") != observation_digest(observed):
                _fail("browser capture DOM observations did not match the exact expectations")


def execute_workbook_browser(
    solution: str | Path, plan: dict[str, Any], *,
    read_consent: Callable[[], dict[str, Any]], storage_state: str | Path,
) -> dict[str, Any]:
    from . import workbook_qualification as qualification

    def guard() -> None:
        qualification._check_consent(plan, read_consent())
        if qualification.current_workbook_ui_plan(solution, plan) != plan:
            _fail("workbook browser inputs or target changed during execution")

    return qualification.execute_workbook_ui(
        solution, plan, read_consent=read_consent,
        browser_runner=lambda current: capture_workbook_browser(
            current, storage_state=storage_state, before_action=guard,
        ),
    )
