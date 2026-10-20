from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import test_customer_usage_attribution as attribution
from sentinel_xdr_migration.packaging import validate_v31_effective_version, validate_v31_target_version
from sentinel_xdr_migration.workflow import initialize_workflow, plan_new_package_release, package_workflow_v3_1


class PythonSolutionVersionPolicyTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.directory.cleanup)
        self.solution = Path(self.directory.name) / "Sample"
        (self.solution / "Data").mkdir(parents=True)
        self.data = self.solution / "Data/Solution_Sample.json"
        self.data.write_text(json.dumps({"Name": "Sample", "Version": "3.1.999"}))

    def snapshot(self):
        return {str(path): path.read_bytes() for path in self.solution.rglob("*") if path.is_file()}

    def test_exact_solution_target_boundaries(self):
        for version in ("3.2.0", "3.2.1", "3.999.999"):
            self.assertEqual(version, validate_v31_target_version(version))
        for version in ("3.1.999", "4.0.0", "4.1.0", "3.2", "3.2.0.0",
                        "03.2.0", "3.02.0", "3.2.00", "3.2.0-preview"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                validate_v31_target_version(version)

    def test_effective_solution_selection_does_not_promote(self):
        for bump in ("none", "patch", "major"):
            with self.subTest(bump=bump), self.assertRaises(ValueError):
                validate_v31_effective_version("3.1.999", bump)
        self.assertEqual("3.2.0", validate_v31_effective_version("3.1.999", "minor"))
        self.assertEqual("3.2.1", validate_v31_effective_version("1.0.0", "none", "3.2.1"))

    def test_authoring_rejects_selected_old_release_without_mutation(self):
        before = self.snapshot()
        for bump in ("none", "patch"):
            with self.subTest(bump=bump), self.assertRaisesRegex(ValueError, ">= 3.2.0"):
                initialize_workflow(self.solution, workflow_profile="authoring", version_bump=bump)
            self.assertEqual(before, self.snapshot())
        with self.assertRaises(ValueError):
            initialize_workflow(self.solution, workflow_profile="authoring", target_version="3.1.999")
        self.assertEqual(before, self.snapshot())

    def test_old_source_discovery_and_explicit_upgrade_are_legal(self):
        state = initialize_workflow(self.solution, workflow_profile="authoring")
        self.assertEqual("pending", state["stages"]["discovery"]["status"])
        for options in ({"target_version": "3.2.1"}, {"version_bump": "minor"}):
            with self.subTest(options=options):
                state = initialize_workflow(
                    self.solution, workflow_profile="authoring", new_run=True, **options,
                )
                self.assertEqual("pending", state["stages"]["discovery"]["status"])
        self.assertEqual("3.1.999", json.loads(self.data.read_text())["Version"])

    def test_release_planning_and_wrapper_preflight_reject_below_floor_before_state_write(self):
        initialize_workflow(self.solution, workflow_profile="authoring")
        before = self.snapshot()
        for bump in ("patch", "major"):
            with self.subTest(bump=bump), self.assertRaisesRegex(ValueError, ">= 3.2.0"):
                plan_new_package_release(
                    self.solution, version_bump=bump, expected_package_input_sha256="a" * 64,
                )
            self.assertEqual(before, self.snapshot())
        with mock.patch("sentinel_xdr_migration.workflow.package_solution_v3_1") as package:
            with self.assertRaisesRegex(ValueError, ">= 3.2.0"):
                package_workflow_v3_1(self.solution, requested_version_bump="patch")
            package.assert_not_called()
        self.assertEqual(before, self.snapshot())


@unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 is required")
class VersionPolicyTests(unittest.TestCase):
    setUp = attribution.AttributionTests.setUp
    run_ps = attribution.AttributionTests.run_ps
    prepare_integration = attribution.AttributionTests.prepare_integration
    package = attribution.AttributionTests.package
    write_metadata = attribution.AttributionTests.write_metadata

    def fixture(self, version="3.2.0", *, xdr=True):
        entry = self.prepare_integration()
        self.write_metadata(attribution.TRACKING_ID)
        self.update_data(Version=version)
        if not xdr:
            self.update_data(**{"XDR Detections": []})
        return entry

    def update_data(self, **changes):
        document = json.loads(self.data.read_text())
        document.update(changes)
        self.data.write_text(json.dumps(document))

    def update_detection(self, version, *, registration=False, fallback=None):
        path = self.solution / "XDR Detections/Test.yaml"
        document = json.loads(path.read_text().removeprefix("---\n"))
        if version is None:
            document.pop("version", None)
        else:
            document["version"] = version
        path.write_text("---\n" + json.dumps(document))
        changes = {"Include XDR Content Registration": registration}
        if fallback is not None:
            changes["XDR Detection Version"] = fallback
        self.update_data(**changes)

    def snapshot(self):
        return {str(path): path.read_bytes() for path in self.solution.rglob("*") if path.is_file()}

    def assert_rejected_unchanged(self, entry, *, pipeline=False, **kwargs):
        before = self.snapshot()
        result = self.package(entry, pipeline, **kwargs)
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("V3.1 version policy", result.stdout + result.stderr)
        self.assertEqual(before, self.snapshot(), "Rejected packaging mutated source or outputs")
        return result

    def test_solution_boundaries_without_xdr_local_and_pipeline(self):
        entry = self.fixture(xdr=False)
        for version, accepted in (("3.0.99", False), ("3.1.999", False),
                                  ("3.2.0", True), ("3.2.1", True),
                                  ("3.999.999", True), ("4.0.0", False), ("4.1.0", False)):
            for pipeline in (False, True):
                with self.subTest(version=version, pipeline=pipeline):
                    self.update_data(Version=version)
                    if accepted:
                        result = self.package(entry, pipeline, calculated_version=version)
                        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                        template = json.loads((self.solution / "Package/mainTemplate.json").read_text())
                        self.assertEqual(version, template["variables"]["_solutionVersion"])
                        self.assertTrue((self.solution / f"Package/{version}.zip").is_file())
                    else:
                        result = self.assert_rejected_unchanged(
                            entry, pipeline=pipeline, calculated_version=version)
                        self.assertIn(version, result.stdout + result.stderr)

    def test_xdr_boundaries_even_without_registration(self):
        entry = self.fixture()
        for version, accepted in (("3.0.99", False), ("3.1.0", True),
                                  ("3.9.99", True), ("4.0.0", False)):
            for registration in (False, True):
                for pipeline in (False, True):
                    with self.subTest(version=version, registration=registration, pipeline=pipeline):
                        self.update_detection(version, registration=registration)
                        if accepted:
                            result = self.package(entry, pipeline)
                            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                            template = json.loads((self.solution / "Package/mainTemplate.json").read_text())
                            registered = [r for r in template["resources"]
                                          if r.get("properties", {}).get("contentKind") == "CustomDetection"]
                            self.assertEqual(1, len(registered))
                            if registration:
                                properties = registered[0]["properties"]
                                self.assertEqual(version, properties["version"])
                                self.assertIn(f"'-','{version}'", properties["contentProductId"])
                                self.assertNotIn("'-','1.0.0'", properties["contentProductId"])
                                self.assertEqual(properties["contentProductId"], properties["id"])
                                self.assertEqual("3.0.0", properties["contentSchemaVersion"])
                        else:
                            result = self.assert_rejected_unchanged(entry, pipeline=pipeline)
                            diagnostic = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout + result.stderr)
                            diagnostic = re.sub(r"\n\s*\|\s*", " ", diagnostic)
                            self.assertIn("CustomDetection 'XDR Detections/Test.yaml'",
                                          " ".join(diagnostic.split()))

    def test_analytic_versions_keep_legacy_floor(self):
        entry = self.fixture()
        path = self.solution / "Analytic Rules/Test.yaml"
        document = json.loads(path.read_text().removeprefix("---\n"))
        for version in ("1.0.0", "2.0.0", "3.9.99", None, "4.0.0"):
            for pipeline in (False, True):
                with self.subTest(version=version, pipeline=pipeline):
                    if version is None:
                        document.pop("version", None)
                    else:
                        document["version"] = version
                    path.write_text("---\n" + json.dumps(document))
                    if version == "4.0.0":
                        result = self.assert_rejected_unchanged(entry, pipeline=pipeline)
                        self.assertIn("AnalyticsRule", result.stdout + result.stderr)
                    else:
                        result = self.package(entry, pipeline)
                        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_bumps_persist_only_accepted_effective_versions(self):
        entry = self.fixture("3.1.0")
        for bump, current, expected in (("none", "3.2.0", "3.2.0"),
                                       ("patch", "3.2.0", "3.2.1"),
                                       ("minor", "3.1.0", "3.2.0")):
            with self.subTest(bump=bump):
                self.update_data(Version=current)
                result = self.package(entry, False, version_bump=bump)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertEqual(expected, json.loads(self.data.read_text())["Version"])
                self.assertTrue((self.solution / f"Package/{expected}.zip").is_file())
        for bump, current in (("major", "3.1.0"), ("minor", "3.99.0"), ("patch", "3.9.99")):
            self.update_data(Version=current)
            if bump == "major":
                self.assert_rejected_unchanged(entry, version_bump=bump)
            else:
                result = self.package(entry, False, version_bump=bump)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        for bump in ("none", "patch"):
            self.update_data(Version="3.1.999")
            self.assert_rejected_unchanged(entry, version_bump=bump)
        self.update_data(Version="3.2.0")
        self.update_detection("1.0.0")
        self.assert_rejected_unchanged(entry, version_bump="patch")

    def test_explicit_target_version_uses_v31_backend_and_rejects_out_of_range_targets(self):
        entry = self.fixture("3.0.7")

        def package_target(target):
            return self.run_ps(
                f"& {attribution.ps_literal(entry)} "
                f"-SolutionDataFolderPath {attribution.ps_literal(self.data.parent)} "
                f"-VersionMode local -VersionBump none "
                f"-TargetVersion {attribution.ps_literal(target)}"
            )

        result = package_target("3.2.1")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("3.2.1", json.loads(self.data.read_text())["Version"])
        self.assertEqual("3.2.1", json.loads(self.metadata.read_text())["version"])
        self.assertTrue((self.solution / "Package" / "3.2.1.zip").is_file())

        result = package_target("3.999.999")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("3.999.999", json.loads(self.data.read_text())["Version"])
        self.assertEqual("3.999.999", json.loads(self.metadata.read_text())["version"])
        self.assertTrue((self.solution / "Package" / "3.999.999.zip").is_file())

        for version in ("3.0.999", "3.1.999", "4.0.0", "3.2", "3.2.0-preview", "03.2.0", "3.02.0", "3.2.00"):
            with self.subTest(version=version):
                before = self.snapshot()
                rejected = package_target(version)
                self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
                self.assertIn("V3.1 target version", rejected.stdout + rejected.stderr)
                self.assertEqual(before, self.snapshot())

    def test_pipeline_mismatch_and_missing_solution_default_fail(self):
        entry = self.fixture(xdr=False)
        self.assert_rejected_unchanged(entry, pipeline=True, calculated_version="3.2.1")
        self.assert_rejected_unchanged(entry, pipeline=True, calculated_version="3.1.999")
        document = json.loads(self.data.read_text())
        document.pop("Version")
        self.data.write_text(json.dumps(document))
        for pipeline in (False, True):
            with self.subTest(pipeline=pipeline):
                self.assert_rejected_unchanged(entry, pipeline=pipeline)

    def test_xdr_own_version_is_required_and_fallbacks_cannot_override_it(self):
        entry = self.fixture()
        for pipeline in (False, True):
            for registration in (False, True):
                with self.subTest(pipeline=pipeline, registration=registration):
                    for version in ("1.0.0", "", None):
                        self.update_detection(version, registration=registration, fallback="3.1.0")
                        result = self.assert_rejected_unchanged(entry, pipeline=pipeline)
                        self.assertIn("major.minor.patch", result.stdout + result.stderr)
                        self.assertIn("reconvert with --overwrite", result.stdout + result.stderr)
                    self.update_detection("3.1.1", registration=registration, fallback="4.0.0")
                    result = self.package(entry, pipeline)
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                    detection = json.loads((self.solution / "XDR Detections/Test.yaml").read_text().removeprefix("---\n"))
                    self.assertEqual("1.0.0", detection["contentProvenance"]["source"]["version"])
                    self.assertEqual("3.1.1", detection["version"])
                    self.update_detection(None, registration=registration)
                    document = json.loads(self.data.read_text())
                    document.pop("XDR Detection Version")
                    self.data.write_text(json.dumps(document))
                    self.assert_rejected_unchanged(entry, pipeline=pipeline)

    def test_xdr_release_requires_three_numeric_components(self):
        policy = attribution.ps_literal(attribution.PACKAGER / "common/versionPolicy.ps1")
        for version in ("3.1", "3.1.0.1", "3.01.0", "3.1.0-preview", "3.1.0\n"):
            with self.subTest(version=version):
                result = self.run_ps(
                    f". {policy}; "
                    "$v31VersionPolicy = @{ Errors = [System.Collections.Generic.List[string]]::new() }; "
                    f"Assert-V31ReleaseVersion -Version {attribution.ps_literal(version)} "
                    "-ContentKind CustomDetection -ContentPath 'test'"
                )
                self.assertNotEqual(0, result.returncode)
                self.assertIn("major.minor.patch", result.stderr)

    def test_catalog_result_is_guarded_without_source_mutation(self):
        entry = self.fixture(xdr=False)
        catalog = self.repository / ".script/package-automation/catalogAPI.ps1"
        catalog.parent.mkdir(parents=True)
        for version in ("3.0.99", "3.1.999", "3.2.0", "4.0.0"):
            # Isolate only the external catalog response, not any packaging or guard logic.
            catalog.write_text(
                "function GetCatalogDetails { return @{} }\n"
                f"function GetPackageVersion {{ return '{version}' }}\n"
            )
            if version != "3.2.0":
                self.assert_rejected_unchanged(entry, version_mode="catalog")
            else:
                before = self.data.read_bytes(), self.metadata.read_bytes()
                result = self.package(entry, False, version_mode="catalog")
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertEqual(before, (self.data.read_bytes(), self.metadata.read_bytes()))

    def test_legacy_context_is_unrestricted_and_checks_cannot_be_swallowed(self):
        policy = attribution.ps_literal(attribution.PACKAGER / "common/versionPolicy.ps1")
        result = self.run_ps(
            f". {policy}; "
            "Assert-V31ReleaseVersion -Version '4.0.0' -ContentKind Solution -ContentPath 'Legacy'; "
            "$v31VersionPolicy = @{ Errors = [System.Collections.Generic.List[string]]::new() }; "
            "try { Assert-V31ReleaseVersion -Version '4.0.0' -ContentKind Workbook -ContentPath 'Example.json' } catch {}; "
            "Assert-V31VersionChecksPassed"
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Workbook 'Example.json'", result.stderr)
        self.assertNotIn("Solution 'Legacy'", result.stderr)

    def test_numeric_bounds_do_not_apply_floor_to_other_content_kinds(self):
        policy = attribution.ps_literal(attribution.PACKAGER / "common/versionPolicy.ps1")
        kinds = ("AnalyticsRule", "HuntingQuery", "Parser", "Workbook", "Playbook", "DataConnector", "LogicAppsCustomConnector",
                 "AzureFunction", "SummaryRule", "Watchlist", "CCF DataConnector/Connections")
        for kind in kinds:
            with self.subTest(kind=kind):
                result = self.run_ps(
                    f". {policy}; "
                    "$v31VersionPolicy = @{ Errors = [System.Collections.Generic.List[string]]::new() }; "
                    f"foreach ($v in @('1.0', '1.0.0', '2.0.0', '3.9.99')) {{ Assert-V31ReleaseVersion -Version $v -ContentKind '{kind}' -ContentPath 'test' }}; "
                    f"Assert-V31ReleaseVersion -Version '4.0' -ContentKind '{kind}' -ContentPath 'test'"
                )
                self.assertNotEqual(0, result.returncode)
                self.assertIn("'4.0'", result.stderr)
                self.assertIn("required < 4.0.0", result.stderr)

    def test_other_generators_reject_their_effective_release_versions(self):
        entry = self.fixture(xdr=False)
        base_data = json.loads(self.data.read_text())
        wrapper = self.repository / "Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1"
        with wrapper.open("a") as stream:
            stream.write("function Invoke-WebRequest { return '{\"items\":[]}' }\n")
        cases = [
            ("Hunting Queries", "Hunting Queries/Test.yaml", {
                "id": "33333333-2222-3333-4444-555555555555", "name": "Hunt",
                "description": "Test", "query": "print Test=1", "version": "4.0.0",
                "requiredDataConnectors": [],
            }, "HuntingQuery"),
            ("Parsers", "Parsers/Test.yaml", {
                "FunctionName": "TestParser", "FunctionQuery": "print Test=1",
                "Function": {"Title": "Test", "Version": "4.0.0"},
            }, "Parser"),
            ("Playbooks", "Playbooks/Test/azuredeploy.json", {
                "parameters": {}, "variables": {}, "resources": [{
                    "type": "Microsoft.Logic/workflows", "apiVersion": "2019-05-01",
                    "name": "test", "tags": {"hidden-SentinelTemplateVersion": "4.0.0"},
                    "properties": {"definition": {"actions": {}, "triggers": {}}},
                }],
            }, "Playbook"),
            ("Data Connectors", "Data Connectors/Test.json", {
                "id": "TestConnector", "title": "Test", "publisher": "Test",
                "descriptionMarkdown": "Test", "graphQueries": [], "dataTypes": [],
                "sampleQueries": [], "instructionSteps": [], "permissions": {},
                "metadata": {"version": "4.0.0"},
            }, "DataConnector"),
        ]
        for field, relative, document, kind in cases:
            for pipeline in (False, True):
                with self.subTest(kind=kind, pipeline=pipeline):
                    path = self.solution / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(("---\n" if relative.endswith(".yaml") else "") + json.dumps(document))
                    data = dict(base_data)
                    data[field] = [relative]
                    self.data.write_text(json.dumps(data))
                    result = self.assert_rejected_unchanged(entry, pipeline=pipeline)
                    self.assertIn(kind, result.stdout + result.stderr)

    def test_workbook_independent_numeric_versions_and_malformed_versions(self):
        policy = attribution.ps_literal(attribution.PACKAGER / "common/versionPolicy.ps1")
        result = self.run_ps(
            f". {policy}; "
            "$v31VersionPolicy = @{ Errors = [System.Collections.Generic.List[string]]::new() }; "
            "foreach ($v in @('1.0', '2.0.0', '3.9.99')) { "
            "Assert-V31ReleaseVersion -Version $v -ContentKind Workbook -ContentPath 'Workbooks/Test.json' }; "
            "foreach ($item in @("
            "@('4.0.0', 'Workbooks/MicrosoftDefenderForOffice365detectionsandinsights.json'), "
            "@('4.0.0', 'MicrosoftDefenderForOffice365detectionsandinsights'), "
            "@('4.0.0', 'MicrosoftDefenderForOffice365detectionsandinsights.json'), "
            "@('5.0.0', 'Workbooks/ThreatIntelligence.json'), "
            "@('5.0.0', 'ThreatIntelligenceWorkbook'), "
            "@('5.0.0', 'ThreatIntelligence.json')"
            ")) { Assert-V31ReleaseVersion -Version $item[0] -ContentKind Workbook -ContentPath $item[1] }; "
            "Assert-V31VersionChecksPassed"
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        rejected_cases = (
            ("4.0.0", "Workbooks/Test.json"),
            ("4.1.0", "Workbooks/Test.json"),
            ("10.2.3.4", "Workbooks/Test.json"),
            ("4.1.0", "Workbooks/MicrosoftDefenderForOffice365detectionsandinsights.json"),
            ("5.0.0", "Workbooks/MicrosoftDefenderForOffice365detectionsandinsights.json"),
            ("4.0.0", "Workbooks/ThreatIntelligence.json"),
            ("5.1.0", "Workbooks/ThreatIntelligence.json"),
            ("", "Workbooks/Test.json"),
            ("Notebook/1.0", "Workbooks/Test.json"),
            ("4.0.0-preview", "Workbooks/Test.json"),
            ("4.0.0\n", "Workbooks/Test.json"),
        )
        for version, content_path in rejected_cases:
            with self.subTest(version=version, content_path=content_path):
                result = self.run_ps(
                    f". {policy}; "
                    "$v31VersionPolicy = @{ Errors = [System.Collections.Generic.List[string]]::new() }; "
                    f"try {{ Assert-V31ReleaseVersion -Version {attribution.ps_literal(version)} "
                    f"-ContentKind Workbook -ContentPath {attribution.ps_literal(content_path)} }} catch {{}}; "
                    "Assert-V31VersionChecksPassed"
                )
                self.assertNotEqual(0, result.returncode)
                self.assertIn("required < 4.0.0", result.stderr)

    def test_workbook_version_does_not_relax_solution_or_xdr_versions(self):
        common = attribution.ps_literal(attribution.PACKAGER / "common/commonFunctions.ps1")
        guards = (
            ("Solution", "Assert-V31SolutionVersion -SolutionName 'Sample' -Version $v",
             ("3.1.999", "4.0.0"), ("3.2.0", "3.2.1")),
            ("CustomDetection", "Assert-V31ReleaseVersion -ContentKind CustomDetection -ContentPath 'XDR Detections/Test.yaml' -Version $v",
             ("3.0.99", "4.0.0", "3.1.0-preview"), ("3.1.0", "3.9.99")),
            ("DefenderWorkbook", "Assert-DefenderWorkbookReleaseVersion -Version $v",
             ("3.0.99", "4.0.0", "3.1.0-preview"), ("3.1.0", "3.9.99")),
        )
        for kind, guard, rejected, accepted in guards:
            with self.subTest(kind=kind):
                result = self.run_ps(
                    f". {common}; "
                    "$v31VersionPolicy = @{ Errors = [System.Collections.Generic.List[string]]::new() }; "
                    "Assert-V31ReleaseVersion -Version '4.0.0' -ContentKind Workbook -ContentPath 'Workbooks/MicrosoftDefenderForOffice365detectionsandinsights.json'; "
                    f"foreach ($v in @({','.join(map(attribution.ps_literal, accepted))})) {{ {guard} }}; "
                    "$rejected = @(); "
                    f"foreach ($v in @({','.join(map(attribution.ps_literal, rejected))})) {{ "
                    f"try {{ {guard} }} catch {{ $rejected += $v }} }}; "
                    "ConvertTo-Json -InputObject $rejected -Compress"
                )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertEqual(list(rejected), json.loads(result.stdout))

    def test_workbook_effective_metadata_version_is_checked_and_preserved_for_exceptions(self):
        common = attribution.ps_literal(attribution.PACKAGER / "common/commonFunctions.ps1")
        metadata = self.solution / "Workbooks/WorkbooksMetadata.json"
        metadata.parent.mkdir()
        metadata.write_text(json.dumps([
            {
                "templateRelativePath": "Test.json", "workbookKey": "Test",
                "title": "Test", "description": "Test", "version": "4.0.0",
                "dataTypesDependencies": [], "dataConnectorsDependencies": [],
            },
            {
                "templateRelativePath": "MicrosoftDefenderForOffice365detectionsandinsights.json",
                "workbookKey": "MicrosoftDefenderForOffice365detectionsandinsights",
                "title": "MDO", "description": "MDO", "version": "4.0.0",
                "dataTypesDependencies": [], "dataConnectorsDependencies": [],
            },
        ]))
        workbook = metadata.with_name("Test.json")
        workbook.write_text(json.dumps({
            "version": "Notebook/1.0",
            "items": [{"type": 1, "content": {"json": "# Test"}}],
        }))
        mdo_workbook = metadata.with_name("MicrosoftDefenderForOffice365detectionsandinsights.json")
        mdo_workbook.write_text(workbook.read_text())
        before = self.snapshot()
        rejected = self.run_ps(
            f". {common}; "
            "$v31VersionPolicy = @{ Errors = [System.Collections.Generic.List[string]]::new() }; "
            "$solutionName = 'Sample'; "
            "$global:workbookCounter = 1; $global:DependencyCriteria = @(); "
            "$global:baseMainTemplate = [pscustomobject]@{variables=[pscustomobject]@{};parameters=[pscustomobject]@{};resources=@()}; "
            "$global:baseCreateUiDefinition = [pscustomobject]@{parameters=[pscustomobject]@{steps=@()}}; "
            "$contentToImport = [pscustomobject]@{TemplateSpec=$true;Name='Sample';Version='3.2.1';Author='Microsoft'}; "
            f"$rawData = Get-Content -LiteralPath {attribution.ps_literal(workbook)} -Raw; "
            "GetWorkbookDataMetadata -file 'Workbooks/Test.json' -isPipelineRun $false "
            "-contentResourceDetails (returnContentResources '3.2.1') "
            f"-baseFolderPath {attribution.ps_literal(str(self.solution) + '/')} "
            "-contentToImport $contentToImport; "
            "Assert-V31VersionChecksPassed"
        )
        self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
        self.assertIn("Workbook 'Workbooks/Test.json'", rejected.stderr)
        self.assertIn("'4.0.0'", rejected.stderr)

        result = self.run_ps(
            f". {common}; "
            "$v31VersionPolicy = @{ Errors = [System.Collections.Generic.List[string]]::new() }; "
            "$solutionName = 'Sample'; "
            "$global:workbookCounter = 1; $global:DependencyCriteria = @(); "
            "$global:baseMainTemplate = [pscustomobject]@{variables=[pscustomobject]@{};parameters=[pscustomobject]@{};resources=@()}; "
            "$global:baseCreateUiDefinition = [pscustomobject]@{parameters=[pscustomobject]@{steps=@()}}; "
            "$contentToImport = [pscustomobject]@{TemplateSpec=$true;Name='Sample';Version='3.2.1';Author='Microsoft'}; "
            f"$rawData = Get-Content -LiteralPath {attribution.ps_literal(mdo_workbook)} -Raw; "
            "GetWorkbookDataMetadata -file 'Workbooks/MicrosoftDefenderForOffice365detectionsandinsights.json' -isPipelineRun $false "
            "-contentResourceDetails (returnContentResources '3.2.1') "
            f"-baseFolderPath {attribution.ps_literal(str(self.solution) + '/')} "
            "-contentToImport $contentToImport; "
            "Assert-V31VersionChecksPassed; "
            "$global:baseMainTemplate | ConvertTo-Json -Depth 50 -Compress"
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        template = json.loads(result.stdout.splitlines()[-1])
        self.assertEqual("4.0.0", template["variables"]["workbookVersion1"])
        registered = template["resources"][0]
        self.assertEqual("[variables('workbookVersion1')]", registered["properties"]["version"])
        self.assertEqual(json.loads(mdo_workbook.read_text()),
                         json.loads(registered["properties"]["mainTemplate"]["resources"][0]["properties"]["serializedData"]))
        self.assertEqual(before, self.snapshot())

    def test_ccf_fallback_and_shared_connection_version(self):
        common = attribution.ps_literal(attribution.PACKAGER / "common/commonFunctions.ps1")
        ccf = attribution.ps_literal(attribution.PACKAGER / "common/createCCPConnector.ps1")
        for version in ("1.0.0", "3.9.99", "4.0.0"):
            with self.subTest(version=version):
                result = self.run_ps(
                    f". {common}; . {ccf}; "
                    "$v31VersionPolicy = @{ Errors = [System.Collections.Generic.List[string]]::new() }; "
                    "$data = [pscustomobject]@{ Name='Sample'; Version='3.1.0'; "
                    f"DataConnectorCCFVersion='{version}' }}; "
                    "createCCPConnectorResources -dataFileMetadata $data "
                    "-solutionFileMetadata ([pscustomobject]@{publisherId='test';offerId='sample'}) "
                    "-solutionName Sample -dcFolderName 'Data Connectors' -ccpDict @(); "
                    "Assert-V31VersionChecksPassed"
                )
                if version == "4.0.0":
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn("DataConnectorCCFVersion", result.stderr)
                else:
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_legacy_entry_points_do_not_enable_v31_policy(self):
        entry = self.fixture("4.0.0", xdr=False)
        legacy = entry.with_name("createSolutionV3.ps1")
        shutil.copyfile(attribution.PACKAGER / "V3/createSolutionV3.ps1", legacy)
        result = self.package(legacy, False, version_bump="patch")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("V3.1 version policy", result.stdout + result.stderr)
        self.assertTrue((self.solution / "Package/4.0.1.zip").is_file())
        pipeline = entry.with_name("legacyPipeline.ps1")
        shutil.copyfile(attribution.PACKAGER / "pipeline/createSolutionV4.ps1", pipeline)
        result = self.package(pipeline, True, calculated_version="4.0.1")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("V3.1 version policy", result.stdout + result.stderr)

    def test_provider_and_conversion_versions_are_not_release_versions(self):
        entry = self.fixture()
        self.update_data(**{"XDR Extension Version": "9.0.0"})
        detection = self.solution / "XDR Detections/Test.yaml"
        document = json.loads(detection.read_text().removeprefix("---\n"))
        document["contentProvenance"]["conversion"] = {"version": "9.0.0", "schemaVersion": "9.0.0"}
        detection.write_text("---\n" + json.dumps(document))
        result = self.package(entry, False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        template = json.loads((self.solution / "Package/mainTemplate.json").read_text())
        xdr = next(r for r in template["resources"] if r["type"] == "Microsoft.Resources/deployments"
                   and r.get("condition") == "[parameters('DeployCustomDetection')]")
        self.assertEqual("9.0.0", xdr["properties"]["template"]["imports"]["MicrosoftSecurity"]["version"])
        self.assertEqual("Microsoft.Security/detectionRules@2025-06-01",
                         xdr["properties"]["template"]["resources"]["detectionRule"]["type"])
        self.assertEqual("1.0.0", document["schemaVersion"])


if __name__ == "__main__":
    unittest.main()
