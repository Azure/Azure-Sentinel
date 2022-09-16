"""This __init__ file will be called once data is generated in webhook and it creates trigger."""
import json
import logging
import os
from datetime import datetime

from ..shared_code.AzureSentinel import AzureSentinel
from ..shared_code.RubrikException import RubrikException

import azure.functions as func

# fetch data from os environment
sentinel_log_type = os.environ.get("Anomalies_table_name")


def main(request: func.HttpRequest) -> func.HttpResponse:
    """
    Start the execution.

    Args:
        request (func.HttpRequest): To get data from request body pushed by webhook

    Returns:
        func.HttpResponse: Status of Http request process (successful/failed).
    """
    logging.info("RubrikAnomalyEvent({}): Start processing...".format(datetime.now()))
    try:
        logging.info("({}): Start getting data.".format(datetime.now()))
        webhook_data = request.get_json()
        logging.info("({}): Got data Successfully.".format(datetime.now()))
    except ValueError as value_error:
        logging.error("Value Error in RubrikAnomalyEvent: {}".format(value_error))
        return func.HttpResponse(
            "Value Error - RubrikAnomalyEvent: {}".format(value_error)
        )
    except Exception as error:
        logging.error("Error in RubrikAnomalyEvent: {}".format(error))
        return func.HttpResponse("Error in RubrikAnomalyEvent: {}".format(error))
    else:
        if webhook_data:
            body = json.dumps(webhook_data)
            logging.info("Got data of Anomaly event via webhook.")
            try:
                logging.info(
                    "({}) Try to post the webhook data from AnomalyEvent.".format(
                        datetime.now()
                    )
                )
                azuresentinel = AzureSentinel()
                status_code = azuresentinel.post_data(
                    body,
                    sentinel_log_type,
                )
            except RubrikException as error:
                logging.error(error)
                return func.HttpResponse(error)
            else:
                if status_code >= 200 and status_code <= 299:
                    return func.HttpResponse(
                        "Data posted successfully to log analytics from RubrikAnomalyEvent."
                    )
                return func.HttpResponse(
                    "Failed to post data from RubrikAnomalyEvent into sentinel."
                )
        else:
            logging.info("No required data found.")
            return func.HttpResponse("No required data found for this trigger.")
