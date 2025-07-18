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
DOMAINTOOLS_API_BASE_URL = "api.domaintools.com"
DEFAULT_HEADERS = {"accept": "application/json", "Content-Type": "application/json"}


def do_hmac_request(uri, api_username, api_key, params=None):
    try:
        signer = DTSigner(api_username, api_key)
        timestamp = datetime.utcnow().strftime(DATE_TIME_FORMAT)

        query = {
            "api_username": api_username,
            "signature": signer.sign(timestamp, uri),
            "timestamp": timestamp,
            "app_partner": "Microsoft",
            "app_name": "Sentinel",
            "app_version": "1.0",
        }
        full_url = urlunparse(
            ("https", DOMAINTOOLS_API_BASE_URL, uri, "", urlencode(query), None)
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
        query = req.params.get("query")
        exclude_query = req.params.get("exclude_query")
        max_length = req.params.get("max_length")
        min_length = req.params.get("min_length")
        has_hyphen = req.params.get("has_hyphen")
        has_number = req.params.get("has_number")
        active_only = req.params.get("active_only")
        deleted_only = req.params.get("deleted_only")
        anchor_left = req.params.get("anchor_left")
        anchor_right = req.params.get("anchor_right")
        page = req.params.get("page")
        if not query:
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                query = req_body.get("query")
                exclude_query = req_body.get("exclude_query")
                max_length = req_body.get("max_length")
                min_length = req_body.get("min_length")
                has_hyphen = req_body.get("has_hyphen")
                has_number = req_body.get("has_number")
                active_only = req_body.get("active_only")
                deleted_only = req_body.get("deleted_only")
                anchor_left = req_body.get("anchor_left")
                anchor_right = req_body.get("anchor_right")
                page = req_body.get("page")
        params = {"query": query}
        if exclude_query:
            params["exclude_query"] = exclude_query
        if max_length:
            params["max_length"] = max_length
        if min_length:
            params["min_length"] = min_length
        if has_hyphen:
            params["has_hyphen"] = has_hyphen
        if min_length:
            params["min_length"] = min_length
        if has_number:
            params["has_number"] = has_number
        if active_only:
            params["active_only"] = active_only
        if deleted_only:
            params["deleted_only"] = deleted_only
        if anchor_left:
            params["anchor_left"] = anchor_left
        if anchor_right:
            params["anchor_right"] = anchor_right
        if page:
            params["page"] = page

        uri = "/v2/domain-search/"
        response = do_hmac_request(uri, api_username, api_key, params=params)
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
