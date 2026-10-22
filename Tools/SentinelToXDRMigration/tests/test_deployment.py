from __future__ import annotations

import base64
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from sentinel_xdr_migration.deployment import (
    _deployment_token,
    _graph_request,
    _validate_deployment_token,
    deploy_solution,
    graph_detection_payload,
)
from sentinel_xdr_migration import dcr_readiness
from sentinel_xdr_migration.graph_readiness import (
    _graph_get,
    _token_diagnostics,
    preflight_deployment,
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


RULE_ID = "11111111-2222-3333-4444-555555555555"


def document(rule_id: str = RULE_ID) -> dict:
    return {
        "schemaVersion": "1.0.0",
        "version": "3.1.0",
        "kind": "CustomDetection",
        "resourceType": "Microsoft.Security/detectionRules",
        "apiVersion": "2026-06-01-preview",
        "contentProvenance": {
            "requiredWorkloads": [{"workload": "mde", "dataTypes": ["DeviceInfo"]}],
            "requiredDataConnectors": [],
            "source": {
                "platform": "Microsoft Sentinel",
                "kind": "AnalyticsRule",
                "id": rule_id,
                "path": "Analytic Rules/rule.yaml",
                "querySha256": "hash",
                "schedule": {
                    "queryFrequency": "1h",
                    "queryPeriod": "1h",
                },
            },
            "conversion": {
                "tool": "sentinel-to-xdr-migration",
                "version": "0.1.0",
                "status": "converted",
                "reviewRequired": False,
                "reviewReasons": [],
                "requiredWorkloads": ["defender"],
                "warnings": [],
                "errors": [],
            },
        },
        "properties": {
            "id": rule_id,
            "displayName": "Test rule",
            "status": "disabled",
            "queryCondition": {"queryText": "DeviceInfo | take 1"},
            "schedule": {"frequency": "PT1H"},
            "detectionAction": {
                "alertTemplate": {
                    "title": "Test rule",
                    "description": "Test",
                    "severity": "low",
                    "entityMappings": {
                        "hosts": [{"id": "host1", "deviceIdColumn": "DeviceId"}]
                    },
                }
            },
        },
    }


class DeploymentTests(unittest.TestCase):
    def write_package_context(self, root: Path) -> dict:
        (root / "Data").mkdir()
        (root / "Data/Solution_Test.json").write_text(json.dumps({
            "Version": "3.1.0", "Metadata": "SolutionMetadata.json",
        }))
        (root / "SolutionMetadata.json").write_text(json.dumps({
            "publisherId": "testpublisher", "offerId": "test-sentinel",
        }))
        return {
            "packageId": "testpublisher.test-sentinel", "packageVersion": "3.1.0",
            "contentId": f"xdr-{RULE_ID}", "contentVersion": "3.1.0",
        }

    def test_custom_detection_token_accepts_scope_supersets_but_not_invalid_claims(
        self,
    ) -> None:
        base = {
            "tid": TARGET["tenantId"],
            "aud": "https://graph.microsoft.com",
            "scp": (
                "CustomDetection.ReadWrite.All CustomDetection.Read.All "
                "User.Read email openid profile"
            ),
        }
        with mock.patch(
            "sentinel_xdr_migration.graph_readiness._token_claims",
            return_value=base,
        ):
            diagnostics = _validate_deployment_token(
                "synthetic-token",
                tenant_id=TARGET["tenantId"],
            )
        self.assertEqual(
            {
                "CustomDetection.Read.All",
                "User.Read",
                "email",
                "openid",
                "profile",
            },
            set(diagnostics["delegatedScopes"]["extraScopeNames"]),
        )
        for claims, message in (
            ({**base, "tid": "wrong-tenant"}, "tenant"),
            ({**base, "aud": "https://other.example"}, "Microsoft Graph"),
            ({**base, "scp": "CustomDetection.Read.All"}, "required delegated"),
            ({**base, "scp": ["CustomDetection.ReadWrite.All"]}, "required delegated"),
            (
                {
                    "tid": TARGET["tenantId"],
                    "aud": "https://graph.microsoft.com",
                    "roles": ["CustomDetection.ReadWrite.All"],
                },
                "required delegated",
            ),
        ):
            with self.subTest(claims=claims), mock.patch(
                "sentinel_xdr_migration.graph_readiness._token_claims",
                return_value=claims,
            ):
                with self.assertRaisesRegex(RuntimeError, message):
                    _validate_deployment_token(
                        "synthetic-token",
                        tenant_id=TARGET["tenantId"],
                    )

    @mock.patch("urllib.request.urlopen")
    def test_graph_write_request_builds_authorized_json_request(
        self, urlopen: mock.Mock
    ) -> None:
        response = mock.MagicMock()
        response.status = 201
        response.read.return_value = b'{"id":"xdr-example"}'
        urlopen.return_value.__enter__.return_value = response

        status, body = _graph_request(
            "POST",
            "https://graph.microsoft.com/beta/security/rules/detectionRules",
            "sample-token",
            {"id": "xdr-example", "status": "disabled"},
        )

        request = urlopen.call_args.args[0]
        self.assertEqual(status, 201)
        self.assertEqual(body, {"id": "xdr-example"})
        self.assertEqual(request.method, "POST")
        self.assertEqual(
            request.get_header("Authorization"),
            "Bearer sample-token",
        )
        self.assertEqual(
            json.loads(request.data),
            {"id": "xdr-example", "status": "disabled"},
        )

    @mock.patch("urllib.request.urlopen")
    def test_graph_preflight_read_request_is_exact_bearer_get(
        self, urlopen: mock.Mock
    ) -> None:
        response = mock.MagicMock()
        response.status = 200
        response.read.return_value = b'{"id":"xdr-example"}'
        urlopen.return_value.__enter__.return_value = response

        status, body = _graph_get(
            "https://graph.microsoft.com/beta/security/rules/"
            "detectionRules/xdr-example",
            "sample-token",
            timeout_seconds=7,
        )

        request = urlopen.call_args.args[0]
        self.assertEqual(status, 200)
        self.assertEqual(body, {"id": "xdr-example"})
        self.assertEqual(request.method, "GET")
        self.assertIsNone(request.data)
        self.assertEqual(
            request.get_header("Authorization"),
            "Bearer sample-token",
        )
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 7)

    def test_payload_is_graph_ready_and_disabled(self) -> None:
        payload = graph_detection_payload(document())

        self.assertEqual(
            payload["@odata.type"], "#microsoft.graph.security.detectionRule"
        )
        self.assertEqual(payload["status"], "disabled")
        self.assertEqual(f"xdr-{RULE_ID}", payload["id"])

    def test_payload_rejects_review_required_detection(self) -> None:
        value = document()
        value["contentProvenance"]["conversion"]["status"] = "needsReview"
        value["contentProvenance"]["conversion"]["reviewRequired"] = True

        with self.assertRaisesRegex(ValueError, "no review required"):
            graph_detection_payload(value)

    def test_payload_projects_first_tactic_and_keeps_compatible_techniques(self) -> None:
        value = document()
        value["properties"]["detectionAction"]["alertTemplate"]["tactics"] = [
            {
                "tactic": "Execution",
                "techniques": [
                    {
                        "technique": "T1059",
                        "subTechniques": ["T1059.001", "T1059.003"],
                    }
                ],
            },
            {
                "tactic": "Persistence",
                "techniques": [{"technique": "T1547"}],
            },
        ]
        authored = json.loads(json.dumps(value))

        payload = graph_detection_payload(value)
        projected = payload["detectionAction"]["alertTemplate"]["tactics"]

        self.assertEqual(
            projected,
            [
                {
                    "tactic": "Execution",
                    "techniques": [
                        {
                            "technique": "T1059",
                            "subTechniques": ["T1059.001", "T1059.003"],
                        }
                    ],
                }
            ],
        )
        self.assertEqual(value, authored)

    def test_preflight_reports_projection_without_modifying_authored_yaml(self) -> None:
        value = document()
        value["properties"]["detectionAction"]["alertTemplate"]["tactics"] = [
            {"tactic": "Execution", "techniques": [{"technique": "T1059"}]},
            {"tactic": "Persistence", "techniques": [{"technique": "T1547"}]},
        ]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            detections = root / "XDR Detections"
            detections.mkdir()
            path = detections / "rule.yaml"
            original = yaml.safe_dump(value)
            path.write_text(original, encoding="utf-8")
            with mock.patch(
                "sentinel_xdr_migration.graph_readiness.require_locked_target",
                return_value=TARGET,
            ):
                report = preflight_deployment(root)

            self.assertEqual(path.read_text(encoding="utf-8"), original)
        self.assertEqual(report["status"], "action-required")
        readiness = report["payloadReadiness"][0]
        self.assertEqual(readiness["status"], "ready")
        projection = readiness["graphTacticProjection"]
        self.assertEqual(projection["projectedTactics"], ["Execution"])
        self.assertEqual(projection["omittedTactics"], ["Persistence"])
        self.assertEqual(projection["classificationParity"], "not-established")
        self.assertEqual(report["permissions"]["writeAuthorization"], "not-tested")

    def test_preflight_read_only_rule_check_does_not_claim_write_readiness(self) -> None:
        claims = {
            "tid": TARGET["tenantId"],
            "aud": "00000003-0000-0000-c000-000000000000",
            "scp": (
                "CustomDetection.ReadWrite.All CustomDetection.Read.All "
                "User.Read email openid profile"
            ),
        }
        encoded = base64.urlsafe_b64encode(
            json.dumps(claims).encode("utf-8")
        ).decode("ascii").rstrip("=")
        credential = mock.Mock()
        credential.get_token.return_value.token = f"header.{encoded}.signature"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            detections = root / "XDR Detections"
            detections.mkdir()
            (detections / "rule.yaml").write_text(
                yaml.safe_dump(document()), encoding="utf-8"
            )
            with (
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness.require_locked_target",
                    return_value=TARGET,
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._get_cached_credential",
                    return_value=credential,
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._graph_get",
                    return_value=(200, {"id": f"xdr-{RULE_ID}"}),
                ) as graph_get,
            ):
                report = preflight_deployment(root, auth_method="azure-cli")

        self.assertEqual(report["status"], "readiness-unconfirmed")
        self.assertEqual(report["readChecks"][0]["status"], "confirmed")
        self.assertTrue(report["readChecks"][0]["exists"])
        self.assertEqual(report["permissions"]["readAccess"], "confirmed")
        self.assertEqual(report["permissions"]["writeAuthorization"], "not-tested")
        self.assertEqual(report["permissions"]["effectiveRole"]["status"], "unknown")
        self.assertEqual(graph_get.call_count, 1)
        credential.get_token.assert_called_once()
        self.assertNotIn("header.", json.dumps(report))
        self.assertEqual(
            report["authentication"]["requestedScope"],
            "https://graph.microsoft.com/.default",
        )
        self.assertEqual(
            report["authentication"]["scopeRequestKind"],
            "graph-resource-default",
        )
        self.assertEqual(
            graph_get.call_args.args[0],
            "https://graph.microsoft.com/beta/security/rules/detectionRules/"
            f"xdr-{RULE_ID}",
        )
        self.assertEqual(
            report["requiredManagementPermission"],
            "CustomDetection.ReadWrite.All",
        )
        self.assertEqual(
            report["managementPermissionGrant"]["status"],
            "ready",
        )
        self.assertEqual(
            report["managementPermissionGrant"]["grantType"],
            "delegated",
        )
        self.assertEqual(
            {
                "CustomDetection.Read.All",
                "User.Read",
                "email",
                "openid",
                "profile",
            },
            set(
                report["authentication"]["delegatedScopeDiagnostics"][
                    "extraScopeNames"
                ]
            ),
        )
        self.assertEqual(report["deploymentReadiness"], "readiness-unconfirmed")

    def test_read_permission_and_successful_get_do_not_establish_deployment_readiness(
        self,
    ) -> None:
        claims = {
            "tid": TARGET["tenantId"],
            "aud": "00000003-0000-0000-c000-000000000000",
            "scp": "CustomDetection.Read.All",
        }
        encoded = base64.urlsafe_b64encode(
            json.dumps(claims).encode("utf-8")
        ).decode("ascii").rstrip("=")
        credential = mock.Mock()
        credential.get_token.side_effect = [
            RuntimeError("write scope unavailable"),
            mock.Mock(token=f"header.{encoded}.signature"),
        ]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            detections = root / "XDR Detections"
            detections.mkdir()
            (detections / "rule.yaml").write_text(
                yaml.safe_dump(document()), encoding="utf-8"
            )
            with (
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness.require_locked_target",
                    return_value=TARGET,
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._get_cached_credential",
                    return_value=credential,
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._graph_get",
                    return_value=(200, {"id": f"xdr-{RULE_ID}"}),
                ) as graph_get,
            ):
                report = preflight_deployment(root, auth_method="device-code")

        self.assertEqual(report["readChecks"][0]["status"], "confirmed")
        self.assertEqual(report["permissions"]["readAccess"], "confirmed")
        self.assertEqual(
            report["managementPermissionGrant"]["status"],
            "missing",
        )
        self.assertEqual(
            report["managementPermissionGrant"]["grantType"],
            "delegated",
        )
        self.assertEqual(
            report["managementPermissionGrant"]["credentialRequestScope"],
            "https://graph.microsoft.com/CustomDetection.Read.All",
        )
        self.assertEqual(report["deploymentReadiness"], "action-required")
        self.assertEqual(report["status"], "action-required")
        self.assertEqual(report["permissions"]["writeAuthorization"], "not-tested")
        graph_get.assert_called_once()

    def test_app_only_write_role_is_distinguished_from_delegated_scope(self) -> None:
        claims = {
            "tid": TARGET["tenantId"],
            "aud": "00000003-0000-0000-c000-000000000000",
            "roles": ["CustomDetection.ReadWrite.All"],
        }
        encoded = base64.urlsafe_b64encode(
            json.dumps(claims).encode("utf-8")
        ).decode("ascii").rstrip("=")
        credential = mock.Mock()
        credential.get_token.return_value.token = f"header.{encoded}.signature"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            detections = root / "XDR Detections"
            detections.mkdir()
            (detections / "rule.yaml").write_text(
                yaml.safe_dump(document()), encoding="utf-8"
            )
            with (
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness.require_locked_target",
                    return_value=TARGET,
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._get_cached_credential",
                    return_value=credential,
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._graph_get",
                    return_value=(200, {"id": f"xdr-{RULE_ID}"}),
                ),
            ):
                report = preflight_deployment(root, auth_method="azure-cli")

        self.assertEqual(
            report["managementPermissionGrant"]["status"],
            "missing",
        )
        self.assertEqual(
            report["managementPermissionGrant"]["grantType"],
            "application",
        )
        self.assertEqual(
            report["managementPermissionGrant"]["claimType"],
            "roles",
        )
        self.assertEqual(report["permissions"]["effectiveRole"]["status"], "unknown")
        self.assertEqual(report["permissions"]["writeAuthorization"], "not-tested")
        self.assertEqual(report["authentication"]["status"], "blocked")
        self.assertEqual(report["deploymentReadiness"], "blocked")

    def test_missing_or_malformed_permission_claims_are_unknown(self) -> None:
        base = {
            "tid": TARGET["tenantId"],
            "aud": "00000003-0000-0000-c000-000000000000",
        }
        cases = [
            (base, "missing"),
            ({**base, "scp": []}, "malformed"),
            ({**base, "roles": "CustomDetection.ReadWrite.All"}, "malformed"),
            ({**base, "scp": " "}, "malformed"),
        ]
        for claims, claim_type in cases:
            with self.subTest(claims=claims):
                diagnostics = _token_diagnostics(claims, TARGET["tenantId"])
                self.assertEqual(
                    diagnostics["managementPermissionGrant"]["status"],
                    "unknown",
                )
                self.assertEqual(
                    diagnostics["managementPermissionGrant"]["claimType"],
                    claim_type,
                )

    def test_preflight_404_does_not_claim_exact_rule_read_access(self) -> None:
        claims = {
            "tid": TARGET["tenantId"],
            "aud": "00000003-0000-0000-c000-000000000000",
            "scp": "CustomDetection.ReadWrite.All",
        }
        encoded = base64.urlsafe_b64encode(
            json.dumps(claims).encode("utf-8")
        ).decode("ascii").rstrip("=")
        credential = mock.Mock()
        credential.get_token.return_value.token = f"header.{encoded}.signature"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            detections = root / "XDR Detections"
            detections.mkdir()
            (detections / "rule.yaml").write_text(
                yaml.safe_dump(document()), encoding="utf-8"
            )
            with (
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness.require_locked_target",
                    return_value=TARGET,
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._get_cached_credential",
                    return_value=credential,
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._graph_get",
                    return_value=(404, {"error": {"code": "NotFound"}}),
                ),
            ):
                report = preflight_deployment(root, auth_method="azure-cli")

        self.assertEqual(report["status"], "unknown")
        self.assertEqual(report["permissions"]["readAccess"], "unknown")
        self.assertEqual(report["readChecks"][0]["status"], "not-found")
        self.assertFalse(report["readChecks"][0]["exists"])

    def test_preflight_missing_cached_auth_does_not_start_login(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            detections = root / "XDR Detections"
            detections.mkdir()
            (detections / "rule.yaml").write_text(
                yaml.safe_dump(document()), encoding="utf-8"
            )
            with (
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness.require_locked_target",
                    return_value=TARGET,
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._get_cached_credential",
                    return_value=None,
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._graph_get"
                ) as graph_get,
            ):
                report = preflight_deployment(root, auth_method="device-code")

        self.assertEqual(report["status"], "action-required")
        self.assertEqual(report["authentication"]["status"], "action-required")
        graph_get.assert_not_called()

    def test_preflight_blocks_review_required_payload_before_auth(self) -> None:
        value = document()
        value["contentProvenance"]["conversion"]["status"] = "needsReview"
        value["contentProvenance"]["conversion"]["reviewRequired"] = True
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            detections = root / "XDR Detections"
            detections.mkdir()
            (detections / "rule.yaml").write_text(
                yaml.safe_dump(value), encoding="utf-8"
            )
            with (
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness.require_locked_target",
                    return_value=TARGET,
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._get_cached_credential"
                ) as credential,
            ):
                report = preflight_deployment(root, auth_method="azure-cli")

        self.assertEqual(report["status"], "blocked")
        self.assertEqual(report["payloadReadiness"][0]["status"], "blocked")
        self.assertIn(
            "no review required",
            report["payloadReadiness"][0]["message"],
        )
        credential.assert_not_called()

    def test_preflight_runs_dcr_diagnostics_before_review_required_payload_block(self) -> None:
        value = document()
        value["contentProvenance"]["conversion"]["status"] = "needsReview"
        value["contentProvenance"]["conversion"]["reviewRequired"] = True
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            detections = root / "XDR Detections"
            detections.mkdir()
            (detections / "rule.yaml").write_text(
                yaml.safe_dump(value), encoding="utf-8"
            )
            target = {
                **TARGET,
                "targetPath": str(root / "qualification-target.json"),
            }
            Path(target["targetPath"]).write_text(
                json.dumps(TARGET), encoding="utf-8"
            )
            dcr_credential = mock.Mock()
            dcr_credential.get_token.return_value.token = "header.mock-token.signature"
            with (
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness.require_locked_target",
                    return_value=target,
                ),
                mock.patch.object(
                    dcr_readiness,
                    "resolve_workspace_customer_id",
                    return_value=TARGET["workspaceCustomerId"],
                ),
                mock.patch.object(
                    dcr_readiness,
                    "azure_cli_credential",
                    return_value=dcr_credential,
                ) as selected_credential,
                mock.patch.object(
                    dcr_readiness,
                    "_check_query_permission",
                    return_value={
                        "status": "ready",
                        "meansDataVisible": False,
                    },
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._get_cached_credential"
                ) as credential,
                mock.patch("urllib.request.urlopen") as urlopen,
            ):
                report = preflight_deployment(root, auth_method="azure-cli")

        self.assertEqual(report["status"], "blocked")
        self.assertEqual(
            report["dcrPermissionPreflight"]["status"],
            "unknown",
        )
        self.assertEqual(
            "confirmed",
            report["dcrPermissionPreflight"]["targetVerification"]["status"],
        )
        self.assertEqual(
            "ready",
            report["dcrPermissionPreflight"]["workspaceQueryPermission"]["status"],
        )
        selected_credential.assert_called_once()
        urlopen.assert_not_called()
        credential.assert_not_called()

    def test_cli_preflight_uses_real_dcr_helper_signature_without_cloud_calls(self) -> None:
        from sentinel_xdr_migration import cli, graph_readiness

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target_path = root / "qualification-target.json"
            target_path.write_text(json.dumps(TARGET), encoding="utf-8")
            target = {**TARGET, "targetPath": str(target_path)}
            azure_credential = mock.Mock()
            azure_credential.get_token.return_value.token = "header.mock-token.signature"
            real_helper = dcr_readiness.preflight_dcr_permissions

            def call_real_helper(solution, locked_target, *, auth_method):
                return real_helper(
                    solution,
                    locked_target,
                    auth_method=auth_method,
                )

            output = io.StringIO()
            with (
                mock.patch.object(
                    graph_readiness,
                    "require_locked_target",
                    return_value=target,
                ),
                mock.patch.object(
                    graph_readiness,
                    "preflight_dcr_permissions",
                    autospec=True,
                    side_effect=call_real_helper,
                ) as dcr_preflight,
                mock.patch.object(
                    dcr_readiness,
                    "resolve_workspace_customer_id",
                    return_value=TARGET["workspaceCustomerId"],
                ),
                mock.patch.object(
                    dcr_readiness,
                    "azure_cli_credential",
                    return_value=azure_credential,
                ) as selected_credential,
                mock.patch.object(
                    dcr_readiness,
                    "_check_query_permission",
                    return_value={
                        "status": "ready",
                        "meansDataVisible": False,
                    },
                ),
                mock.patch("urllib.request.urlopen") as urlopen,
                contextlib.redirect_stdout(output),
            ):
                result = cli.main(
                    [
                        "preflight-deployment",
                        "--solution",
                        str(root),
                        "--auth-method",
                        "azure-cli",
                    ]
                )

        report = json.loads(output.getvalue())
        self.assertEqual(0, result)
        self.assertEqual("blocked", report["status"])
        self.assertEqual(
            "unknown",
            report["dcrPermissionPreflight"]["status"],
        )
        self.assertEqual(
            "confirmed",
            report["dcrPermissionPreflight"]["targetVerification"]["status"],
        )
        self.assertEqual(
            "ready",
            report["dcrPermissionPreflight"]["workspaceQueryPermission"]["status"],
        )
        selected_credential.assert_called_once()
        dcr_preflight.assert_called_once_with(
            root.resolve(),
            target,
            auth_method="azure-cli",
        )

    def test_preflight_preserves_forbidden_read_and_unknown_role(self) -> None:
        claims = {
            "tid": TARGET["tenantId"],
            "aud": "00000003-0000-0000-c000-000000000000",
            "scp": "CustomDetection.ReadWrite.All",
        }
        encoded = base64.urlsafe_b64encode(
            json.dumps(claims).encode("utf-8")
        ).decode("ascii").rstrip("=")
        credential = mock.Mock()
        credential.get_token.return_value.token = f"header.{encoded}.signature"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            detections = root / "XDR Detections"
            detections.mkdir()
            (detections / "rule.yaml").write_text(
                yaml.safe_dump(document()), encoding="utf-8"
            )
            with (
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness.require_locked_target",
                    return_value=TARGET,
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._get_cached_credential",
                    return_value=credential,
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._graph_get",
                    return_value=(
                        403,
                        {"error": {"code": "Authorization_RequestDenied"}},
                    ),
                ),
            ):
                report = preflight_deployment(root, auth_method="azure-cli")

        self.assertEqual(report["status"], "blocked")
        self.assertEqual(report["permissions"]["readAccess"], "denied")
        self.assertEqual(report["permissions"]["effectiveRole"]["status"], "unknown")
        self.assertEqual(report["readChecks"][0]["status"], "denied")
        self.assertEqual(report["readChecks"][0]["httpStatus"], 403)
        self.assertEqual(
            report["readChecks"][0]["graphErrorCode"],
            "Authorization_RequestDenied",
        )

    def test_preflight_preserves_unknown_graph_error_instead_of_reporting_pass(self) -> None:
        claims = {
            "tid": TARGET["tenantId"],
            "aud": "00000003-0000-0000-c000-000000000000",
            "scp": "CustomDetection.ReadWrite.All",
        }
        encoded = base64.urlsafe_b64encode(
            json.dumps(claims).encode("utf-8")
        ).decode("ascii").rstrip("=")
        credential = mock.Mock()
        credential.get_token.return_value.token = f"header.{encoded}.signature"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            detections = root / "XDR Detections"
            detections.mkdir()
            (detections / "rule.yaml").write_text(
                yaml.safe_dump(document()), encoding="utf-8"
            )
            with (
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness.require_locked_target",
                    return_value=TARGET,
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._get_cached_credential",
                    return_value=credential,
                ),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._graph_get",
                    return_value=(
                        503,
                        {"error": {"code": "ServiceUnavailable"}},
                    ),
                ),
            ):
                report = preflight_deployment(root, auth_method="azure-cli")

        self.assertEqual(report["status"], "unknown")
        self.assertEqual(report["readChecks"][0]["status"], "unknown")
        self.assertEqual(report["readChecks"][0]["httpStatus"], 503)
        self.assertEqual(
            report["readChecks"][0]["graphErrorCode"],
            "ServiceUnavailable",
        )

    def test_preflight_does_not_continue_after_locked_target_mismatch(self) -> None:
        with (
            mock.patch(
                "sentinel_xdr_migration.graph_readiness.require_locked_target",
                side_effect=ValueError("tenantId does not match the locked qualification target"),
            ),
            mock.patch(
                "sentinel_xdr_migration.graph_readiness._get_cached_credential"
            ) as credential,
        ):
            with self.assertRaisesRegex(ValueError, "locked qualification target"):
                preflight_deployment("unused", auth_method="azure-cli")

        credential.assert_not_called()

    @mock.patch("azure.identity.AzureCliCredential")
    def test_deployment_token_falls_back_to_azure_cli(
        self, credential: mock.Mock
    ) -> None:
        claims = {
            "tid": TARGET["tenantId"],
            "aud": "https://graph.microsoft.com",
            "scp": "CustomDetection.ReadWrite.All User.Read email openid profile",
        }
        encoded = base64.urlsafe_b64encode(
            json.dumps(claims).encode("utf-8")
        ).decode("ascii").rstrip("=")
        token_value = f"header.{encoded}.signature"
        credential.return_value.get_token.return_value.token = token_value
        with tempfile.TemporaryDirectory() as temp:
            token = _deployment_token(temp, tenant_id=TARGET["tenantId"])

        self.assertEqual(token, token_value)

    @mock.patch(
        "sentinel_xdr_migration.deployment._deployment_token",
        return_value="token",
    )
    @mock.patch(
        "sentinel_xdr_migration.deployment.require_locked_target",
        return_value=TARGET,
    )
    @mock.patch("sentinel_xdr_migration.deployment._graph_request")
    def test_deploy_creates_missing_rule(
        self, request: mock.Mock, _target: mock.Mock, _token: mock.Mock
    ) -> None:
        request.side_effect = [
            (404, {"error": {"code": "NotFound"}}),
            (201, {"id": RULE_ID}),
            (200, {"id": RULE_ID, "status": "disabled"}),
        ]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "XDR Detections"
            output.mkdir()
            (output / "rule.yaml").write_text(
                yaml.safe_dump(document()), encoding="utf-8"
            )

            provenance = self.write_package_context(root)
            request.side_effect = [
                (404, {"error": {"code": "NotFound"}}),
                (201, {"id": RULE_ID}),
                (200, {"id": RULE_ID, "status": "disabled", "contentProvenance": provenance}),
            ]
            result = deploy_solution(root)

        self.assertEqual(result["succeeded"], 1)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["results"][0]["deployedStatus"], "disabled")
        self.assertEqual(request.call_args_list[1].args[0], "POST")
        self.assertEqual(f"xdr-{RULE_ID}", request.call_args_list[1].args[3]["id"])
        self.assertTrue(result["results"][0]["tacticProjectionVerified"])

    @mock.patch(
        "sentinel_xdr_migration.deployment._deployment_token",
        return_value="token",
    )
    @mock.patch(
        "sentinel_xdr_migration.deployment.require_locked_target",
        return_value=TARGET,
    )
    @mock.patch("sentinel_xdr_migration.deployment._graph_request")
    def test_deploy_fails_if_graph_readback_does_not_match_projection(
        self, request: mock.Mock, _target: mock.Mock, _token: mock.Mock
    ) -> None:
        value = document()
        value["properties"]["detectionAction"]["alertTemplate"]["tactics"] = [
            {"tactic": "Execution", "techniques": [{"technique": "T1059"}]},
            {"tactic": "Persistence", "techniques": [{"technique": "T1547"}]},
        ]
        request.side_effect = [
            (404, {"error": {"code": "NotFound"}}),
            (201, {"id": RULE_ID}),
            (
                200,
                {
                    "id": RULE_ID,
                    "status": "disabled",
                    "detectionAction": {"alertTemplate": {"tactics": []}},
                },
            ),
        ]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "XDR Detections"
            output.mkdir()
            (output / "rule.yaml").write_text(
                yaml.safe_dump(value), encoding="utf-8"
            )

            self.write_package_context(root)
            result = deploy_solution(root)

        self.assertEqual(result["succeeded"], 0)
        self.assertFalse(result["results"][0]["tacticProjectionVerified"])
        self.assertEqual(
            result["results"][0]["tacticProjection"]["omittedTactics"],
            ["Persistence"],
        )

    @mock.patch(
        "sentinel_xdr_migration.deployment._deployment_token",
        return_value="token",
    )
    @mock.patch(
        "sentinel_xdr_migration.deployment.require_locked_target",
        return_value=TARGET,
    )
    @mock.patch("sentinel_xdr_migration.deployment._graph_request")
    def test_deploy_updates_existing_rule(
        self, request: mock.Mock, _target: mock.Mock, _token: mock.Mock
    ) -> None:
        request.side_effect = [
            (200, {"id": RULE_ID}),
            (200, {"id": RULE_ID}),
            (200, {"id": RULE_ID, "status": "disabled"}),
        ]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "XDR Detections"
            output.mkdir()
            (output / "rule.yaml").write_text(
                yaml.safe_dump(document()), encoding="utf-8"
            )

            provenance = self.write_package_context(root)
            request.side_effect = [
                (200, {"id": RULE_ID}),
                (200, {"id": RULE_ID}),
                (200, {"id": RULE_ID, "status": "disabled", "contentProvenance": provenance}),
            ]
            result = deploy_solution(root)

        self.assertEqual(result["succeeded"], 1)
        self.assertEqual(result["results"][0]["deployedStatus"], "disabled")
        self.assertEqual(request.call_args_list[1].args[0], "PATCH")
        self.assertTrue(request.call_args_list[1].args[1].endswith("/xdr-" + RULE_ID))
        update = request.call_args_list[1].args[3]
        self.assertNotIn("id", update)

    def test_deployment_requires_matching_provenance_readback(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "XDR Detections"
            output.mkdir()
            (output / "rule.yaml").write_text(yaml.safe_dump(document()))
            self.write_package_context(root)
            with (
                mock.patch("sentinel_xdr_migration.deployment.require_locked_target", return_value=TARGET),
                mock.patch("sentinel_xdr_migration.deployment._deployment_token", return_value="token"),
                mock.patch("sentinel_xdr_migration.deployment._graph_request", side_effect=[
                    (404, {}), (201, {}), (200, {"status": "disabled"}),
                ]),
            ):
                result = deploy_solution(root)
        self.assertEqual(0, result["succeeded"])
        self.assertFalse(result["results"][0]["contentProvenanceVerified"])
        self.assertTrue(result["results"][0]["tacticProjectionVerified"])
        self.assertEqual("DeploymentVerificationFailed", result["results"][0]["error"]["code"])


if __name__ == "__main__":
    unittest.main()
