"""This __init__ file will be called once the trigger is generated."""

import datetime
import logging
import azure.functions as func
import base64
import hashlib
import hmac
import json
import os
import time
import requests
from .state_manager import StateManager
from .exports_store import ExportsTableStore
from Exceptions.ArmisExceptions import (
    ArmisException,
    ArmisDataNotFoundException,
    ArmisTimeOutException,
)


API_KEY = os.environ["ArmisSecretKey"]
url = os.environ["ArmisURL"]
connection_string = os.environ["AzureWebJobsStorage"]
customer_id = os.environ["WorkspaceID"]
shared_key = os.environ["WorkspaceKey"]
armis_devices_table_name = os.environ["ArmisDeviceTableName"]

HTTP_ERRORS = {
    400: "Armis Device Connector: Bad request: Missing aql parameter.",
    401: "Armis Device Connector: Authentication error: Authorization information is missing or invalid."
}
ERROR_MESSAGES = {
    "ACCESS_TOKEN_NOT_FOUND": "Armis Device Connector: Access token not found. please check Key.",
    "HOST_CONNECTION_ERROR": "Armis Device Connector: Invalid host while verifying 'armis account'."
}

CHECKPOINT_TABLE_NAME = "ArmisDeviceCheckpoint"

PAGE_SIZE = 1000
MAX_RETRY = 5
FUNCTION_APP_TIMEOUT_SECONDS = 570
body = ""


