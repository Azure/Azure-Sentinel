"""Shared GTI (VirusTotal) large-file upload helper for the GTIFileUpload Azure Function."""

from io import BytesIO
from os import environ

import requests
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient

gti_base_url = environ.get("GTIBaseUrl", "https://www.virustotal.com")
scope = environ.get("SCOPE", "https://monitor.azure.com//.default")


class GTIUploader:
    """Wrapper class shared by GTI playbooks to upload a blob larger than 32MB.

    Uploads to Google Threat Intelligence (VirusTotal) using the large-file upload URL flow.
    """

    def __init__(self, log):
        """Store the logger instance used for diagnostics."""
        self.log = log

    def download_blob(self, storage_account_name: str, container_name: str, blob_path: str) -> BytesIO:
        """Download blob content directly from Azure Blob Storage.

        Uses the Function App's own managed identity (Storage Blob Data Reader role required).
        """
        domain = "blob.core.usgovcloudapi.net" if ".us" in scope else "blob.core.windows.net"
        account_url = f"https://{storage_account_name}.{domain}"
        blob_service_client = BlobServiceClient(account_url, credential=ManagedIdentityCredential())
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
        self.log.info("Downloading blob %s/%s from %s", container_name, blob_path, storage_account_name)
        return BytesIO(blob_client.download_blob().readall())

    def get_upload_url(self, api_key: str) -> requests.Response:
        """Request a one-time upload URL from GTI for files larger than 32MB."""
        return requests.get(
            f"{gti_base_url}/api/v3/private/files/upload_url",
            headers={
                "x-apikey": api_key,
                "User-Agent": "azure-sentinel-gti-upload-function/1.0",
            },
            timeout=60,
        )

    def submit_large_file(
        self,
        upload_url: str,
        api_key: str,
        file_name: str,
        file_content: BytesIO,
        disable_sandbox: bool | None = None,
        password: str | None = None,
        storage_region: str | None = None,
    ) -> requests.Response:
        """POST the file content to the GTI upload URL, with any optional submission parameters."""
        data = {}
        if disable_sandbox:
            data["disable_sandbox"] = str(disable_sandbox).lower()
        if password:
            data["password"] = password
        if storage_region:
            data["storage_region"] = storage_region

        return requests.post(
            upload_url,
            headers={
                "x-apikey": api_key,
                "User-Agent": "azure-sentinel-gti-upload-function/1.0",
            },
            files={"file": (file_name, file_content)},
            data=data,
            timeout=600,
        )

    def upload(
        self,
        storage_account_name: str,
        container_name: str,
        blob_path: str,
        api_key: str,
        disable_sandbox: bool | None = None,
        password: str | None = None,
        storage_region: str | None = None,
    ) -> dict:
        """Download the blob and submit it to GTI via the large-file upload URL flow.

        Returns:
            dict: {"analysisId": str|None, "statusCode": int, "error": str|None}
        """
        file_content = self.download_blob(storage_account_name, container_name, blob_path)

        upload_url_response = self.get_upload_url(api_key)
        if upload_url_response.status_code != 200:
            self.log.error("Failed to obtain GTI upload URL. Status: %s", upload_url_response.status_code)
            return {
                "analysisId": None,
                "statusCode": upload_url_response.status_code,
                "error": f"Failed to obtain GTI upload URL: {upload_url_response.text}",
            }

        upload_url = upload_url_response.json().get("data")
        file_name = blob_path.rsplit("/", 1)[-1]
        submit_response = self.submit_large_file(
            upload_url,
            api_key,
            file_name,
            file_content,
            disable_sandbox=disable_sandbox,
            password=password,
            storage_region=storage_region,
        )
        if submit_response.status_code != 200:
            self.log.error("Failed to submit large file to GTI. Status: %s", submit_response.status_code)
            return {
                "analysisId": None,
                "statusCode": submit_response.status_code,
                "error": f"Failed to submit large file to GTI: {submit_response.text}",
            }

        analysis_id = submit_response.json().get("data", {}).get("id")
        return {"analysisId": analysis_id, "statusCode": submit_response.status_code, "error": None}
