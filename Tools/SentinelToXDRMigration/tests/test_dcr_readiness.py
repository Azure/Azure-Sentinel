from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
INGESTION_ROOT = REPOSITORY_ROOT / "Tools" / "AzureMonitorLogsIngestion"
sys.path.insert(0, str(INGESTION_ROOT))

from azure_monitor_logs_ingestion.contract import load_contract  # noqa: E402
from azure_monitor_logs_ingestion.registry import resolve_contract  # noqa: E402
from sentinel_xdr_migration import dcr_readiness  # noqa: E402


TARGET = {
    "tenantId": "11111111-2222-4333-8444-555555555555",
    "subscriptionId": "22222222-3333-4444-8555-666666666666",
    "workspaceResourceId": (
        "/subscriptions/22222222-3333-4444-8555-666666666666/"
        "resourceGroups/rg/providers/Microsoft.OperationalInsights/workspaces/ws"
    ),
    "workspaceCustomerId": "33333333-4444-4555-8666-777777777777",
}


def contract_plan() -> dict:
    resolution = resolve_contract("CommonSecurityLog")
    return {
        "status": "planned",
        "targetSha256": "target-fingerprint",
        "inventory": {"sha256": "inventory-fingerprint"},
        "groups": [
            {
                "table": "CommonSecurityLog",
                "schemaFingerprint": resolution["schemaFingerprint"],
                "transformFingerprint": resolution["transformFingerprint"],
                "ruleIds": ["11111111-2222-3333-4444-555555555555"],
            }
        ],
        "rules": [
            {
                "ruleId": "11111111-2222-3333-4444-555555555555",
                "status": "manual-review-required",
                "blockers": ["fixture review is pending"],
            }
        ],
    }


def candidate_resources():
    resolution = resolve_contract("CommonSecurityLog")
    contract_path = INGESTION_ROOT / resolution["contractPath"]
    contract = load_contract(contract_path)
    dce_id, dcr_id, table_id = dcr_readiness._arm_resource_ids(TARGET, contract)
    dce = {
        "id": dce_id,
        "tags": {
            "managed-by": "azure-monitor-logs-ingestion",
            "ingestion-contract": contract.name,
        },
        "properties": {"logsIngestion": {"endpoint": "https://example.invalid"}},
    }
    dcr = {
        "id": dcr_id,
        "kind": "Direct",
        "tags": {
            "managed-by": "azure-monitor-logs-ingestion",
            "ingestion-contract": contract.name,
        },
        "properties": {
            "dataCollectionEndpointId": dce_id,
            "streamDeclarations": {
                contract.input_stream: {
                    "columns": [column.as_dict() for column in contract.input_columns]
                }
            },
            "dataFlows": [
                {
                    "streams": [contract.input_stream],
                    "destinations": ["workspace"],
                    "outputStream": contract.destination.output_stream,
                    "transformKql": contract.transform_kql,
                }
            ],
            "destinations": {
                "logAnalytics": [
                    {
                        "workspaceResourceId": TARGET["workspaceResourceId"],
                        "name": "workspace",
                    }
                ]
            },
        },
    }
    table = {
        "id": table_id,
        "properties": {
            "schema": {
                "standardColumns": [
                    column.as_dict() for column in contract.destination.columns
                ]
            }
        },
    }
    return contract, dce, dcr, table


def response_body(value: dict):
    response = mock.MagicMock()
    response.status = 200
    response.read.return_value = json.dumps(value).encode("utf-8")
    context = mock.MagicMock()
    context.__enter__.return_value = response
    return context


