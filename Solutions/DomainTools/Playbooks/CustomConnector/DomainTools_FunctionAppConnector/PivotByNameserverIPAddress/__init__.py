import json
import logging
from datetime import datetime
from hashlib import sha256
from hmac import new
from os import environ
from urllib.parse import urlencode, urlunparse

import azure.functions as func
import requests

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
ENDPOINT = f"/v1/iris-investigate/"
DOMAINTOOLS_API_BASE_URL = "api.domaintools.com"
DEFAULT_HEADERS = {"accept": "application/json", "Content-Type": "application/json"}


def do_hmac_request(api_username, api_key, params=None):
    try:
        signer = DTSigner(api_username, api_key)
        timestamp = datetime.utcnow().strftime(DATE_TIME_FORMAT)

        query = {
            "api_username": api_username,
            "signature": signer.sign(timestamp, ENDPOINT),
            "timestamp": timestamp,
            "app_partner": "Microsoft",
            "app_name": "Sentinel",
            "app_version": "1.0",
        }
        full_url = urlunparse(
            ("https", DOMAINTOOLS_API_BASE_URL, ENDPOINT, "", urlencode(query), None)
        )
        response = requests.get(full_url, params=params, headers=DEFAULT_HEADERS)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logging.info(f"Request failed: {e}")
        return response


class DTSigner:
    def __init__(self, api_username: str, api_key: str) -> None:
        self.api_username = api_username
        self.api_key = api_key

    def sign(self, timestamp: str, uri: str) -> str:
        """
        Generates a digital signature for the given timestamp and URI.

        Args:
            timestamp (str): The timestamp to include in the signature.
            uri (str): The URI to include in the signature.

        Returns:
            str: The generated digital signature.
        """
        params = "".join([self.api_username, timestamp, uri])
        return new(
            self.api_key.encode("utf-8"), params.encode("utf-8"), digestmod=sha256
        ).hexdigest()


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f"Resource Requested: {func.HttpRequest}")

    try:
        api_key = environ["APIKey"]
        api_username = environ["APIUsername"]
        nameserver_ip = req.params.get("nameserver_ip")
        active = req.params.get("active")
        create_date = req.params.get("create_date")
        expiration_date = req.params.get("expiration_date")
        create_date_within = req.params.get("create_date_within")
        first_seen_within = req.params.get("first_seen_within")
        position = req.params.get("position")

        if not nameserver_ip:
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                nameserver_ip = req_body.get("nameserver_ip")
                active = req_body.get("active")
                create_date = req_body.get("create_date")
                expiration_date = req_body.get("expiration_date")
                create_date_within = req_body.get("create_date_within")
                first_seen_within = req_body.get("first_seen_within")
                position = req_body.get("position")

        params = {"nameserver_ip": nameserver_ip}
        if active:
            params["active"] = active
        if create_date:
            params["create_date"] = create_date
        if expiration_date:
            params["expiration_date"] = expiration_date
        if create_date_within:
            params["create_date_within"] = create_date_within
        if first_seen_within:
            params["first_seen_within"] = first_seen_within
        if position:
            params["position"] = position

        response = do_hmac_request(api_username, api_key, params)

        return func.HttpResponse(
            json.dumps(response.json()),
            headers={"Content-Type": "application/json"},
            status_code=200,
        )

    except KeyError as ke:
        logging.error(f"Invalid Settings. {ke.args} configuration is missing.")
        return func.HttpResponse(
            "Invalid Settings. Configuration is missing.", status_code=500
        )
    except Exception as ex:
        logging.error(f"Exception Occured: {str(ex)}")
        return func.HttpResponse("Internal Server Exception", status_code=500)
