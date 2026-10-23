from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest

from sentinel_xdr_migration.report_dashboard import render_dashboard
from sentinel_xdr_migration.converter import load_config
from test_report_dashboard import report, rule
from test_report_review import review_rule


@unittest.skipUnless(os.environ.get("SENTINEL_REPORT_BROWSER_TESTS") == "1", "Opt-in installed-browser tests")
class ReportReviewBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from playwright.sync_api import sync_playwright

        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            channel=os.environ.get("SENTINEL_REPORT_BROWSER_CHANNEL", "chrome"), headless=True
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self) -> None:
        self.context = self.browser.new_context(accept_downloads=True, viewport={"width": 1440, "height": 1000})
        self.page = self.context.new_page()
        self.errors = []
        self.remote = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on("request", lambda request: self.remote.append(request.url) if request.url.startswith(("http:", "https:")) else None)
        first = review_rule("First", "a", ["Execution", "Collection"], ["T1059", "T1005"])
        second = review_rule("Second", "b", ["Collection", "Exfiltration"], ["T1005", "T1020"])
        green = rule("Info only")
        green["analyticRule"]["id"] = "c"
        green["informational"] = ["Equivalent entity mapping"]
        red = rule("Failed")
        red["analyticRule"]["id"] = "d"
        red["errors"] = [{"stage": "conversion", "message": "Hard failure"}]
        gray = rule("Unknown")
        gray["analyticRule"]["id"] = "e"
        gray["customDetection"].update(conversionStatus="not-run", structuralStatus="not-generated")
        self.value = report(first, second, green, red, gray)
        self.page.set_content(render_dashboard(self.value))

    def tearDown(self) -> None:
        self.assertFalse(self.errors, self.errors)
        self.assertFalse(self.remote, self.remote)
        self.context.close()

    def select_rules(self) -> None:
        self.page.locator("#bulk-review > details > summary").click()
        self.page.locator("#select-visible").click()

    def choose(self, rule_id: str, tactic: str, technique: str, *, confirm: bool = True) -> None:
        section = self.page.locator(f'fieldset[data-decision-id="{rule_id}"]')
        section.locator('select[data-choice="tactic"]').select_option(tactic)
        section.locator(f'input[data-choice="technique"][value="{technique}"]').check()
        if confirm:
            section.locator('input[data-choice="confirmed"]').check()

    def test_details_opens_with_source_and_converted_queries_visible(self) -> None:
        self.page.get_by_role("button", name="Details for First").click()
        detail = self.page.locator("#rule-detail-0")
        self.assertTrue(detail.is_visible())
        self.assertIn("Source Sentinel KQL", detail.inner_text())
        self.assertIn("Converted XDR KQL", detail.inner_text())
        self.assertIn("DeviceEvents", detail.inner_text())
        self.assertLess(
            detail.inner_text().index("Source Sentinel KQL"),
            detail.inner_text().index("Recorded checks"),
        )
        self.assertFalse(detail.locator("details > summary", has_text="queries").count())
        self.assertIn("not proof of semantic equivalence", detail.inner_text())

    def test_empty_inventory_and_unrecorded_consent_are_omitted_but_denial_is_visible(self) -> None:
        self.value["deploymentPlanning"] = {
            "deploymentPlan": {
                "packageResourceInventory": [],
                "planningConsent": {"status": "not-recorded"},
            },
        }
        self.page.set_content(render_dashboard(self.value))
        self.assertEqual(self.page.get_by_role("heading", name="Package resource inventory").count(), 0)
        self.assertEqual(self.page.locator(".planning-summary-card", has_text="Advance planning consent").count(), 0)

        self.value["deploymentPlanning"]["deploymentPlan"].update({
            "packageResourceInventory": [{
                "type": "Microsoft.Security/detectionRules",
                "apiVersion": "2026-06-01-preview",
                "count": 1,
            }],
            "planningConsent": {"status": "denied"},
        })
        self.page.set_content(render_dashboard(self.value))
        self.assertEqual(self.page.get_by_role("heading", name="Package resource inventory").count(), 1)
        self.assertIn("Microsoft.Security/detectionRules", self.page.locator("#deployment-planning").inner_text())
        self.assertEqual(self.page.locator(".planning-summary-card", has_text="Advance planning consent").count(), 1)
        self.assertIn("denied", self.page.locator("#deployment-planning").inner_text())

    def test_bulk_refuses_incompatible_rules_and_requires_individual_confirmation(self) -> None:
        self.select_rules()
        self.page.locator("#bulk-tactic").select_option("Execution")
        self.page.locator("#set-bulk-tactic").click()
        self.assertIn("Second: Execution is not in the source tactic list", self.page.locator("#bulk-feedback").inner_text())
        self.assertEqual(self.page.locator('input[data-choice="technique"]:checked').count(), 0)
        self.assertEqual(self.page.locator('input[data-choice="confirmed"]:checked').count(), 0)
        self.page.locator("#new-config").check()
        self.page.locator("#preview-decisions").click()
        self.assertIn("at least one compatible technique", self.page.locator("#review-feedback").inner_text())
        self.choose("a", "Execution", "T1059", confirm=False)
        self.choose("b", "Collection", "T1005")
        self.page.locator("#preview-decisions").click()
        self.assertIn("individual compatibility/behavior confirmation", self.page.locator("#review-feedback").inner_text())
        self.page.locator('fieldset[data-decision-id="a"] input[data-choice="confirmed"]').check()
        self.page.locator("#preview-decisions").click()
        self.assertTrue(self.page.locator("#review-preview").is_visible())
        self.assertEqual(self.page.locator('tbody.rule[data-status="review"]').count(), 2)
        self.page.locator('fieldset[data-decision-id="a"] input[value="T1059"]').uncheck()
        self.assertTrue(self.page.locator("#download-config").is_disabled())
        self.assertFalse(self.page.locator('fieldset[data-decision-id="a"] input[data-choice="confirmed"]').is_checked())

    def test_import_merge_download_preserves_settings_and_prototype_keys_as_data(self) -> None:
        self.select_rules()
        self.choose("a", "Execution", "T1059")
        self.choose("b", "Collection", "T1005")
        config = {
            "workspace": "retain", "__proto__": {"polluted": "no"}, "constructor": {"prototype": {"polluted": "no"}},
            "ruleOverrides": {
                "a": {"tactic": "Collection", "techniques": ["T1005"], "entityMappings": {"custom": "preserve"}},
                "other": {"tactic": "Execution", "techniques": ["T1106"]},
                "__proto__": {"polluted": "no"},
            },
        }
        self.page.locator("#review-config-file").set_input_files({
            "name": "existing.json", "mimeType": "application/json", "buffer": json.dumps(config).encode()
        })
        self.page.get_by_text("Imported existing.json; unrelated settings will be preserved.", exact=True).wait_for()
        self.page.locator("#preview-decisions").click()
        merged = json.loads(self.page.locator("#config-preview").inner_text())
        self.assertEqual(merged["workspace"], "retain")
        self.assertEqual(merged["ruleOverrides"]["other"], config["ruleOverrides"]["other"])
        self.assertEqual(merged["ruleOverrides"]["a"]["entityMappings"], {"custom": "preserve"})
        self.assertEqual(merged["ruleOverrides"]["a"]["tactic"], "Execution")
        self.assertEqual(merged["__proto__"], config["__proto__"])
        self.assertEqual(merged["ruleOverrides"]["__proto__"], config["ruleOverrides"]["__proto__"])
        self.assertIsNone(self.page.evaluate("({}).polluted"))
        manifest = json.loads(self.page.locator("#manifest-preview").inner_text())
        self.assertFalse(manifest["applied"])
        self.assertEqual(len(manifest["decisions"]), 2)
        self.assertTrue(all(item["sourceSha256"] == "a" * 64 for item in manifest["decisions"]))
        with tempfile.TemporaryDirectory() as folder:
            for button, name, expected in (
                ("download-config", "migration-reviewed-overrides.json", merged),
                ("download-manifest", "migration-reviewed-overrides.review.json", manifest),
            ):
                with self.page.expect_download() as event:
                    self.page.locator("#" + button).click()
                download = event.value
                self.assertEqual(download.suggested_filename, name)
                target = Path(folder) / name
                download.save_as(target)
                self.assertEqual(json.loads(target.read_text()), expected)
                if button == "download-config":
                    self.assertEqual(load_config(Path(folder), explicit=target), merged)
        self.assertEqual(self.page.locator('tbody.rule[data-status="review"]').count(), 2)
        self.page.locator("#clear-selection").click()
        self.assertEqual(self.page.locator(".review-select:checked").count(), 0)
        self.assertFalse(self.page.locator("#review-preview").is_visible())

    def test_chart_keyboard_filters_info_green_and_mobile_theme(self) -> None:
        for color, count in (("green", 1), ("yellow", 2), ("red", 1), ("gray", 1)):
            self.page.locator(f'button[data-chart-filter="{color}"]').click()
            self.assertEqual(self.page.locator("tbody.rule:visible").count(), count)
        arc = self.page.locator('circle[data-chart-filter="green"]')
        arc.focus()
        self.page.keyboard.press("Enter")
        self.assertEqual(self.page.locator("tbody.rule:visible").count(), 1)
        self.assertIn("Info only", self.page.locator("tbody.rule:visible").inner_text())
        self.page.locator('input[name="finding"][value="info"]').check()
        self.assertEqual(self.page.locator("tbody.rule:visible").count(), 1)
        self.page.locator("#clear").click()
        self.assertEqual(self.page.locator("tbody.rule:visible").count(), 5)
        self.page.emulate_media(color_scheme="dark")
        self.page.set_content(render_dashboard(self.value))
        self.assertEqual(self.page.locator("html").get_attribute("data-theme"), "dark")
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"))

    def test_findings_chart_filters_warning_review_union_separately_from_rules_chart(self) -> None:
        for kind, count in (("error", 1), ("attention", 2), ("info", 1)):
            self.page.locator(f'button[data-findings-chart-filter="{kind}"]').click()
            self.assertEqual(self.page.locator("tbody.rule:visible").count(), count)
        segment = self.page.locator('path[data-findings-chart-filter="attention"]')
        segment.focus()
        self.page.keyboard.press(" ")
        self.assertEqual(self.page.locator("tbody.rule:visible").count(), 2)
        self.assertIn("Warnings / reviews", self.page.locator("#finding-chart-filter-label").inner_text())
        self.page.locator('button[data-chart-filter="green"]').click()
        self.assertEqual(self.page.locator("tbody.rule:visible").count(), 1)
        self.assertEqual(self.page.locator("#finding-chart-filter-label").inner_text(), "")
        self.page.locator('button[data-findings-chart-filter="error"]').click()
        self.assertEqual(self.page.locator("#chart-filter-label").inner_text(), "")
        self.page.locator("#clear").click()
        self.assertEqual(self.page.locator("tbody.rule:visible").count(), 5)
        self.assertEqual(self.page.locator("#finding-chart-filter-label").inner_text(), "")

    def test_hostile_payload_and_invalid_import_are_not_executed(self) -> None:
        self.value["rules"][0]["name"] = '</script><img src=x onerror="window.injected=true">'
        self.page.set_content(render_dashboard(self.value))
        self.select_rules()
        self.assertIsNone(self.page.evaluate("window.injected"))
        self.page.locator("#review-config-file").set_input_files({
            "name": "invalid.json", "mimeType": "application/json", "buffer": b'{"ruleOverrides":{"a":null}}'
        })
        self.page.get_by_text("Import rejected:", exact=False).wait_for()
        self.page.locator("#preview-decisions").click()
        self.assertIn("Import the existing configuration", self.page.locator("#review-feedback").inner_text())
        self.assertTrue(self.page.locator("#download-config").is_disabled())

    def test_migration_flow_adapts_to_recorded_profile_and_station_evidence_links(self) -> None:
        self.assertEqual(
            self.page.locator("[data-flow-station]").evaluate_all(
                "nodes => nodes.map(node => node.dataset.flowStation)"
            ),
            ["discovery", "conversion", "validation", "packaging", "report", "publication"],
        )
        validation = self.page.locator('[data-flow-station="validation"]')
        validation.focus()
        self.page.keyboard.press("Enter")
        self.assertEqual(self.page.evaluate("location.hash"), "#flow-evidence-validation")
        self.assertIn("Mandatory structural validation", self.page.locator("#flow-evidence-validation").inner_text())

        self.value["workflow"].update(
            profile="qualification",
            profileSelectionConfirmed=True,
            status="blocked",
            packageFreshness={"status": "current", "reason": None},
        )
        self.value["workflow"]["stages"].update({
            "packaging": {"status": "passed"},
            "deployment": {"status": "blocked", "message": "Local suite failed."},
            "mockIngestion": {"status": "pending"},
            "alertParity": {"status": "pending"},
        })
        self.page.set_content(render_dashboard(self.value))
        self.assertIn("Qualification · lab validation", self.page.locator("#flow-heading").inner_text())
        self.assertEqual(
            self.page.locator("[data-flow-station]").evaluate_all(
                "nodes => nodes.map(node => node.dataset.flowStation)"
            ),
            [
                "discovery", "conversion", "validation", "packaging",
                "validationSuite", "preflight", "deployment", "mockIngestion",
                "queryValidation", "alertParity", "packageAcceptance",
                "report", "publication",
            ],
        )
        deployment = self.page.locator('[data-flow-station="deployment"]')
        deployment.focus()
        self.page.keyboard.press("Enter")
        self.assertEqual(self.page.evaluate("location.hash"), "#flow-evidence-deployment")
        self.assertIn("Local suite failed.", self.page.locator("#flow-evidence-deployment").inner_text())
        self.assertIn("Blocked", self.page.locator("#flow-evidence-deployment").inner_text())
        self.page.locator('[data-flow-station="publication"]').click()
        self.assertEqual(self.page.evaluate("location.hash"), "#flow-evidence-publication")
        self.assertIn("Not tracked", self.page.locator("#flow-evidence-publication").inner_text())
        self.assertIn("does not prove publication", self.page.locator("#flow-evidence-publication").inner_text())
        self.assertTrue(self.page.locator('[data-flow-station="packageAcceptance"]').is_visible())
        self.assertIn(
            "full-package deployment and read-back are separate",
            self.page.locator("#flow-evidence-packageAcceptance").inner_text().lower(),
        )
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"))
