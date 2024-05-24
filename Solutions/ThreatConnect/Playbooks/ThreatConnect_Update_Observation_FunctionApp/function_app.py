import logging

import azure.functions as func
from azure.functions.decorators.core import AuthLevel
from azure.functions.decorators.http import HttpMethod
from requests import Response
from requests.exceptions import HTTPError

from hmac_auth import HmacAuth
from tc_session import TcSession

required_variables = [
    "tc_base_url",
    "tc_api_access_id",
    "tc_api_secret_key",
    "data",
]

# mapping from Azure Sentinel Entity information to TC Indicator.
# key is lowercase Azure `kind`
# value is dict with `name` key corresponding to TC `type`, and other key/value pairs
# map from key in Azure Entity `properties` to TC key
indicator_type_map = {
    "ip": {
        "_meta": {
            "name": "Address",
            "summary_key": "address",
        },
        "address": "ip",
    },
    "url": {
        "_meta": {
            "name": "URL",
            "summary_key": "url",
        },
        "url": "text",
    },
    "filehash": {
        "_meta": {
            "name": "File",
            "summary_key": "value",
        },
        # filehash is different; logic will be done in the function
    },
    "dns": {
        "_meta": {
            "name": "Host",
            "summary_key": "domainName",
        },
        "domainName": "hostName",
    },
    "network-traffic": {
        "_meta": {
            "name": "TODO",
            "summary_key": "TODO",
        },
        # TODO: what are the properties?
    },
}

app = func.FunctionApp()


def get_api_branch_for_indicator_type(indicator_type: str, session: TcSession) -> str:
    """Return the API branch for the given indicator type."""
    response = session.get("/api/v2/types/indicatorTypes")
    response.raise_for_status()
    indicator_types = (
        response.json().get("data", {}).get("indicatorType", [])
    )  # skipping error checking
    indicator_type = [i for i in indicator_types if i.get("name") == indicator_type][0]
    return indicator_type.get("apiBranch")


def get_or_create_indicator(entity_data: dict, session: TcSession) -> list:
    entity_kind = entity_data["kind"].lower()
    summary_key = indicator_type_map[entity_kind]["_meta"]["summary_key"]
    summary = entity_data["properties"][summary_key]
    indicators = get_indicators(summary, session)
    if len(indicators) == 0:
        # create an indicator
        indicator = map_indicator(entity_data)
        indicator = create_indicator(indicator, session)
        indicators = [indicator]
    return indicators


def get_indicators(summary: str, session: TcSession):
    """Get a ThreatConnect indicator object by its value."""
    tc_api_endpoint = "/api/v3/indicators/"
    response = session.get(url=tc_api_endpoint, params={"tql": f'summary = "{summary}"'})
    indicators = response.json().get("data")
    return indicators


def update_observation(indicators: dict, session: TcSession) -> Response | None:
    # get the api branch for the indicator type (use the first result since they'll all be the same type)
    api_branch = get_api_branch_for_indicator_type(indicators[0].get("type"), session)

    # iterate over each owner, b/c the api account might not have permissions to write observations to
    # to all owners.  This is ok b/c observations are pooled across owners.
    for indicator in indicators:
        owner = indicator.get("ownerName")
        response = session.post(
            f'/api/v2/indicators/{api_branch}/{indicator.get("summary")}/observations',
            params={"owner": owner},
            json={
                "count": 1,
            },
        )
        try:
            response.raise_for_status()
        except HTTPError:
            continue  # we don't have write access to this owner, so try the next one
        else:
            return response  # we were able to write an observation, so we're done
    return None


def create_indicator(indicator: dict, session: TcSession) -> dict:
    """Create a ThreatConnect indicator object by its value."""
    tc_api_endpoint = "/api/v3/indicators"
    response = session.post(url=tc_api_endpoint, json=indicator)
    # raise Exception(indicator)
    response.raise_for_status()
    indicator = response.json().get("data")
    return indicator


def map_indicator(entity_data: dict) -> dict:
    entity_kind = entity_data["kind"].lower()
    indicator_data = {
        "type": indicator_type_map[entity_kind]["_meta"]["name"],
    }

    if entity_kind == "filehash":
        algorithm = entity_data["properites"]["algorithm"].lower()
        if algorithm == "unknown" or algorithm == "sha256ac":
            raise ValueError('Invalid hash algorithm. Must be one of ["md5", "sha1", "sha256"]')
        indicator_data[algorithm] = entity_data["properties"]["value"]
        return indicator_data

    for entity_key, indicator_key in indicator_type_map[entity_kind].items():
        # print(entity_key)
        if entity_key == "_meta":
            continue
        indicator_data[indicator_key] = entity_data["properties"][entity_key]

    return indicator_data


# TODO: write observations (call method i think)
@app.function_name(name="update_observation")
@app.route(
    route="",
    auth_level=AuthLevel.ANONYMOUS,
    methods=[HttpMethod.POST],
)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    # validate input
    try:
        req_body = req.get_json()
        for variable in required_variables:
            if req_body.get(variable) is None:
                raise TypeError(f"Missing {variable}.")

        tc_base_url = req_body.get("tc_base_url")
        tc_api_access_id = req_body.get("tc_api_access_id")
        tc_api_secret_key = req_body.get("tc_api_secret_key")
        entity_data = req_body.get("data")
        if entity_data["kind"].lower() not in indicator_type_map:
            return func.HttpResponse(
                body=f"Indicator kind must be one of {list(indicator_type_map.keys())}.",
                status_code=422,
            )
    except (TypeError, ValueError) as e:
        return func.HttpResponse(body=str(e), status_code=400)

    # map indicator data
    # indicator_data = map_indicator(entity_data)
    # update_observation(indicators, session)
    # get_indicators(indicator_data["summary_key"], session)

    session = TcSession(
        HmacAuth(tc_api_access_id, tc_api_secret_key),
        base_url=tc_base_url,
        verify=False,
    )
    try:
        indicators = get_or_create_indicator(entity_data, session)
    except ValueError as e:
        return func.HttpResponse(body=str(e), status_code=400)
    observation = update_observation(indicators, session)
    return func.HttpResponse(
        body=observation.content,
        status_code=observation.status_code,
    )
