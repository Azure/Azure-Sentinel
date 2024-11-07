
import logging
import requests
from urllib.parse import urlparse
import azure.functions as func
import os
import json

management_url = os.environ.get('CP_MGMT_API') # must end in /
hostname = urlparse(management_url).hostname
verify = False


def main(req):
    logging.info('Python HTTP trigger function processed a request.')
    logging.info(f"Check Point Management API: {management_url}")

    # Check that we are only using POST or GET
    if (req.method != "POST") and (req.method != "GET"):
        return func.HttpResponse(
            "Method Not Allowed",
            status_code=405
        )

    # Copy the headers from the original request
    headers = dict(req.headers)
    headers["Host"] = hostname
    # Debugging
    logging.info('{}\n{}\n{}\n'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items())
    ))
    logging.info(f"Route params: {req.route_params}")
    # Get the path to add to the request
    path = req.route_params.get("path")
    logging.info(f"Request path: {path}")
    url = management_url + path


    # Create the proxy request for GET
    if (req.method == "GET"):
        r = requests.request(
            headers=headers,
            verify=verify,
            url=url,
            method="GET"
        )
        logging.info(r.headers)
        return func.HttpResponse(r.content)

    # Create the proxy request for POST 
    if (req.method == "POST"):
        r = requests.request(
            data=req.get_body(),
            headers=headers,
            verify=verify,
            url=url,
            method="POST"
        )

        return func.HttpResponse(r.content)


    return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
        )
