import logging

from base64 import b64encode
from pathlib import PurePosixPath, PureWindowsPath

log = logging.getLogger(__name__)


class WithSecureClient:
    def __init__(
        self,
        elements_api_url,
        client_id,
        client_secret,
        engine,
        engine_group,
        rest_client,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._api_url = elements_api_url
        self._events_path = "/security-events/v1/security-events"
        self._engine = engine
        self._engine_group = engine_group
        self.rest = rest_client

    def get_events_after(self, from_date):
        token = self._authenticate()
        return self._get_events_after(token, from_date)

    def _authenticate(self):
        auth_header = b64encode(
            bytes(self._client_id + ":" + self._client_secret, "utf-8")
        ).decode("utf-8")
        headers = {
            "Content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Accept": "application/json",
            "Authorization": "Basic " + auth_header,
            "User-Agent": "sentinel-connector",
        }

        data = {"grant_type": "client_credentials", "scope": "connect.api.read"}

        header_keys_to_log = ["Content-type", "Accept", "User-Agent"]
        headers_to_log = {key: headers[key] for key in header_keys_to_log}
        log.info(
            f"Executing authorization request to Elements API... "
            f"headers={headers_to_log}, "
            f"body={data}"
        )
        response = self.rest.post(
            self._api_url + "/as/token.oauth2", data=data, headers=headers
        )
        log.info("Response headers=" + str(response.headers))

        if response.ok:
            res_body = response.json()
            return res_body["access_token"]
        else:
            log.info("Response=" + response.text)
            log.info("Transaction-id=" + response.headers.get("X-Transaction"))
            raise Exception("Authentication failed")

    def _get_events_after(self, auth_token, from_date, org_id=None):
        next_page = None
        fetch_page = True
        log.info(f"Reading events created after {from_date}")
        all_events = []
        while fetch_page:
            page = self._get_events_page(auth_token, from_date, org_id, next_page)
            next_page = page.get("nextAnchor")

            fetch_page = next_page is not None
            for event in page["items"]:
                all_events.append(SecurityEvent(**event))

        return all_events

    def _get_events_page(self, auth_token, from_date, org_id=None, next_page=None):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + auth_token,
            "User-Agent": "my-script",
        }
        log.info("engine: %s " % self._engine)
        log.info("engine_group: %s " % self._engine_group)
        if self._engine and self._engine != "default":
            engine_param = "engine"
            engine_param_value = self._engine
        elif self._engine_group and self._engine_group != "default":
            engine_param = "engineGroup"
            engine_param_value = self._engine_group
        else:
            engine_param = "engineGroup"
            engine_param_value = "epp,edr,ecp"

        data = {
            "limit": 20,
            "persistenceTimestampStart": from_date,
            "order": "asc",
            engine_param: engine_param_value,
            "exclusiveStart": "true",
        }

        if next_page:
            data["anchor"] = next_page

        if org_id:
            data["organizationId"] = org_id

        headers_to_log = dict(headers)
        headers_to_log["Authorization"] = "REDACTED"
        log.info(
            f"Reading security events after {from_date}. Request={data}, request headers={headers_to_log}"
        )
        response = self.rest.post(
            self._api_url + self._events_path, data=data, headers=headers
        )
        tx_id = response.headers.get("X-Transaction", "unknown")
        log.info(f"Elements API response. headers={response.headers}, tx-id={tx_id}")

        if not response.ok:
            log.info("Error %s", response.text)
            raise Exception("Request error")

        return response.json()


class SecurityEvent:
    def __init__(self, **kwargs):
        self.details = kwargs.get("details", {})
        self.device = kwargs.get("device", {})
        for k, v in kwargs.items():
            if not hasattr(self, k):
                setattr(self, k, v)

    def infection_name(self):
        name = self.details.get("infectionName", "")
        return self.details.get("name", name)

    def file_path(self):
        if "filePath" in self.details:
            return self.details["filePath"]
        elif "object" in self.details:
            return self.details["object"]
        else:
            return self.details.get("path", "")

    def host_name(self):
        if not self.device:
            return None
        if "name" in self.device:
            return self.device.get("name")
        elif "id" in self.device:
            return self.device.get("id")
        elif "winsAddress" in self.device:
            return self.device.get("winsAddress")
        return None

    def _file_name(self, key):
        posix = PureWindowsPath(self.details.get(key, "")).as_posix()
        return PurePosixPath(posix).name

    def process_name(self):
        return self._file_name("process")

    def file_name(self):
        return self._file_name("filePath")
