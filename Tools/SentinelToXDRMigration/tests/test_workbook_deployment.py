from __future__ import annotations

import json
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

from sentinel_xdr_migration.workbook_deployment import (
    WORKBOOK_DEPLOYMENT_ENDPOINT,
    _validate_workbook_deployment_token,
    deploy_workbooks,
    graph_workbook_payload,
    xdr_workbook_files,
)
from sentinel_xdr_migration.workbook_playwright import (
    extract_dom_workbook_errors,
    verify_deployed_workbooks_playwright,
)

TARGET = {
    "tenantId": "11111111-2222-4333-8444-555555555555",
    "subscriptionId": "22222222-3333-4444-8555-666666666666",
    "workspaceResourceId": (
        "/subscriptions/22222222-3333-4444-8555-666666666666/"
        "resourceGroups/rg/providers/Microsoft.OperationalInsights/workspaces/ws"
    ),
    "workspaceCustomerId": "33333333-4444-4555-8666-777777777777",
}

CONTENT_ID = "d4cd6cd5-32ca-5b45-a169-d2df36ac2a4e"
INSTANCE_ID = "9220a213-5c34-5e86-91f3-53dcd1c1f07c"


def workbook_document(
    *,
    content_id: str = CONTENT_ID,
    instance_id: str = INSTANCE_ID,
    display_name: str = "Atlassian Jira Audit",
    conversion_status: str = "converted",
    review_required: bool = False,
) -> dict:
    return {
        "version": "Notebook/1.0",
        "items": [
            {
                "type": 3,
                "content": {
                    "version": "KqlItem/1.0",
                    "query": "JiraAudit_CL | summarize count()",
                    "queryType": 0,
                    "resourceType": "microsoft.security/workbooks",
                },
            }
        ],
        "isLocked": False,
        "fallbackResourceIds": ["defender/workbooks"],
        "xdrMetadata": {
            "contentId": content_id,
            "instanceId": instance_id,
            "version": "3.2.2",
            "schemaVersion": "1.0.0",
            "displayName": display_name,
        },
        "contentProvenance": {
            "source": {
                "platform": "Microsoft Sentinel",
                "kind": "Workbook",
                "path": "Workbooks/AtlassianJiraAudit.json",
                "sha256": "abc123",
            },
            "conversion": {
                "tool": "sentinel-to-xdr-migration",
                "version": "0.1.0",
                "status": conversion_status,
                "reviewRequired": review_required,
                "queries": [],
            },
            "requiredWorkloads": [
                {"workload": "sentinel", "dataTypes": ["JiraAudit_CL"]}
            ],
            "requiredDataConnectors": [
                {
                    "connectorId": "JiraAuditConnector",
                    "dataTypes": ["JiraAudit_CL"],
                }
            ],
            "requiredWorkspaceFunctions": [],
        },
    }


