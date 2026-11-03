import gzip
import hashlib
import hmac
import importlib.util
import json
import os
from pathlib import Path
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from zipfile import ZipFile

import azure.functions as func
from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import HttpResponse, HttpTransport
from azure.identity import AzureAuthorityHosts
from azure.monitor.ingestion import LogsIngestionClient


CONNECTOR_ROOT = Path(__file__).resolve().parents[1]
SOURCE = CONNECTOR_ROOT / "GithubWebhookConnectorV2" / "__init__.py"
CLOUDS = (
    (
        "https://example.eastus-1.ingest.monitor.azure.com",
        AzureAuthorityHosts.AZURE_PUBLIC_CLOUD,
        "https://monitor.azure.com//.default",
    ),
    (
        "https://example.usgovvirginia-1.ingest.monitor.azure.us",
        AzureAuthorityHosts.AZURE_GOVERNMENT,
        "https://monitor.azure.us/.default",
    ),
)


class UploadResponse(HttpResponse):
    def __init__(self, request, status_code):
        super().__init__(request, None)
        self.status_code = status_code
        self.reason = "No Content" if status_code == 204 else "Forbidden"
        self.headers = {}

    def body(self):
        return b""


class RecordingTransport(HttpTransport):
    def __init__(self):
        self.requests = []
        self.status_code = 204

    def open(self):
        pass

    def close(self):
        pass

    def __exit__(self, *args):
        self.close()

    def send(self, request, **kwargs):
        self.requests.append(request)
        return UploadResponse(request, self.status_code)


