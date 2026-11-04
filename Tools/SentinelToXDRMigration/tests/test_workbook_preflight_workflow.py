from __future__ import annotations

import base64
import io
import json
import time
from types import SimpleNamespace
from unittest import mock

import pytest

from sentinel_xdr_migration import cli
from sentinel_xdr_migration import workbook_preflight_workflow as preflight
from test_workbook_arm_validation import TARGET


PRINCIPAL = "12345678-1111-2222-3333-123456789abc"
ACCOUNT = {"id": TARGET["subscriptionId"], "tenantId": TARGET["tenantId"]}
ACCOUNT_OPERATION = {
    "id": "account", "kind": "azure-cli-account", "method": "LOCAL",
    "subscriptionId": TARGET["subscriptionId"],
}
WORKSPACE_OPERATION = {
    "id": "workspace", "kind": "arm-get", "method": "GET",
    "url": f"https://management.azure.com{TARGET['workspaceResourceId']}?api-version=2023-09-01",
}
GRAPH_OPERATION = {
    "id": "workbook", "kind": "graph-get", "method": "GET",
    "url": "https://graph.microsoft.com/beta/security/workbooks/12345678-1111-2222-3333-123456789abc",
}


def token(**overrides):
    claims = {
        "oid": PRINCIPAL, "tid": TARGET["tenantId"],
        "aud": "https://management.azure.com/", **overrides,
    }
    encoded = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    return SimpleNamespace(token=f"e30.{encoded}.fixture-only", expires_on=time.time() + 3600)


@pytest.fixture
def provider():
    credential = mock.Mock()
    credential.get_token.return_value = token()
    response = mock.MagicMock()
    response.__enter__.return_value = response
    response.status = 200
    response.read.return_value = json.dumps({"id": TARGET["workspaceResourceId"]}).encode()
    with mock.patch("sentinel_xdr_migration.graph_client_config.azure_cli_credential", return_value=credential), \
         mock.patch.object(preflight, "execution_profile", return_value="/fixture/private-profile"), \
         mock.patch("sentinel_xdr_migration.arm_acceptance_support._run_cli", return_value=(0, ACCOUNT, "")) as account, \
         mock.patch.object(preflight, "_open_read", return_value=response) as network:
        read = preflight.default_reader(
            TARGET, operations=[ACCOUNT_OPERATION, WORKSPACE_OPERATION, GRAPH_OPERATION],
        )
        yield read, credential, account, network


def test_reader_creation_is_offline_and_uses_one_observed_arm_principal(provider):
    read, credential, account, network = provider
    credential.get_token.assert_not_called()
    account.assert_not_called()
    network.assert_not_called()
    observed = read(ACCOUNT_OPERATION)
    assert observed["body"]["principal"]["objectId"] == PRINCIPAL
    assert "accessToken" not in json.dumps(observed)
    assert "fixture-only" not in json.dumps(observed)
    result = read(WORKSPACE_OPERATION)
    assert result["principalId"] == PRINCIPAL
    assert result["tenantId"] == TARGET["tenantId"]
    assert network.call_args.args[0].get_method() == "GET"
    assert network.call_args.args[0].get_header("Authorization") == f"Bearer {credential.get_token.return_value.token}"
    credential.get_token.assert_called_once_with("https://management.azure.com/.default")


def test_reader_does_not_infer_extension_auth_from_arm_or_hunting_credentials(provider):
    read, credential, account, network = provider
    result = read(GRAPH_OPERATION)
    assert result["statusCode"] == 0
    assert result["body"]["error"]["code"] == "MicrosoftSecurityIdentityUnverified"
    credential.get_token.assert_not_called()
    account.assert_not_called()
    network.assert_not_called()


def test_account_reader_overrides_general_deployment_cli_timeout(provider):
    read, _, account, _ = provider
    read(ACCOUNT_OPERATION)
    runner = account.call_args.kwargs["runner"]
    with mock.patch.object(preflight.subprocess, "run") as process:
        runner(["az", "account", "show"], timeout=1800, capture_output=True)
    assert process.call_args.kwargs["timeout"] == 15


@pytest.mark.parametrize("changes", [
    {"method": "POST"}, {"method": "DELETE"},
    {"url": "https://other.example/subscriptions/fixture"},
    {"url": "https://management.azure.com/subscriptions/other/resourceGroups/test"},
])
def test_unplanned_operations_stop_before_authentication_or_network(provider, changes):
    read, credential, account, network = provider
    with pytest.raises(ValueError, match="frozen approved read plan"):
        read({**WORKSPACE_OPERATION, **changes})
    credential.get_token.assert_not_called()
    account.assert_not_called()
    network.assert_not_called()