class DcrReadinessTests(unittest.TestCase):
    def _run_preflight(self, root: Path, *, responses, plan=None):
        target_path = root / "qualification-target.json"
        target_path.write_text(json.dumps(TARGET), encoding="utf-8")
        target = {**TARGET, "targetPath": str(target_path)}
        credential = mock.Mock()
        credential.get_token.return_value.token = "header.private-token.signature"
        with (
            mock.patch.object(
                dcr_readiness, "_build_local_plan", return_value=plan or contract_plan()
            ),
            mock.patch.object(
                dcr_readiness, "resolve_workspace_customer_id", return_value=TARGET["workspaceCustomerId"]
            ),
            mock.patch.object(
                dcr_readiness, "azure_cli_credential", return_value=credential
            ),
            mock.patch.object(
                dcr_readiness,
                "_check_query_permission",
                return_value={
                    "status": "ready",
                    "detail": "read-only query succeeded",
                    "meansDataVisible": False,
                },
            ),
            mock.patch("urllib.request.urlopen", side_effect=responses) as urlopen,
        ):
            report = dcr_readiness.preflight_dcr_permissions(
                root, target, auth_method="azure-cli"
            )
        return report, urlopen

    def test_wildcards_custom_roles_and_exclusions_are_evaluated(self):
        self.assertEqual(
            "ready",
            dcr_readiness._action_permission(
                [{"actions": ["Microsoft.Insights/*"], "notActions": []}],
                dcr_readiness.INGESTION_ACTION,
            )["status"],
        )
        self.assertEqual(
            "denied",
            dcr_readiness._action_permission(
                [
                    {
                        "actions": ["*"],
                        "notActions": ["Microsoft.Insights/Telemetry/*"],
                    }
                ],
                dcr_readiness.INGESTION_ACTION,
            )["status"],
        )
        self.assertEqual(
            "ready",
            dcr_readiness._action_permission(
                [
                    {
                        "actions": ["*"],
                        "notActions": ["Microsoft.Insights/Telemetry/*"],
                    },
                    {"dataActions": ["Microsoft.Insights/Telemetry/Write"]},
                ],
                dcr_readiness.INGESTION_ACTION,
            )["status"],
        )
        self.assertEqual(
            "denied",
            dcr_readiness._action_permission(
                [
                    {
                        "dataActions": ["Microsoft.Insights/*"],
                        "notDataActions": ["Microsoft.Insights/Telemetry/Write"],
                    }
                ],
                dcr_readiness.INGESTION_ACTION,
            )["status"],
        )

    def test_malformed_partial_and_conditioned_permission_responses_are_unknown(self):
        malformed = dcr_readiness._action_permission(
            [{"actions": "Microsoft.Insights/*"}], dcr_readiness.INGESTION_ACTION
        )
        conditioned = dcr_readiness._action_permission(
            [{"actions": ["*"], "condition": "@Resource[foo]"}],
            dcr_readiness.INGESTION_ACTION,
        )
        self.assertEqual("unknown", malformed["status"])
        self.assertEqual("unknown", conditioned["status"])
        with mock.patch.object(
            dcr_readiness, "_arm_get", return_value=(200, {"value": "invalid"})
        ):
            malformed_response = dcr_readiness._permissions_for_scope(
                "token", "/scope"
            )
        self.assertEqual("unknown", malformed_response["inspectionStatus"])
        with mock.patch.object(
            dcr_readiness, "_arm_get", return_value=(200, {"value": [], "nextLink": "next"})
        ):
            partial = dcr_readiness._permissions_for_scope("token", "/scope")
        self.assertEqual("unknown", partial["inspectionStatus"])

    def test_permission_inspection_http_failures_remain_distinct(self):
        for code, expected in ((401, "unavailable"), (403, "denied"), (404, "unknown")):
            with self.subTest(code=code), mock.patch.object(
                dcr_readiness, "_arm_get", return_value=(code, {"error": {"code": "failure"}})
            ):
                report = dcr_readiness._permissions_for_scope("token", "/scope")
            self.assertEqual(expected, report["inspectionStatus"])
            self.assertEqual(code, report["httpStatus"])
        with mock.patch.object(
            dcr_readiness,
            "_arm_get",
            return_value=(403, {"error": {"code": "AuthorizationFailed", "message": "forbidden"}}),
        ):
            ingestion = dcr_readiness._check_action(
                "token", "/exact/dcr", dcr_readiness.INGESTION_ACTION
            )
        self.assertEqual("unknown", ingestion["status"])
        self.assertEqual("denied", ingestion["inspectionStatus"])
        self.assertEqual("AuthorizationFailed", ingestion["error"]["code"])

    def test_error_evidence_redacts_identity_and_token_material(self):
        value = (
            "client 'person@example.com' with object id "
            "'11111111-2222-4333-8444-555555555555' sent Bearer "
            "secret.jwt.value"
        )
        sanitized = dcr_readiness._safe_message(value)
        self.assertNotIn("person@example.com", sanitized)
        self.assertNotIn("11111111-2222-4333-8444-555555555555", sanitized)
        self.assertNotIn("secret.jwt.value", sanitized)

    def test_unselected_credentials_do_not_start_authentication_or_permission_calls(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target_path = root / "qualification-target.json"
            target_path.write_text(json.dumps(TARGET), encoding="utf-8")
            target = {**TARGET, "targetPath": str(target_path)}
            with (
                mock.patch.object(
                    dcr_readiness, "_build_local_plan", return_value=contract_plan()
                ),
                mock.patch.object(
                    dcr_readiness, "azure_cli_credential"
                ) as credential_factory,
                mock.patch.object(
                    dcr_readiness, "resolve_workspace_customer_id"
                ) as verify_target,
                mock.patch.object(dcr_readiness, "artifact_path", return_value=root / "report.json"),
                mock.patch.object(dcr_readiness, "write_json_artifact"),
                mock.patch("urllib.request.urlopen") as urlopen,
            ):
                report = dcr_readiness.preflight_dcr_permissions(
                    root, target, auth_method=None
                )
        self.assertEqual("action-required", report["status"])
        self.assertEqual("action-required", report["authentication"]["status"])
        credential_factory.assert_not_called()
        verify_target.assert_not_called()
        urlopen.assert_not_called()

    def test_workspace_query_permission_is_separate_and_read_only(self):
        client = mock.Mock()
        with (
            mock.patch.object(
                dcr_readiness, "logs_query_client", return_value=client
            ),
            mock.patch.object(
                dcr_readiness,
                "execute_workspace_query",
                return_value={"status": "passed", "rowCount": 0},
            ) as query,
        ):
            result = dcr_readiness._check_query_permission(TARGET, mock.Mock())
        self.assertEqual("ready", result["status"])
        self.assertFalse(result["meansDataVisible"])
        self.assertEqual(TARGET["workspaceCustomerId"], query.call_args.args[1])
        self.assertEqual("print SentinelXdrPreflight=1", query.call_args.args[2])
        client.close.assert_called_once()

    def test_existing_compatible_dcr_checks_telemetry_permission_without_writes(self):
        _, dce, dcr, table = candidate_resources()
        responses = [
            response_body(dce),
            response_body(dcr),
            response_body(table),
            response_body(
                {
                    "value": [
                        {
                            "actions": ["Microsoft.Insights/Telemetry/Write"],
                            "notActions": [],
                            "dataActions": [],
                            "notDataActions": [],
                        }
                    ]
                }
            ),
        ]
        with tempfile.TemporaryDirectory() as temp:
            report, urlopen = self._run_preflight(Path(temp), responses=responses)
            saved = Path(report["reportPath"])
            self.assertTrue(saved.is_file())
            persisted = json.loads(saved.read_text(encoding="utf-8"))

        candidate = report["contracts"][0]
        self.assertEqual("ready", report["workspaceQueryPermission"]["status"])
        self.assertEqual("ready", candidate["resourceReadAccess"]["status"])
        self.assertEqual("compatible", candidate["tableSchemaCompatibility"]["status"])
        self.assertEqual("ready", candidate["ingestionAuthorization"]["status"])
        self.assertEqual("not-needed", candidate["tableCreationAuthorization"]["status"])
        self.assertEqual(0, report["payloadsSent"])
        self.assertEqual("ready", report["status"])
        self.assertEqual(64, len(candidate["resourceFingerprint"]))
        self.assertEqual(4, urlopen.call_count)
        self.assertTrue(all(call.args[0].method == "GET" for call in urlopen.call_args_list))
        self.assertNotIn("private-token", json.dumps(persisted))
        self.assertEqual("registered-contract-resolver", candidate["candidateProvenance"])

    def test_missing_pair_checks_exact_resource_group_creation_scopes(self):
        _, _, _, table = candidate_resources()
        with tempfile.TemporaryDirectory() as temp:
            target_path = Path(temp) / "qualification-target.json"
            target_path.write_text(json.dumps(TARGET), encoding="utf-8")
            target = {**TARGET, "targetPath": str(target_path)}
            credential = mock.Mock()
            credential.get_token.return_value.token = "header.token.signature"
            group_scope = (
                "/subscriptions/22222222-3333-4444-8555-666666666666/"
                "resourceGroups/rg"
            )
            with (
                mock.patch.object(
                    dcr_readiness, "_build_local_plan", return_value=contract_plan()
                ),
                mock.patch.object(
                    dcr_readiness,
                    "resolve_workspace_customer_id",
                    return_value=TARGET["workspaceCustomerId"],
                ),
                mock.patch.object(
                    dcr_readiness, "azure_cli_credential", return_value=credential
                ),
                mock.patch.object(
                    dcr_readiness,
                    "_check_query_permission",
                    return_value={"status": "ready"},
                ),
                mock.patch.object(
                    dcr_readiness,
                    "_check_resource",
                    side_effect=[
                        ("missing", None, {"httpStatus": 404}),
                        ("missing", None, {"httpStatus": 404}),
                        ("present", table, {"httpStatus": 200}),
                    ],
                ),
                mock.patch.object(
                    dcr_readiness,
                    "_check_action",
                    side_effect=lambda token, scope, action: {
                        "status": "ready",
                        "scope": scope,
                        "requiredAction": action,
                    },
                ) as check_action,
                mock.patch.object(dcr_readiness, "artifact_path", return_value=Path(temp) / "report.json"),
                mock.patch.object(dcr_readiness, "write_json_artifact"),
            ):
                report = dcr_readiness.preflight_dcr_permissions(
                    Path(temp), target, auth_method="azure-cli"
                )

        candidate = report["contracts"][0]
        self.assertEqual("not-yet-verifiable", candidate["ingestionAuthorization"]["status"])
        self.assertEqual("ready", candidate["resourceProvisioningAuthorization"]["status"])
        self.assertNotIn("roleAssignment", candidate["resourceProvisioningAuthorization"])
        self.assertEqual(2, check_action.call_count)
        self.assertEqual(
            [(group_scope, dcr_readiness.DCR_WRITE_ACTION), (group_scope, dcr_readiness.DCE_WRITE_ACTION)],
            [(call.args[1], call.args[2]) for call in check_action.call_args_list],
        )

    def test_missing_native_table_does_not_trigger_table_creation_permission_check(self):
        contract, _, _, _ = candidate_resources()
        _, _, table_id = dcr_readiness._arm_resource_ids(TARGET, contract)
        with tempfile.TemporaryDirectory() as temp:
            target_path = Path(temp) / "qualification-target.json"
            target_path.write_text(json.dumps(TARGET), encoding="utf-8")
            target = {**TARGET, "targetPath": str(target_path)}
            credential = mock.Mock()
            credential.get_token.return_value.token = "header.token.signature"
            with (
                mock.patch.object(
                    dcr_readiness, "_build_local_plan", return_value=contract_plan()
                ),
                mock.patch.object(
                    dcr_readiness,
                    "resolve_workspace_customer_id",
                    return_value=TARGET["workspaceCustomerId"],
                ),
                mock.patch.object(
                    dcr_readiness, "azure_cli_credential", return_value=credential
                ),
                mock.patch.object(
                    dcr_readiness,
                    "_check_query_permission",
                    return_value={"status": "ready"},
                ),
                mock.patch.object(
                    dcr_readiness,
                    "_check_resource",
                    side_effect=[
                        ("missing", None, {"httpStatus": 404}),
                        ("missing", None, {"httpStatus": 404}),
                        ("missing", None, {"httpStatus": 404}),
                    ],
                ),
                mock.patch.object(
                    dcr_readiness, "_check_action", return_value={"status": "ready"}
                ) as check_action,
                mock.patch.object(dcr_readiness, "artifact_path", return_value=Path(temp) / "report.json"),
                mock.patch.object(dcr_readiness, "write_json_artifact"),
            ):
                report = dcr_readiness.preflight_dcr_permissions(
                    Path(temp), target, auth_method="azure-cli"
                )

        candidate = report["contracts"][0]
        self.assertEqual("blocked", candidate["tableSchemaCompatibility"]["status"])
        self.assertEqual("not-needed", candidate["tableCreationAuthorization"]["status"])
        self.assertEqual("not-needed", candidate["resourceProvisioningAuthorization"]["status"])
        check_action.assert_not_called()

    def test_locked_workspace_customer_mismatch_is_rejected_before_arm_access(self):
        with tempfile.TemporaryDirectory() as temp:
            target_path = Path(temp) / "qualification-target.json"
            target_path.write_text(json.dumps(TARGET), encoding="utf-8")
            target = {**TARGET, "targetPath": str(target_path)}
            credential_factory = mock.Mock()
            with (
                mock.patch.object(
                    dcr_readiness, "_build_local_plan", return_value=contract_plan()
                ),
                mock.patch.object(
                    dcr_readiness, "resolve_workspace_customer_id", return_value="bad-id"
                ),
                mock.patch.object(
                    dcr_readiness, "azure_cli_credential", credential_factory
                ),
                mock.patch.object(dcr_readiness, "artifact_path", return_value=Path(temp) / "report.json"),
                mock.patch.object(dcr_readiness, "write_json_artifact"),
            ):
                report = dcr_readiness.preflight_dcr_permissions(
                    Path(temp), target, auth_method="azure-cli"
                )
            credential_factory.assert_not_called()
            self.assertEqual("blocked", report["status"])
            self.assertEqual("blocked", report["targetVerification"]["status"])

    def test_authenticated_tenant_and_subscription_mismatches_are_blocked(self):
        for message in (
            "authenticated Azure tenant does not match the locked target",
            "active Azure subscription does not match the locked target",
        ):
            with self.subTest(message=message), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                target_path = root / "qualification-target.json"
                target_path.write_text(json.dumps(TARGET), encoding="utf-8")
                target = {**TARGET, "targetPath": str(target_path)}
                credential_factory = mock.Mock()
                with (
                    mock.patch.object(
                        dcr_readiness, "_build_local_plan", return_value=contract_plan()
                    ),
                    mock.patch.object(
                        dcr_readiness,
                        "resolve_workspace_customer_id",
                        side_effect=RuntimeError(message),
                    ),
                    mock.patch.object(
                        dcr_readiness, "azure_cli_credential", credential_factory
                    ),
                    mock.patch.object(
                        dcr_readiness,
                        "artifact_path",
                        return_value=root / "report.json",
                    ),
                    mock.patch.object(dcr_readiness, "write_json_artifact"),
                ):
                    report = dcr_readiness.preflight_dcr_permissions(
                        root, target, auth_method="azure-cli"
                    )
                self.assertEqual("blocked", report["status"])
                self.assertEqual("blocked", report["targetVerification"]["status"])
                self.assertIn(message, report["targetVerification"]["reason"])
                credential_factory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
