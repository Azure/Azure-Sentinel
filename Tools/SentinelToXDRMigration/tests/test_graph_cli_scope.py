from __future__ import annotations

import base64
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml
from azure.core.exceptions import ClientAuthenticationError

from azure.identity._credentials import azure_cli

from sentinel_xdr_migration.graph_readiness import (
    AZURE_CLI_GRAPH_SCOPE,
    GRAPH_RESOURCE,
    preflight_deployment,
)
from sentinel_xdr_migration.deployment import (
    DEPLOYMENT_SCOPE,
    _deployment_token,
)
from sentinel_xdr_migration.graph_auth import (
    delegated_scope_diagnostics,
    validate_delegated_graph_claims,
    credential_token_scope,
)
from sentinel_xdr_migration.graph_client_config import (
    DEFAULT_GRAPH_CLIENT_ID,
    configure_azure_cli_profile,
    configure_graph_client,
)

TENANT_ID = "11111111-2222-4333-8444-555555555555"
SOURCE_ID = "11111111-2222-3333-4444-555555555555"


def locked_target() -> dict[str, str]:
    return {
        "tenantId": TENANT_ID,
        "subscriptionId": "22222222-3333-4444-8555-666666666666",
        "workspaceResourceId": (
            "/subscriptions/22222222-3333-4444-8555-666666666666/"
            "resourceGroups/rg/providers/Microsoft.OperationalInsights/workspaces/ws"
        ),
        "workspaceCustomerId": "33333333-4444-4555-8666-777777777777",
    }


def detection_document() -> dict:
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
                "id": SOURCE_ID,
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
            "id": SOURCE_ID,
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
                        "hosts": [
                            {"id": "host1", "deviceIdColumn": "DeviceId"}
                        ]
                    },
                }
            },
        },
    }


def access_token() -> str:
    claims = {
        "tid": TENANT_ID,
        "aud": "00000003-0000-0000-c000-000000000000",
        "scp": (
            "CustomDetection.Read.All CustomDetection.ReadWrite.All "
            "User.Read email openid profile"
        ),
    }
    encoded = base64.urlsafe_b64encode(
        json.dumps(claims).encode("utf-8")
    ).decode("ascii").rstrip("=")
    return f"header.{encoded}.signature"


