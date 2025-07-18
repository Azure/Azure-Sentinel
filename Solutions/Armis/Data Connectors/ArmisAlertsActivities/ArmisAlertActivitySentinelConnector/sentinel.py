"""Module for Sentinel utility."""

import inspect
import base64
import hashlib
import hmac
import logging
import datetime
import requests
from Exceptions.ArmisExceptions import ArmisException
from . import consts

customer_id = consts.WORKSPACE_ID
shared_key = consts.WORKSPACE_KEY


class AzureSentinel:
    """AzureSentinel is Used to post data to log analytics."""

    def build_signature(
        self,
        date,
        content_length,
        method,
        content_type,
        resource,
    ):
        """To build the signature."""
        x_headers = "x-ms-date:" + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
        ).decode()
        authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
        return authorization

    # Build and send a request to the POST API
    def post_data(self, body, log_type, timestamp):
        """Build and send a request to the POST API."""
        method = "POST"
        content_type = "application/json"
        resource = "/api/logs"
        rfc1123date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        content_length = len(body)
        timestamp_date = timestamp
        __method_name = inspect.currentframe().f_code.co_name
        try:
            signature = self.build_signature(
                rfc1123date,
                content_length,
                method,
                content_type,
                resource,
            )
            uri = "https://" + customer_id + ".ods.opinsights.azure.com" + resource + "?api-version=2016-04-01"

            headers = {
                "content-type": content_type,
                "Authorization": signature,
                "Log-Type": log_type,
                "x-ms-date": rfc1123date,
                "time-generated-field": timestamp_date,
            }

            response = requests.post(uri, data=body, headers=headers, timeout=consts.REQUEST_TIMEOUT)
            if response.status_code >= 200 and response.status_code <= 299:
                logging.info(consts.LOG_FORMAT.format(__method_name, "Data posted successfully to microsoft sentinel."))
            elif response.status_code == 400:
                logging.error(
                    consts.LOG_FORMAT.format(
                        __method_name, "Bad Request = {}, Status code : {}.".format(response.text, response.status_code)
                    )
                )
                raise ArmisException()
            elif response.status_code == 403:
                logging.error(
                    consts.LOG_FORMAT.format(__method_name, "Forbidden, Status code : {}.".format(response.status_code))
                )
                raise ArmisException()
            elif response.status_code == 404:
                logging.error(
                    consts.LOG_FORMAT.format(
                        __method_name, "Request Not Found , Status code : {}.".format(response.status_code)
                    )
                )
                raise ArmisException()
            elif response.status_code == 429:
                logging.error(
                    consts.LOG_FORMAT.format(
                        __method_name,
                        "Too Many Requests, Status code : {}.".format(response.status_code),
                    )
                )
                raise ArmisException()
            elif response.status_code == 500:
                logging.error(
                    consts.LOG_FORMAT.format(
                        __method_name,
                        "Internal Server Error, Status code : {}.".format(response.status_code),
                    )
                )
                raise ArmisException()
            elif response.status_code == 503:
                logging.error(
                    consts.LOG_FORMAT.format(
                        __method_name,
                        "Service Unavailable, Status code : {}.".format(response.status_code),
                    )
                )
                raise ArmisException()
            else:
                logging.error(
                    consts.LOG_FORMAT.format(
                        __method_name,
                        "Error while posting data to microsoft sentinel Response code: {}.".format(
                            response.status_code
                        ),
                    )
                )
                raise ArmisException()
        except requests.ConnectionError as err:
            logging.error(
                consts.LOG_FORMAT.format(
                    __method_name,
                    "Connection Error while posting data to microsoft sentinel : {}.".format(err),
                )
            )
            raise ArmisException()
        except requests.HTTPError as err:
            logging.error(
                consts.LOG_FORMAT.format(
                    __method_name,
                    "HTTP Error while posting data to microsoft sentinel : {}.".format(err),
                )
            )
            raise ArmisException()
        except requests.Timeout as err:
            logging.error(
                consts.LOG_FORMAT.format(
                    __method_name,
                    "Timeout Error while posting data to microsoft sentinel : {}.".format(err),
                )
            )
            raise ArmisException()
        except requests.exceptions.InvalidURL as err:
            logging.error(
                consts.LOG_FORMAT.format(
                    __method_name,
                    "Invalid URL Error while posting data to microsoft sentinel : {}.".format(err),
                )
            )
            raise ArmisException()
        except ArmisException:
            raise ArmisException()
        except Exception as err:
            logging.error(
                consts.LOG_FORMAT.format(
                    __method_name, "Error while posting data to microsoft sentinel : {}.".format(err)
                )
            )
            raise ArmisException()
