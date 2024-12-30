# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from ._client import LogsIngestionClient as GeneratedClient


class LogsIngestionClient(GeneratedClient):
    """The asynchronous client for uploading logs to Azure Monitor.

    :param endpoint: The Data Collection Endpoint for the Data Collection Rule, for example
     https://dce-name.eastus-2.ingest.monitor.azure.com.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: Api Version. Default value is "2023-01-01". Note that overriding
     this default value may result in unsupported behavior.
    :paramtype api_version: str
    """


__all__: List[str] = ["LogsIngestionClient"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