class AzureCliGraphScopeTests(unittest.TestCase):
    def test_required_scope_policy_accepts_valid_extras_and_blocks_invalid_claims(
        self,
    ) -> None:
        diagnostics = delegated_scope_diagnostics(
            "CustomDetection.ReadWrite.All User.Read email openid profile",
            ("https://graph.microsoft.com/CustomDetection.ReadWrite.All",),
        )
        self.assertEqual("satisfied", diagnostics["status"])
        self.assertEqual(
            ["email", "openid", "profile", "User.Read"],
            diagnostics["extraScopeNames"],
        )
        base_claims = {
            "tid": TENANT_ID,
            "aud": "https://graph.microsoft.com",
            "scp": "CustomDetection.ReadWrite.All User.Read",
        }
        self.assertEqual(
            "satisfied",
            validate_delegated_graph_claims(
                base_claims,
                tenant_id=TENANT_ID,
                required_scopes=(
                    "https://graph.microsoft.com/CustomDetection.ReadWrite.All",
                ),
                purpose="test",
            )["delegatedScopes"]["status"],
        )
        invalid_claims = (
            ({**base_claims, "tid": "wrong-tenant"}, "tenant"),
            ({**base_claims, "aud": "https://other.example"}, "Microsoft Graph"),
            ({**base_claims, "scp": "User.Read"}, "required delegated"),
            ({**base_claims, "scp": ["CustomDetection.ReadWrite.All"]}, "required delegated"),
            (
                {
                    "tid": TENANT_ID,
                    "aud": "https://graph.microsoft.com",
                    "roles": ["CustomDetection.ReadWrite.All"],
                },
                "required delegated",
            ),
        )
        for claims, message in invalid_claims:
            with self.subTest(claims=claims), self.assertRaisesRegex(
                RuntimeError, message
            ):
                validate_delegated_graph_claims(
                    claims,
                    tenant_id=TENANT_ID,
                    required_scopes=(
                        "https://graph.microsoft.com/CustomDetection.ReadWrite.All",
                    ),
                    purpose="test",
                )

    def _preflight_patches(self, cli_backend: mock.Mock):
        root = Path("preflight-fixture").resolve()
        return (
            mock.patch(
                "sentinel_xdr_migration.graph_readiness.require_locked_target",
                return_value=locked_target(),
            ),
            mock.patch(
                "sentinel_xdr_migration.graph_readiness.preflight_dcr_permissions",
                return_value={"status": "not-requested"},
            ),
            mock.patch(
                "sentinel_xdr_migration.graph_readiness.xdr_detection_files",
                side_effect=lambda _directory: [
                    root / "XDR Detections" / "rule.yaml"
                ],
            ),
            mock.patch.object(
                Path,
                "read_text",
                return_value=yaml.safe_dump(detection_document()),
            ),
            mock.patch.object(azure_cli, "_run_command", cli_backend),
            mock.patch(
                "sentinel_xdr_migration.graph_readiness._graph_get",
                return_value=(200, {"id": f"xdr-{SOURCE_ID}"}),
            ),
        )

    def test_non_cli_credentials_keep_exact_permission_scopes(self) -> None:
        self.assertEqual(
            credential_token_scope("device-code", DEPLOYMENT_SCOPE),
            DEPLOYMENT_SCOPE,
        )
        self.assertEqual(
            credential_token_scope(
                "browser",
                "https://graph.microsoft.com/CustomDetection.Read.All",
            ),
            "https://graph.microsoft.com/CustomDetection.Read.All",
        )

    @mock.patch("azure.identity._credentials.azure_cli._run_command")
    def test_deployment_token_uses_graph_resource_with_cached_azure_cli(
        self, cli_command: mock.Mock
    ) -> None:
        cli_command.return_value = json.dumps(
            {
                "accessToken": access_token(),
                "expires_on": 2_000_000_000,
            }
        )
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
            state_root = Path(temp) / "synthetic-auth-state"
            configure_graph_client(
                state_root, "customDetection", DEFAULT_GRAPH_CLIENT_ID
            )
            configure_azure_cli_profile(
                state_root, Path(temp) / "synthetic-azure-cli-profile"
            )
            with mock.patch(
                "sentinel_xdr_migration.deployment._state_dir",
                return_value=state_root,
            ):
                token = _deployment_token(tenant_id=TENANT_ID)

        self.assertEqual(token, access_token())
        cli_command.assert_called_once()
        command = cli_command.call_args.args[0]
        self.assertEqual(
            command,
            [
                "account",
                "get-access-token",
                "--output",
                "json",
                "--resource",
                GRAPH_RESOURCE,
                "--tenant",
                TENANT_ID,
            ],
        )
        self.assertNotIn("CustomDetection.ReadWrite.All", command)

    def test_azure_cli_preflight_uses_graph_default_resource_and_exact_locked_tenant(self) -> None:
        observed: list[tuple[list[str], int]] = []

        def cli_backend(args: list[str], timeout: int) -> str:
            observed.append((args, timeout))
            return json.dumps(
                {
                    "accessToken": access_token(),
                    "expires_on": 2_000_000_000,
                }
            )

        patches = self._preflight_patches(mock.Mock(side_effect=cli_backend))
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5] as graph_get:
            report = preflight_deployment(
                "preflight-fixture",
                auth_method="azure-cli",
            )

        self.assertEqual(len(observed), 1)
        command, timeout = observed[0]
        self.assertEqual(
            command,
            [
                "account",
                "get-access-token",
                "--output",
                "json",
                "--resource",
                GRAPH_RESOURCE,
                "--tenant",
                TENANT_ID,
            ],
        )
        self.assertEqual(timeout, 10)
        self.assertNotIn("CustomDetection.ReadWrite.All", command)
        self.assertNotIn("CustomDetection.Read.All", command)
        self.assertEqual(
            report["authentication"]["requestedScope"],
            AZURE_CLI_GRAPH_SCOPE,
        )
        self.assertEqual(
            report["authentication"]["scopeRequestKind"],
            "graph-resource-default",
        )
        self.assertEqual(report["status"], "readiness-unconfirmed")
        self.assertEqual(report["permissions"]["writeAuthorization"], "not-tested")
        self.assertEqual(graph_get.call_count, 1)
        self.assertNotIn(access_token(), json.dumps(report))

    def test_azure_cli_resource_failure_is_action_required_without_second_scope_or_get(self) -> None:
        backend = mock.Mock(
            side_effect=ClientAuthenticationError("controlled token backend failure")
        )
        patches = self._preflight_patches(backend)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5] as graph_get:
            report = preflight_deployment(
                "preflight-fixture",
                auth_method="azure-cli",
            )

        backend.assert_called_once()
        self.assertEqual(
            report["authentication"]["requestedScope"],
            AZURE_CLI_GRAPH_SCOPE,
        )
        self.assertEqual(report["status"], "action-required")
        self.assertEqual(
            report["authentication"]["readScopeAcquisition"]["status"],
            "not-attempted",
        )
        graph_get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