@pytest.mark.parametrize("claims", [
    {"tid": "aaaaaaaa-1111-2222-3333-444444444444"},
    {"aud": "https://graph.microsoft.com"},
    {"oid": "not-an-object-id"},
])
def test_wrong_token_bindings_never_dispatch(provider, claims):
    read, credential, _, network = provider
    credential.get_token.return_value = token(**claims)
    with pytest.raises(ValueError, match="principal|tenant binding"):
        read(ACCOUNT_OPERATION)
    network.assert_not_called()


def test_account_target_mismatch_never_acquires_a_token(provider):
    read, credential, account, network = provider
    account.return_value = (0, {**ACCOUNT, "tenantId": "wrong"}, "")
    result = read(ACCOUNT_OPERATION)
    assert result["body"]["tenantId"] == "wrong"
    credential.get_token.assert_not_called()
    network.assert_not_called()


def test_expired_access_token_is_rejected_before_arm_dispatch(provider):
    read, credential, _, network = provider
    credential.get_token.return_value.expires_on = time.time() - 60
    with pytest.raises(ValueError, match="current principal/tenant"):
        read(WORKSPACE_OPERATION)
    network.assert_not_called()


def test_changed_cached_principal_blocks_before_arm_read(provider):
    read, credential, _, network = provider
    read(ACCOUNT_OPERATION)
    credential.get_token.return_value.expires_on = time.time() - 1
    credential.get_token.return_value = token(oid="aaaaaaaa-1111-2222-3333-444444444444")
    with pytest.raises(ValueError, match="principal changed"):
        read(WORKSPACE_OPERATION)
    network.assert_not_called()


def test_http_errors_do_not_export_tokens_or_provider_error_body(provider):
    read, _, _, network = provider
    network.side_effect = preflight.urllib.error.HTTPError(
        WORKSPACE_OPERATION["url"], 403, "Bearer fixture-private", {}, io.BytesIO(b"private"),
    )
    result = read(WORKSPACE_OPERATION)
    assert result["statusCode"] == 403
    assert result["body"]["error"]["code"] == "ArmReadRejected"
    assert "fixture-private" not in json.dumps(result)


def test_sdk_auth_failure_is_explicit_and_sanitized(provider):
    from azure.core.exceptions import ClientAuthenticationError

    read, credential, _, network = provider
    credential.get_token.side_effect = ClientAuthenticationError("Bearer fixture-private")
    with pytest.raises(ValueError, match="no sign-in") as exc:
        read(ACCOUNT_OPERATION)
    assert "fixture-private" not in str(exc.value)
    network.assert_not_called()


def test_profile_change_blocks_before_auth_or_dispatch(provider):
    read, credential, _, network = provider
    with mock.patch.object(preflight, "execution_profile", return_value="/different-profile"):
        with pytest.raises(ValueError, match="profile changed"):
            read(WORKSPACE_OPERATION)
    credential.get_token.assert_not_called()
    network.assert_not_called()


def test_oversized_response_is_rejected_before_json_parsing(provider):
    from sentinel_xdr_migration.workbook_preflight import MAX_RESPONSE_BYTES

    read, _, _, network = provider
    response = network.return_value.__enter__.return_value
    response.read.return_value = b"x" * (MAX_RESPONSE_BYTES + 1)
    with pytest.raises(ValueError, match="bounded evidence size"):
        read(WORKSPACE_OPERATION)
    response.read.assert_called_once_with(MAX_RESPONSE_BYTES + 1)


def test_redirects_are_not_followed_by_authenticated_reader():
    request = preflight.urllib.request.Request(
        WORKSPACE_OPERATION["url"], headers={"Authorization": "Bearer fixture-only"},
    )
    handler = preflight._RejectRedirect()
    assert handler.redirect_request(
        request, None, 302, "Found", {}, "https://other.example/collect",
    ) is None
    with mock.patch.object(preflight.urllib.request, "build_opener") as build:
        preflight._open_read(request, timeout=15)
    assert isinstance(build.call_args.args[0], preflight._RejectRedirect)
    build.return_value.open.assert_called_once_with(request, timeout=15)


@pytest.mark.parametrize("name,arguments", [
    ("workflow-arm-preflight-plan", []),
    ("workflow-arm-preflight-review", [
        "--preflight-plan-sha256", "a" * 64, "--actor", "fixture",
        "--reference", "review", "--decision", "approved",
    ]),
    ("workflow-arm-preflight-execute", ["--preflight-plan-sha256", "a" * 64]),
    ("workflow-arm-preflight-revoke", ["--actor", "fixture", "--reference", "revoke"]),
])
def test_preflight_cli_requires_explicit_run_without_execution(name, arguments):
    with pytest.raises(SystemExit) as exc:
        cli.main([name, "--solution", "fixture", *arguments])
    assert exc.value.code == 2
