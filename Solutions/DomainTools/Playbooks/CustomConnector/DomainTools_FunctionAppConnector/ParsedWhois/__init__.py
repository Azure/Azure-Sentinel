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


def flatten(resp):
    try:
        my_dict = {}
        for k, v in resp.items():
            if isinstance(v, list):
                # check each element list type
                if v:
                    if isinstance(v[0], str):
                        my_dict[k] = ", ".join([z for z in v])
                    elif isinstance(v[0], int):
                        my_dict[k] = ", ".join([str(z) for z in v])
                    elif isinstance(v[0], dict):
                        ss = []
                        for each in v:
                            ss.append(flatten(each))
                        my_dict[f"{k}"] = ss
                else:
                    my_dict[k] = ""
            elif isinstance(v, dict):
                rdict = flatten(v)
                if rdict:
                    for x, y in rdict.items():
                        my_dict[f"{k}_{x}"] = y
            else:
                my_dict[k] = v
        return my_dict
    except Exception as ex:
        logging.error(ex)
        return {}


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f"Resource Requested: {func.HttpRequest}")

    try:
        api_key = environ["APIKey"]
        api_username = environ["APIUsername"]
        query = req.params.get("query")
        from_playbook = req.params.get("from_playbook")
        if not query:
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                query = req_body.get("query")
                from_playbook = req_body.get("from_playbook")
        uri = f"/v1/{query}/whois/parsed/"
        response = do_hmac_request(uri, api_username, api_key)
        if from_playbook:
            output = dict()
            for k, v in flatten(response.json()["response"]).items():
                if isinstance(v, list):
                    output[k] = [
                        [{"Key": x, "Value": y} for x, y in z.items()] for z in v
                    ]
                else:
                    output[k] = v
        else:
            output = response.json()["response"]

        return func.HttpResponse(
            json.dumps(output),
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