class WorkbookDeploymentTests(unittest.TestCase):
    def write_package_context(self, root: Path) -> dict[str, str]:
        (root / "Data").mkdir(parents=True, exist_ok=True)
        (root / "Data" / "Solution_Test.json").write_text(
            json.dumps({"Version": "3.2.2", "Metadata": "SolutionMetadata.json"}),
            encoding="utf-8",
        )
        (root / "SolutionMetadata.json").write_text(
            json.dumps({"publisherId": "testpublisher", "offerId": "test-sentinel"}),
            encoding="utf-8",
        )
        return {
            "packageId": "testpublisher.test-sentinel",
            "packageVersion": "3.2.2",
        }

    def test_workbook_token_validation_enforces_scope_and_tenant(self) -> None:
        base_claims = {
            "tid": TARGET["tenantId"],
            "aud": "https://graph.microsoft.com",
            "scp": "Workbooks.ReadWrite.All Workbooks.Read.All User.Read",
        }
        with mock.patch(
            "sentinel_xdr_migration.graph_readiness._token_claims",
            return_value=base_claims,
        ):
            diagnostics = _validate_workbook_deployment_token(
                "synthetic-token",
                tenant_id=TARGET["tenantId"],
            )
        self.assertEqual(
            "satisfied",
            diagnostics["delegatedScopes"]["status"],
        )

        for invalid_claims, expected_error in (
            ({**base_claims, "tid": "wrong-tenant"}, "tenant"),
            ({**base_claims, "aud": "https://other.example"}, "Microsoft Graph"),
            ({**base_claims, "scp": "Workbooks.Read.All"}, "required delegated"),
        ):
            with self.subTest(claims=invalid_claims), mock.patch(
                "sentinel_xdr_migration.graph_readiness._token_claims",
                return_value=invalid_claims,
            ):
                with self.assertRaisesRegex(RuntimeError, expected_error):
                    _validate_workbook_deployment_token(
                        "synthetic-token",
                        tenant_id=TARGET["tenantId"],
                    )

    def test_graph_workbook_payload_strips_xdr_metadata_and_sets_package_provenance(
        self,
    ) -> None:
        doc = workbook_document()
        package_ctx = {
            "packageId": "testpublisher.test-sentinel",
            "packageVersion": "3.2.2",
        }
        instance_id, payload, metadata = graph_workbook_payload(
            doc, package_context=package_ctx
        )

        self.assertEqual(instance_id, INSTANCE_ID)
        self.assertEqual(metadata["contentId"], CONTENT_ID)
        self.assertEqual(metadata["displayName"], "Atlassian Jira Audit")
        self.assertEqual(set(payload.keys()), {"name", "content"})
        self.assertEqual(payload["name"], "Atlassian Jira Audit")
        self.assertNotIn("id", payload)
        self.assertNotIn("xdrMetadata", payload["content"])
        self.assertEqual(payload["content"]["version"], "Notebook/1.0")
        self.assertEqual(
            payload["content"]["contentProvenance"],
            {
                "packageId": "testpublisher.test-sentinel",
                "packageVersion": "3.2.2",
                "contentId": CONTENT_ID,
                "contentVersion": "3.2.2",
            },
        )
        # Original document is not mutated
        self.assertIn("xdrMetadata", doc)

    def test_graph_workbook_payload_rejects_review_required_or_invalid_metadata(
        self,
    ) -> None:
        with self.assertRaisesRegex(ValueError, "reviewRequired"):
            graph_workbook_payload(
                workbook_document(
                    conversion_status="needsReview", review_required=True
                )
            )
        with self.assertRaisesRegex(ValueError, "xdrMetadata.instanceId must be a valid GUID"):
            graph_workbook_payload(workbook_document(instance_id="not-a-guid"))

    def test_deploy_workbooks_upserts_via_patch_and_verifies_get_readback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Solutions" / "TestSolution"
            wb_dir = root / "XDR Workbooks"
            wb_dir.mkdir(parents=True)
            self.write_package_context(root)
            wb_file = wb_dir / "AtlassianJiraAudit.json"
            doc = workbook_document()
            wb_file.write_text(json.dumps(doc, indent=2), encoding="utf-8")

            expected_content = {
                "version": "Notebook/1.0",
                "items": doc["items"],
                "isLocked": False,
                "fallbackResourceIds": ["defender/workbooks"],
                "contentProvenance": {
                    "packageId": "testpublisher.test-sentinel",
                    "packageVersion": "3.2.2",
                    "contentId": CONTENT_ID,
                    "contentVersion": "3.2.2",
                },
            }
            readback_body = {
                "id": INSTANCE_ID,
                "name": "Atlassian Jira Audit",
                "createdByUpn": "user@contoso.com",
                "lastUpdatedByUpn": "user@contoso.com",
                "createdAtDateTime": "2026-04-20T00:00:00Z",
                "updatedAtDateTime": "2026-04-20T00:00:00Z",
                "content": expected_content,
            }

            with (
                mock.patch(
                    "sentinel_xdr_migration.workbook_deployment.require_locked_target",
                    return_value=TARGET,
                ),
                mock.patch(
                    "sentinel_xdr_migration.workbook_deployment._workbook_deployment_token",
                    return_value="sample-token",
                ),
                mock.patch(
                    "sentinel_xdr_migration.workbook_deployment._graph_request",
                    side_effect=[
                        (201, readback_body),
                        (200, readback_body),
                    ],
                ) as graph_req,
            ):
                report = deploy_workbooks(root)

            self.assertEqual(report["status"], "passed")
            self.assertEqual(report["deployed"], 1)
            self.assertEqual(report["failed"], 0)
            self.assertTrue(report["readbackReconciliation"]["readbackVerified"])
            item = report["results"][0]
            self.assertEqual(item["operation"], "created")
            self.assertEqual(item["statusCode"], 201)
            self.assertTrue(item["readbackVerified"])
            self.assertTrue(item["contentProvenanceVerified"])

            expected_url = f"{WORKBOOK_DEPLOYMENT_ENDPOINT}/{INSTANCE_ID}"
            self.assertEqual(graph_req.call_count, 2)
            self.assertEqual(graph_req.call_args_list[0].args[:3], ("PATCH", expected_url, "sample-token"))
            self.assertEqual(graph_req.call_args_list[1].args[:3], ("GET", expected_url, "sample-token"))
            self.assertTrue(Path(report["reportPath"]).is_file())

    def test_deploy_workbooks_fails_when_readback_mismatches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Solutions" / "TestSolution"
            wb_dir = root / "XDR Workbooks"
            wb_dir.mkdir(parents=True)
            self.write_package_context(root)
            wb_file = wb_dir / "AtlassianJiraAudit.json"
            wb_file.write_text(json.dumps(workbook_document()), encoding="utf-8")

            bad_readback = {
                "id": INSTANCE_ID,
                "name": "Wrong Name",
                "content": {"version": "Notebook/1.0", "items": []},
            }

            with (
                mock.patch(
                    "sentinel_xdr_migration.workbook_deployment.require_locked_target",
                    return_value=TARGET,
                ),
                mock.patch(
                    "sentinel_xdr_migration.workbook_deployment._workbook_deployment_token",
                    return_value="sample-token",
                ),
                mock.patch(
                    "sentinel_xdr_migration.workbook_deployment._graph_request",
                    side_effect=[
                        (200, bad_readback),
                        (200, bad_readback),
                    ],
                ),
            ):
                report = deploy_workbooks(root)

            self.assertEqual(report["status"], "failed")
            self.assertEqual(report["deployed"], 0)
            self.assertEqual(report["failed"], 1)
            self.assertFalse(report["readbackReconciliation"]["readbackVerified"])
            self.assertEqual(
                report["results"][0]["error"]["code"],
                "WorkbookDeploymentVerificationFailed",
            )

    def test_real_repo_xdr_workbook_generates_valid_graph_payload(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        jira_workbooks = repo_root / "Solutions" / "AtlassianJiraAudit" / "XDR Workbooks"
        files = xdr_workbook_files(jira_workbooks)
        self.assertEqual(len(files), 1)
        doc = json.loads(files[0].read_text(encoding="utf-8"))
        instance_id, payload, metadata = graph_workbook_payload(
            doc,
            package_context={
                "packageId": "azuresentinel.azure-sentinel-solution-atlassianjiraaudit",
                "packageVersion": "3.2.2",
            },
        )
        self.assertEqual(instance_id, "9220a213-5c34-5e86-91f3-53dcd1c1f07c")
        self.assertEqual(metadata["contentId"], "4c268806-7fba-5251-98b0-67e130bbcd07")
        self.assertEqual(payload["name"], "AtlassianJiraAudit")
        self.assertNotIn("xdrMetadata", payload["content"])
        self.assertEqual(payload["content"]["version"], "Notebook/1.0")
        self.assertEqual(
            payload["content"]["contentProvenance"]["contentId"],
            "4c268806-7fba-5251-98b0-67e130bbcd07",
        )

    def test_extract_dom_workbook_errors_detects_kql_and_panel_errors(self) -> None:
        errors = extract_dom_workbook_errors(
            [
                "LinuxMachines\nwarning 1\ninfo 1",
                "Events Over Time\n\uea39\nThis query couldn't run. If it uses workspace data, select a workspace.",
                "Events, by time: Query Time\nThis query could not run because some parameters are not set. Please set: Azure Firewalls",
                "Azure Firewalls = <unset>",
                "Azure Security Center Secure Score\nPlease select resources to query.",
                "SyntaxError:Failed to parse query, error: SYN0002: A recognition error occurred. [line:position=1:12]",
                "SemanticalError:Failed to resolve table or column expression named 'JiraAudit'",
            ]
        )
        self.assertEqual(len(errors), 6)
        self.assertIn("Events Over Time: This query couldn't run", errors[0])
        self.assertIn("This query could not run because some parameters are not set", errors[1])
        self.assertIn("Azure Firewalls = <unset>", errors[2])
        self.assertIn("Azure Security Center Secure Score: Please select resources to query.", errors[3])
        self.assertIn("SyntaxError:Failed to parse query", errors[4])
        self.assertIn("SemanticalError:Failed to resolve table", errors[5])

    def test_verify_deployed_workbooks_playwright_updates_evidence_without_saving_pngs(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Solutions" / "TestSolution"
            wb_dir = root / "XDR Workbooks"
            wb_dir.mkdir(parents=True)
            wb_file = wb_dir / "LinuxMachines.json"
            wb_file.write_text(json.dumps(workbook_document(display_name="LinuxMachines")), encoding="utf-8")

            # 1. Clean pass updates qualification-evidence.json without PNGs in Evidence/
            pass_res = verify_deployed_workbooks_playwright(
                root,
                target=TARGET,
                playwright_runner=lambda wb, _tgt: {
                    "workbook": wb,
                    "displayName": "LinuxMachines",
                    "instanceId": INSTANCE_ID,
                    "status": "passed",
                    "tilesRendered": True,
                    "queryErrors": [],
                    "javascriptErrors": [],
                    "saveEditObserved": False,
                },
            )
            self.assertEqual(pass_res["status"], "passed")
            self.assertTrue(pass_res["playwrightVerified"])
            ev_path = Path(pass_res["qualificationEvidencePath"])
            self.assertTrue(ev_path.is_file())
            ev_doc = json.loads(ev_path.read_text(encoding="utf-8"))
            self.assertTrue(ev_doc["uiTraversal"]["domVerified"])
            self.assertEqual(ev_doc["uiTraversal"]["status"], "passed")
            self.assertEqual(list((root / "Evidence").glob("*.png")), [])

            # 2. Unresolvable panel error marks qualification-evidence.json as failed with exact error
            fail_res = verify_deployed_workbooks_playwright(
                root,
                target=TARGET,
                playwright_runner=lambda wb, _tgt: {
                    "workbook": wb,
                    "displayName": "AtlassianJiraAudit",
                    "instanceId": INSTANCE_ID,
                    "status": "failed",
                    "tilesRendered": True,
                    "queryErrors": [
                        "SemanticalError: union column 'EventCreationTime' type mismatch"
                    ],
                    "javascriptErrors": [],
                    "saveEditObserved": False,
                },
            )
            self.assertEqual(fail_res["status"], "failed")
            self.assertFalse(fail_res["playwrightVerified"])
            ev_doc_fail = json.loads(ev_path.read_text(encoding="utf-8"))
            self.assertFalse(ev_doc_fail["uiTraversal"]["domVerified"])
            self.assertEqual(ev_doc_fail["uiTraversal"]["status"], "failed")
            self.assertFalse(ev_doc_fail["workbookQualification"]["passed"])
            self.assertTrue(
                any(
                    "SemanticalError" in err
                    for err in ev_doc_fail["workbookQualification"]["unresolvableErrors"]
                )
            )


if __name__ == "__main__":
    unittest.main()
