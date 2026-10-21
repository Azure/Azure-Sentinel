from __future__ import annotations

import base64
from contextlib import contextmanager, redirect_stdout
from io import StringIO
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sentinel_xdr_migration.delegated_app_registration import (
    APP_DISPLAY_NAME,
    APP_REDIRECT_URI,
    BOOTSTRAP_SCOPE,
    BOOTSTRAP_SCOPES,
    CUSTOM_DETECTION_SCOPE,
    CUSTOM_DETECTION_SCOPE_ID,
    GRAPH_RESOURCE_APP_ID,
    READBACK_SCOPES,
    THREAT_HUNTING_SCOPE,
    THREAT_HUNTING_SCOPE_ID,
    _list_owned_apps,
    _list_owned_application_ids,
    _registration_payload,
    diagnose_app_readback_scopes,
    plan_delegated_app_registration,
    plan_delegated_app_permission_update,
    register_delegated_app,
    setup_app_readback_authentication,
    verify_delegated_app_readback,
    verify_delegated_app_permission_update,
)
from sentinel_xdr_migration.graph_client_config import (
    DEFAULT_GRAPH_CLIENT_ID,
    PRIVATE_AUTH_CONFIG_NAME,
    azure_cli_credential,
    azure_cli_profile,
    configure_azure_cli_profile,
    configure_graph_client,
    graph_auth_record_path,
    graph_token_cache_name,
    read_delegated_app_registration,
    read_private_auth_config,
    resolve_graph_client_id,
    verify_graph_auth_binding,
    write_graph_auth_metadata,
    write_delegated_app_registration,
)
from sentinel_xdr_migration.artifacts import create_run
from sentinel_xdr_migration.cli import main as cli_main

TENANT_ID = "11111111-2222-4333-8444-555555555555"
CUSTOM_CLIENT_ID = "11111111-2222-3333-4444-555555555555"
OBJECT_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
APP_ID = "99999999-8888-7777-6666-555555555555"
READBACK_TENANT_ID = TENANT_ID
READBACK_APPLICATION_ID = APP_ID
READBACK_OBJECT_ID = OBJECT_ID
READBACK_DISPLAY_NAME = "Example-Sentinel-XDR-Application"
READBACK_AUTH_CLIENT_ID = DEFAULT_GRAPH_CLIENT_ID
READBACK_SCOPE_DIAGNOSTIC_RUN_ID = "test-readback-run"