class ArmisDevice:
    """This class will process the Device data and post it into the Microsoft sentinel."""

    def __init__(self, start_time):
        """__init__ method will initialize object of class."""
        self.start_time = start_time
        self._link = url
        self._header = {}
        self._secret_key = API_KEY
        self._data_device_from = 0
        self.last_seen = None
        self.logs_starts_with = "Armis Device Connector"

    def _get_access_token_device(self, armis_link_suffix):
        """
        _get_access_token_device will fetch the access token using api and set it in header for further use.

        Args:
            armis_link_suffix (String): This variable will be suffix/add-on to the link.

        """
        if self._secret_key is not None and self._link is not None:
            body = {"secret_key": self._secret_key}
            try:
                response = requests.post((self._link + armis_link_suffix), data=body)
                if response.status_code == 200:
                    logging.info("{}: Getting access token.".format(self.logs_starts_with))
                    response = response.json()
                    _access_token = response.get("data", {}).get("access_token")
                    self._header.update({"Authorization": _access_token})
                elif response.status_code == 400:
                    raise ArmisException(
                        "{}: Please check either armis URL or armis secret key is wrong.".format(self.logs_starts_with)
                    )
                else:
                    raise ArmisException(
                        "{}: Error while generating the access token. Code: {} Message: {}.".format(
                            self.logs_starts_with, response.status_code, response.text
                        )
                    )
            except ArmisException as err:
                logging.error(err)
                raise ArmisException(
                    "{}: Error while generating the access token.".format(self.logs_starts_with)
                )
        else:
            raise ArmisException(
                "{}: The secret key or link has not been initialized.".format(self.logs_starts_with)
            )

    def validate_timestamp(self, last_seen_time):
        """function is used to validate the timestamp format. The timestamp should be in
        ISO 8601 format 'YYYY-MM-DDTHH:MM:SS'. If the timestamp is not in correct format, it will
        be formatted according to the given timestamp format.

        Args:
            last_seen_time (String): Timestamp string to be validated.

        Returns:
            String: Validated timestamp string.
        """
        try:
            if len(last_seen_time) != 19:
                if len(last_seen_time) == 10:
                    last_seen_time += "T00:00:00"
                    logging.info(
                        "{}: 'T:00:00:00' added as only date is available.".format(self.logs_starts_with)
                    )
                else:
                    splited_time = last_seen_time.split("T")
                    if len(splited_time[1]) == 5:
                        splited_time[1] += ":00"
                        logging.info(
                            "{}: ':00' added as seconds not available.".format(self.logs_starts_with)
                        )
                    elif len(splited_time[1]) == 2:
                        splited_time[1] += ":00:00"
                        logging.info(
                            "{}: ':00:00' added as only hour is available.".format(self.logs_starts_with)
                        )
                    last_seen_time = "T".join(splited_time)
            return last_seen_time
        except Exception as err:
            logging.error("{}: Error occurred: {}".format(self.logs_starts_with, err))
            raise ArmisException(err)

    def _get_device_data(self, armis_link_suffix, parameter):
        """Get_device_data is used to get data using api.

        Args:
            self: Armis object.
            armis_link_suffix (String): will be containing the other part of link.
            parameter (json): will contain the json data to sends to parameter to get data from REST API.

        """
        try:
            for i in range(MAX_RETRY + 1):
                response = requests.get(
                    (self._link + armis_link_suffix),
                    params=parameter,
                    headers=self._header,
                )
                if response.status_code == 200:
                    logging.info("{}: Status Code : 200".format(self.logs_starts_with))
                    results = response.json()

                    if results["data"]["count"] == 0:
                        raise ArmisDataNotFoundException(
                            "{}: Data not found.".format(self.logs_starts_with)
                        )

                    if (
                        "data" in results
                        and "results" in results["data"]
                        and "total" in results["data"]
                        and "count" in results["data"]
                        and "next" in results["data"]
                    ):
                        total_data_length = results["data"]["total"]
                        count_per_frame_data = results["data"]["count"]
                        data = results["data"]["results"]

                        for i in data:
                            i["armis_device_time"] = i["lastSeen"]

                        self._data_device_from = results["data"]["next"]
                        last_seen_time = data[-1]["lastSeen"][:19]
                        last_seen_time = self.validate_timestamp(last_seen_time)

                        logging.info(
                            "{}: Updated last_seen to: {} for next API call.".format(
                                self.logs_starts_with, last_seen_time
                            )
                        )

                        return (
                            data,
                            last_seen_time,
                            total_data_length,
                            count_per_frame_data,
                        )
                    else:
                        raise ArmisException(
                            "{}: There are no proper keys in data."
                        )

                elif response.status_code == 400:
                    logging.error(
                        "{}: Status Code : 400, Error: {}".format(
                            self.logs_starts_with, HTTP_ERRORS[400]
                        )
                    )
                    raise ArmisException(HTTP_ERRORS[400])

                elif response.status_code == 401:
                    logging.info(
                        "{}: Retry number: {}".format(self.logs_starts_with, str(i + 1))
                    )
                    logging.error(
                        "{}: Status Code : 401, Error: {}".format(
                            self.logs_starts_with, HTTP_ERRORS[401]
                        )
                    )
                    self._get_access_token_device("/access_token/")
                    continue
                else:
                    raise ArmisException(
                        "{}: Error while fetching data. status Code:{} error message:{}.".format(
                            self.logs_starts_with, response.status_code, response.text
                        )
                    )
            logging.error("{}: Max retry reached.".format(self.logs_starts_with))
            raise ArmisException("{}: Max retry reached.".format(self.logs_starts_with))

        except requests.exceptions.ConnectionError:
            logging.error(ERROR_MESSAGES["HOST_CONNECTION_ERROR"])
            raise ArmisException(
                "{}: Connection error while getting data from device api.".format(self.logs_starts_with)
            )

        except requests.exceptions.RequestException as request_err:
            logging.error(request_err)
            raise ArmisException(
                "{}: Request error while getting data from Device api.".format(self.logs_starts_with)
            )

        except ArmisException as err:
            logging.error(err)
            raise ArmisException(
                "{}: Error while getting data from device api.".format(self.logs_starts_with)
            )

        except ArmisDataNotFoundException as err:
            logging.info(err)
            raise ArmisDataNotFoundException()

    def _fetch_device_data(
        self,
        checkpoint_table_object: ExportsTableStore,
        table_name,
        last_seen_not_available
    ):
        """Fetch_device_data is used to push all the data into table.

        Args:
            checkpoint_table_object (object): Azure Storage table object.
            table_name (String): table name to store the data in microsoft sentinel.
            last_seen_not_available (bool): it is a flag that contains the value if last seen exists or not.
        """
        try:
            if last_seen_not_available:
                aql_data = "in:devices"
            else:
                aql_data = "in:devices after:{}".format(self.last_seen)
            logging.info("{}: aql query: {}".format(self.logs_starts_with, aql_data))
            self._get_access_token_device("/access_token/")

            azuresentinel = AzureSentinel()
            parameter_device = {
                "aql": aql_data,
                "orderBy": "lastSeen",
                "length": PAGE_SIZE,
                "from": 0
            }
            while self._data_device_from is not None:
                if int(time.time()) >= self.start_time + FUNCTION_APP_TIMEOUT_SECONDS:
                    raise ArmisTimeOutException()
                (
                    data,
                    last_seen_time,
                    total_data_length,
                    count_per_frame_data,
                ) = self._get_device_data("/search/", parameter_device)
                logging.info(
                    "{}: Total length of data is {}.".format(self.logs_starts_with, total_data_length)
                )
                if total_data_length < PAGE_SIZE:
                    logging.info(
                        "{}: Last page is not ready due to delay of data in Armis"
                        ", Hence Stopping Execution. "
                        "Last Page Details - lastSeen: {}, Total Records: {}, Count: {}"
                        ".".format(self.logs_starts_with, last_seen_time, total_data_length, count_per_frame_data)
                    )
                    break
                azuresentinel.post_data(customer_id, json.dumps(data), table_name)
                logging.info(
                    "{}: Collected: {} device data and ingested into sentinel with table name: {}.".format(
                        self.logs_starts_with, count_per_frame_data, table_name
                    )
                )
                last_seen_time = datetime.datetime.strptime(
                    last_seen_time, "%Y-%m-%dT%H:%M:%S"
                )
                last_seen_time = last_seen_time.strftime("%Y-%m-%dT%H:%M:%S")
                self.last_seen = last_seen_time
                checkpoint_table_object.merge(
                    "armisdevice",
                    "devicecheckpoint",
                    {"last_seen": self.last_seen}
                )
                logging.info(
                    "{}: Updated last_seen to '{}' in Checkpoint table".format(
                        self.logs_starts_with, last_seen_time
                    )
                )

                parameter_device.update({"aql": "in:devices after:{}".format(self.last_seen)})
                logging.info(
                    "{}: Updated aql query: {}.".format(self.logs_starts_with, parameter_device["aql"])
                )

            logging.info(
                "{}: Data collection and ingestion is completed till last_seen: {}".format(
                    self.logs_starts_with, self.last_seen
                )
            )

        except ArmisException as err:
            logging.error(err)
            raise ArmisException(
                "{}: Error while processing the data.".format(self.logs_starts_with)
            )
        except ArmisTimeOutException:
            raise ArmisTimeOutException()
        except ArmisDataNotFoundException:
            raise ArmisDataNotFoundException()

    def check_data_exists_or_not_device(self):
        """Check_data_exists_or_not is to check if the data is exists or not using the timestamp file.

        Args:
            self: Armis object.

        """

        try:
            self.state_devices = StateManager(
                connection_string=connection_string, file_path="funcarmisdevicesfile"
            )
            checkpoint_table_obj = ExportsTableStore(
                connection_string=connection_string, table_name=CHECKPOINT_TABLE_NAME
            )
            last_time_devices = self.state_devices.get()

            if last_time_devices is not None:
                self.last_seen = last_time_devices
                logging.info(
                    "{}: The checkpoint file is available in device endpoint file share.".format(self.logs_starts_with)
                )
                logging.info(
                    "{}: Last timestamp stored in file for devices: {}".format(
                        self.logs_starts_with, self.last_seen
                    )
                )
                logging.info("{}: Creating Checkpoint table.".format(self.logs_starts_with))
                checkpoint_table_obj.create()

                logging.info(
                    "{}: Storing value in Checkpoint table - last_seen: {}".format(
                        self.logs_starts_with, self.last_seen
                    )
                )
                checkpoint_table_obj.merge(
                    "armisdevice",
                    "devicecheckpoint",
                    {"last_seen": self.last_seen}
                )
                self.state_devices.delete()
                logging.info(
                    "{}: Checkpoint file deleted from fileshare.".format(self.logs_starts_with)
                )
                self._fetch_device_data(
                    checkpoint_table_obj,
                    armis_devices_table_name,
                    False
                )
                return

            # last_time_devices is None
            is_last_seen_not_available = False
            record = checkpoint_table_obj.get("armisdevice", "devicecheckpoint")
            if not record:
                # first iteration and start from the beginning
                logging.info("{}: Creating Checkpoint table.".format(self.logs_starts_with))
                checkpoint_table_obj.create()
                checkpoint_table_obj.post(
                    "armisdevice", "devicecheckpoint", {"last_seen": None}
                )
                is_last_seen_not_available = True
            else:
                logging.info(
                    "{}: Fetching Entity from Checkpoint table: {}".format(
                        self.logs_starts_with, CHECKPOINT_TABLE_NAME
                    )
                )
                self.last_seen = record.get("last_seen")
                offset = record.get("offset")
                if offset or offset == 0:
                    logging.info(
                        "{}: Removing the offset from checkpoint.".format(
                            self.logs_starts_with
                        )
                    )
                    checkpoint_table_obj.upsert(
                        "armisdevice",
                        "devicecheckpoint",
                        {"last_seen": self.last_seen, "offset": None}
                    )
                logging.info(
                    "{}: last_seen: {} is available in Checkpoint Table.".format(
                        self.logs_starts_with, self.last_seen
                    )
                )
                if not self.last_seen:
                    logging.info(
                        "{}: last_seen value not available in checkpoint table.".format(self.logs_starts_with)
                    )
                    is_last_seen_not_available = True
                else:
                    logging.info(
                        "{}: last_seen value is available in checkpoint table.".format(self.logs_starts_with)
                    )
            self._fetch_device_data(
                checkpoint_table_obj,
                armis_devices_table_name,
                is_last_seen_not_available
            )

        except ArmisTimeOutException:
            logging.info(
                "{}: 9:30 mins executed hence stopping the execution.".format(self.logs_starts_with)
            )
            return
        except ArmisException as err:
            logging.error(err)
            raise ArmisException(
                "{}: Error occured during checking whether log table exist or not.".format(self.logs_starts_with)
            )

        except ArmisDataNotFoundException:
            raise ArmisDataNotFoundException()


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
        string_to_hash = (
            method
            + "\n"
            + str(content_length)
            + "\n"
            + content_type
            + "\n"
            + x_headers
            + "\n"
            + resource
        )
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
        ).decode()
        authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
        return authorization

    # Build and send a request to the POST API
    def post_data(self, customer_id, body, log_type):
        """Build and send a request to the POST API."""
        method = "POST"
        content_type = "application/json"
        resource = "/api/logs"
        rfc1123date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        content_length = len(body)
        try:
            signature = self.build_signature(
                rfc1123date,
                content_length,
                method,
                content_type,
                resource,
            )
        except ArmisException as err:
            logging.error("Armis Device Connector: Error occured: {}".format(err))
            raise ArmisException(
                "Armis Device Connector: Error while generating signature for log analytics."
            )

        uri = (
            "https://"
            + customer_id
            + ".ods.opinsights.azure.com"
            + resource
            + "?api-version=2016-04-01"
        )

        headers = {
            "content-type": content_type,
            "Authorization": signature,
            "Log-Type": log_type,
            "x-ms-date": rfc1123date
        }
        try:
            response = requests.post(uri, data=body, headers=headers)
            if response.status_code >= 200 and response.status_code <= 299:
                logging.info(
                    "Armis Device Connector: Data posted successfully to microsoft sentinel."
                )
            else:
                raise ArmisException(
                    "Armis Device Connector: Response code: {} from posting data to log analytics.".format(
                        response.status_code
                    )
                )

        except ArmisException as err:
            logging.error(err)
            raise ArmisException(
                "Armis Device Connector: Error while posting data to microsoft sentinel."
            )


def main(mytimer: func.TimerRequest) -> None:
    """
    Start the execution.

    Args:
        mytimer (func.TimerRequest): This variable will be used to trigger the function.

    """
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    logging.info(
        "Armis Device Connector: Python timer trigger function ran at {}.".format(utc_timestamp)
    )
    start_time = time.time()
    armis_obj = ArmisDevice(start_time)
    try:
        armis_obj.check_data_exists_or_not_device()
    except ArmisDataNotFoundException:
        pass

    utc_timestamp_final = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    logging.info(
        "Armis Device Connector: execution completed for device at {}.".format(utc_timestamp_final)
    )
    if mytimer.past_due:
        logging.info("Armis Device Connector: The timer is past due!")