class CloudAuthenticationTests(unittest.TestCase):
    def load_connector(self, endpoint, secret=""):
        environment = {
            "DCR_RULE_ID": "dcr-test",
            "DCR_STREAM_NAME": "Custom-GitHubAdvancedSecurityAlerts_CL",
            "GithubWebhookSecret": secret,
        }
        if endpoint is not None:
            environment["DCE_ENDPOINT"] = endpoint
        credential = Mock(spec=["get_token", "close"])
        credential.get_token.return_value = AccessToken("test-token", int(time.time()) + 3600)
        transport = RecordingTransport()

        def create_client(*args, **kwargs):
            return LogsIngestionClient(*args, transport=transport, retry_total=0, **kwargs)

        spec = importlib.util.spec_from_file_location("github_webhook_v2_test", SOURCE)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(os.environ, environment, clear=True):
            with patch("azure.identity.DefaultAzureCredential", return_value=credential) as factory:
                with patch("azure.monitor.ingestion.LogsIngestionClient", side_effect=create_client):
                    spec.loader.exec_module(module)
        self.addCleanup(module.client.close)
        return module, credential, transport, factory

    def test_upload_uses_each_clouds_scope_authority_and_endpoint(self):
        for endpoint, authority, scope in CLOUDS:
            with self.subTest(endpoint=endpoint):
                module, credential, transport, factory = self.load_connector(endpoint)
                factory.assert_called_once_with(authority=authority)
                body = b'{"action": "created", "repository": {"name": "example"}}'
                request = func.HttpRequest(
                    method="POST",
                    url="https://example.test/github/GithubWebhookConnectorV2",
                    headers={"x-github-event": "repository"},
                    body=body,
                )
                context = SimpleNamespace(retry_context=SimpleNamespace(retry_count=0))
                response = module.main(request, context)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(credential.get_token.call_args.args, (scope,))
                self.assertEqual(len(transport.requests), 1)
                upload = transport.requests[0]
                self.assertTrue(upload.url.startswith(
                    endpoint + "/dataCollectionRules/dcr-test/streams/Custom-GitHubAdvancedSecurityAlerts_CL"
                ))
                self.assertEqual(upload.headers["Authorization"], "Bearer test-token")
                data = upload.body
                if upload.headers.get("Content-Encoding") == "gzip":
                    data = gzip.decompress(data)
                log = json.loads(data)[0]
                self.assertEqual(log["event"], "repository")
                self.assertEqual(log["action"], "created")
                self.assertEqual(json.loads(log["repository"]), {"name": "example"})
                self.assertTrue(log["TimeGenerated"].endswith("Z"))

    def test_government_hostname_is_case_insensitive_and_allows_trailing_slash(self):
        endpoint = "https://EXAMPLE.USGOVVIRGINIA-1.INGEST.MONITOR.AZURE.US/"
        _, _, _, factory = self.load_connector(endpoint)
        factory.assert_called_once_with(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)

    def test_missing_or_unsupported_endpoint_fails_explicitly(self):
        for endpoint in (
            None,
            "",
            "http://example.ingest.monitor.azure.us",
            "https://example.test",
            "https://example.ingest.monitor.azure.us.example.test",
            "https://example.test/path.ingest.monitor.azure.us",
            "https://example.test?endpoint=.ingest.monitor.azure.us",
        ):
            with self.subTest(endpoint=endpoint):
                with self.assertLogs(level="ERROR") as logs:
                    with self.assertRaisesRegex(ValueError, "DCE_ENDPOINT"):
                        self.load_connector(endpoint)
                self.assertIn("DCE_ENDPOINT", logs.output[0])

    def test_webhook_signature_validation_is_preserved_in_both_clouds(self):
        body = b'{"action": "created"}'
        secret = "unit-test-webhook-secret"
        signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        context = SimpleNamespace(retry_context=SimpleNamespace(retry_count=0))
        for endpoint, _, _ in CLOUDS:
            for supplied_signature in (None, "sha256=invalid", signature):
                with self.subTest(endpoint=endpoint, signature=supplied_signature):
                    module, _, transport, _ = self.load_connector(endpoint, secret)
                    headers = {"x-github-event": "repository"}
                    if supplied_signature is not None:
                        headers["x-hub-signature-256"] = supplied_signature
                    response = module.main(func.HttpRequest(
                        method="POST", url="https://example.test/webhook", headers=headers, body=body
                    ), context)
                    accepted = supplied_signature == signature
                    self.assertEqual(response.status_code, 200 if accepted else 403)
                    self.assertEqual(len(transport.requests), 1 if accepted else 0)

    def test_upload_failure_remains_an_error(self):
        for endpoint, _, _ in CLOUDS:
            with self.subTest(endpoint=endpoint):
                module, _, transport, _ = self.load_connector(endpoint)
                transport.status_code = 403
                with self.assertLogs(level="ERROR"):
                    with self.assertRaises(HttpResponseError):
                        module.post_data('{"action": "created"}')

    def test_arm_uses_resource_endpoints_without_extra_cloud_inputs(self):
        template_path = CONNECTOR_ROOT / "azuredeploy_GithubWebhookV2_API_FunctionApp.json"
        template = json.loads(template_path.read_text(encoding="utf-8-sig"))
        self.assertEqual(set(template["parameters"]), {"FunctionName", "WorkspaceName", "GithubWebhookSecret"})
        self.assertEqual(template["variables"]["StorageSuffix"], "[environment().suffixes.storage]")
        app = next(resource for resource in template["resources"] if resource["type"] == "Microsoft.Web/sites")
        settings = next(resource for resource in app["resources"] if resource["name"] == "appsettings")["properties"]
        self.assertEqual(settings["DCE_ENDPOINT"],
                         "[reference(resourceId('Microsoft.Insights/dataCollectionEndpoints', variables('DCEName')), '2022-06-01').logsIngestion.endpoint]")

    def test_deployment_zip_contains_current_source(self):
        with ZipFile(CONNECTOR_ROOT / "GithubWebhookV2.zip") as archive:
            source = archive.read("GithubWebhookConnectorV2/__init__.py").decode("utf-8-sig")
        self.assertEqual(source.replace("\r\n", "\n"), SOURCE.read_text(encoding="utf-8-sig"))


if __name__ == "__main__":
    unittest.main()
