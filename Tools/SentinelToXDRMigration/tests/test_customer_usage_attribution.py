from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

from sentinel_xdr_migration.packaging import V31_TOOLKIT_PATHS


ROOT = Path(__file__).resolve().parents[3]
PACKAGER = ROOT / "Tools" / "Create-Azure-Sentinel-Solution"
TRACKING_ID = "pid-399fb80b-c914-4257-b61e-91ab73733888-partnercenter"
ABSENT = object()


def ps_literal(value: Path | str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


@unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 is required")
class AttributionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix=".v3-1-test-", dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.repository = Path(self.temp.name)
        self.solution = self.repository / "Solutions" / "Sample"
        self.data = self.solution / "Data" / "Solution_Sample.json"
        self.metadata = self.solution / "SolutionMetadata.json"
        self.data.parent.mkdir(parents=True)
        self.metadata.write_text("{}", encoding="utf-8")

    def run_ps(self, command: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["pwsh", "-NoProfile", "-NonInteractive", "-Command",
             "$ErrorActionPreference = 'Stop'; $env:SENTINEL_SKIP_ATTRIBUTION_LOOKUP = '1'; "
             + getattr(self, "ps_prelude", "") + command],
            cwd=self.repository, capture_output=True, text=True,
        )

    def write_metadata(self, tracking_id=ABSENT) -> None:
        value = {
            "publisherId": "testpublisher",
            "offerId": "test-sentinel",
            "version": "3.2.0",
            "firstPublishDate": "2021-01-01",
            "providers": ["Microsoft"],
            "categories": {"domains": ["Security"]},
            "support": {"name": "Test", "tier": "Microsoft", "link": "https://example.com"},
        }
        if tracking_id is not ABSENT:
            value["trackingId"] = tracking_id
        self.metadata.write_text(json.dumps(value), encoding="utf-8")

    def helper(self, tracking_id=ABSENT, warn: bool = True) -> subprocess.CompletedProcess:
        self.write_metadata(tracking_id)
        return self.run_ps(
            f". {ps_literal(PACKAGER / 'common/customerUsageAttribution.ps1')}; "
            "$template = [pscustomobject]@{ resources = @() }; "
            f"Add-CustomerUsageAttribution -SolutionMetadataPath {ps_literal(self.metadata)} "
            f"-Template $template -WarnIfMissing ${str(warn).lower()}; "
            "$template | ConvertTo-Json -Depth 30"
        )

    def test_required_absent_null_and_blank_fail_with_actionable_error(self) -> None:
        for value in (ABSENT, None, "", " \t"):
            with self.subTest(value=value):
                self.mock_lookup(failure="throw [System.TimeoutException]::new(); ")
                result = self.helper(value)
                self.assertNotEqual(0, result.returncode)
                for text in ("Packaging stopped", "Partner Center", "Technical", "configuration",
                             "SolutionMetadata.json", "rebuild", "publisherId", "offerId"):
                    self.assertIn(text, result.stderr)
        self.ps_prelude = ""
        result = self.helper(warn=False)
        self.assertEqual({"resources": []}, json.loads(result.stdout))

    def test_complete_ids_are_preserved_and_marker_shape_is_exact(self) -> None:
        self.mock_lookup(failure="throw 'NETWORK MUST NOT RUN'; ")
        for tracking_id in (TRACKING_ID, "pid-contoso-myoffer-partnercenter"):
            with self.subTest(tracking_id=tracking_id):
                result = self.helper(tracking_id)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual({"resources": [self.marker(tracking_id)]}, json.loads(result.stdout))

    def test_required_lookup_ignores_each_skip_control_and_persists_marker(self) -> None:
        for value in (ABSENT, None, "", " \t"):
            for skip, environment in ((False, False), (True, False), (False, True), (True, True)):
                with self.subTest(value=value, skip=skip, environment=environment):
                    self.write_metadata(value)
                    self.mock_lookup()
                    if environment:
                        self.ps_prelude += "$env:SENTINEL_SKIP_ATTRIBUTION_LOOKUP = '1'; "
                    extra = "-WarnIfMissing $true" + (" -SkipAttributionLookup" if skip else "")
                    result = self.lookup_helper(extra)
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertIn("LOOKUP_CALLS=2", result.stdout)
                    self.assertEqual(TRACKING_ID, json.loads(self.metadata.read_text())["trackingId"])
                    self.assertEqual({"resources": [self.marker(TRACKING_ID)]},
                                     json.loads((self.repository / "result.json").read_text()))

    @staticmethod
    def marker(tracking_id: str) -> dict:
        return {
            "type": "Microsoft.Resources/deployments",
            "apiVersion": "2025-04-01",
            "name": tracking_id,
            "properties": {
                "mode": "Incremental",
                "template": {
                    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
                    "contentVersion": "1.0.0.0",
                    "resources": [],
                },
            },
        }

    def test_invalid_supplied_ids_fail_instead_of_synthesizing(self) -> None:
        for value in ("399fb80b-c914-4257-b61e-91ab73733888", 123, {}, [],
                      "pid-", "pid-bad/name", "[variables('trackingId')]",
                      TRACKING_ID + " ", "pid-" + "a" * 61, "pid-ok\n"):
            with self.subTest(value=value):
                result = self.helper(value)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("Invalid trackingId", result.stderr)

    def test_duplicate_marker_is_rejected(self) -> None:
        self.write_metadata(TRACKING_ID)
        add_marker = (
            f"Add-CustomerUsageAttribution -SolutionMetadataPath {ps_literal(self.metadata)} "
            "-Template $template; "
        )
        command = (
            f". {ps_literal(PACKAGER / 'common/customerUsageAttribution.ps1')}; "
            "$template = [pscustomobject]@{ resources = @() }; "
        )
        result = self.run_ps(command + add_marker + add_marker)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Duplicate customer usage", result.stderr)

    def prepare_integration(self) -> Path:
        for relative in V31_TOOLKIT_PATHS:
            source = ROOT / relative
            destination = self.repository / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        tools = self.repository / "Tools" / "Create-Azure-Sentinel-Solution"
        entry = tools / "V3" / "createSolutionV3_1.ps1"
        # Run real packaging, but isolate output and exclude the unrelated full validators.
        (tools / "common/commonFunctions.ps1").write_text(
            f". {ps_literal(PACKAGER / 'common/commonFunctions.ps1')}\n"
            f"function global:git {{ $global:LASTEXITCODE = 0; {ps_literal(self.repository)} }}\n"
            "function RunArmTtkOnPackage { }\n"
            "function CheckJsonIsValid { }\n",
            encoding="utf-8",
        )
        source_id = "11111111-2222-3333-4444-555555555555"
        rule = {
            "id": source_id, "name": "Test rule", "description": "Packaging test.",
            "severity": "Medium", "kind": "Scheduled", "version": "1.0.0",
            "query": "print Test = 1", "queryFrequency": "1h", "queryPeriod": "1h",
            "triggerOperator": "gt", "triggerThreshold": 0, "tactics": ["Execution"],
            "requiredDataConnectors": [], "entityMappings": [],
        }
        detection = {
            "schemaVersion": "1.0.0", "version": "3.1.0",
            "kind": "CustomDetection", "resourceType": "Microsoft.Security/detectionRules",
            "apiVersion": "2025-06-01",
            "contentProvenance": {"requiredWorkloads": [], "requiredDataConnectors": [], "source": {
                "id": source_id, "version": "1.0.0",
                "platform": "Microsoft Sentinel", "kind": "AnalyticsRule",
            }},
            "properties": {
                "id": source_id,
                "displayName": "Test detection", "status": "disabled",
                "queryCondition": {"queryText": "print Test = 1"},
                "detectionAction": {"alertTemplate": {"tactics": [{"tactic": "Execution"}], "entityMappings": {}}},
            },
        }
        for folder, document in (("Analytic Rules", rule), ("XDR Detections", detection)):
            path = self.solution / folder / "Test.yaml"
            path.parent.mkdir()
            path.write_text("---\n" + json.dumps(document), encoding="utf-8")
        self.data.write_text(json.dumps({
            "Name": "Sample", "Author": "Test", "Description": "Test package",
            "Version": "3.2.0", "TemplateSpec": True,
            "Analytic Rules": ["Analytic Rules/Test.yaml"],
            "XDR Detections": ["XDR Detections/Test.yaml"],
            "Metadata": "SolutionMetadata.json",
            "trackingId": "pid-stale-data-partnercenter",
        }), encoding="utf-8")
        return entry

    def package(
        self, entry: Path, pipeline: bool, *,
        version_bump: str = "none", version_mode: str = "local",
        calculated_version: str = "3.2.0",
        skip_lookup: bool = False,
    ) -> subprocess.CompletedProcess:
        extra = " -SkipAttributionLookup" if skip_lookup else ""
        if not pipeline:
            return self.run_ps(
                f"& {ps_literal(entry)} -SolutionDataFolderPath {ps_literal(self.data.parent)} "
                f"-VersionMode {version_mode} -VersionBump {version_bump}{extra}"
            )
        return self.run_ps(
            f"$data = Get-Content -Raw {ps_literal(self.data)} | ConvertFrom-Json; "
            f"$metadata = Get-Content -Raw {ps_literal(self.metadata)} | ConvertFrom-Json; "
            "foreach ($property in $metadata.PSObject.Properties) { "
            "if ($property.Name -notin @('version', 'trackingId')) { "
            "$data | Add-Member -NotePropertyName $property.Name -NotePropertyValue $property.Value } }; "
            f"& {ps_literal(entry)} {ps_literal(str(self.repository) + '/')} 'Sample' $data "
            "'Solution_Sample.json' 'Data Connectors' 'Data' 'test' '1' '1' "
            f"{ps_literal(calculated_version)} '3.0.0' $false{extra}"
        )

    def mock_lookup(self, *, catalog=None, document=None, failure="", mutation="") -> None:
        if catalog is None:
            catalog = {"items": [{
                "publisherId": "testpublisher", "offerId": "test-sentinel",
                "ocpSolutionId": "must-not-be-used",
                "plans": [{
                    "id": "0001", "planId": "different-plan-id",
                    "artifacts": [{
                        "type": "Template", "name": "DefaultTemplate",
                        "uri": "https://catalogartifact.azureedge.net/publicartifacts/test/mainTemplate.json",
                    }],
                }],
            }]}
        if document is None:
            document = {
                "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
                "contentVersion": "1.0.0.0", "resources": [self.marker(TRACKING_ID)],
            }
            document["resources"][0]["apiVersion"] = "2020-10-01"
        for name, value in (("catalog.json", catalog), ("published.json", document)):
            (self.repository / name).write_text(json.dumps(value), encoding="utf-8")
        self.ps_prelude = (
            "$env:SENTINEL_SKIP_ATTRIBUTION_LOOKUP = '0'; "
            "$global:lookupCalls = 0; "
            "function global:Invoke-WebRequest { param($Uri, $Method, $TimeoutSec, $OperationTimeoutSeconds, $MaximumRedirection) "
            "if ($TimeoutSec -ne 20 -or $MaximumRedirection -ne 0 -or $Method -ne 'Get') { throw 'Unbounded request' }; "
            "if ((Get-Command Microsoft.PowerShell.Utility\\Invoke-WebRequest).Parameters.ContainsKey('OperationTimeoutSeconds') "
            "-and $OperationTimeoutSeconds -ne 20) { throw 'Unbounded read' }; "
            "$global:lookupCalls++; "
            + failure
            + "if ($Uri -like 'https://catalogapi.azure.com/*') { "
            "if ([uri]::UnescapeDataString($Uri) -notlike \"*publisherId eq 'testpublisher' and offerId eq 'test-sentinel'*\") "
            "{ throw 'Wrong catalog identity filter' }; "
            f"$content = Get-Content -Raw {ps_literal(self.repository / 'catalog.json')} "
            "} else { "
            + mutation
            + f"$content = Get-Content -Raw {ps_literal(self.repository / 'published.json')} "
            "}; [pscustomobject]@{ Content = $content } }; "
        )

    def lookup_helper(self, extra="") -> subprocess.CompletedProcess:
        return self.run_ps(
            f". {ps_literal(PACKAGER / 'common/customerUsageAttribution.ps1')}; "
            "$template = [pscustomobject]@{ resources = @() }; "
            f"Add-CustomerUsageAttribution -SolutionMetadataPath {ps_literal(self.metadata)} "
            f"-Template $template {extra}; "
            f"$template | ConvertTo-Json -Depth 30 | Set-Content {ps_literal(self.repository / 'result.json')}; "
            "Write-Host \"LOOKUP_CALLS=$global:lookupCalls\""
        )

    def test_discovery_persists_exact_id_preserving_bytes_and_replay_is_offline(self) -> None:
        for value in (ABSENT, None, "", " \t"):
            with self.subTest(value=value):
                self.write_metadata(value)
                metadata = json.loads(self.metadata.read_text())
                metadata["nested"] = {"trackingId": "never replace é", "text": "line1\nline2"}
                original = json.dumps(metadata, indent="\t", ensure_ascii=False).replace("\n", "\r\n") + "\r\n"
                self.metadata.write_bytes(b"\xef\xbb\xbf" + original.encode())
                self.mock_lookup()
                result = self.lookup_helper()
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                expected = dict(metadata, trackingId=TRACKING_ID)
                self.assertEqual(expected, json.loads(self.metadata.read_text(encoding="utf-8-sig")))
                updated = self.metadata.read_bytes()
                if value is ABSENT:
                    expected_text = original.replace('{\r\n\t', '{\r\n\t"trackingId": "' + TRACKING_ID + '",\r\n\t', 1)
                else:
                    expected_text = original.replace('"trackingId": ' + json.dumps(value),
                                                     '"trackingId": "' + TRACKING_ID + '"', 1)
                self.assertEqual(b"\xef\xbb\xbf" + expected_text.encode(), updated)
                self.assertEqual({"resources": [self.marker(TRACKING_ID)]},
                                 json.loads((self.repository / "result.json").read_text()))
                for text in ("publisherId=testpublisher", "offerId=test-sentinel",
                             "planId=different-plan-id", "templateURL=https://",
                             "updated metadata=", "LOOKUP_CALLS=2"):
                    self.assertIn(text, result.stdout)
                self.mock_lookup(failure="throw 'NETWORK MUST NOT RUN'; ")
                result = self.lookup_helper()
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertIn("LOOKUP_CALLS=0", result.stdout)
                self.assertEqual(updated, self.metadata.read_bytes())

    def test_ambiguous_or_nonconformant_remote_documents_warn_without_writes(self) -> None:
        self.mock_lookup()
        catalog = json.loads((self.repository / "catalog.json").read_text())
        document = json.loads((self.repository / "published.json").read_text())
        import copy
        cases = []
        for label in ("wrong publisher", "wrong offer", "multiple offers", "multiple plans",
                      "multiple artifacts", "missing uri", "missing plan id", "catalog array",
                      "pagination"):
            value = copy.deepcopy(catalog)
            offer = value["items"][0]
            if label == "wrong publisher":
                offer["publisherId"] = "other"
            elif label == "wrong offer":
                offer["offerId"] = "other"
            elif label == "multiple offers":
                value["items"].append(copy.deepcopy(offer))
            elif label == "multiple plans":
                offer["plans"].append(copy.deepcopy(offer["plans"][0]))
            elif label == "multiple artifacts":
                offer["plans"][0]["artifacts"] *= 2
            elif label == "missing uri":
                del offer["plans"][0]["artifacts"][0]["uri"]
            elif label == "missing plan id":
                del offer["plans"][0]["planId"]
            elif label == "catalog array":
                value = []
            else:
                value["nextLink"] = "https://catalogapi.azure.com/next"
            cases.append((label, value, document))
        for label in ("missing marker", "multiple markers", "functional wrapper", "linked template",
                      "conditional marker", "expression", "bad id", "root array", "unversioned object",
                      "bad schema", "bad version", "scalar resource", "bad marker api"):
            value = copy.deepcopy(document)
            marker = value["resources"][0]
            if label == "missing marker":
                value["resources"] = []
            elif label == "multiple markers":
                value["resources"].append(copy.deepcopy(marker))
            elif label == "functional wrapper":
                marker["properties"]["template"]["resources"] = [{"type": "Microsoft.Security/detectionRules"}]
            elif label == "linked template":
                marker["properties"]["templateLink"] = {"uri": "https://example.invalid"}
            elif label == "conditional marker":
                marker["condition"] = False
            elif label == "expression":
                marker["name"] = "[concat('pid-', 'not-literal')]"
            elif label == "bad id":
                marker["name"] = "pid-invalid/name"
            elif label == "root array":
                value = [value]
            elif label == "bad schema":
                value["$schema"] = "https://schemaXmanagementXazure.com/schemas/2019-04-01/deploymentTemplate.json#"
            elif label == "bad version":
                value["contentVersion"] = ""
            elif label == "scalar resource":
                value["resources"].append("invalid resource")
            elif label == "bad marker api":
                marker["apiVersion"] = "invalid"
            else:
                value["resources"] = {"marker": marker}
            cases.append((label, catalog, value))
        for label, catalog_value, document_value in cases:
            with self.subTest(label=label):
                self.write_metadata()
                before = self.metadata.read_bytes()
                self.mock_lookup(catalog=catalog_value, document=document_value)
                result = self.lookup_helper()
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn("CUSTOMER USAGE ATTRIBUTION: Published lookup failed [", result.stdout)
                self.assertNotIn("ATTRIBUTION SOURCE:", result.stdout)
                self.assertEqual(before, self.metadata.read_bytes())
                self.assertEqual({"resources": []}, json.loads((self.repository / "result.json").read_text()))

    def test_symbolic_root_uses_literal_name_not_symbolic_key(self) -> None:
        self.write_metadata()
        self.mock_lookup()
        path = self.repository / "published.json"
        document = json.loads(path.read_text())
        document["languageVersion"] = "2.0"
        document["resources"] = {"symbolicMarker": document["resources"][0]}
        path.write_text(json.dumps(document))
        result = self.lookup_helper()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(TRACKING_ID, json.loads(self.metadata.read_text())["trackingId"])

    def test_network_and_json_failures_are_classified_and_redacted(self) -> None:
        failures = (
            ("throw [System.TimeoutException]::new('secret?sig=hidden'); ", "timeout"),
            ("throw [System.Net.Http.HttpRequestException]::new('secret?sig=hidden'); ", "network/read failure"),
            ("$e = [Exception]::new('secret?sig=hidden'); "
             "$e | Add-Member Response ([pscustomobject]@{StatusCode=503}); throw $e; ", "HTTP 503"),
            ("return [pscustomobject]@{ Content = 'invalid json secret?sig=hidden' }; ", "invalid JSON"),
        )
        for stage in ("catalog", "template"):
            for failure, classification in failures:
                with self.subTest(stage=stage, classification=classification):
                    self.write_metadata()
                    before = self.metadata.read_bytes()
                    condition = "$global:lookupCalls -eq " + ("1" if stage == "catalog" else "2")
                    self.mock_lookup(failure=f"if ({condition}) {{ {failure} }}; ")
                    result = self.lookup_helper()
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertIn(f"{stage}: {classification}", result.stdout)
                    self.assertNotIn("hidden", result.stdout + result.stderr)
                    self.assertEqual(before, self.metadata.read_bytes())

    def test_duplicate_json_properties_are_not_silently_overwritten(self) -> None:
        self.write_metadata()
        before = self.metadata.read_bytes()
        self.mock_lookup()
        path = self.repository / "published.json"
        path.write_text(path.read_text().replace(
            '"resources": [', '"resources": [], "resources": [', 1))
        result = self.lookup_helper()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("template: invalid JSON", result.stdout)
        self.assertEqual(before, self.metadata.read_bytes())

    def test_protected_template_url_query_is_not_logged(self) -> None:
        self.write_metadata()
        self.mock_lookup()
        path = self.repository / "catalog.json"
        catalog = json.loads(path.read_text())
        catalog["items"][0]["plans"][0]["artifacts"][0]["uri"] += "?sig=hidden-secret&se=expiry"
        path.write_text(json.dumps(catalog))
        result = self.lookup_helper()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("ATTRIBUTION SOURCE:", result.stdout)
        self.assertNotIn("hidden-secret", result.stdout + result.stderr)
        self.assertNotIn("?sig=", result.stdout + result.stderr)

    def test_explicit_values_and_skip_controls_never_lookup(self) -> None:
        for value, extra in ((TRACKING_ID, ""), ("bad/id", ""), (ABSENT, "-SkipAttributionLookup"),
                             (ABSENT, "")):
            with self.subTest(value=value, extra=extra):
                self.write_metadata(value)
                before = self.metadata.read_bytes()
                self.mock_lookup(failure="throw 'NETWORK MUST NOT RUN'; ")
                if value is ABSENT and not extra:
                    self.ps_prelude += "$env:SENTINEL_SKIP_ATTRIBUTION_LOOKUP = '1'; "
                result = self.lookup_helper(extra)
                if value == "bad/id":
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn("Invalid trackingId", result.stderr)
                else:
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn("LOOKUP_CALLS=0", result.stdout)
                self.assertNotIn("NETWORK MUST NOT RUN", result.stdout + result.stderr)
                self.assertEqual(before, self.metadata.read_bytes())

    def test_write_failure_and_concurrent_edit_are_hard_errors(self) -> None:
        for failure in ("write", "concurrent"):
            with self.subTest(failure=failure):
                self.write_metadata()
                before = self.metadata.read_bytes()
                if failure == "write":
                    mutation = f"$global:lockedMetadata = [IO.File]::Open({ps_literal(self.metadata)}, 'Open', 'Read', 'None'); "
                else:
                    mutation = f"[IO.File]::AppendAllText({ps_literal(self.metadata)}, ' '); "
                self.mock_lookup(mutation=mutation)
                result = self.lookup_helper()
                self.assertNotEqual(0, result.returncode)
                self.assertIn("metadata write failed", result.stderr)
                self.assertNotIn("ATTRIBUTION SOURCE:", result.stdout)
                self.assertEqual(before + (b" " if failure == "concurrent" else b""), self.metadata.read_bytes())
                self.assertEqual([], list(self.solution.glob("*.attribution-*")))

    def test_lookup_local_and_pipeline_use_authoritative_metadata_and_keep_cached_id_on_bump(self) -> None:
        entry = self.prepare_integration()
        for pipeline in (False, True):
            for skip, environment in ((False, False), (True, False), (False, True)):
                with self.subTest(pipeline=pipeline, skip=skip, environment=environment):
                    self.write_metadata()
                    self.mock_lookup()
                    if environment:
                        self.ps_prelude += "$env:SENTINEL_SKIP_ATTRIBUTION_LOOKUP = '1'; "
                    result = self.package(entry, pipeline, skip_lookup=skip)
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                    template = json.loads((self.solution / "Package/mainTemplate.json").read_text())
                    markers = [r for r in template["resources"] if r.get("name") == TRACKING_ID]
                    self.assertEqual(1, len(markers))
                    self.assertEqual(TRACKING_ID,
                                     json.loads(self.metadata.read_text()).get("trackingId"))
        self.write_metadata()
        self.mock_lookup()
        result = self.package(entry, False, version_bump="patch")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        metadata = json.loads(self.metadata.read_text())
        self.assertEqual("3.2.1", metadata["version"])
        self.assertEqual(TRACKING_ID, metadata["trackingId"])

    def test_failed_packaging_prerequisite_does_not_persist_discovery(self) -> None:
        entry = self.prepare_integration()
        self.write_metadata()
        before = self.metadata.read_bytes()
        data = json.loads(self.data.read_text())
        data["Version"] = "4.0.0"
        self.data.write_text(json.dumps(data))
        self.mock_lookup()
        result = self.package(entry, False)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("V3.1 version policy", result.stdout + result.stderr)
        self.assertNotIn("ATTRIBUTION SOURCE:", result.stdout)
        self.assertEqual(before, self.metadata.read_bytes())

    def test_local_and_positional_pipeline_preserve_nested_xdr_and_authoritative_id(self) -> None:
        entry = self.prepare_integration()
        self.write_metadata(TRACKING_ID)
        before = self.data.read_bytes(), self.metadata.read_bytes()
        self.mock_lookup(failure="throw 'NETWORK MUST NOT RUN'; ")
        for pipeline in (False, True):
            with self.subTest(pipeline=pipeline):
                result = self.package(entry, pipeline)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                package = self.solution / "Package"
                template = json.loads((package / "mainTemplate.json").read_text(encoding="utf-8-sig"))
                self.assertNotIn("languageVersion", template)
                self.assertIsInstance(template["resources"], list)
                deployments = [r for r in template["resources"] if r["type"] == "Microsoft.Resources/deployments"]
                self.assertEqual(2, len(deployments))
                self.assertIn(self.marker(TRACKING_ID), deployments)
                xdr = next(r for r in deployments if r["name"] != TRACKING_ID)
                self.assertEqual("[parameters('DeployCustomDetection')]", xdr["condition"])
                self.assertEqual("2.0", xdr["properties"]["template"]["languageVersion"])
                self.assertIsInstance(xdr["properties"]["template"]["resources"], dict)
                self.assertEqual(
                    "disabled",
                    xdr["properties"]["template"]["resources"]["detectionRule"]["properties"]["status"],
                )
                analytic = next(r for r in template["resources"]
                                if r.get("properties", {}).get("contentKind") == "AnalyticsRule")
                self.assertEqual("[parameters('DeployAnalyticsRule')]", analytic["condition"])
                self.assertEqual("3.0.0", analytic["properties"]["contentSchemaVersion"])
                self.assertEqual("3.2.0", template["variables"]["_solutionVersion"])
                self.assertNotIn("trackingId", json.dumps(template))
                self.assertNotIn("pid-stale-data", json.dumps(template))
                with zipfile.ZipFile(package / "3.2.0.zip") as archive:
                    self.assertEqual(template, json.loads(archive.read("mainTemplate.json").decode("utf-8-sig")))
                self.assertEqual(before, (self.data.read_bytes(), self.metadata.read_bytes()))

    def test_required_lookup_failures_stop_entry_points_before_artifacts_or_metadata_writes(self) -> None:
        entry = self.prepare_integration()
        for pipeline in (False, True):
            for failure in ("network", "ambiguity", "invalid supplied ID"):
                with self.subTest(pipeline=pipeline, failure=failure):
                    self.write_metadata("bad/id" if failure == "invalid supplied ID" else ABSENT)
                    before = self.metadata.read_bytes()
                    if failure == "ambiguity":
                        self.mock_lookup(catalog={"items": []})
                    else:
                        self.mock_lookup(failure="throw [System.TimeoutException]::new('secret?sig=hidden'); ")
                    self.ps_prelude += "$env:SENTINEL_SKIP_ATTRIBUTION_LOOKUP = '1'; "
                    result = self.package(entry, pipeline, skip_lookup=True)
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn("Invalid trackingId" if failure == "invalid supplied ID"
                                  else "Required published lookup failed", result.stderr)
                    self.assertNotIn("hidden", result.stdout + result.stderr)
                    self.assertNotIn("Package Generated Successfully", result.stdout)
                    self.assertEqual(before, self.metadata.read_bytes())
                    self.assertFalse((self.solution / "Package").exists())
                    self.assertEqual([], list(self.solution.glob("*.attribution-*")))

    def test_optional_packaging_preserves_offline_skips_and_warning_only_failures(self) -> None:
        entry = self.prepare_integration()
        data = json.loads(self.data.read_text())
        del data["XDR Detections"]
        self.data.write_text(json.dumps(data))
        for pipeline in (False, True):
            for route in ("switch", "environment", "failure"):
                with self.subTest(pipeline=pipeline, route=route):
                    self.write_metadata()
                    before = self.metadata.read_bytes()
                    self.mock_lookup(failure="throw [System.TimeoutException]::new(); ")
                    if route == "environment":
                        self.ps_prelude += "$env:SENTINEL_SKIP_ATTRIBUTION_LOOKUP = '1'; "
                    result = self.package(entry, pipeline, skip_lookup=route == "switch")
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertEqual(route == "failure", "Published lookup failed" in result.stdout)
                    self.assertEqual(before, self.metadata.read_bytes())
                    template = json.loads((self.solution / "Package/mainTemplate.json").read_text())
                    self.assertFalse(any(r["type"] == "Microsoft.Resources/deployments"
                                         for r in template["resources"]))
                    self.assertTrue((self.solution / "Package/3.2.0.zip").exists())


if __name__ == "__main__":
    unittest.main()
