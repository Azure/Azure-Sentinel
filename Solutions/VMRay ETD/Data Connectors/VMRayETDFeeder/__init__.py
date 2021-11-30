import base64
import hmac
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import formatdate
from enum import Enum
from typing import Dict, Iterator, List, NamedTuple, Optional

import azure.functions as func
import requests


LOG_TYPE = "vmray_emails"


class Verdict(Enum):
    clean = "clean"
    suspicious = "suspicious"
    malicious = "malicious"


@dataclass
class Config:
    workspace_id: str
    workspace_key: str
    log_analytics_url: str
    vmray_platform_url: str
    vmray_api_key: str
    poll_additional_fields: List[str]
    poll_minimum_verdict: Verdict
    verify_tls: bool

    @classmethod
    def from_environ(cls) -> "Config":
        poll_additional_fields = []
        for field in os.environ["POLL_ADDITIONAL_FIELDS"].split(","):
            field = field.strip()
            if field.startswith("email_"):
                poll_additional_fields.append(field)
            else:
                logging.error(
                    "Ignoring invalid entry in POLL_ADDITIONAL_FIELDS: '%s'", field
                )

        try:
            poll_minimum_verdict = Verdict(os.environ["POLL_MINIMUM_VERDICT"])
        except ValueError:
            logging.error("POLL_MINIMUM_VERDICT value is invalid; falling back to 'clean'")
            poll_minimum_verdict = Verdict.clean

        verify_tls_env = os.environ["VERIFY_VMRAY_PLATFORM_TLS"].lower()
        try:
            verify_tls = {"true": True, "false": False}[verify_tls_env]
        except KeyError:
            logging.error("VERIFY_VMRAY_PLATFORM_TLS value is invalid; defaulting to 'true'")
            verify_tls = True

        return cls(
            workspace_id=os.environ["WORKSPACE_ID"],
            workspace_key=os.environ["WORKSPACE_KEY"],
            log_analytics_url=os.environ["LOG_ANALYTICS_URL"],
            vmray_platform_url=os.environ["VMRAY_PLATFORM_URL"],
            vmray_api_key=os.environ["VMRAY_API_KEY"],
            poll_additional_fields=poll_additional_fields,
            poll_minimum_verdict=poll_minimum_verdict,
            verify_tls=verify_tls,
        )


@dataclass
class State:
    last_poll: datetime

    @classmethod
    def load(cls, raw: str) -> "State":
        dict_ = json.loads(raw)
        return cls(
            last_poll=datetime.fromisoformat(dict_["last_poll"]),
        )

    def dump(self) -> str:
        dict_ = {
            "last_poll": self.last_poll.isoformat(),
        }
        return json.dumps(dict_)


class APIError(Exception):
    @classmethod
    def expected(cls, code: int, message: str) -> "APIError":
        return cls(f"({code}) {message}")

    @classmethod
    def unexpected(cls, resp: requests.Response) -> "APIError":
        return cls(f"Unexpected error: ({resp.status_code}) {resp.text}")


class FeederError(Exception):
    pass


EmailInfo = Dict[str, object]


REQUIRED_API_FIELDS = [
    "email_vmray_uuid",
    "email_message_id",
    "email_sent",
    "email_received",
    "email_sensor_id",
    "email_verdict",
    "email_verdict_reached",
    "email_webif_url",
]