class DelegatedAppRegistrationTests(unittest.TestCase):
    def test_advanced_hunting_auth_accepts_scope_superset_and_rejects_invalid_claims(
        self,
    ) -> None:
        from sentinel_xdr_migration.onboarding import GRAPH_SCOPE, _login_advanced_hunting

        class Record:
            tenant_id = TENANT_ID

            def serialize(self):
                return "synthetic-auth-record"

        def jwt(claims: dict) -> str:
            encoded = base64.urlsafe_b64encode(
                json.dumps(claims).encode()
            ).decode().rstrip("=")
            return f"header.{encoded}.signature"

        base_claims = {
            "tid": TENANT_ID,
            "aud": "https://graph.microsoft.com",
            "scp": "ThreatHunting.Read.All User.Read email openid profile",
        }
        cases = (
            (base_claims, "completed"),
            ({**base_claims, "scp": "User.Read"}, "failed"),
            ({**base_claims, "tid": "wrong-tenant"}, "failed"),
            ({**base_claims, "aud": "https://other.example"}, "failed"),
            ({**base_claims, "scp": ["ThreatHunting.Read.All"]}, "failed"),
            (
                {
                    "tid": TENANT_ID,
                    "aud": "https://graph.microsoft.com",
                    "roles": ["ThreatHunting.Read.All"],
                },
                "failed",
            ),
        )
        for claims, expected_status in cases:
            with self.subTest(claims=claims), tempfile.TemporaryDirectory() as temp:
                with (
                    mock.patch("azure.identity.DeviceCodeCredential") as credential_type,
                    mock.patch("azure.identity.TokenCachePersistenceOptions"),
                ):
                    credential_type.return_value.authenticate.return_value = Record()
                    credential_type.return_value.get_token.return_value.token = jwt(claims)
                    result = _login_advanced_hunting(Path(temp), TENANT_ID)
                self.assertEqual(expected_status, result["status"])
                credential_type.return_value.authenticate.assert_called_once_with(
                    scopes=[GRAPH_SCOPE]
                )
                credential_type.return_value.get_token.assert_called_once_with(
                    GRAPH_SCOPE
                )
                if expected_status == "completed":
                    self.assertEqual(
                        ["email", "openid", "profile", "User.Read"],
                        result["scopeDiagnostics"]["extraScopeNames"],
                    )
                    self.assertTrue(list(Path(temp).rglob("*.json")))
                else:
                    self.assertEqual([], list(Path(temp).rglob("*.json")))

    @staticmethod
    def _readback_settings(**updates):
        value = {
            "id": READBACK_OBJECT_ID,
            "appId": READBACK_APPLICATION_ID,
            "displayName": READBACK_DISPLAY_NAME,
            "signInAudience": "AzureADMyOrg",
            "publicClient": {"redirectUris": ["http://localhost"]},
            "requiredResourceAccess": [{
                "resourceAppId": GRAPH_RESOURCE_APP_ID,
                "resourceAccess": [{
                    "id": CUSTOM_DETECTION_SCOPE_ID,
                    "type": "Scope",
                }, {
                    "id": THREAT_HUNTING_SCOPE_ID,
                    "type": "Scope",
                }],
            }],
            "passwordCredentials": [],
            "keyCredentials": [],
        }
        value.update(updates)
        return value

    @contextmanager
    def _scope_diagnostic_fixtures(
        self,
        temp: str,
        claims: dict | None,
        *,
        target_tenant: str = READBACK_TENANT_ID,
        auth_record: object | None = "approved-record",
        auth_error: Exception | None = None,
    ):
        root = Path(temp) / "Solutions" / "Cisco"
        root.mkdir(parents=True)
        workflow_state = Path(temp) / "workflow-state.json"
        workflow_state.write_text(json.dumps({
            "runId": READBACK_SCOPE_DIAGNOSTIC_RUN_ID,
            "context": {
                "workflowProfile": "qualification",
                "tenantId": READBACK_TENANT_ID,
                "targetContextLocked": True,
            },
        }), encoding="utf-8")
        private = Path(temp) / "private"
        write_delegated_app_registration(private, {
            "schemaVersion": 1,
            "applicationId": READBACK_APPLICATION_ID,
            "objectId": READBACK_OBJECT_ID,
            "tenantId": READBACK_TENANT_ID,
            "displayName": READBACK_DISPLAY_NAME,
            "status": "reconciliation-required",
        })
        configure_graph_client(private, "appReadback", DEFAULT_GRAPH_CLIENT_ID)
        configure_graph_client(private, "appRegistration", DEFAULT_GRAPH_CLIENT_ID)
        readback_record_path = graph_auth_record_path(
            private,
            "appReadback",
            DEFAULT_GRAPH_CLIENT_ID,
            "app-readback-auth-record.json",
        )
        readback_record_path.write_text("mock readback record", encoding="utf-8")
        write_graph_auth_metadata(
            readback_record_path,
            purpose="appReadback",
            client_id=DEFAULT_GRAPH_CLIENT_ID,
            tenant_id=READBACK_TENANT_ID,
        )
        bootstrap_record_path = graph_auth_record_path(
            private,
            "appRegistration",
            DEFAULT_GRAPH_CLIENT_ID,
            "app-registration-auth-record.json",
        )
        bootstrap_record_path.write_text("mock bootstrap record", encoding="utf-8")
        write_graph_auth_metadata(
            bootstrap_record_path,
            purpose="appRegistration",
            client_id=DEFAULT_GRAPH_CLIENT_ID,
            tenant_id=READBACK_TENANT_ID,
        )
        record = mock.Mock(
            tenant_id=READBACK_TENANT_ID,
            client_id=DEFAULT_GRAPH_CLIENT_ID,
        )
        if auth_error is not None:
            auth_patch = mock.patch(
                "sentinel_xdr_migration.delegated_app_registration._load_auth_record",
                side_effect=auth_error,
            )
        else:
            auth_patch = mock.patch(
                "sentinel_xdr_migration.delegated_app_registration._load_auth_record",
                return_value=record if auth_record is not None else None,
            )
        with (
            mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.existing_artifact_path",
                return_value=workflow_state,
            ),
            mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": target_tenant},
            ),
            auth_patch as load_auth_record,
            mock.patch(
                "azure.identity.InteractiveBrowserCredential"
            ) as credential_type,
            mock.patch("azure.identity.TokenCachePersistenceOptions") as cache_options,
            mock.patch(
                "sentinel_xdr_migration.graph_readiness._token_claims",
                return_value=claims,
            ),
            mock.patch(
                "sentinel_xdr_migration.delegated_app_registration._graph_request"
            ) as graph_request,
            mock.patch(
                "sentinel_xdr_migration.delegated_app_registration._list_owned_application_ids"
            ) as owned_applications,
        ):
            credential_type.return_value.authenticate.side_effect = AssertionError(
                "interactive authentication is not expected in scope-diagnostic fixtures"
            )
            credential_type.return_value.get_token.return_value.token = (
                "opaque-synthetic-token-not-for-output"
            )
            yield {
                "root": root,
                "private": private,
                "readbackRecordPath": readback_record_path,
                "bootstrapRecordPath": bootstrap_record_path,
                "credential": credential_type,
                "cache": cache_options,
                "loadAuthRecord": load_auth_record,
                "graphRequest": graph_request,
                "ownedApplications": owned_applications,
            }

    def test_registration_payload_is_single_tenant_public_and_one_delegated_scope(self) -> None:
        payload = _registration_payload()
        self.assertEqual(APP_DISPLAY_NAME, "Sentinel-XDR-CustomDetection")
        self.assertEqual(payload["displayName"], APP_DISPLAY_NAME)
        self.assertEqual(payload["signInAudience"], "AzureADMyOrg")
        self.assertEqual(payload["publicClient"], {"redirectUris": [APP_REDIRECT_URI]})
        self.assertEqual(
            payload["requiredResourceAccess"],
            [
                {
                    "resourceAppId": GRAPH_RESOURCE_APP_ID,
                    "resourceAccess": [
                        {"id": CUSTOM_DETECTION_SCOPE_ID, "type": "Scope"}
                    ],
                }
            ],
        )
        self.assertEqual(CUSTOM_DETECTION_SCOPE, "CustomDetection.ReadWrite.All")

    def test_private_client_configuration_is_namespaced_and_keeps_default_compatibility(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "private"
            self.assertEqual(
                resolve_graph_client_id(root, "customDetection"),
                DEFAULT_GRAPH_CLIENT_ID,
            )
            self.assertEqual(
                graph_auth_record_path(
                    root, "customDetection", DEFAULT_GRAPH_CLIENT_ID, "auth.json"
                ).resolve(),
                (root / "auth.json").resolve(),
            )
            self.assertEqual(
                graph_token_cache_name(
                    "customDetection", DEFAULT_GRAPH_CLIENT_ID, "cache"
                ),
                "cache",
            )
            configure_graph_client(root, "customDetection", CUSTOM_CLIENT_ID)
            self.assertEqual(
                resolve_graph_client_id(root, "customDetection"), CUSTOM_CLIENT_ID
            )
            custom_record = graph_auth_record_path(
                root, "customDetection", CUSTOM_CLIENT_ID, "auth.json"
            )
            self.assertNotEqual(custom_record, root / "auth.json")
            self.assertNotEqual(
                graph_token_cache_name("customDetection", CUSTOM_CLIENT_ID, "cache"),
                "cache",
            )
            self.assertEqual(
                json.loads((root / PRIVATE_AUTH_CONFIG_NAME).read_text())[
                    "graphClientIds"
                ]["customDetection"],
                CUSTOM_CLIENT_ID,
            )
            self.assertEqual((root.stat().st_mode & 0o777), 0o700)
            self.assertEqual(((root / PRIVATE_AUTH_CONFIG_NAME).stat().st_mode & 0o777), 0o600)

    def test_auth_binding_rejects_client_and_tenant_mismatches(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record_path = graph_auth_record_path(
                root, "customDetection", CUSTOM_CLIENT_ID, "auth.json"
            )
            record = mock.Mock(tenant_id=TENANT_ID, client_id=CUSTOM_CLIENT_ID)
            write_graph_auth_metadata(
                record_path,
                purpose="customDetection",
                client_id=CUSTOM_CLIENT_ID,
                tenant_id=TENANT_ID,
            )
            verify_graph_auth_binding(
                record_path,
                record,
                purpose="customDetection",
                client_id=CUSTOM_CLIENT_ID,
                tenant_id=TENANT_ID,
            )
            with self.assertRaisesRegex(ValueError, "client"):
                verify_graph_auth_binding(
                    record_path,
                    record,
                    purpose="customDetection",
                    client_id=DEFAULT_GRAPH_CLIENT_ID,
                    tenant_id=TENANT_ID,
                )
            with self.assertRaisesRegex(ValueError, "tenant"):
                verify_graph_auth_binding(
                    record_path,
                    record,
                    purpose="customDetection",
                    client_id=CUSTOM_CLIENT_ID,
                    tenant_id="00000000-0000-0000-0000-000000000001",
                )

    def test_bootstrap_authentication_accepts_scope_superset_without_changing_request(self) -> None:
        class Record:
            tenant_id = TENANT_ID
            username = "operator@example.invalid"

            def serialize(self):
                return "serialized-test-record"

        with tempfile.TemporaryDirectory() as temp:
            with (
                mock.patch(
                    "azure.identity.DeviceCodeCredential"
                ) as credential_type,
                mock.patch(
                    "azure.identity.TokenCachePersistenceOptions"
                ) as cache_options,
            ):
                credential_type.return_value.authenticate.return_value = Record()
                claims = {
                    "tid": TENANT_ID,
                    "aud": "https://graph.microsoft.com",
                    "scp": (
                        "AppRegistration.Create User.Read App.Read.All "
                        "email openid profile"
                    ),
                }
                encoded = base64.urlsafe_b64encode(
                    json.dumps(claims).encode()
                ).decode().rstrip("=")
                credential_type.return_value.get_token.return_value.token = (
                    f"header.{encoded}.signature"
                )
                from sentinel_xdr_migration.delegated_app_registration import (
                    setup_app_registration_authentication,
                )

                result = setup_app_registration_authentication(
                    tenant_id=TENANT_ID,
                    auth_method="device-code",
                    state_dir=temp,
                )
            self.assertEqual(result["scopes"], list(BOOTSTRAP_SCOPES))
            self.assertFalse(result["appRegistrationPerformed"])
            self.assertFalse(result["adminConsentRequested"])
            credential_type.return_value.authenticate.assert_called_once_with(
                scopes=list(BOOTSTRAP_SCOPES)
            )
            credential_type.return_value.get_token.assert_called_once_with(
                *BOOTSTRAP_SCOPES
            )
            record_path = Path(temp) / "app-registration-auth-record.json"
            self.assertEqual(record_path.read_text(), "serialized-test-record")
            self.assertEqual((record_path.stat().st_mode & 0o777), 0o600)
            metadata = json.loads(
                Path(f"{record_path}.metadata.json").read_text()
            )
            self.assertEqual(metadata["purpose"], "appRegistration")
            self.assertEqual(metadata["clientId"], DEFAULT_GRAPH_CLIENT_ID)

    def test_readback_auth_uses_explicit_private_client_configuration(self) -> None:
        class Record:
            tenant_id = READBACK_TENANT_ID
            username = "operator@example.invalid"

            def serialize(self):
                return "serialized-test-readback-record"

        with tempfile.TemporaryDirectory() as temp:
            with (
                mock.patch("azure.identity.InteractiveBrowserCredential") as credential_type,
                mock.patch(
                    "azure.identity.TokenCachePersistenceOptions"
                ) as cache_options,
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._token_claims",
                    return_value={
                        "tid": READBACK_TENANT_ID,
                        "aud": "https://graph.microsoft.com",
                        "scp": "User.Read Application.Read.All",
                    },
                ),
            ):
                credential = credential_type.return_value
                credential.authenticate.return_value = Record()
                credential.get_token.return_value.token = "token"
                setup_app_readback_authentication(
                    tenant_id=READBACK_TENANT_ID,
                    readback_client_id=CUSTOM_CLIENT_ID,
                    state_dir=temp,
                )
                credential_type.assert_called_once_with(
                    client_id=CUSTOM_CLIENT_ID,
                    tenant_id=READBACK_TENANT_ID,
                    cache_persistence_options=cache_options.return_value,
                )
                credential.authenticate.assert_called_once_with(
                    scopes=list(READBACK_SCOPES)
                )
                credential.get_token.assert_called_once_with(*READBACK_SCOPES)
                self.assertIsInstance(credential, mock.Mock)
            self.assertEqual(
                CUSTOM_CLIENT_ID,
                resolve_graph_client_id(temp, "appReadback"),
            )
            self.assertTrue(
                graph_auth_record_path(
                    temp,
                    "appReadback",
                    CUSTOM_CLIENT_ID,
                    "app-readback-auth-record.json",
                ).is_file()
            )

    def test_configured_public_client_has_separate_readback_record_and_cache(self) -> None:
        class Record:
            tenant_id = READBACK_TENANT_ID
            username = "operator@example.invalid"

            def serialize(self):
                return "serialized-approved-readback-record"

        from sentinel_xdr_migration.delegated_app_registration import _app_readback_token

        self.assertEqual(DEFAULT_GRAPH_CLIENT_ID, READBACK_AUTH_CLIENT_ID)
        with tempfile.TemporaryDirectory() as temp:
            with (
                mock.patch("azure.identity.InteractiveBrowserCredential") as credential_type,
                mock.patch("azure.identity.TokenCachePersistenceOptions") as cache_options,
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._token_claims",
                    return_value={
                        "tid": READBACK_TENANT_ID,
                        "aud": "https://graph.microsoft.com",
                        "scp": (
                            "User.Read Application.Read.All email openid profile"
                        ),
                    },
                ),
            ):
                credential_type.return_value.authenticate.return_value = Record()
                credential_type.return_value.get_token.return_value.token = "token"
                setup_app_readback_authentication(
                    tenant_id=READBACK_TENANT_ID,
                    readback_client_id=DEFAULT_GRAPH_CLIENT_ID,
                    state_dir=temp,
                )
            readback_record = graph_auth_record_path(
                temp,
                "appReadback",
                DEFAULT_GRAPH_CLIENT_ID,
                "app-readback-auth-record.json",
            )
            bootstrap_record = graph_auth_record_path(
                temp,
                "appRegistration",
                DEFAULT_GRAPH_CLIENT_ID,
                "app-registration-auth-record.json",
            )
            self.assertEqual("app-readback-auth-record.json", readback_record.name)
            self.assertNotEqual(readback_record, bootstrap_record)
            self.assertEqual("serialized-approved-readback-record", readback_record.read_text())
            bootstrap_record = graph_auth_record_path(
                temp,
                "appRegistration",
                DEFAULT_GRAPH_CLIENT_ID,
                "app-registration-auth-record.json",
            )
            bootstrap_record.write_text("bootstrap-only-record")
            write_graph_auth_metadata(
                bootstrap_record,
                purpose="appRegistration",
                client_id=DEFAULT_GRAPH_CLIENT_ID,
                tenant_id=READBACK_TENANT_ID,
            )
            self.assertEqual(
                "sentinel_xdr_migration_app_readback",
                cache_options.call_args.kwargs["name"],
            )

            record = mock.Mock(
                tenant_id=READBACK_TENANT_ID,
                client_id=DEFAULT_GRAPH_CLIENT_ID,
            )
            with (
                mock.patch(
                    "sentinel_xdr_migration.delegated_app_registration._load_auth_record",
                    return_value=record,
                ) as load_record,
                mock.patch("azure.identity.InteractiveBrowserCredential") as credential_type,
                mock.patch("azure.identity.TokenCachePersistenceOptions") as cache_options,
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._token_claims",
                    return_value={
                        "tid": READBACK_TENANT_ID,
                        "aud": "https://graph.microsoft.com",
                        "scp": "User.Read Application.Read.All",
                    },
                ),
            ):
                credential_type.return_value.get_token.return_value.token = "token"
                self.assertEqual(
                    "token",
                    _app_readback_token(Path(temp), READBACK_TENANT_ID),
                )
            load_record.assert_called_once_with(readback_record)
            self.assertEqual(
                "sentinel_xdr_migration_app_readback",
                cache_options.call_args.kwargs["name"],
            )

    def test_readback_default_client_never_falls_back_or_reuses_bootstrap_cache(self) -> None:
        from sentinel_xdr_migration.delegated_app_registration import _app_readback_token

        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(RuntimeError, "not configured"):
                _app_readback_token(Path(temp), READBACK_TENANT_ID)
            configure_graph_client(temp, "appRegistration", DEFAULT_GRAPH_CLIENT_ID)
            bootstrap_record = graph_auth_record_path(
                temp,
                "appRegistration",
                DEFAULT_GRAPH_CLIENT_ID,
                "app-registration-auth-record.json",
            )
            bootstrap_record.write_text("bootstrap-only-record")
            configure_graph_client(temp, "appReadback", DEFAULT_GRAPH_CLIENT_ID)
            self.assertNotEqual(
                bootstrap_record,
                graph_auth_record_path(
                    temp,
                    "appReadback",
                    DEFAULT_GRAPH_CLIENT_ID,
                    "app-readback-auth-record.json",
                ),
            )
            with self.assertRaisesRegex(RuntimeError, "readback browser authentication is missing"):
                _app_readback_token(Path(temp), READBACK_TENANT_ID)

    def test_owned_application_projection_allows_omitted_annotation_and_bounds_pagination(self) -> None:
        calls = []

        def paged(method, url, token, body=None):
            calls.append((method, url))
            if len(calls) == 1:
                return 200, {
                    "value": [{"id": READBACK_OBJECT_ID}],
                    "@odata.nextLink": (
                        "https://graph.microsoft.com/v1.0/me/ownedObjects/"
                        "microsoft.graph.application?$skiptoken=page2"
                    ),
                }
            return 200, {
                "value": [{
                    "id": "01234567-89ab-cdef-0123-456789abcdef",
                    "@odata.type": "#microsoft.graph.application",
                }]
            }

        result = _list_owned_application_ids("token", graph_request=paged)
        self.assertEqual(
            [READBACK_OBJECT_ID, "01234567-89ab-cdef-0123-456789abcdef"],
            result,
        )
        self.assertTrue(all(method == "GET" for method, _ in calls))
        self.assertIn("%24select=id", calls[0][1])
        self.assertEqual(2, len(calls))

        for unsafe_link in (
            "https://evil.example/v1.0/me/ownedObjects/microsoft.graph.application",
            "https://graph.microsoft.com.evil.example/v1.0/me/ownedObjects/microsoft.graph.application",
            "https://graph.microsoft.com/v1.0/applications",
        ):
            with self.subTest(unsafe_link=unsafe_link):
                count = []

                def unsafe(method, url, token, body=None):
                    count.append(method)
                    return 200, {
                        "value": [{"id": READBACK_OBJECT_ID}],
                        "@odata.nextLink": unsafe_link,
                    }

                with self.assertRaisesRegex(RuntimeError, "unsafe continuation"):
                    _list_owned_application_ids("token", graph_request=unsafe)
                self.assertEqual(["GET"], count)

        def wrong_type(method, url, token, body=None):
            return 200, {
                "value": [{
                    "id": READBACK_OBJECT_ID,
                    "@odata.type": "#microsoft.graph.servicePrincipal",
                }]
            }

        with self.assertRaisesRegex(RuntimeError, "conflicting explicit object type"):
            _list_owned_application_ids("token", graph_request=wrong_type)

        page_count = []

        def too_many_pages(method, url, token, body=None):
            page_count.append(method)
            return 200, {
                "value": [],
                "@odata.nextLink": (
                    "https://graph.microsoft.com/v1.0/me/ownedObjects/"
                    "microsoft.graph.application?$skiptoken=next"
                ),
            }

        with self.assertRaisesRegex(RuntimeError, "10-page safety bound"):
            _list_owned_application_ids("token", graph_request=too_many_pages)
        self.assertEqual(10, len(page_count))

    def test_readback_token_requires_tenant_audience_and_required_scopes(self) -> None:
        from sentinel_xdr_migration.delegated_app_registration import _app_readback_token

        with tempfile.TemporaryDirectory() as temp:
            configure_graph_client(temp, "appReadback", DEFAULT_GRAPH_CLIENT_ID)
            record_path = graph_auth_record_path(
                temp,
                "appReadback",
                DEFAULT_GRAPH_CLIENT_ID,
                "app-readback-auth-record.json",
            )
            record_path.write_text("test-record")
            write_graph_auth_metadata(
                record_path,
                purpose="appReadback",
                client_id=DEFAULT_GRAPH_CLIENT_ID,
                tenant_id=READBACK_TENANT_ID,
            )
            record = mock.Mock(
                tenant_id=READBACK_TENANT_ID,
                client_id=DEFAULT_GRAPH_CLIENT_ID,
            )
            with (
                mock.patch(
                    "sentinel_xdr_migration.delegated_app_registration._load_auth_record",
                    return_value=record,
                ),
                mock.patch("azure.identity.InteractiveBrowserCredential") as credential_type,
                mock.patch("azure.identity.TokenCachePersistenceOptions"),
                mock.patch(
                    "sentinel_xdr_migration.graph_readiness._token_claims",
                    return_value={
                        "tid": READBACK_TENANT_ID,
                        "aud": "https://graph.microsoft.com",
                        "scp": "User.Read Application.Read.All",
                    },
                ),
            ):
                credential_type.return_value.get_token.return_value.token = "token"
                self.assertEqual("token", _app_readback_token(Path(temp), READBACK_TENANT_ID))
                credential_type.return_value.get_token.assert_called_once_with(
                    *READBACK_SCOPES
                )

            for claims, tenant, should_pass, message in (
                (
                    {"tid": READBACK_TENANT_ID, "aud": "https://graph.microsoft.com",
                     "scp": (
                         "User.Read Application.Read.All Directory.Read.All "
                         "email openid profile"
                     )},
                    READBACK_TENANT_ID,
                    True,
                    "",
                ),
                (
                    {"tid": "00000000-0000-0000-0000-000000000001",
                     "aud": "https://graph.microsoft.com",
                     "scp": "User.Read Application.Read.All"},
                    READBACK_TENANT_ID,
                    False,
                    "tenant",
                ),
                (
                    {"tid": READBACK_TENANT_ID, "aud": "https://other.example",
                     "scp": "User.Read Application.Read.All"},
                    READBACK_TENANT_ID,
                    False,
                    "Microsoft Graph",
                ),
                (
                    {"tid": READBACK_TENANT_ID, "aud": "https://graph.microsoft.com",
                     "scp": "User.Read"},
                    READBACK_TENANT_ID,
                    False,
                    "must include",
                ),
                (
                    {"tid": READBACK_TENANT_ID, "aud": "https://graph.microsoft.com",
                     "scp": ["User.Read", "Application.Read.All"]},
                    READBACK_TENANT_ID,
                    False,
                    "must include",
                ),
                (
                    {"tid": READBACK_TENANT_ID, "aud": "https://graph.microsoft.com",
                     "roles": ["User.Read", "Application.Read.All"]},
                    READBACK_TENANT_ID,
                    False,
                    "must include",
                ),
            ):
                with (
                    mock.patch(
                        "sentinel_xdr_migration.delegated_app_registration._load_auth_record",
                        return_value=record,
                    ),
                    mock.patch("azure.identity.InteractiveBrowserCredential") as credential_type,
                    mock.patch("azure.identity.TokenCachePersistenceOptions"),
                    mock.patch(
                        "sentinel_xdr_migration.graph_readiness._token_claims",
                        return_value=claims,
                    ),
                ):
                    credential_type.return_value.get_token.return_value.token = "token"
                    if should_pass:
                        self.assertEqual("token", _app_readback_token(Path(temp), tenant))
                    else:
                        with self.assertRaisesRegex(RuntimeError, message):
                            _app_readback_token(Path(temp), tenant)

    def test_scope_diagnostic_accepts_required_scope_superset_and_never_calls_graph(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            claims = {
                "tid": READBACK_TENANT_ID,
                "aud": "https://graph.microsoft.com",
                "scp": (
                    "User.Read Application.Read.All AppRegistration.Create "
                    "CustomDetection.ReadWrite.All email openid profile "
                    "ThreatHunting.Read.All"
                ),
            }
            with self._scope_diagnostic_fixtures(temp, claims) as fixtures:
                before_registration = read_delegated_app_registration(
                    fixtures["private"]
                )
                before_config = read_private_auth_config(fixtures["private"])
                result = diagnose_app_readback_scopes(
                    fixtures["root"],
                    run_id=READBACK_SCOPE_DIAGNOSTIC_RUN_ID,
                    state_dir=fixtures["private"],
                )
                self.assertEqual("required-scopes-present", result["status"])
                self.assertEqual("valid", result["scopeClaimStatus"])
                self.assertEqual(
                    {"User.Read", "Application.Read.All"},
                    set(result["expectedScopeNames"]),
                )
                self.assertEqual(
                    {
                        "User.Read",
                        "Application.Read.All",
                        "AppRegistration.Create",
                        "CustomDetection.ReadWrite.All",
                        "email",
                        "openid",
                        "profile",
                        "ThreatHunting.Read.All",
                    },
                    set(result["actualScopeNames"]),
                )
                self.assertEqual([], result["missingScopeNames"])
                self.assertEqual(
                    [
                        "AppRegistration.Create",
                        "CustomDetection.ReadWrite.All",
                        "email",
                        "openid",
                        "profile",
                        "ThreatHunting.Read.All",
                    ],
                    result["extraScopeNames"],
                )
                self.assertEqual(0, result["graphResourceRequests"])
                self.assertFalse(result["interactivePromptUsed"])
                self.assertFalse(result["privateConfigurationChanged"])
                self.assertEqual(
                    before_registration,
                    read_delegated_app_registration(fixtures["private"]),
                )
                self.assertEqual(
                    before_config,
                    read_private_auth_config(fixtures["private"]),
                )
                fixtures["credential"].assert_called_once()
                credential_options = fixtures["credential"].call_args.kwargs
                self.assertEqual(DEFAULT_GRAPH_CLIENT_ID, credential_options["client_id"])
                self.assertEqual(READBACK_TENANT_ID, credential_options["tenant_id"])
                self.assertTrue(credential_options["disable_automatic_authentication"])
                fixtures["credential"].return_value.authenticate.assert_not_called()
                fixtures["credential"].return_value.get_token.assert_called_once_with(
                    *READBACK_SCOPES
                )
                fixtures["cache"].assert_called_once()
                self.assertEqual(
                    "sentinel_xdr_migration_app_readback",
                    fixtures["cache"].call_args.kwargs["name"],
                )
                fixtures["loadAuthRecord"].assert_called_once_with(
                    fixtures["readbackRecordPath"]
                )
                self.assertNotEqual(
                    fixtures["readbackRecordPath"],
                    fixtures["bootstrapRecordPath"],
                )
                fixtures["graphRequest"].assert_not_called()
                fixtures["ownedApplications"].assert_not_called()
                self.assertNotIn(
                    "opaque-synthetic-token-not-for-output",
                    json.dumps(result),
                )
                self.assertNotIn("claims", result)
                self.assertNotIn("token", result)

    def test_scope_diagnostic_reports_missing_and_extra_names_and_gates_on_missing_only(self) -> None:
        cases = (
            ("User.Read", {"Application.Read.All"}, set(), False),
            (
                "User.Read Application.Read.All AppRegistration.Create",
                set(),
                {"AppRegistration.Create"},
                True,
            ),
            (
                "User.Read Directory.Read.All",
                {"Application.Read.All"},
                {"Directory.Read.All"},
                False,
            ),
            (
                "User.Read Application.Read.All email openid profile",
                set(),
                {"email", "openid", "profile"},
                True,
            ),
        )
        for scope_claim, expected_missing, expected_extra, should_pass in cases:
            with self.subTest(scope_claim=scope_claim), tempfile.TemporaryDirectory() as temp:
                claims = {
                    "tid": READBACK_TENANT_ID,
                    "aud": "https://graph.microsoft.com",
                    "scp": scope_claim,
                }
                with self._scope_diagnostic_fixtures(temp, claims) as fixtures:
                    result = diagnose_app_readback_scopes(
                        fixtures["root"],
                        run_id=READBACK_SCOPE_DIAGNOSTIC_RUN_ID,
                        state_dir=fixtures["private"],
                    )
                    self.assertEqual(
                        "required-scopes-present" if should_pass else "scope-mismatch",
                        result["status"],
                    )
                    self.assertEqual(expected_missing, set(result["missingScopeNames"]))
                    self.assertEqual(expected_extra, set(result["extraScopeNames"]))
                    self.assertEqual(0, result["graphResourceRequests"])
                    fixtures["graphRequest"].assert_not_called()
                    fixtures["ownedApplications"].assert_not_called()

                    from sentinel_xdr_migration.delegated_app_registration import (
                        _app_readback_token,
                    )

                    if should_pass:
                        self.assertEqual(
                            "opaque-synthetic-token-not-for-output",
                            _app_readback_token(
                                fixtures["private"], READBACK_TENANT_ID
                            ),
                        )
                    else:
                        with self.assertRaisesRegex(
                            RuntimeError, "must include"
                        ):
                            _app_readback_token(
                                fixtures["private"], READBACK_TENANT_ID
                            )

    def test_scope_diagnostic_blocks_missing_malformed_and_untrusted_claims(self) -> None:
        cases = (
            (
                {"tid": READBACK_TENANT_ID, "aud": "https://graph.microsoft.com"},
                "missing",
            ),
            (
                {
                    "tid": READBACK_TENANT_ID,
                    "aud": "https://graph.microsoft.com",
                    "scp": ["User.Read", "Application.Read.All"],
                },
                "malformed",
            ),
            (
                {
                    "tid": READBACK_TENANT_ID,
                    "aud": "https://graph.microsoft.com",
                    "scp": "User.Read https://graph.microsoft.com/Application.Read.All",
                },
                "malformed",
            ),
            (
                {
                    "tid": "00000000-0000-0000-0000-000000000001",
                    "aud": "https://graph.microsoft.com",
                    "scp": "User.Read Application.Read.All",
                },
                "not-available",
            ),
            (
                {
                    "tid": READBACK_TENANT_ID,
                    "aud": "https://other.example",
                    "scp": "User.Read Application.Read.All",
                },
                "not-available",
            ),
        )
        for claims, claim_status in cases:
            with self.subTest(claims=claims), tempfile.TemporaryDirectory() as temp:
                with self._scope_diagnostic_fixtures(temp, claims) as fixtures:
                    result = diagnose_app_readback_scopes(
                        fixtures["root"],
                        run_id=READBACK_SCOPE_DIAGNOSTIC_RUN_ID,
                        state_dir=fixtures["private"],
                    )
                    self.assertEqual("diagnostic-blocked", result["status"])
                    self.assertEqual(claim_status, result["scopeClaimStatus"])
                    self.assertEqual([], result["actualScopeNames"])
                    self.assertEqual(
                        {"User.Read", "Application.Read.All"},
                        set(result["missingScopeNames"]),
                    )
                    self.assertEqual([], result["extraScopeNames"])
                    self.assertEqual(0, result["graphResourceRequests"])
                    self.assertNotIn("https://graph.microsoft.com", json.dumps(result))
                    fixtures["graphRequest"].assert_not_called()
                    fixtures["ownedApplications"].assert_not_called()

    def test_scope_diagnostic_cache_failures_suppress_sensitive_details_and_never_prompt(self) -> None:
        sensitive_error = (
            "Bearer synthetic-access-token /private/state/auth-record.json "
            "client_secret=synthetic-secret claims={\"tid\":\"synthetic-tenant\"}"
        )
        for auth_record, auth_error in (
            (None, None),
            (None, RuntimeError(sensitive_error)),
        ):
            with self.subTest(auth_error=auth_error), tempfile.TemporaryDirectory() as temp:
                claims = {
                    "tid": READBACK_TENANT_ID,
                    "aud": "https://graph.microsoft.com",
                    "scp": "User.Read Application.Read.All",
                }
                with self._scope_diagnostic_fixtures(
                    temp,
                    claims,
                    auth_record=auth_record,
                    auth_error=auth_error,
                ) as fixtures:
                    result = diagnose_app_readback_scopes(
                        fixtures["root"],
                        run_id=READBACK_SCOPE_DIAGNOSTIC_RUN_ID,
                        state_dir=fixtures["private"],
                    )
                    self.assertEqual("diagnostic-blocked", result["status"])
                    self.assertEqual("not-available", result["scopeClaimStatus"])
                    self.assertEqual([], result["actualScopeNames"])
                    self.assertEqual(
                        {"User.Read", "Application.Read.All"},
                        set(result["missingScopeNames"]),
                    )
                    for sensitive_value in (
                        "synthetic-access-token",
                        "/private/state/auth-record.json",
                        "synthetic-secret",
                        "synthetic-tenant",
                    ):
                        self.assertNotIn(sensitive_value, result["reason"])
                    fixtures["credential"].assert_not_called()
                    fixtures["graphRequest"].assert_not_called()
                    fixtures["ownedApplications"].assert_not_called()

    def test_scope_diagnostic_is_bound_to_exact_run_and_locked_tenant(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            claims = {
                "tid": READBACK_TENANT_ID,
                "aud": "https://graph.microsoft.com",
                "scp": "User.Read Application.Read.All",
            }
            with self._scope_diagnostic_fixtures(temp, claims) as fixtures:
                with self.assertRaisesRegex(
                    ValueError,
                    "scope diagnostic requires the exact pinned Qualification run and tenant",
                ):
                    diagnose_app_readback_scopes(
                        fixtures["root"],
                        run_id="different-run",
                        state_dir=fixtures["private"],
                    )
                with mock.patch(
                    "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                    return_value={"tenantId": "00000000-0000-0000-0000-000000000001"},
                ):
                    with self.assertRaisesRegex(
                        RuntimeError,
                        "private app-registration record is not bound to the locked tenant",
                    ):
                        diagnose_app_readback_scopes(
                            fixtures["root"],
                            run_id=READBACK_SCOPE_DIAGNOSTIC_RUN_ID,
                            state_dir=fixtures["private"],
                        )
                fixtures["credential"].assert_not_called()
                fixtures["graphRequest"].assert_not_called()
                fixtures["ownedApplications"].assert_not_called()

    def test_scope_diagnostic_cli_requires_run_and_preserves_blocked_exit_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            solution = Path(temp) / "Cisco"
            create_run(solution, run_id=READBACK_SCOPE_DIAGNOSTIC_RUN_ID)
            output = StringIO()
            with redirect_stdout(output), self.assertRaises(SystemExit) as missing_run:
                cli_main([
                    "diagnose-app-readback-scopes",
                    "--solution",
                    str(solution),
                ])
            self.assertEqual(2, missing_run.exception.code)

            with (
                redirect_stdout(output),
                mock.patch(
                    "sentinel_xdr_migration.delegated_app_registration.diagnose_app_readback_scopes",
                    return_value={"status": "required-scopes-present"},
                ) as diagnostic,
            ):
                status = cli_main([
                    "diagnose-app-readback-scopes",
                    "--solution",
                    str(solution),
                    "--run-id",
                    READBACK_SCOPE_DIAGNOSTIC_RUN_ID,
                ])
            self.assertEqual(0, status)
            diagnostic.assert_called_once_with(
                str(solution),
                run_id=READBACK_SCOPE_DIAGNOSTIC_RUN_ID,
            )
            with (
                redirect_stdout(output),
                mock.patch(
                    "sentinel_xdr_migration.delegated_app_registration.diagnose_app_readback_scopes",
                    return_value={"status": "scope-mismatch"},
                ),
            ):
                status = cli_main([
                    "diagnose-app-readback-scopes",
                    "--solution",
                    str(solution),
                    "--run-id",
                    READBACK_SCOPE_DIAGNOSTIC_RUN_ID,
                ])
            self.assertEqual(1, status)

    def test_readback_requires_owned_exact_object_and_gets_only_approved_settings(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            registration = {
                "schemaVersion": 1,
                "applicationId": READBACK_APPLICATION_ID,
                "objectId": READBACK_OBJECT_ID,
                "tenantId": READBACK_TENANT_ID,
                "displayName": READBACK_DISPLAY_NAME,
                "status": "created-needs-ownership-verification",
                "creationSnapshot": {"status": 201},
            }
            write_delegated_app_registration(temp, registration)
            methods = []
            urls = []

            def request(method, url, token, body=None):
                methods.append(method)
                urls.append(url)
                if len(methods) == 1:
                    return 200, {
                        "value": [{
                            "id": READBACK_OBJECT_ID,
                            "@odata.type": "#microsoft.graph.application",
                        }]
                    }
                self.assertIsNone(body)
                return 200, self._readback_settings()

            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": READBACK_TENANT_ID},
            ):
                result = verify_delegated_app_readback(
                    Path(temp) / "Example",
                    state_dir=temp,
                    token_provider=lambda _state, _tenant: "read-only-token",
                    graph_request=request,
                )
            self.assertEqual("readback-verified-private-config-completed", result["status"])
            self.assertEqual(["GET", "GET"], methods)
            self.assertIn("/me/ownedObjects/microsoft.graph.application?", urls[0])
            self.assertIn("%24select=id", urls[0])
            self.assertIn(f"/applications/{READBACK_OBJECT_ID}?", urls[1])
            self.assertIn("passwordCredentials", urls[1])
            self.assertIn("keyCredentials", urls[1])
            self.assertFalse(result["graphWritesPerformed"])
            saved = read_delegated_app_registration(temp)
            self.assertEqual("configured", saved["status"])
            self.assertEqual(
                "created-needs-ownership-verification",
                saved["creationStatus"],
            )
            self.assertEqual({"status": 201}, saved["creationSnapshot"])
            self.assertEqual("passed", saved["readbackVerification"]["status"])
            self.assertFalse(saved["readbackVerification"]["adminConsentVerified"])
            self.assertEqual(
                READBACK_APPLICATION_ID,
                read_private_auth_config(temp)["graphClientIds"]["customDetection"],
            )
            self.assertEqual(
                READBACK_APPLICATION_ID,
                read_private_auth_config(temp)["graphClientIds"]["advancedHunting"],
            )

    def test_readback_unknown_ids_can_complete_only_after_exact_owned_get_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            calls = []
            write_delegated_app_registration(
                temp,
                {
                    "schemaVersion": 1,
                    "applicationId": READBACK_APPLICATION_ID,
                    "objectId": READBACK_OBJECT_ID,
                    "tenantId": READBACK_TENANT_ID,
                    "displayName": READBACK_DISPLAY_NAME,
                    "status": "create-outcome-unknown",
                },
            )

            def request(method, url, token, body=None):
                self.assertEqual("GET", method)
                self.assertIsNone(body)
                calls.append(url)
                if "/ownedObjects/" in url:
                    return 200, {"value": [{
                        "id": READBACK_OBJECT_ID,
                        "@odata.type": "#microsoft.graph.application",
                    }]}
                self.assertIn(f"/applications/{READBACK_OBJECT_ID}?", url)
                return 200, self._readback_settings()

            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": READBACK_TENANT_ID},
            ):
                result = verify_delegated_app_readback(
                    Path(temp) / "Example",
                    state_dir=temp,
                    token_provider=lambda _state, _tenant: "read-only-token",
                    graph_request=request,
                )
            self.assertEqual("readback-verified-private-config-completed", result["status"])
            self.assertEqual("create-outcome-unknown", result["preservedCreationStatus"])
            self.assertEqual(2, len(calls))
            self.assertTrue(result["privateConfigurationCompleted"])
            self.assertFalse(result["graphWritesPerformed"])
            self.assertFalse(result["adminConsentVerified"])

    def test_readback_failure_matrix_does_not_complete_private_configuration(self) -> None:
        cases = (
            ("not-owned", lambda: (200, {"value": []})),
            ("owned-object-type-conflict", lambda: (200, {"value": [{
                "id": READBACK_OBJECT_ID,
                "@odata.type": "#microsoft.graph.servicePrincipal",
            }]})),
            ("duplicate-owned", lambda: (200, {"value": [
                {"id": READBACK_OBJECT_ID, "@odata.type": "#microsoft.graph.application"},
                {"id": READBACK_OBJECT_ID, "@odata.type": "#microsoft.graph.application"},
            ]})),
        )
        for name, owned_response in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                original = {
                    "schemaVersion": 1,
                    "applicationId": READBACK_APPLICATION_ID,
                    "objectId": READBACK_OBJECT_ID,
                    "tenantId": READBACK_TENANT_ID,
                    "displayName": READBACK_DISPLAY_NAME,
                    "status": "reconciliation-required",
                }
                write_delegated_app_registration(temp, original)
                calls = []

                def request(method, url, token, body=None):
                    calls.append(method)
                    return owned_response()

                with mock.patch(
                    "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                    return_value={"tenantId": READBACK_TENANT_ID},
                ):
                    result = verify_delegated_app_readback(
                        Path(temp) / "Example",
                        state_dir=temp,
                        token_provider=lambda _state, _tenant: "read-only-token",
                        graph_request=request,
                    )
                self.assertEqual("verification-blocked", result["status"])
                self.assertEqual(["GET"], calls)
                self.assertFalse(result["privateConfigurationCompleted"])
                self.assertEqual(
                    "reconciliation-required",
                    read_delegated_app_registration(temp)["status"],
                )

        mismatch_cases = (
            ("wrong-client-id", {"appId": "00000000-0000-0000-0000-000000000001"}),
            ("wrong-name", {"displayName": "Other"}),
            ("wrong-audience", {"signInAudience": "AzureADMultipleOrgs"}),
            ("redirect-drift", {"publicClient": {"redirectUris": ["https://elsewhere"]}}),
            ("additional-delegated-permission", {"requiredResourceAccess": [{
                "resourceAppId": GRAPH_RESOURCE_APP_ID,
                "resourceAccess": [
                    {"id": CUSTOM_DETECTION_SCOPE_ID, "type": "Scope"},
                    {"id": "00000000-0000-0000-0000-000000000001", "type": "Scope"},
                ],
            }]}),
            ("application-permission", {"requiredResourceAccess": [{
                "resourceAppId": GRAPH_RESOURCE_APP_ID,
                "resourceAccess": [{"id": "00000000-0000-0000-0000-000000000001",
                                    "type": "Role"}],
            }]}),
            ("password-credential", {"passwordCredentials": [{"keyId": "not-exposed"}]}),
            ("key-credential", {"keyCredentials": [{"keyId": "not-exposed"}]}),
            ("redacted-permission-field", {"requiredResourceAccess": None}),
        )
        for name, updates in mismatch_cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                write_delegated_app_registration(
                    temp,
                    {
                        "schemaVersion": 1,
                        "applicationId": READBACK_APPLICATION_ID,
                        "objectId": READBACK_OBJECT_ID,
                        "tenantId": READBACK_TENANT_ID,
                        "displayName": READBACK_DISPLAY_NAME,
                        "status": "reconciliation-required",
                    },
                )
                calls = []

                def request(method, url, token, body=None):
                    calls.append(method)
                    if len(calls) == 1:
                        return 200, {"value": [{
                            "id": READBACK_OBJECT_ID,
                            "@odata.type": "#microsoft.graph.application",
                        }]}
                    return 200, self._readback_settings(**updates)

                with mock.patch(
                    "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                    return_value={"tenantId": READBACK_TENANT_ID},
                ):
                    result = verify_delegated_app_readback(
                        Path(temp) / "Example",
                        state_dir=temp,
                        token_provider=lambda _state, _tenant: "read-only-token",
                        graph_request=request,
                    )
                self.assertEqual("verification-blocked", result["status"])
                self.assertEqual(["GET", "GET"], calls)
                self.assertFalse(result["privateConfigurationCompleted"])
                self.assertEqual(
                    "reconciliation-required",
                    read_delegated_app_registration(temp)["status"],
                )

    def test_readback_refuses_wrong_target_foreign_private_ids_cache_and_graph_denial(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            pending = {
                "schemaVersion": 1,
                "applicationId": READBACK_APPLICATION_ID,
                "objectId": READBACK_OBJECT_ID,
                "tenantId": READBACK_TENANT_ID,
                "displayName": READBACK_DISPLAY_NAME,
                "status": "reconciliation-required",
            }
            write_delegated_app_registration(temp, pending)
            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": "00000000-0000-0000-0000-000000000001"},
            ):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "private app-registration record is not bound to the locked tenant",
                ):
                    verify_delegated_app_readback(
                        Path(temp) / "Example",
                        state_dir=temp,
                        token_provider=lambda *_args: self.fail("must not authenticate"),
                    )

            for field, value in (
                ("tenantId", "00000000-0000-0000-0000-000000000001"),
                ("displayName", "Other"),
                ("applicationId", "00000000-0000-0000-0000-000000000001"),
                ("objectId", "00000000-0000-0000-0000-000000000001"),
            ):
                foreign = dict(pending, **{field: value})
                write_delegated_app_registration(temp, foreign)
                with mock.patch(
                    "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                    return_value={"tenantId": READBACK_TENANT_ID},
                ):
                    if field == "tenantId":
                        with self.assertRaisesRegex(
                            RuntimeError,
                            "private app-registration record is not bound to the locked tenant",
                        ):
                            verify_delegated_app_readback(
                                Path(temp) / "Example",
                                state_dir=temp,
                                token_provider=lambda *_args: self.fail("must not authenticate"),
                            )
                        continue

                    def request(method, url, token, body=None):
                        self.assertEqual("GET", method)
                        self.assertIsNone(body)
                        if "/ownedObjects/" in url:
                            return 200, {"value": [{
                                "id": READBACK_OBJECT_ID,
                                "@odata.type": "#microsoft.graph.application",
                            }]}
                        return 200, self._readback_settings()

                    result = verify_delegated_app_readback(
                        Path(temp) / "Example",
                        state_dir=temp,
                        token_provider=lambda *_args: "synthetic-read-only-token",
                        graph_request=request,
                    )
                    self.assertEqual("verification-blocked", result["status"])
                    self.assertEqual(
                        "not-owned-or-not-visible" if field == "objectId" else "verified",
                        result["ownership"],
                    )
                    self.assertEqual(
                        "not-read" if field == "objectId" else "mismatch-or-incomplete",
                        result["settings"],
                    )
                    self.assertFalse(result["privateConfigurationCompleted"])
                    self.assertFalse(result["graphWritesPerformed"])
                    self.assertEqual(foreign, read_delegated_app_registration(temp))

            write_delegated_app_registration(temp, pending)
            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": READBACK_TENANT_ID},
            ):
                missing_cache = verify_delegated_app_readback(
                    Path(temp) / "Example",
                    state_dir=temp,
                    token_provider=lambda *_args: (_ for _ in ()).throw(
                        RuntimeError(
                            "app readback browser authentication is missing; run "
                            "`setup-app-readback-auth` explicitly first; Bearer "
                            "secret.access.token"
                        )
                    ),
                )
                self.assertEqual("verification-blocked", missing_cache["status"])
                self.assertEqual("not-run", missing_cache["ownership"])
                self.assertIn("setup-app-readback-auth", missing_cache["reason"])
                self.assertNotIn("secret.access.token", missing_cache["reason"])

                calls = []

                def denied(method, url, token, body=None):
                    calls.append(method)
                    return 403, {"error": {"message": "denied"}}

                blocked = verify_delegated_app_readback(
                    Path(temp) / "Example",
                    state_dir=temp,
                    token_provider=lambda *_args: "read-only-token",
                    graph_request=denied,
                )
                self.assertEqual("verification-blocked", blocked["status"])
                self.assertEqual("unverified", blocked["ownership"])
                self.assertEqual(["GET"], calls)
                self.assertEqual(
                    "reconciliation-required",
                    read_delegated_app_registration(temp)["status"],
                )

    def test_readback_cli_is_separate_and_reports_blocked_status_as_failure(self) -> None:
        output = StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as help_exit:
            cli_main(["verify-delegated-app-readback", "--help"])
        self.assertEqual(0, help_exit.exception.code)
        self.assertIn("--solution", output.getvalue())
        self.assertNotIn("--approve", output.getvalue())
        self.assertNotIn("register-delegated-app", output.getvalue())

        with tempfile.TemporaryDirectory() as temp, redirect_stdout(output), mock.patch(
            "sentinel_xdr_migration.delegated_app_registration.verify_delegated_app_readback",
            return_value={
                "status": "verification-blocked",
                "graphWritesPerformed": False,
            },
        ):
            status = cli_main([
                "verify-delegated-app-readback",
                "--solution",
                str(Path(temp) / "Example"),
            ])
        self.assertEqual(1, status)

    def test_manual_permission_update_plan_is_exact_and_verifier_is_get_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            solution = Path(temp) / "Example"
            legacy_permissions = [{
                "resourceAppId": GRAPH_RESOURCE_APP_ID,
                "resourceAccess": [{
                    "id": CUSTOM_DETECTION_SCOPE_ID,
                    "type": "Scope",
                }],
            }]
            desired_permissions = [{
                "resourceAppId": GRAPH_RESOURCE_APP_ID,
                "resourceAccess": [
                    {"id": CUSTOM_DETECTION_SCOPE_ID, "type": "Scope"},
                    {"id": THREAT_HUNTING_SCOPE_ID, "type": "Scope"},
                ],
            }]
            registration = {
                "schemaVersion": 1,
                "applicationId": READBACK_APPLICATION_ID,
                "objectId": READBACK_OBJECT_ID,
                "tenantId": READBACK_TENANT_ID,
                "displayName": READBACK_DISPLAY_NAME,
                "status": "reconciliation-required",
            }
            write_delegated_app_registration(temp, registration)
            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": READBACK_TENANT_ID},
            ):
                plan = plan_delegated_app_permission_update(
                    solution,
                    state_dir=temp,
                )
            self.assertEqual(READBACK_TENANT_ID, plan["tenantId"])
            self.assertEqual(READBACK_APPLICATION_ID, plan["applicationId"])
            self.assertEqual(READBACK_OBJECT_ID, plan["objectId"])
            self.assertEqual(READBACK_DISPLAY_NAME, plan["displayName"])
            self.assertEqual(legacy_permissions, plan["previouslyApprovedRequiredResourceAccess"])
            self.assertEqual(desired_permissions, plan["desiredRequiredResourceAccess"])
            self.assertEqual(
                [CUSTOM_DETECTION_SCOPE, THREAT_HUNTING_SCOPE],
                plan["desiredDelegatedScopeNames"],
            )
            self.assertFalse(plan["automatedReplacementSupported"])
            self.assertEqual([], plan["writeOperations"])

            calls = []

            def request(method, url, token, body=None):
                calls.append((method, url, body))
                self.assertEqual("GET", method)
                if "/ownedObjects/" in url:
                    return 200, {"value": [{
                        "id": READBACK_OBJECT_ID,
                        "@odata.type": "#microsoft.graph.application",
                    }]}
                return 200, self._readback_settings(
                    requiredResourceAccess=legacy_permissions
                )

            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": READBACK_TENANT_ID},
            ):
                legacy_result = verify_delegated_app_permission_update(
                    solution,
                    expected_plan_sha256=plan["planSha256"],
                    state_dir=temp,
                    token_provider=lambda *_: "synthetic-readonly-token",
                    graph_request=request,
                )
            self.assertEqual("manual-update-required", legacy_result["status"])
            self.assertTrue(legacy_result["manualPermissionAdditionRequired"])
            self.assertFalse(legacy_result["automatedUpdatePerformed"])
            self.assertEqual(["GET", "GET"], [method for method, _, _ in calls])
            self.assertTrue(all(body is None for _, _, body in calls))
            self.assertEqual(
                "reconciliation-required",
                read_delegated_app_registration(temp)["status"],
            )
            self.assertEqual({}, read_private_auth_config(temp)["graphClientIds"])

            calls.clear()

            def desired_request(method, url, token, body=None):
                calls.append((method, url, body))
                self.assertEqual("GET", method)
                if "/ownedObjects/" in url:
                    return 200, {"value": [{
                        "id": READBACK_OBJECT_ID,
                        "@odata.type": "#microsoft.graph.application",
                    }]}
                return 200, self._readback_settings(
                    requiredResourceAccess=desired_permissions
                )

            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": READBACK_TENANT_ID},
            ):
                verified = verify_delegated_app_permission_update(
                    solution,
                    expected_plan_sha256=plan["planSha256"],
                    state_dir=temp,
                    token_provider=lambda *_: "synthetic-readonly-token",
                    graph_request=desired_request,
                )
            self.assertEqual("manual-permission-update-verified", verified["status"])
            self.assertFalse(verified["automatedUpdatePerformed"])
            self.assertFalse(verified["graphWritesPerformed"])
            self.assertEqual(["GET", "GET"], [method for method, _, _ in calls])
            self.assertTrue(all(body is None for _, _, body in calls))
            clients = read_private_auth_config(temp)["graphClientIds"]
            self.assertEqual(READBACK_APPLICATION_ID, clients["customDetection"])
            self.assertEqual(READBACK_APPLICATION_ID, clients["advancedHunting"])

    def test_manual_permission_update_blocks_wrong_plan_and_unreviewed_settings(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            solution = Path(temp) / "Example"
            write_delegated_app_registration(
                temp,
                {
                    "schemaVersion": 1,
                    "applicationId": READBACK_APPLICATION_ID,
                    "objectId": READBACK_OBJECT_ID,
                    "tenantId": READBACK_TENANT_ID,
                    "displayName": READBACK_DISPLAY_NAME,
                    "status": "reconciliation-required",
                },
            )
            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": READBACK_TENANT_ID},
            ):
                plan = plan_delegated_app_permission_update(
                    solution,
                    state_dir=temp,
                )
                with self.assertRaisesRegex(ValueError, "plan has changed"):
                    verify_delegated_app_permission_update(
                        solution,
                        expected_plan_sha256="0" * 64,
                        state_dir=temp,
                        token_provider=lambda *_: self.fail("must not authenticate"),
                    )

            extra_permission = [{
                "resourceAppId": GRAPH_RESOURCE_APP_ID,
                "resourceAccess": [
                    {"id": CUSTOM_DETECTION_SCOPE_ID, "type": "Scope"},
                    {"id": THREAT_HUNTING_SCOPE_ID, "type": "Scope"},
                    {"id": "00000000-0000-0000-0000-000000000001", "type": "Scope"},
                ],
            }]

            def request(method, url, token, body=None):
                self.assertEqual("GET", method)
                if "/ownedObjects/" in url:
                    return 200, {"value": [{
                        "id": READBACK_OBJECT_ID,
                        "@odata.type": "#microsoft.graph.application",
                    }]}
                return 200, self._readback_settings(
                    requiredResourceAccess=extra_permission
                )

            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": READBACK_TENANT_ID},
            ):
                result = verify_delegated_app_permission_update(
                    solution,
                    expected_plan_sha256=plan["planSha256"],
                    state_dir=temp,
                    token_provider=lambda *_: "synthetic-readonly-token",
                    graph_request=request,
                )
            self.assertEqual("verification-blocked", result["status"])
            self.assertFalse(result["graphWritesPerformed"])
            self.assertEqual(
                "reconciliation-required",
                read_delegated_app_registration(temp)["status"],
            )
            self.assertEqual({}, read_private_auth_config(temp)["graphClientIds"])

    def test_manual_permission_update_cli_routes_without_selecting_workflow_run(self) -> None:
        output = StringIO()
        with (
            mock.patch("sentinel_xdr_migration.cli.select_run") as select_run,
            mock.patch("sentinel_xdr_migration.cli.configure_logging") as configure_logging,
            mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.plan_delegated_app_permission_update",
                return_value={"status": "manual-readback-required"},
            ) as plan,
            redirect_stdout(output),
        ):
            self.assertEqual(
                0,
                cli_main([
                    "plan-delegated-app-permission-update",
                    "--solution",
                    "solution",
                ]),
            )
        plan.assert_called_once_with("solution")
        select_run.assert_not_called()
        configure_logging.assert_not_called()

        with (
            mock.patch("sentinel_xdr_migration.cli.select_run") as select_run,
            mock.patch("sentinel_xdr_migration.cli.configure_logging") as configure_logging,
            mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.verify_delegated_app_permission_update",
                return_value={"status": "manual-update-required"},
            ) as verify,
            redirect_stdout(output),
        ):
            self.assertEqual(
                1,
                cli_main([
                    "verify-delegated-app-permission-update",
                    "--solution",
                    "solution",
                    "--expected-plan-sha256",
                    "a" * 64,
                ]),
            )
        verify.assert_called_once_with(
            "solution",
            expected_plan_sha256="a" * 64,
        )
        select_run.assert_not_called()
        configure_logging.assert_not_called()

    def test_bootstrap_client_override_is_private_and_cache_namespaced(self) -> None:
        class Record:
            tenant_id = TENANT_ID
            username = "operator@example.invalid"

            def serialize(self):
                return "serialized-test-record"

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with (
                mock.patch(
                    "azure.identity.DeviceCodeCredential"
                ) as credential_type,
                mock.patch("azure.identity.TokenCachePersistenceOptions") as cache,
            ):
                credential_type.return_value.authenticate.return_value = Record()
                claims = {
                    "tid": TENANT_ID,
                    "aud": GRAPH_RESOURCE_APP_ID,
                    "scp": (
                        "AppRegistration.Create User.Read Directory.Read.All "
                        "email openid profile"
                    ),
                }
                encoded = base64.urlsafe_b64encode(
                    json.dumps(claims).encode()
                ).decode().rstrip("=")
                credential_type.return_value.get_token.return_value.token = (
                    f"header.{encoded}.signature"
                )
                from sentinel_xdr_migration.delegated_app_registration import (
                    setup_app_registration_authentication,
                )

                setup_app_registration_authentication(
                    tenant_id=TENANT_ID,
                    bootstrap_client_id=CUSTOM_CLIENT_ID,
                    state_dir=root,
                )
            self.assertEqual(
                credential_type.call_args.kwargs["client_id"], CUSTOM_CLIENT_ID
            )
            self.assertEqual(
                cache.call_args.kwargs["name"],
                graph_token_cache_name(
                    "appRegistration",
                    CUSTOM_CLIENT_ID,
                    "sentinel_xdr_migration_app_registration",
                ),
            )
            self.assertEqual(
                resolve_graph_client_id(root, "appRegistration"),
                CUSTOM_CLIENT_ID,
            )
            self.assertFalse((root / "app-registration-auth-record.json").exists())
            records = [
                path
                for path in root.glob("app-registration-auth-record.*.json")
                if not path.name.endswith(".metadata.json")
            ]
            self.assertEqual(len(records), 1)

    def test_private_graph_state_cannot_be_placed_under_logs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Logs"
            with self.assertRaisesRegex(ValueError, "Logs"):
                configure_graph_client(root, "customDetection", CUSTOM_CLIENT_ID)

    def test_azure_cli_profile_is_explicit_isolated_and_restored(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profile = root / "lab-cli"
            result = configure_azure_cli_profile(root / "state", profile)
            self.assertEqual(result["azureConfigDir"], str(profile.resolve()))
            original = os.environ.get("AZURE_CONFIG_DIR")
            with azure_cli_profile(result["azureConfigDir"]):
                self.assertEqual(os.environ["AZURE_CONFIG_DIR"], result["azureConfigDir"])
            self.assertEqual(os.environ.get("AZURE_CONFIG_DIR"), original)
            with self.assertRaisesRegex(ValueError, "separate profile"):
                configure_azure_cli_profile(root / "state", Path.home() / ".azure")

    def test_profiled_cli_credential_scopes_environment_to_token_request(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            profile = str((Path(temp) / "cli").resolve())
            with mock.patch(
                "azure.identity.AzureCliCredential"
            ) as credential_type:
                with mock.patch.dict(os.environ, {"AZURE_CONFIG_DIR": profile}):
                    credential_type.return_value.get_token.side_effect = (
                        lambda *_scopes, **_kwargs: self.assertEqual(
                            os.environ["AZURE_CONFIG_DIR"], profile
                        )
                    )
                    credential = azure_cli_credential(
                        state_root=Path(temp) / "state"
                    )
                    credential.get_token("scope")
                credential_type.return_value.get_token.assert_called_once_with("scope")

    def test_plan_is_read_only_and_declares_no_consent_or_grants(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            solution = Path(temp) / "solution"
            solution.mkdir()
            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": TENANT_ID},
            ):
                plan = plan_delegated_app_registration(solution, state_dir=Path(temp) / "state")
            self.assertEqual(plan["status"], "approval-required")
            self.assertTrue(plan["authorization"]["exactScopeApprovalRequired"])
            self.assertEqual(plan["maximumApplicationCreates"], 1)
            self.assertIn("not-verified", plan["tenantWideDisplayNameUniqueness"])
            self.assertFalse(plan["bootstrap"]["adminConsentRequested"])
            self.assertTrue(plan["bootstrap"]["declarationIsNotConsent"])
            self.assertEqual(
                plan["bootstrap"]["delegatedScopes"], list(BOOTSTRAP_SCOPES)
            )
            self.assertFalse((Path(temp) / "state").exists())

    def test_requested_app_display_name_changes_plan_hash_and_rejects_old_hash(self) -> None:
        proposed_name = "Example-Offline-Registration-App"
        graph = mock.Mock()
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / "state"
            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": TENANT_ID},
            ):
                default_plan = plan_delegated_app_registration(temp, state_dir=state)
                named_plan = plan_delegated_app_registration(
                    temp, state_dir=state, app_display_name=proposed_name
                )
                self.assertEqual(default_plan["app"]["displayName"], APP_DISPLAY_NAME)
                self.assertEqual(named_plan["app"]["displayName"], proposed_name)
                self.assertNotEqual(default_plan["planSha256"], named_plan["planSha256"])
                with self.assertRaisesRegex(ValueError, "plan has changed"):
                    register_delegated_app(
                        temp,
                        expected_plan_sha256=default_plan["planSha256"],
                        approve_exact_app_registration=True,
                        state_dir=state,
                        app_display_name=proposed_name,
                        token_provider=lambda *_: "controlled-token",
                        graph_request=graph,
                    )
            graph.assert_not_called()

    def test_cli_forwards_exact_display_name_for_plan_and_registration(self) -> None:
        proposed_name = "Example-Offline-Registration-App"
        run_id = "20261011T200000Z-" + "a" * 32
        with (
            mock.patch("sentinel_xdr_migration.cli.select_run", return_value=None) as select_run,
            mock.patch("sentinel_xdr_migration.cli.configure_logging"),
            mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.plan_delegated_app_registration",
                return_value={"status": "approval-required"},
            ) as plan,
            redirect_stdout(StringIO()),
        ):
            self.assertEqual(
                cli_main([
                    "plan-delegated-app-registration",
                    "--solution", "solution",
                    "--run-id", run_id,
                    "--app-display-name", proposed_name,
                ]),
                0,
            )
        plan.assert_called_once_with("solution", app_display_name=proposed_name)
        select_run.assert_called_once_with("solution", run_id)

        with (
            mock.patch("sentinel_xdr_migration.cli.select_run", return_value=None) as select_run,
            mock.patch("sentinel_xdr_migration.cli.configure_logging"),
            mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.register_delegated_app",
                return_value={"status": "configured", "operation": "created"},
            ) as register,
            redirect_stdout(StringIO()),
        ):
            self.assertEqual(
                cli_main([
                    "register-delegated-app",
                    "--solution", "solution",
                    "--run-id", run_id,
                    "--app-display-name", proposed_name,
                    "--expected-plan-sha256", "a" * 64,
                    "--approve-exact-app-registration",
                ]),
                0,
            )
        register.assert_called_once_with(
            "solution",
            expected_plan_sha256="a" * 64,
            approve_exact_app_registration=True,
            app_display_name=proposed_name,
        )
        select_run.assert_called_once_with("solution", run_id)

    def test_changed_name_requires_reconciliation_without_renaming_or_creating(self) -> None:
        proposed_name = "Example-Offline-Registration-App"
        calls = []
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / "state"
            write_delegated_app_registration(
                state,
                {
                    "schemaVersion": 1,
                    "applicationId": APP_ID,
                    "objectId": OBJECT_ID,
                    "tenantId": TENANT_ID,
                    "displayName": APP_DISPLAY_NAME,
                    "status": "configured",
                },
            )
            existing_old_name = {
                **_registration_payload(),
                "id": OBJECT_ID,
                "appId": APP_ID,
            }
            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": TENANT_ID},
            ):
                plan = plan_delegated_app_registration(
                    temp, state_dir=state, app_display_name=proposed_name
                )
                self.assertEqual(plan["status"], "reconciliation-required")
                self.assertEqual(
                    plan["recordedRegistration"]["displayName"], APP_DISPLAY_NAME
                )
                with self.assertRaisesRegex(RuntimeError, "refusing to create a duplicate"):
                    register_delegated_app(
                        temp,
                        expected_plan_sha256=plan["planSha256"],
                        approve_exact_app_registration=True,
                        state_dir=state,
                        app_display_name=proposed_name,
                        token_provider=lambda *_: "controlled-token",
                        graph_request=lambda method, *_args, **_kwargs: (
                            calls.append(method) or 200,
                            {"value": [existing_old_name]},
                        ),
                    )
            self.assertEqual(calls, ["GET"])

    def test_registration_requires_explicit_exact_plan_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(PermissionError, "explicit"):
                register_delegated_app(
                    temp,
                    expected_plan_sha256="0" * 64,
                    state_dir=Path(temp) / "state",
                )

    def test_registration_hash_and_target_are_rechecked_before_any_graph_call(self) -> None:
        graph = mock.Mock()
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": TENANT_ID},
            ):
                plan = plan_delegated_app_registration(temp, state_dir=Path(temp) / "state")
                with self.assertRaisesRegex(ValueError, "plan has changed"):
                    register_delegated_app(
                        temp,
                        expected_plan_sha256="0" * 64,
                        approve_exact_app_registration=True,
                        state_dir=Path(temp) / "state",
                        token_provider=lambda *_: "controlled-token",
                        graph_request=graph,
                    )
            graph.assert_not_called()

    def test_bootstrap_token_requires_tenant_audience_and_minimum_scopes(self) -> None:
        from sentinel_xdr_migration.delegated_app_registration import (
            BOOTSTRAP_AUTH_RECORD_NAME,
            _bootstrap_token,
        )

        def jwt(claims: dict) -> str:
            encoded = base64.urlsafe_b64encode(
                json.dumps(claims).encode()
            ).decode().rstrip("=")
            return f"header.{encoded}.signature"

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record_path = root / BOOTSTRAP_AUTH_RECORD_NAME
            record_path.write_text("serialized")
            write_graph_auth_metadata(
                record_path,
                purpose="appRegistration",
                client_id=DEFAULT_GRAPH_CLIENT_ID,
                tenant_id=TENANT_ID,
            )
            base_claims = {
                "tid": TENANT_ID,
                "aud": GRAPH_RESOURCE_APP_ID,
                "scp": (
                    "AppRegistration.Create User.Read App.Read.All "
                    "email openid profile"
                ),
            }
            record = type("Record", (), {"tenant_id": TENANT_ID})()
            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration._load_auth_record",
                return_value=record,
            ), mock.patch(
                "azure.identity.DeviceCodeCredential"
            ) as credential_type:
                credential_type.return_value.get_token.return_value.token = jwt(
                    base_claims
                )
                self.assertEqual(_bootstrap_token(root, TENANT_ID), jwt(base_claims))
                credential_type.return_value.get_token.return_value.token = jwt(
                    {**base_claims, "tid": "00000000-0000-0000-0000-000000000001"}
                )
                with self.assertRaisesRegex(RuntimeError, "tenant"):
                    _bootstrap_token(root, TENANT_ID)
                credential_type.return_value.get_token.return_value.token = jwt(
                    {**base_claims, "aud": "https://other.example"}
                )
                with self.assertRaisesRegex(RuntimeError, "Microsoft Graph"):
                    _bootstrap_token(root, TENANT_ID)
                credential_type.return_value.get_token.return_value.token = jwt(
                    {**base_claims, "scp": "AppRegistration.Create"}
                )
                with self.assertRaisesRegex(RuntimeError, "required delegated"):
                    _bootstrap_token(root, TENANT_ID)
                credential_type.return_value.get_token.return_value.token = jwt(
                    {
                        **base_claims,
                        "scp": ["AppRegistration.Create", "User.Read"],
                    }
                )
                with self.assertRaisesRegex(RuntimeError, "required delegated"):
                    _bootstrap_token(root, TENANT_ID)
                credential_type.return_value.get_token.return_value.token = jwt(
                    {
                        "tid": TENANT_ID,
                        "aud": GRAPH_RESOURCE_APP_ID,
                        "roles": ["AppRegistration.Create", "User.Read"],
                    }
                )
                with self.assertRaisesRegex(RuntimeError, "required delegated"):
                    _bootstrap_token(root, TENANT_ID)

    def test_registration_lists_owned_apps_then_creates_exactly_one(self) -> None:
        proposed_name = "Example-Offline-Registration-App"
        payload = _registration_payload(proposed_name)
        created = {
            **payload,
            "id": OBJECT_ID,
            "appId": APP_ID,
        }
        calls = []
        get_count = 0

        def graph_request(method, url, token, body=None):
            nonlocal get_count
            calls.append((method, url, body))
            if method == "GET":
                get_count += 1
                return 200, {"value": [] if get_count == 1 else [created]}
            return 201, created

        with tempfile.TemporaryDirectory() as temp:
            solution = Path(temp) / "solution"
            solution.mkdir()
            state = Path(temp) / "private"
            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": TENANT_ID},
            ):
                plan = plan_delegated_app_registration(
                    solution, state_dir=state, app_display_name=proposed_name
                )
                result = register_delegated_app(
                    solution,
                    expected_plan_sha256=plan["planSha256"],
                    approve_exact_app_registration=True,
                    state_dir=state,
                    app_display_name=proposed_name,
                    token_provider=lambda _state, tenant: (
                        self.assertEqual(tenant, TENANT_ID) or "controlled-token"
                    ),
                    graph_request=graph_request,
                )
            self.assertEqual(result["status"], "configured")
            self.assertEqual(result["operation"], "created")
            self.assertEqual(result["applicationId"], APP_ID)
            self.assertEqual(result["displayName"], proposed_name)
            self.assertEqual(result["adminConsent"], "not-requested")
            self.assertEqual([call[0] for call in calls], ["GET", "POST", "GET"])
            self.assertEqual(calls[1][2], payload)
            private_config = json.loads(
                (state / PRIVATE_AUTH_CONFIG_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(
                private_config["graphClientIds"]["customDetection"], APP_ID
            )
            self.assertEqual(
                private_config["delegatedAppRegistration"]["displayName"],
                proposed_name,
            )
            reports = list(solution.rglob("delegated-app-registration.report.json"))
            self.assertEqual(len(reports), 1)
            report = json.loads(reports[0].read_text())
            self.assertEqual(report["adminConsent"], "not-requested")
            self.assertEqual(report["displayName"], proposed_name)
            self.assertEqual(report["applicationPermissionGrant"], "not-requested")
            self.assertNotIn("secret", json.dumps(private_config).casefold())

    def test_registration_reuses_exact_owned_app_but_never_modifies_existing_app(self) -> None:
        proposed_name = "Example-Offline-Registration-App"
        payload = _registration_payload(proposed_name)
        matching = {**payload, "id": OBJECT_ID, "appId": APP_ID}
        calls = []

        def graph_request(method, url, token, body=None):
            calls.append(method)
            return 200, {"value": [matching]}

        with tempfile.TemporaryDirectory() as temp:
            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": TENANT_ID},
            ):
                plan = plan_delegated_app_registration(
                    temp,
                    state_dir=Path(temp) / "state",
                    app_display_name=proposed_name,
                )
                result = register_delegated_app(
                    temp,
                    expected_plan_sha256=plan["planSha256"],
                    approve_exact_app_registration=True,
                    state_dir=Path(temp) / "state",
                    app_display_name=proposed_name,
                    token_provider=lambda *_: "controlled-token",
                    graph_request=graph_request,
                )
            self.assertEqual(result["operation"], "reused-exact-owned-app")
            self.assertEqual(result["displayName"], proposed_name)
            self.assertEqual(calls, ["GET"])

        calls.clear()
        changed = {**matching, "publicClient": {"redirectUris": ["https://evil.invalid"]}}
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": TENANT_ID},
            ):
                plan = plan_delegated_app_registration(
                    temp,
                    state_dir=Path(temp) / "state",
                    app_display_name=proposed_name,
                )
                with self.assertRaisesRegex(RuntimeError, "different settings"):
                    register_delegated_app(
                        temp,
                        expected_plan_sha256=plan["planSha256"],
                        approve_exact_app_registration=True,
                        state_dir=Path(temp) / "state",
                        app_display_name=proposed_name,
                        token_provider=lambda *_: "controlled-token",
                        graph_request=lambda method, *_args: (
                            calls.append(method) or 200,
                            {"value": [changed]},
                        ),
                    )
            self.assertEqual(calls, ["GET"])

    def test_owned_app_listing_refuses_non_graph_continuation(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "unsafe continuation"):
            _list_owned_apps(
                "controlled-token",
                graph_request=lambda *_: (
                    200,
                    {
                        "value": [],
                        "@odata.nextLink": "https://example.invalid/steal-token",
                    },
                ),
            )

    def test_owned_app_listing_fails_closed_when_permission_is_insufficient(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "cannot safely verify ownership"):
            _list_owned_apps(
                "controlled-token",
                graph_request=lambda *_: (403, {"error": {"message": "forbidden"}}),
            )

    def test_registration_fails_closed_when_owned_app_properties_are_redacted(self) -> None:
        calls = []
        with tempfile.TemporaryDirectory() as temp:
            solution = Path(temp) / "solution"
            solution.mkdir()
            state = Path(temp) / "private"
            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": TENANT_ID},
            ):
                plan = plan_delegated_app_registration(solution, state_dir=state)
                with self.assertRaisesRegex(RuntimeError, "cannot read enough"):
                    register_delegated_app(
                        solution,
                        expected_plan_sha256=plan["planSha256"],
                        approve_exact_app_registration=True,
                        state_dir=state,
                        token_provider=lambda *_: "controlled-token",
                        graph_request=lambda method, *_args, **_kwargs: (
                            calls.append(method) or 200,
                            {"value": [{"id": OBJECT_ID, "@odata.type": "#microsoft.graph.application"}]},
                        ),
                    )
            self.assertEqual(calls, ["GET"])

    def test_created_app_not_visible_as_owned_blocks_configuration_and_future_duplicate(self) -> None:
        payload = _registration_payload()
        created = {**payload, "id": OBJECT_ID, "appId": APP_ID}
        with tempfile.TemporaryDirectory() as temp:
            solution = Path(temp) / "solution"
            solution.mkdir()
            state = Path(temp) / "private"
            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": TENANT_ID},
            ):
                plan = plan_delegated_app_registration(solution, state_dir=state)
                responses = iter(
                    [
                        (200, {"value": []}),
                        (201, created),
                        (200, {"value": []}),
                    ]
                )
                result = register_delegated_app(
                    solution,
                    expected_plan_sha256=plan["planSha256"],
                    approve_exact_app_registration=True,
                    state_dir=state,
                    token_provider=lambda *_: "controlled-token",
                    graph_request=lambda *_args, **_kwargs: next(responses),
                )
                self.assertEqual(result["status"], "reconciliation-required")
                persisted = json.loads(
                    (state / PRIVATE_AUTH_CONFIG_NAME).read_text(encoding="utf-8")
                )["delegatedAppRegistration"]
                self.assertEqual(
                    persisted["status"], "created-needs-ownership-verification"
                )
                next_plan = plan_delegated_app_registration(solution, state_dir=state)
                self.assertEqual(next_plan["status"], "reconciliation-required")
                with self.assertRaisesRegex(RuntimeError, "refusing to create a duplicate"):
                    register_delegated_app(
                        solution,
                        expected_plan_sha256=next_plan["planSha256"],
                        approve_exact_app_registration=True,
                        state_dir=state,
                        token_provider=lambda *_: "controlled-token",
                        graph_request=lambda *_args, **_kwargs: (200, {"value": []}),
                    )

    def test_post_create_owned_app_readback_failure_is_reported_without_success_claim(self) -> None:
        proposed_name = "Example-Offline-Registration-App"
        payload = _registration_payload(proposed_name)
        created = {**payload, "id": OBJECT_ID, "appId": APP_ID}
        get_count = 0

        def graph_request(method, *_args, **_kwargs):
            nonlocal get_count
            if method == "GET":
                get_count += 1
                if get_count == 1:
                    return 200, {"value": []}
                return 403, {"error": {"message": "readback denied"}}
            return 201, created

        with tempfile.TemporaryDirectory() as temp:
            solution = Path(temp) / "solution"
            solution.mkdir()
            state = Path(temp) / "private"
            with mock.patch(
                "sentinel_xdr_migration.delegated_app_registration.require_locked_target",
                return_value={"tenantId": TENANT_ID},
            ):
                plan = plan_delegated_app_registration(
                    solution, state_dir=state, app_display_name=proposed_name
                )
                result = register_delegated_app(
                    solution,
                    expected_plan_sha256=plan["planSha256"],
                    approve_exact_app_registration=True,
                    state_dir=state,
                    app_display_name=proposed_name,
                    token_provider=lambda *_: "controlled-token",
                    graph_request=graph_request,
                )

            self.assertEqual(result["status"], "reconciliation-required")
            self.assertEqual(result["operation"], "created")
            self.assertEqual(result["displayName"], proposed_name)
            self.assertFalse(result["ownershipVerified"])
            self.assertIn("HTTP 403", result["error"])
            self.assertEqual(result["reason"], result["error"])
            reports = list(solution.rglob("delegated-app-registration.report.json"))
            self.assertEqual(len(reports), 1)
            report = json.loads(reports[0].read_text())
            self.assertEqual(report["status"], "reconciliation-required")
            self.assertEqual(report["displayName"], proposed_name)
            self.assertEqual(report["reason"], result["reason"])
            self.assertEqual(report["error"], result["error"])
            private = json.loads(
                (state / PRIVATE_AUTH_CONFIG_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(
                private["delegatedAppRegistration"]["displayName"],
                proposed_name,
            )
            self.assertNotIn("customDetection", private.get("graphClientIds", {}))

    def test_bundled_graph_scope_templates_exist_and_offer_builds_remediation(self) -> None:
        from solution_manager.qualification.delegated_app_registration import (
            GRAPH_SCOPE_ARM_TEMPLATE_PATH,
            GRAPH_SCOPE_BICEP_TEMPLATE_PATH,
            build_missing_graph_scope_arm_offer,
        )

        self.assertTrue(GRAPH_SCOPE_ARM_TEMPLATE_PATH.is_file())
        self.assertTrue(GRAPH_SCOPE_BICEP_TEMPLATE_PATH.is_file())

        arm_payload = json.loads(
            GRAPH_SCOPE_ARM_TEMPLATE_PATH.read_text(encoding="utf-8")
        )
        self.assertEqual(arm_payload.get("languageVersion"), "2.0")
        self.assertEqual(
            arm_payload.get("imports", {}).get("MicrosoftGraph", {}),
            {"provider": "MicrosoftGraph", "version": "1.0.0"},
        )
        bicep_text = GRAPH_SCOPE_BICEP_TEMPLATE_PATH.read_text(encoding="utf-8")
        self.assertIn("microsoftgraph/v1.0:1.0.0", bicep_text)
        self.assertIn("Microsoft.Graph/oauth2PermissionGrants@v1.0", bicep_text)

        offer = build_missing_graph_scope_arm_offer(
            missing_scopes=["CustomDetection.ReadWrite.All", "ThreatHunting.Read.All"],
            resource_group="rg-sentinel-qual",
            subscription_id="00000000-0000-0000-0000-000000000099",
            app_unique_name="Sentinel-XDR-CustomDetection",
            grant_to_azure_cli=True,
        )
        self.assertEqual(offer["status"], "arm_template_remediation_available")
        self.assertTrue(offer["requiresExplicitApproval"])
        self.assertEqual(
            offer["missingScopes"],
            ["CustomDetection.ReadWrite.All", "ThreatHunting.Read.All"],
        )
        self.assertEqual(offer["armTemplatePath"], str(GRAPH_SCOPE_ARM_TEMPLATE_PATH))
        self.assertEqual(offer["bicepTemplatePath"], str(GRAPH_SCOPE_BICEP_TEMPLATE_PATH))
        self.assertEqual(
            offer["resourcesCreated"],
            [
                "Microsoft.Graph/applications@v1.0",
                "Microsoft.Graph/servicePrincipals@v1.0",
                "Microsoft.Graph/oauth2PermissionGrants@v1.0",
            ],
        )
        self.assertIn("az deployment group create", offer["deploymentCommand"])
        self.assertIn("--template-file", offer["deploymentCommand"])
        self.assertIn('appUniqueName="Sentinel-XDR-CustomDetection"', offer["deploymentCommand"])
        self.assertIn("grantToAzureCli=true", offer["deploymentCommand"])
        self.assertIn("grant-graph-hunting-scopes.arm.json", offer["approvalPrompt"])
        self.assertIn("ThreatHunting.Read.All", offer["approvalPrompt"])
        self.assertIn("CustomDetection.ReadWrite.All", offer["approvalPrompt"])

        default_offer = build_missing_graph_scope_arm_offer(
            missing_scopes=["ThreatHunting.Read.All"],
            resource_group="rg-sentinel-qual",
        )
        self.assertIn("grantToAzureCli=false", default_offer["deploymentCommand"])

        with self.assertRaises(ValueError):
            build_missing_graph_scope_arm_offer(
                missing_scopes=["Directory.ReadWrite.All"],
                resource_group="rg-sentinel-qual",
            )


if __name__ == "__main__":
    unittest.main()
