import json
import logging
import msal
import requests
from collections import namedtuple
from typing import List, Dict, Any
from requests.adapters import HTTPAdapter
from requests_ratelimiter import LimiterSession
from urllib3.util import Retry

# Public indicator types consumed by starter
INDICATOR_TYPES = ["ipv4", "domain"]

LumenSetup = namedtuple("LumenSetup", ["api_key", "base_url", "tries"])
MSALSetup = namedtuple("MSALSetup", ["tenant_id", "client_id", "client_secret", "workspace_id"])


class LumenSentinelUpdater:
    """Minimal uploader shared by activities (token + upload logic)."""
    def __init__(self, lumen_setup: LumenSetup, msal_setup: MSALSetup):
        self.lumen_api_key = lumen_setup.api_key
        self.lumen_base_url = lumen_setup.base_url
        self.lumen_tries = lumen_setup.tries
        self.msal_tenant_id = msal_setup.tenant_id
        self.msal_client_id = msal_setup.client_id
        self.msal_client_secret = msal_setup.client_secret
        self.msal_workspace_id = msal_setup.workspace_id
        self.limiter_session = LimiterSession(
            per_minute=95,
            limit_statuses=[429, 503]
        )
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.limiter_session.mount("http://", adapter)
        self.limiter_session.mount("https://", adapter)
        self.bearer_token = None
        self.token_expiry_seconds = None

    def get_lumen_presigned_urls(self, indicator_types: List[str]) -> Dict[str, str]:
        headers = {
            'Authorization': self.lumen_api_key,
            'Content-Type': 'application/json'
        }
        urls = {}
        for itype in indicator_types:
            url = f"{self.lumen_base_url}/{itype}"
            r = self.limiter_session.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            data = r.json()
            presigned = data.get('url')
            if not presigned:
                raise ValueError(f"No presigned URL returned for {itype}")
            urls[itype] = presigned
            logging.info(f"Got presigned URL for {itype}")
        return urls

    def acquire_token(self):
        scope = ["https://management.azure.com/.default"]
        app = msal.ConfidentialClientApplication(
            self.msal_client_id,
            authority=f"https://login.microsoftonline.com/{self.msal_tenant_id}",
            client_credential=self.msal_client_secret
        )
        result = app.acquire_token_silent(scopes=scope, account=None)
        if not result:
            result = app.acquire_token_for_client(scopes=scope)
        if 'access_token' not in result:
            raise ValueError(result.get('error_description'))
        logging.debug("Token acquired")
        return result['access_token'], result['expires_in']

    def upload_stix_objects_to_sentinel(self, token: str, stix_objects: List[Dict[str, Any]]) -> requests.Response:
        url = f"https://api.ti.sentinel.azure.com/workspaces/{self.msal_workspace_id}/threat-intelligence-stix-objects:upload"
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
        params = {'api-version': '2024-02-01-preview'}
        payload = {'sourcesystem': 'Lumen', 'stixobjects': stix_objects}
        resp = self.limiter_session.post(url, headers=headers, params=params, json=payload, timeout=30)
        return resp
