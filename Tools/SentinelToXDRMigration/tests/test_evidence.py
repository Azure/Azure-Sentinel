from __future__ import annotations

import hashlib
import io
import json
import shutil
import subprocess
import unittest
import uuid
from copy import deepcopy
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import yaml

from sentinel_xdr_migration.authoring_contract import seal_authoring_contract
from sentinel_xdr_migration.artifacts import report_directory, using_run
from sentinel_xdr_migration.cli import main
from sentinel_xdr_migration.content_paths import yaml_files
from sentinel_xdr_migration.evidence import _markdown, _public_solution_name, export_evidence
from sentinel_xdr_migration.workflow import initialize_workflow, workflow_status


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.storage = Path.cwd() / (".evidence-test-" + uuid.uuid4().hex)
        self.solution = self.storage / "Solutions" / "Sample"
        self.solution.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.storage)
        self.state = initialize_workflow(self.solution, workflow_profile="authoring", version_bump="none")
        self.run = report_directory(self.solution)
        self.run_id = self.run.name
        self.source = self.solution / "Analytic Rules" / "Rule.yaml"
        self.output = self.solution / "XDR Detections" / "Rule.yaml"
        self.source.parent.mkdir()
        self.output.parent.mkdir()
        self.source.write_text(yaml.safe_dump({"id": "source-rule", "version": "1.2.3", "query": "DeviceEvents"}))
        self.output.write_text(yaml.safe_dump({
            "version": "3.1.0", "contentProvenance": {
                "source": {"id": "source-rule", "path": "Analytic Rules/Rule.yaml",
                           "querySha256": hashlib.sha256(b"DeviceEvents").hexdigest()},
                "conversion": {"version": "0.1.0"},
            },
        }))

    def write(self, name, value):
        (self.run / name).write_text(json.dumps(value))

    def export(self):
        result = export_evidence(self.solution)
        return json.loads((self.solution / result["evidence"]).read_text())

    def authoring_contract(self, statuses, *, rule_ids=None, qualification_statuses=None):
        inventory = []
        results = []
        rule_ids = rule_ids or [f"source-rule-{index}" for index in range(len(statuses))]
        qualification_statuses = qualification_statuses or ["untested"] * len(statuses)
        for index, (status, rule_id, qualification) in enumerate(
            zip(statuses, rule_ids, qualification_statuses)
        ):
            source_hash = f"{index + 1:064x}"
            inventory.append({
                "ruleId": rule_id,
                "sha256": source_hash,
                "evidenceReferences": [{
                    "path": "evidence/private-tenant-secret.json",
                    "sha256": "c" * 64,
                    "kind": "source",
                }],
            })
            findings = []
            if index == 0:
                findings.extend([
                    {
                        "findingId": "warning-1",
                        "kind": "warning",
                        "message": "PRIVATE_WARNING_PROSE",
                        "unresolved": False,
                        "evidenceReferences": [],
                    },
                    {
                        "findingId": "assumption-1",
                        "kind": "assumption",
                        "message": "PRIVATE_ASSUMPTION_PROSE",
                        "unresolved": False,
                        "evidenceReferences": [],
                    },
                ])
            if status in {"blocked", "suppressed"}:
                findings.append({
                    "findingId": "error-1",
                    "kind": "error",
                    "message": "PRIVATE_ERROR_PROSE",
                    "unresolved": True,
                    "evidenceReferences": [],
                })
            qualification_references = []
            if qualification == "qualified":
                qualification_references = [
                    {
                        "path": f"evidence/runtime-{index}.json",
                        "sha256": "d" * 64,
                        "kind": "runtimeVerification",
                    },
                    {
                        "path": f"evidence/parity-{index}.json",
                        "sha256": "e" * 64,
                        "kind": "alertParity",
                    },
                ]
            results.append({
                "ruleId": rule_id,
                "sourceSha256": source_hash,
                "status": status,
                "deploymentDisposition": {
                    "migrated": "normal",
                    "blocked": "deploymentBlocked",
                    "suppressed": "suppressed",
                    "unprocessed": "normal",
                }[status],
                "target": {
                    "path": f"XDR Detections/private-tenant-{index}.yaml",
                    "sha256": "b" * 64,
                    "structurallyValid": True,
                } if status != "unprocessed" else None,
                "reviewRequired": index == 0,
                "mappingAssumptions": ["PRIVATE_MAPPING_ASSUMPTION_PROSE"] if index == 0 else [],
                "findings": findings,
                "qualificationStatus": qualification,
                "qualificationEvidenceReferences": qualification_references,
                "evidenceReferences": [],
            })
        return seal_authoring_contract({
            "schemaVersion": "1.0.0",
            "runId": self.run_id,
            "source": {
                "identity": "PRIVATE_SOURCE_IDENTITY workspace tenant /Users/private",
                "sha256": "a" * 64,
            },
            "inventory": {"complete": True, "rules": inventory},
            "results": results,
            "environmentErrors": [{
                "code": "providerUnavailable",
                "message": "PRIVATE_ENVIRONMENT_ERROR tenant workspace",
                "evidenceReferences": [],
            }],
            "entityValueParityPolicy": {
                "assertion": "value-preserved-in-actual-corresponding-alert",
                "comparison": "value-only",
                "entityTypeIdentifierAndCustomFieldMayDiffer": True,
                "requiredForQualification": True,
            },
        })

    def manifest(self):
        self.write("manifest.json", {"total": 3, "converted": 1, "needsReview": 1, "excluded": 1, "results": [
            {"sourceRelativePath": "Analytic Rules/Rule.yaml", "outputRelativePath": "XDR Detections/Rule.yaml",
             "status": status, "reviewRequired": status == "needsReview"} for status in ("converted", "needsReview", "excluded")
        ]})

    def test_all_statuses_counts_hashes_and_original_reports_preserved(self):
        self.manifest()
        state = json.loads((self.run / "workflow-state.json").read_text())
        state["workflowStatus"] = "blocked"
        state["stages"]["discovery"]["status"] = "passed"
        state["stages"]["conversion"]["status"] = "blocked"
        self.write("workflow-state.json", state)
        self.write("runtime-validation.graph.json", {
            "total": 4, "valid": 1, "invalid": 1, "blocked": 1, "notRun": 1,
            "results": [{"detection": "Rule.yaml", "status": status, "error": "raw-private-response"}
                        for status in ("passed", "failed", "blocked", "not-run")],
        })
        before = {p.name: p.read_bytes() for p in self.run.iterdir()}
        evidence = self.export()
        self.assertEqual("blocked", evidence["recordedWorkflowStatus"])
        self.assertEqual("notRequired", evidence["stages"]["alertParity"]["recordedStatus"])
        self.assertEqual("pending", evidence["stages"]["packaging"]["recordedStatus"])
        report = evidence["reports"]["runtimeGraph"]
        self.assertEqual(["passed", "failed", "blocked", "not-run"], [x["recordedStatus"] for x in report["items"]])
        self.assertTrue(all(
            item["queryHashBinding"]["status"] == "stale-or-missing"
            for item in report["items"]
        ))
        self.assertEqual(1, report["counts"]["invalid"])
        for item in report["items"]:
            reference = item["content"]
            self.assertFalse(Path(reference["path"]).is_absolute())
            self.assertEqual(hashlib.sha256(self.output.read_bytes()).hexdigest(), reference["sha256"])
        self.assertEqual("matches", evidence["reports"]["conversion"]["items"][0]["provenance"]["sourceQuery"])
        self.assertEqual("unsupported", evidence["reports"]["conversion"]["items"][0]["provenance"]["historicalValidationBinding"])
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.run.iterdir()})
        self.assertNotIn("raw-private-response", json.dumps(evidence))

    def test_solution_env_is_never_read_or_copied_into_optional_evidence(self):
        private_marker = "PRIVATE_ENV_SENTINEL_DO_NOT_EXPORT"
        (self.solution / ".env").write_text(
            f"PRIVATE_SETTING={private_marker}\n", encoding="utf-8"
        )
        evidence = self.export()
        exported = json.dumps(evidence) + "\n" + (
            self.solution / "Evidence" / self.run_id / "summary.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn(private_marker, exported)
        self.assertTrue((self.solution / ".env").is_file())

    def test_runtime_result_records_exact_current_query_binding(self):
        source_query = "DeviceEvents | where TimeGenerated > ago(4h)"
        target_query = "DeviceEvents | where Timestamp >= ago(2h)"
        self.source.write_text(yaml.safe_dump({
            "id": "source-rule", "query": source_query,
        }))
        self.output.write_text(yaml.safe_dump({
            "version": "3.1.0",
            "contentProvenance": {
                "source": {"id": "source-rule", "path": "Analytic Rules/Rule.yaml"},
            },
            "properties": {
                "queryCondition": {"queryText": target_query},
            },
        }))
        self.write("runtime-validation.graph.json", {
            "provider": "graph",
            "results": [{
                "detection": "Rule.yaml",
                "status": "passed",
                "querySha256": hashlib.sha256(target_query.encode()).hexdigest(),
            }],
        })
        self.write("runtime-validation.triage-mcp.json", {
            "provider": "triage-mcp",
            "results": [{
                "detection": "Rule.yaml",
                "status": "passed",
                "querySha256": hashlib.sha256(source_query.encode()).hexdigest(),
            }],
        })
        self.write("runtime-validation.azure-monitor-sdk.json", {
            "provider": "azure-monitor-sdk",
            "results": [{
                "detection": "Rule.yaml",
                "status": "passed",
                "querySha256": hashlib.sha256(source_query.encode()).hexdigest(),
                "tables": [{"columns": [{"name": "DeviceEvents"}], "rows": [["private row"]]}],
            }],
        })

        evidence = self.export()
        self.assertEqual(
            "matches",
            evidence["reports"]["runtimeGraph"]["items"][0]["queryHashBinding"]["status"],
        )
        self.assertEqual(
            "matches",
            evidence["reports"]["runtimeTriage"]["items"][0]["queryHashBinding"]["status"],
        )
        sdk_item = evidence["reports"]["runtimeAzureMonitorSdk"]["items"][0]
        self.assertEqual("azure-monitor-sdk", sdk_item["provider"])
        self.assertEqual("matches", sdk_item["queryHashBinding"]["status"])
        self.assertNotIn("private row", json.dumps(evidence))

    def test_completed_workflow_does_not_turn_missing_evidence_into_pass(self):
        state = json.loads((self.run / "workflow-state.json").read_text())
        state["workflowStatus"] = "completed"
        self.write("workflow-state.json", state)
        evidence = self.export()
        self.assertEqual("completed", evidence["recordedWorkflowStatus"])
        self.assertEqual("missing", evidence["reports"]["packaging"]["availability"])
        self.assertEqual("unknown", evidence["reports"]["packaging"]["recordedStatus"])
        self.assertEqual("unsupported", evidence["baselineDecision"]["availability"])
        self.assertEqual("recorded-only-not-attested", evidence["verification"])

    def test_free_text_provider_payloads_credentials_ids_and_urls_never_exported(self):
        secrets = [
            "Bearer eyJhbGciOi-secret", "password=pwd123", "tenant-private-value",
            "11111111-2222-3333-4444-555555555555",
            "/Users/alice/credentials", r"C:\Users\alice\credentials",
            "https://host.invalid/private?sig=SIGNED_SECRET",
        ]
        state = json.loads((self.run / "workflow-state.json").read_text())
        state["context"]["tenantId"] = secrets[3]
        state["context"]["versionBump"] = secrets[0]
        state["context"]["workflowProfile"] = secrets[1]
        for item in state["stages"].values():
            item.update(message=secrets, evidence=secrets, artifacts={"providerResponse": secrets})
        self.write("workflow-state.json", state)
        self.write("manifest.json", {"unknown": secrets, "results": [
            {"status": secret, "displayName": secret, "source": secret, "output": secret,
             "warnings": secrets, "reviewReasons": secrets, "errors": secrets,
             "providerResponse": {"records": secrets}, "toolVersion": secret, "command": secret}
            for secret in secrets
        ]})
        self.write("packaging.v3_1.json", {"status": "failed", "warnings": secrets, "attributionSources": secrets, "version": secrets[0], "mainTemplate": secrets[4]})
        self.write("alert-parity-report.json", {"status": "failed", "comparisons": [
            {"detection": "Rule.yaml", "passed": False, "alerts": secrets, "error": secrets}
        ]})
        self.write("raw-provider-response.json", {"records": secrets})
        evidence = self.export()
        published = "\n".join(path.read_text() for path in (self.solution / "Evidence" / self.run_id).iterdir())
        for secret in secrets:
            self.assertNotIn(secret, published)
        self.assertNotIn("raw-provider-response", published)
        self.assertEqual("failed", evidence["reports"]["alertParity"]["items"][0]["recordedStatus"])
        self.assertEqual(7, evidence["reports"]["conversion"]["items"][0]["errorCount"])

    def test_unknown_invalid_missing_and_mismatched_reports_are_explicit(self):
        (self.run / "manifest.json").write_text("{invalid private")
        self.write("runtime-validation.graph.json", {"runId": "different-run", "status": "passed"})
        self.write("structural-validation.json", {"results": [{"valid": False, "file": "XDR Detections/Rule.yaml", "errors": ["private"]}, {"status": "novel-status"}]})
        evidence = self.export()
        self.assertEqual("invalid", evidence["reports"]["conversion"]["availability"])
        self.assertEqual("run-mismatch", evidence["reports"]["runtimeGraph"]["availability"])
        self.assertEqual("unknown", evidence["reports"]["runtimeGraph"]["recordedStatus"])
        self.assertEqual(["failed", "unknown"], [x["recordedStatus"] for x in evidence["reports"]["structural"]["items"]])

    def test_stale_source_provenance_not_treated_as_verified(self):
        self.manifest()
        self.source.write_text(yaml.safe_dump({"id": "source-rule", "query": "changed"}))
        item = self.export()["reports"]["conversion"]["items"][0]
        self.assertEqual("mismatch", item["provenance"]["sourceQuery"])

    def test_never_overwrites_snapshot_or_loads_it_as_workflow_state(self):
        self.export()
        destination = self.solution / "Evidence" / self.run_id
        original = (destination / "evidence.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "never overwrite"):
            export_evidence(self.solution, authoring_contract=self.authoring_contract(["migrated"]))
        self.assertEqual(original, (destination / "evidence.json").read_bytes())
        (destination / "workflow-state.json").write_text('{"workflowStatus":"completed"}')
        self.assertEqual("inProgress", workflow_status(self.solution)["workflowStatus"])
        (self.run / "workflow-state.json").unlink()
        with self.assertRaisesRegex(ValueError, "does not exist"):
            workflow_status(self.solution)

    @mock.patch("sentinel_xdr_migration.evidence._utc_now", return_value="2026-10-07T15:00:00+00:00")
    def test_identical_inputs_produce_identical_snapshot_bytes(self, clock):
        self.manifest()
        self.export()
        destination = self.solution / "Evidence" / self.run_id
        original = {p.name: p.read_bytes() for p in destination.iterdir()}
        shutil.rmtree(destination)
        self.export()
        self.assertEqual(original, {p.name: p.read_bytes() for p in destination.iterdir()})

    def test_authoring_contract_projects_every_rule_counts_and_validated_digests_only(self):
        contract = self.authoring_contract(["migrated", "blocked", "suppressed", "unprocessed"])
        result = export_evidence(self.solution, authoring_contract=contract)
        evidence_path = self.solution / result["evidence"]
        evidence = json.loads(evidence_path.read_text())
        projection = evidence["authoringContract"]
        self.assertEqual(4, len(projection["rules"]))
        self.assertEqual(
            ["source-rule-0", "source-rule-1", "source-rule-2", "source-rule-3"],
            [item["sourceRuleId"] for item in projection["rules"]],
        )
        self.assertEqual(
            ["migrated", "blocked", "suppressed", "unprocessed"],
            [item["outcome"] for item in projection["rules"]],
        )
        self.assertEqual(["untested"] * 4, [item["qualificationStatus"] for item in projection["rules"]])
        self.assertTrue(all(item["qualificationStatus"] != "qualified" for item in projection["rules"]))
        first = projection["rules"][0]
        self.assertTrue(first["targetStructurallyValid"])
        self.assertTrue(first["reviewRequired"])
        self.assertEqual(0, first["unresolvedErrorCount"])
        self.assertEqual(1, first["mappingAssumptionCount"])
        self.assertEqual(1, first["assumptionFindingCount"])
        self.assertEqual({"error": 0, "warning": 1, "assumption": 1}, first["findingCounts"])
        self.assertEqual(1, projection["rules"][1]["unresolvedErrorCount"])
        self.assertEqual(1, projection["rules"][2]["unresolvedErrorCount"])
        self.assertEqual({"N": 4, "M": 1, "E": 2}, {
            key: projection["coverage"][key] for key in ("N", "M", "E")
        })
        self.assertFalse(projection["coverage"]["migrationThreshold"]["met"])
        self.assertFalse(projection["coverage"]["errorStopThreshold"]["reached"])
        self.assertEqual(80, projection["coverage"]["migrationThreshold"]["successPercent"])
        self.assertEqual("strictlyGreaterThan", projection["coverage"]["errorStopThreshold"]["comparison"])
        self.assertEqual("advisory-only", projection["coverage"]["scope"])
        for key in ("coverageAuthorizesOperations", "packagingAuthorized", "deploymentAuthorized",
                    "ingestionAuthorized", "prCreationAuthorized"):
            self.assertFalse(projection["coverage"][key])
        self.assertEqual("validated-record-only-not-rehashed-or-authenticated",
                         projection["evidenceDigestBinding"])
        for item in projection["rules"]:
            self.assertTrue(all(len(digest) == 64 for digest in item["evidenceDigests"]))
            self.assertNotIn("path", item)
        self.assertIn("c" * 64, first["evidenceDigests"])
        published = evidence_path.read_text() + (self.solution / result["summary"]).read_text()
        for private_text in (
            "PRIVATE_SOURCE_IDENTITY", "PRIVATE_WARNING_PROSE", "PRIVATE_ASSUMPTION_PROSE",
            "PRIVATE_MAPPING_ASSUMPTION_PROSE", "PRIVATE_ERROR_PROSE",
            "PRIVATE_ENVIRONMENT_ERROR", "private-tenant-secret.json",
            "XDR Detections/private-tenant-0.yaml",
        ):
            self.assertNotIn(private_text, published)
        summary = (self.solution / result["summary"]).read_text()
        self.assertIn("Coverage is advisory only and never authorizes packaging", summary)
        self.assertIn("c" * 64, summary)

    def test_sensitive_source_rule_id_is_withheld_without_dropping_inventory_row(self):
        contract = self.authoring_contract(
            ["unprocessed"], rule_ids=["private-tenant-token"],
        )
        result = export_evidence(self.solution, authoring_contract=contract)
        projection = json.loads((self.solution / result["evidence"]).read_text())["authoringContract"]
        self.assertEqual(1, len(projection["rules"]))
        self.assertIsNone(projection["rules"][0]["sourceRuleId"])
        self.assertEqual("withheld", projection["rules"][0]["sourceRuleIdAvailability"])
        self.assertNotIn("private-tenant-token", json.dumps(projection))

    def test_authoring_contract_thresholds_and_qualification_counts_are_exact(self):
        success = self.authoring_contract(
            ["migrated"] * 8 + ["unprocessed"] * 2,
            qualification_statuses=["qualified"] + ["untested"] * 9,
        )
        success_result = export_evidence(self.solution, authoring_contract=success)
        success_projection = json.loads((self.solution / success_result["evidence"]).read_text())["authoringContract"]
        self.assertEqual((10, 8, 0), tuple(success_projection["coverage"][key] for key in ("N", "M", "E")))
        self.assertTrue(success_projection["coverage"]["migrationThreshold"]["met"])
        self.assertEqual(1, success_projection["coverage"]["qualified"])
        self.assertEqual(9, success_projection["coverage"]["untested"])
        shutil.rmtree(self.solution / "Evidence")

        stop = self.authoring_contract(["blocked"] * 6 + ["unprocessed"] * 4)
        stop_result = export_evidence(self.solution, authoring_contract=stop)
        stop_projection = json.loads((self.solution / stop_result["evidence"]).read_text())["authoringContract"]
        self.assertEqual((10, 0, 6), tuple(stop_projection["coverage"][key] for key in ("N", "M", "E")))
        self.assertTrue(stop_projection["coverage"]["errorStopThreshold"]["reached"])
        self.assertFalse(stop_projection["coverage"]["deploymentAuthorized"])
        self.assertFalse(stop_projection["coverage"]["prCreationAuthorized"])

    def test_authoring_contract_validation_and_run_binding_fail_before_writing(self):
        contract = self.authoring_contract(["migrated"])
        invalid = deepcopy(contract)
        invalid["inventory"]["rules"][0]["sha256"] = "not-a-sha256"
        with self.assertRaises(ValueError):
            export_evidence(self.solution, authoring_contract=invalid)
        self.assertFalse((self.solution / "Evidence").exists())

        mismatched = deepcopy(contract)
        mismatched["runId"] = "another-run"
        mismatched.pop("coverage")
        mismatched.pop("operationEligibility")
        mismatched = seal_authoring_contract(mismatched)
        with self.assertRaisesRegex(ValueError, "does not match the selected evidence run"):
            export_evidence(self.solution, authoring_contract=mismatched)
        self.assertFalse((self.solution / "Evidence").exists())

    @mock.patch("sentinel_xdr_migration.evidence._utc_now", return_value="2026-10-07T15:00:00+00:00")
    def test_authoring_contract_projection_has_stable_snapshot_bytes(self, clock):
        contract = self.authoring_contract(["migrated", "blocked", "unprocessed"])
        result = export_evidence(self.solution, authoring_contract=contract)
        destination = self.solution / "Evidence" / self.run_id
        original = {path.name: path.read_bytes() for path in destination.iterdir()}
        shutil.rmtree(destination)
        export_evidence(self.solution, authoring_contract=contract)
        self.assertEqual(original, {path.name: path.read_bytes() for path in destination.iterdir()})

    @mock.patch("sentinel_xdr_migration.evidence._utc_now", return_value="2026-10-07T15:00:00+00:00")
    def test_header_public_name_current_version_and_requested_action(self, clock):
        (self.solution / "SolutionMetadata.json").write_text(json.dumps({"version": "3.0.18", "Author": "private-user"}))
        data = self.solution / "Data"
        data.mkdir()
        (data / "Solution_Sample.json").write_text(json.dumps({"Name": "https://private.invalid", "Version": "3.0.18"}))
        state = json.loads((self.run / "workflow-state.json").read_text())
        state["context"]["versionBump"] = "minor"
        state["workflowStatus"] = "blocked"
        self.write("workflow-state.json", state)
        evidence = self.export()
        self.assertEqual("Sample", evidence["solution"]["name"])
        self.assertEqual("3.0.18", evidence["solution"]["currentVersion"])
        self.assertEqual("available", evidence["solution"]["versionAvailability"])
        self.assertIsNone(evidence["solution"]["requestedTargetVersion"])
        self.assertEqual("2026-10-07T15:00:00+00:00", evidence["exportedAt"])
        summary = (self.solution / "Evidence" / self.run_id / "summary.md").read_text()
        for text in ("# Migration evidence — Sample", "Profile: **authoring**",
                     "Current solution version at export: **3.0.18**", "Requested version action: **minor**",
                     "Requested target solution version: **unknown (not recorded)**",
                     "export tool, not historical run version", "2026-10-07T15:00:00+00:00"):
            self.assertIn(text, summary)
        self.assertNotIn("private-user", json.dumps(evidence))
        self.assertNotIn("https://", json.dumps(evidence))
        self.assertNotIn(str(self.storage), summary)
        for source in evidence["solution"]["versionSources"]:
            path = self.solution / ("SolutionMetadata.json" if source["kind"] == "solution-metadata" else "Data/Solution_Sample.json")
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), source["sha256"])

    def test_header_missing_optional_metadata_is_unknown_not_invented(self):
        evidence = self.export()
        self.assertEqual("missing", evidence["solution"]["versionAvailability"])
        self.assertIsNone(evidence["solution"]["currentVersion"])
        self.assertIsNone(evidence["solution"]["requestedTargetVersion"])
        old = dict(evidence)
        old.pop("solution")
        old.pop("exportedAt")
        summary = _markdown(old)
        self.assertIn("Current solution version at export: **unknown**", summary)
        self.assertIn("Evidence exported at (UTC): **unknown (not recorded)**", summary)
        self.assertNotIn(evidence["exportedAt"], summary)
        self.assertNotIn("3.1.0", summary)

    def test_header_only_enrichment_preserves_old_results_and_export_identity(self):
        evidence = self.export()
        evidence.pop("exportedAt")
        original_results = json.dumps(evidence["reports"], sort_keys=True)
        original_exporter = dict(evidence["exporter"])
        evidence["solution"].update(
            currentVersion="3.0.18", versionObservation="header-update",
            requestedTargetVersion=None,
        )
        evidence["headerUpdatedAt"] = "2026-10-07T16:00:00+00:00"
        evidence["headerRenderer"] = {"version": "0.1.0"}
        summary = _markdown(evidence)
        self.assertIn("Current solution version at header update: **3.0.18**", summary)
        self.assertIn("Evidence exported at (UTC): **unknown (not recorded)**", summary)
        self.assertIn("Header updated at (UTC): **2026-10-07T16:00:00+00:00**", summary)
        self.assertIn("original results, hashes and export identity are preserved", summary)
        self.assertEqual(original_results, json.dumps(evidence["reports"], sort_keys=True))
        self.assertEqual(original_exporter, evidence["exporter"])
        evidence["headerUpdatedAt"] = "https://private.invalid"
        evidence["headerRenderer"]["version"] = "/Users/private"
        summary = _markdown(evidence)
        self.assertNotIn("private", summary)

    def test_header_injected_names_and_versions_are_withheld(self):
        for value in (
            "https://host.invalid?sig=private", "www.private.invalid", "../outside",
            "/Users/private", r"C:\Users\private", "alice@example.com", "Name\nPersonal",
            "11111111-2222-3333-4444-555555555555", "token private",
            "Name | [private](https://host.invalid)", "<script>private</script>",
        ):
            with self.subTest(value=value):
                self.assertIsNone(_public_solution_name(value))
        (self.solution / "SolutionMetadata.json").write_text(json.dumps({
            "version": "3.0.18\n/Users/private", "Name": "Personal secret", "Author": "private-user",
        }))
        evidence = self.export()
        self.assertIsNone(evidence["solution"]["currentVersion"])
        self.assertEqual("invalid", evidence["solution"]["versionAvailability"])
        self.assertNotIn("private", json.dumps(evidence))

    def test_header_relocated_copy_uses_solution_name_not_parent_identity(self):
        copied = self.storage / "private-user-home" / "Solutions" / "Microsoft Defender XDR"
        shutil.copytree(self.solution, copied)
        result = export_evidence(copied)
        evidence = json.loads((copied / result["evidence"]).read_text())
        self.assertEqual("Microsoft Defender XDR", evidence["solution"]["name"])
        self.assertNotIn("private-user-home", json.dumps(evidence))
        self.assertNotIn(str(self.storage), (copied / result["summary"]).read_text())

    def test_header_multiple_data_copies_and_conflicting_versions_are_not_selected(self):
        data = self.solution / "Data"
        data.mkdir()
        first = data / "Solution_Sample.json"
        first.write_text('{"Version":"3.0.18"}')
        second = data / "Solution_Copy.json"
        second.write_text('{"Version":"3.1.0"}')
        evidence = self.export()
        self.assertEqual("ambiguous", evidence["solution"]["versionAvailability"])
        self.assertIsNone(evidence["solution"]["currentVersion"])
        shutil.rmtree(self.solution / "Evidence")
        second.unlink()
        (self.solution / "SolutionMetadata.json").write_text('{"version":"3.1.0"}')
        evidence = self.export()
        self.assertEqual("conflict", evidence["solution"]["versionAvailability"])
        self.assertIsNone(evidence["solution"]["currentVersion"])

    def test_header_data_version_available_when_metadata_does_not_declare_version(self):
        data = self.solution / "Data"
        data.mkdir()
        (data / "Solution_Sample.json").write_text('{"Version":"3.0.18"}')
        (self.solution / "SolutionMetadata.json").write_text('{"Name":"ignored-private-value"}')
        evidence = self.export()
        self.assertEqual("3.0.18", evidence["solution"]["currentVersion"])
        self.assertEqual("available", evidence["solution"]["versionAvailability"])
        self.assertEqual("not-recorded", evidence["solution"]["versionSources"][0]["availability"])
        self.assertNotIn("ignored-private-value", json.dumps(evidence))

    def test_multi_run_requires_selection_and_isolates_results(self):
        self.manifest()
        second = initialize_workflow(self.solution, workflow_profile="authoring", new_run=True)
        with self.assertRaisesRegex(ValueError, "multiple migration runs"):
            self.export()
        with using_run(self.solution, second["runId"]):
            self.assertEqual("missing", self.export()["reports"]["conversion"]["availability"])
        with using_run(self.solution, self.run_id):
            self.assertEqual(3, self.export()["reports"]["conversion"]["counts"]["total"])

    def test_traversal_symlink_and_unsafe_content_paths_are_rejected(self):
        for run_id in ("../outside", "/outside"):
            with self.assertRaises(ValueError):
                with using_run(self.solution, run_id):
                    self.export()
        (self.solution / "Evidence").symlink_to(self.storage, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.export()
        (self.solution / "Evidence").unlink()
        self.write("manifest.json", {"results": [{"source": "Analytic Rules/../secret.yaml", "output": "XDR Detections/token.yaml"}]})
        item = self.export()["reports"]["conversion"]["items"][0]
        self.assertEqual("withheld", item["source"]["availability"])
        self.assertEqual("withheld", item["output"]["availability"])

    def test_cli_does_not_configure_logging_or_change_state(self):
        output = io.StringIO()
        before = {p.name: p.read_bytes() for p in self.run.iterdir()}
        with mock.patch("sentinel_xdr_migration.cli.configure_logging") as logging, redirect_stdout(output):
            status = main(["export-evidence", "--solution", str(self.solution), "--run-id", self.run_id])
        self.assertEqual(0, status)
        logging.assert_not_called()
        self.assertEqual("exported", json.loads(output.getvalue())["status"])
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.run.iterdir()})

    def test_missing_run_does_not_create_state_or_evidence(self):
        shutil.rmtree(self.solution / "Logs")
        with self.assertRaisesRegex(ValueError, "existing run"):
            self.export()
        self.assertFalse((self.solution / "Evidence").exists())

    def test_changed_input_aborts_before_writing(self):
        with mock.patch("sentinel_xdr_migration.evidence._Snapshot.unchanged", return_value=False):
            with self.assertRaisesRegex(ValueError, "inputs changed"):
                self.export()
        self.assertFalse((self.solution / "Evidence").exists())

    def test_state_identity_mismatch_cannot_be_exported(self):
        state = json.loads((self.run / "workflow-state.json").read_text())
        state["runId"] = "unrelated-run"
        self.write("workflow-state.json", state)
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.export()
        self.assertFalse((self.solution / "Evidence").exists())

    def test_consolidated_structural_and_runtime_results_are_preserved(self):
        self.write("migration-report.json", {"rules": [{
            "sourceFile": "Analytic Rules/Rule.yaml",
            "analyticRule": {"alertStatus": "not-run", "runtime": [{"status": "blocked", "provider": "triage-mcp", "records": ["private"]}]},
            "customDetection": {"structuralStatus": "passed", "conversionStatus": "needsReview", "runtime": []},
        }]})
        evidence = self.export()
        item = evidence["reports"]["solutionReport"]["items"][0]
        self.assertEqual("blocked", item["analyticRule"]["runtime"][0]["recordedStatus"])
        self.assertEqual("not-run", item["analyticRule"]["alertStatus"])
        self.assertEqual("not-recorded", item["customDetection"]["runtimeAvailability"])
        summary = (self.solution / "Evidence" / self.run_id / "summary.md").read_text()
        self.assertIn("structural: passed=1", summary)
        self.assertNotIn("private", json.dumps(evidence))

    def test_content_discovery_excludes_evidence_logs_and_reports(self):
        for name in ("Evidence", "Logs", "Reports"):
            path = self.output.parent / name / "private.yaml"
            path.parent.mkdir()
            path.write_text("private: true")
        self.assertEqual([self.output], yaml_files(self.output.parent))

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 is required")
    def test_powershell_input_guard_and_fixed_zip_inputs(self):
        root = Path(__file__).resolve().parents[3] / "Tools/Create-Azure-Sentinel-Solution"
        common = root / "common/commonFunctions.ps1"
        script = (
            "$ErrorActionPreference='Stop'; . '" + str(common).replace("'", "''") + "'; "
            "foreach ($folder in @('Evidence','Logs','Reports','eViDeNcE')) { "
            "$rejected=$false; try { Assert-NoOperationalContent -Content "
            "([pscustomobject]@{'Playbooks'=@(\"$folder/private.json\")}) } "
            "catch {$rejected=$true}; if (-not $rejected) {throw 'unsafe content accepted'} }; "
            "foreach ($value in @('Evidence/private.json', '[\"Logs/private.json\"]')) { "
            "$rejected=$false; try { Assert-NoOperationalContent -Content "
            "([pscustomobject]@{'Playbooks'=$value}) } "
            "catch {$rejected=$true}; if (-not $rejected) {throw 'unsafe string content accepted'} }; "
            "Assert-NoOperationalContent -Content ([pscustomobject]@{'Analytic Rules'=@('Analytic Rules/Rule.yaml')})"
        )
        result = subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn('Path            = "$solutionFolder/createUiDefinition.json", "$solutionFolder/mainTemplate.json"', common.read_text())
        for name in ("common/createSolutionLocal.ps1", "V3/createSolutionV3.ps1", "V3/createSolutionV3_1.ps1"):
            self.assertIn("Assert-NoOperationalContent -Content $contentToImport", (root / name).read_text())


if __name__ == "__main__":
    unittest.main()