class Feeder:
    def __init__(self, config: Config, state: State):
        self.config = config
        self.state = state

    @property
    def api_url(self) -> str:
        return f"{self.config.vmray_platform_url}/rest"

    @property
    def auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"api_key {self.config.vmray_api_key}"}

    def feed(self) -> None:
        """
        Feed email data fetched from the ETD API into Log Analytics.

        We feed the data in batches to limit our memory usage and to
        ensure the requests to the Log Analytics API don't become too
        large.
        """

        poll_from = self.state.last_poll
        poll_until = datetime.now(tz=timezone.utc)
        logging.info("Polling from %s until %s", poll_from, poll_until)

        batches_iter = self.poll_etd(poll_from, poll_until)
        count = 0
        while True:
            try:
                batch = next(batches_iter)
            except (requests.RequestException, APIError) as exc:
                raise FeederError(f"Error polling from VMRay ETD: {exc}")
            except StopIteration:
                break

            try:
                self.push_to_log_analytics(batch)
            except (requests.RequestException, APIError) as exc:
                raise FeederError(f"Error pushing to Log Analytics: {exc}")

            count += len(batch)

        logging.info("Pushed %d emails", count)
        self.state.last_poll = poll_until

    def poll_etd(self, start: datetime, end: datetime) -> Iterator[List[EmailInfo]]:
        time_fmt = "%Y-%m-%dT%H:%M:%S.%f"
        poll_interval = f"{start.strftime(time_fmt)}~{end.strftime(time_fmt)}"

        fields = REQUIRED_API_FIELDS + self.config.poll_additional_fields
        fields_spec = "(" + ",".join(fields) + ")"

        fixed_params = {
            "email_verdict_reached": poll_interval,
            "_fields": fields_spec,
        }

        verdict_filters_map: Dict[Verdict, List[Optional[str]]] = {
            Verdict.clean: [None],
            Verdict.suspicious: ["suspicious", "malicious"],
            Verdict.malicious: ["malicious"],
        }
        verdict_filters = verdict_filters_map[self.config.poll_minimum_verdict]

        for verdict in verdict_filters:
            if verdict:
                params = {"email_verdict": verdict, **fixed_params}
            else:
                params = fixed_params

            yield from (b for b in self.poll_etd_with_params(params) if b)

    def poll_etd_with_params(self, params: Dict[str, str]) -> Iterator[List[EmailInfo]]:
        resp = requests.get(
            url=f"{self.api_url}/email",
            headers=self.auth_headers,
            params=params,
            verify=self.config.verify_tls,
        )
        etd_resp = extract_etd_response(resp)
        yield etd_resp.emails

        while etd_resp.continuation_id:
            resp = requests.get(
                url=f"{self.api_url}/continuation/{etd_resp.continuation_id}",
                headers=self.auth_headers,
                verify=self.config.verify_tls,
            )
            etd_resp = extract_etd_response(resp)
            yield etd_resp.emails

    def push_to_log_analytics(self, email_data: List[EmailInfo]) -> None:
        method = "POST"
        resource = "/api/logs"
        content_type = "application/json"
        data = json.dumps(email_data)
        content_length = len(data)
        x_ms_date = formatdate(usegmt=True)

        def build_signature() -> str:
            string_to_sign = "\n".join(
                [
                    method,
                    str(content_length),
                    content_type,
                    f"x-ms-date:{x_ms_date}",
                    resource,
                ]
            )
            bytes_to_sign = string_to_sign.encode("utf-8")
            key = base64.b64decode(self.config.workspace_key)
            mac = hmac.digest(key, bytes_to_sign, "sha256")
            signature = base64.b64encode(mac).decode()
            return signature

        signature = build_signature()
        shared_key = f"{self.config.workspace_id}:{signature}"

        resp = requests.request(
            method=method,
            url=f"{self.config.log_analytics_url}{resource}",
            params={"api-version": "2016-04-01"},
            headers={
                "Authorization": f"SharedKey {shared_key}",
                "Content-Type": content_type,
                "Log-Type": LOG_TYPE,
                "x-ms-date": x_ms_date,
                "time-generated-field": "email_verdict_reached",
            },
            data=data,
        )

        success = 200 <= resp.status_code < 300
        if not success:
            raise APIError.unexpected(resp)


class ETDResponse(NamedTuple):
    emails: List[EmailInfo]
    continuation_id: Optional[int]


def extract_etd_response(resp: requests.Response) -> ETDResponse:
    try:
        resp_json = resp.json()
        result = resp_json["result"]
        if result == "ok":
            emails = resp_json["data"]
            continuation_id = resp_json.get("continuation_id")
        else:
            error_msg = resp_json["error_msg"]
            raise APIError.expected(resp.status_code, error_msg)

    except (ValueError, KeyError):
        raise APIError.unexpected(resp)

    return ETDResponse(emails, continuation_id)


def main(timer: func.TimerRequest, state: func.InputStream) -> str:
    if state:
        decoded = state.read().decode()
        state_ = State.load(decoded)
    else:
        now = datetime.now(tz=timezone.utc)
        state_ = State(
            last_poll=now - timedelta(minutes=10),
        )

    config = Config.from_environ()

    try:
        feeder = Feeder(config, state_)
        feeder.feed()
    except FeederError as exc:
        logging.error("%s", exc)
        raise

    return feeder.state.dump()
