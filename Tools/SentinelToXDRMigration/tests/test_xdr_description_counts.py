from __future__ import annotations

import json
import re
import shutil
import unittest
import zipfile

import test_customer_usage_attribution as attribution


@unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 is required")
class XdrDescriptionCountTests(unittest.TestCase):
    setUp = attribution.AttributionTests.setUp
    run_ps = attribution.AttributionTests.run_ps
    prepare_integration = attribution.AttributionTests.prepare_integration
    package = attribution.AttributionTests.package
    write_metadata = attribution.AttributionTests.write_metadata

    def configure(self, xdr_count, *, analytics=True, hunting=False, registration=False):
        data = json.loads(self.data.read_text())
        data["Analytic Rules"] = ["Analytic Rules/Test.yaml"] if analytics else []
        data["Hunting Queries"] = ["Hunting Queries/Test.yaml"] if hunting else []
        data["Include XDR Content Registration"] = registration
        # Count-like author text must not be mistaken for the generated inventory.
        data["Description"] = "Test package: **Analytic Rules:** 99, keep this text."
        detection = json.loads(
            (self.solution / "XDR Detections/Test.yaml").read_text().removeprefix("---\n")
        )
        data["XDR Detections"] = []
        rule = json.loads(
            (self.solution / "Analytic Rules/Test.yaml").read_text().removeprefix("---\n")
        )
        if xdr_count:
            data["Analytic Rules"] = []
        for index in range(xdr_count):
            detection["properties"]["id"] = f"{index + 2:08d}-2222-3333-4444-555555555555"
            detection["contentProvenance"]["source"]["id"] = detection["properties"]["id"]
            rule["id"] = detection["properties"]["id"]
            source = f"Analytic Rules/Count{index}.yaml"
            (self.solution / source).write_text("---\n" + json.dumps(rule))
            data["Analytic Rules"].append(source)
            relative = f"XDR Detections/Count{index}.yaml"
            (self.solution / relative).write_text("---\n" + json.dumps(detection))
            data["XDR Detections"].append(relative)
        path = self.solution / "Hunting Queries/Test.yaml"
        path.parent.mkdir(exist_ok=True)
        path.write_text("---\n" + json.dumps({
            "id": "33333333-2222-3333-4444-555555555555", "name": "Test hunt",
            "description": "Packaging test.", "query": "print Test=1",
            "version": "1.0.0", "requiredDataConnectors": [],
        }))
        self.data.write_text(json.dumps(data))

    def assert_summary(self, expected):
        package = self.solution / "Package"
        ui = json.loads((package / "createUiDefinition.json").read_text(encoding="utf-8-sig"))
        template = json.loads((package / "mainTemplate.json").read_text(encoding="utf-8-sig"))
        description = ui["parameters"]["config"]["basics"]["description"]
        data = json.loads(self.data.read_text())
        self.assertIn(data["Description"] + "\n\n" + expected + "\n\n[Learn more", description)
        self.assertNotRegex(description, r"\{\{|\}\}|, \n|, ,")
        self.assertNotIn("XDR Custom Detections:", description)
        content_packages = [
            resource for resource in template["resources"]
            if resource["type"] == "Microsoft.OperationalInsights/workspaces/providers/contentPackages"
        ]
        self.assertTrue(content_packages)
        for resource in content_packages:
            html = resource["properties"]["descriptionHtml"]
            expected_html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", expected)
            if expected:
                self.assertIn(f"<p>{expected_html}</p>", html)
            else:
                self.assertNotIn("XDR Detections:", html)
            self.assertNotRegex(html, r"\{\{|\}\}|, </p>|, ,")
            self.assertIn("keep this text.", html)
        self.assertNotIn("xdr", json.dumps([
            step for step in ui["parameters"]["steps"] if step.get("name") != "contentSelection"
        ]).lower())
        self.assertNotIn("E5Flavor", json.dumps(ui))
        with zipfile.ZipFile(package / f"{template['variables']['_solutionVersion']}.zip") as archive:
            self.assertEqual(ui, json.loads(archive.read("createUiDefinition.json").decode("utf-8-sig")))
            self.assertEqual(template, json.loads(archive.read("mainTemplate.json").decode("utf-8-sig")))
        return description, [r["properties"]["descriptionHtml"] for r in content_packages], template

    def test_local_and_pipeline_counts_and_registration(self):
        entry = self.prepare_integration()
        self.write_metadata(attribution.TRACKING_ID)
        cases = (
            (0, True, True),
            (0, False, False),
            (1, True, False),
            (3, True, True),
            (3, True, False),
        )
        for count, analytics, hunting in cases:
            expected = ", ".join(
                f"**{label}:** {number}"
                for label, number in (
                    ("Analytic Rules", max(int(analytics), count)), ("XDR Detections", count),
                    ("Hunting Queries", int(hunting)),
                ) if number
            )
            for registration in (False, True):
                self.configure(count, analytics=analytics, hunting=hunting, registration=registration)
                sources = {
                    path: path.read_bytes() for path in self.solution.rglob("*")
                    if path.is_file() and "Package" not in path.parts
                }
                for pipeline in (False, True):
                    with self.subTest(count=count, analytics=analytics, hunting=hunting,
                                      registration=registration, pipeline=pipeline):
                        result = self.package(entry, pipeline)
                        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                        _, _, template = self.assert_summary(expected)
                        deployments = [r for r in template["resources"]
                                       if r["type"] == "Microsoft.Resources/deployments"]
                        self.assertEqual(count + 1, len(deployments))
                        self.assertIn(attribution.AttributionTests.marker(attribution.TRACKING_ID),
                                      deployments)
                        registered = [r for r in template["resources"]
                                      if r.get("properties", {}).get("contentKind") == "CustomDetection"]
                        self.assertEqual(count, len(registered))
                        for deployment in deployments:
                            if deployment["name"] != attribution.TRACKING_ID:
                                self.assertEqual("disabled", deployment["properties"]["template"]
                                                 ["resources"]["detectionRule"]["properties"]["status"])
                        self.assertEqual(sources, {path: path.read_bytes() for path in sources})

    def test_zero_and_legacy_descriptions_are_unchanged(self):
        entry = self.prepare_integration()
        self.write_metadata()
        self.configure(0, hunting=True)
        expected = "**Analytic Rules:** 1, **Hunting Queries:** 1"
        result = self.package(entry, False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        baseline = self.assert_summary(expected)[:2]
        data = json.loads(self.data.read_text())
        data.pop("XDR Detections")
        self.data.write_text(json.dumps(data))
        for pipeline in (False, True):
            with self.subTest(absent_xdr=True, pipeline=pipeline):
                result = self.package(entry, pipeline)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertEqual(baseline, self.assert_summary(expected)[:2])
        data = json.loads(self.data.read_text())
        data["Version"] = "3.1.0"
        self.data.write_text(json.dumps(data))
        for relative, pipeline in (
            ("V3/createSolutionV3.ps1", False),
            ("pipeline/createSolutionV4.ps1", True),
        ):
            legacy = entry.with_name("legacy.ps1")
            shutil.copyfile(attribution.PACKAGER / relative, legacy)
            # Even with XDR inputs present, legacy paths must not add this display count.
            self.configure(1, hunting=True)
            with self.subTest(entry=relative):
                result = self.package(legacy, pipeline, version_bump="patch",
                                      calculated_version="3.1.1")
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertEqual(baseline, self.assert_summary(expected)[:2])

    def test_failed_detection_generation_does_not_publish_a_partial_count(self):
        entry = self.prepare_integration()
        self.write_metadata(attribution.TRACKING_ID)
        self.configure(1)
        result = self.package(entry, False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assert_summary("**Analytic Rules:** 1, **XDR Detections:** 1")
        outputs = {path: path.read_bytes() for path in (self.solution / "Package").iterdir()}
        data = json.loads(self.data.read_text())
        data["XDR Detections"].append("XDR Detections/Missing.yaml")
        self.data.write_text(json.dumps(data))
        for pipeline in (False, True):
            with self.subTest(pipeline=pipeline):
                result = self.package(entry, pipeline)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("Custom Detection file not found", result.stdout + result.stderr)
                self.assertEqual(outputs, {path: path.read_bytes() for path in outputs})

    def test_summary_insertion_handles_empty_and_trailing_categories(self):
        cases = (
            ("", "**XDR Detections:** 2"),
            ("**Analytic Rules:** 15", "**Analytic Rules:** 15, **XDR Detections:** 2"),
            ("**Hunting Queries:** 15", "**XDR Detections:** 2, **Hunting Queries:** 15"),
            ("**Data Connectors:** 1, **Parsers:** 2, **Workbooks:** 3, ",
             "**Data Connectors:** 1, **Parsers:** 2, **Workbooks:** 3, **XDR Detections:** 2"),
            ("**Analytic Rules:** 15, **Hunting Queries:** 15, **Watchlists:** 1, ",
             "**Analytic Rules:** 15, **XDR Detections:** 2, **Hunting Queries:** 15, **Watchlists:** 1"),
            ("**Summary Rules:** 1, **Playbooks:** 2",
             "**XDR Detections:** 2, **Summary Rules:** 1, **Playbooks:** 2"),
            ("**Custom Azure Logic Apps Connectors:** 1, **Function Apps:** 2, **Playbooks:** 3",
             "**XDR Detections:** 2, **Custom Azure Logic Apps Connectors:** 1, **Function Apps:** 2, **Playbooks:** 3"),
        )
        common = attribution.ps_literal(attribution.PACKAGER / "common/commonFunctions.ps1")
        for summary, expected in cases:
            for newline in ("\n", "\r\n"):
                with self.subTest(summary=summary, newline=repr(newline)):
                    prefix = "keep before" + newline * 2 + "{{SolutionDescription}}" + newline * 2
                    suffix = newline * 2 + "keep after"
                    result = self.run_ps(
                        f". {common}; "
                        "$global:baseCreateUiDefinition.parameters.config.basics.description = "
                        f"{attribution.ps_literal(prefix + summary + suffix)}; "
                        "Update-XdrDescriptionCount -Count 2; "
                        "$global:baseCreateUiDefinition.parameters.config.basics.description | ConvertTo-Json"
                    )
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertEqual(prefix + expected + suffix, json.loads(result.stdout))


if __name__ == "__main__":
    unittest.main()
