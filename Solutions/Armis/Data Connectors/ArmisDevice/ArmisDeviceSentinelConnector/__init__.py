"""This __init__ file will be called once the trigger is generated."""
import datetime
import logging
import azure.functions as func
import base64
import hashlib
import hmac
import json
import os
import requests
from .state_manager import StateManager
from Exceptions.ArmisExceptions import ArmisException, ArmisDataNotFoundException

API_KEY = os.environ["ArmisSecretKey"]
url = os.environ["ArmisURL"]
connection_string = os.environ["AzureWebJobsStorage"]
customer_id = os.environ["WorkspaceID"]
shared_key = os.environ["WorkspaceKey"]
armis_devices = os.environ["ArmisDeviceTableName"]
is_avoid_duplicates = os.environ["AvoidDuplicates"]

HTTP_ERRORS = {
    400: "Armis Device Connector: Bad request: Missing aql parameter.",
    401: "Armis Device Connector: Authentication error: Authorization information is missing or invalid.",
}
ERROR_MESSAGES = {
    "ACCESS_TOKEN_NOT_FOUND": "Armis Device Connector: Access token not found. please check Key.",
    "HOST_CONNECTION_ERROR": "Armis Device Connector: Invalid host while verifying 'armis account'.",
}

body = ""


class ArmisDevice:
    """This class will process the Device data and post it into the Microsoft sentinel."""

    def __init__(self):
        """__init__ method will initialize object of class."""
        self._link = url
        self._header = {}
        self._secret_key = API_KEY
        self._data_device_from = 0
        self._retry_device_token = 1

    def _get_access_token_device(self, armis_link_suffix):
        """
        _get_access_token_device will fetch the access token using api and set it in header for further use.

        Args:
            armis_link_suffix (String): This variable will be suffix/add-on to the link.

        """
        if self._secret_key is not None and self._link is not None:
            parameter = {"secret_key": self._secret_key}
            try:
                response = requests.post(
                    (self._link + armis_link_suffix), params=parameter
                )
                if response.status_code == 200:
                    logging.info("Armis Device Connector: Getting access token.")
                    _access_token = json.loads(response.text)["data"]["access_token"]
                    self._header.update({"Authorization": _access_token})
                elif response.status_code == 400:
                    raise ArmisException(
                        "Armis Device Connector: Please check either armis URL or armis secret key is wrong."
                    )

                else:
                    raise ArmisException(
                        "Armis Device Connector: Error while generating the access token. error code: {}.".format(
                            response.status_code
                        )
                    )

            except ArmisException as err:
                logging.error(err)
                raise ArmisException(
                    "Armis Device Connector: Error while generating the access token."
                )

        else:
            raise ArmisException(
                "Armis Device Connector: The secret key or link has not been initialized."
            )

    def _get_device_data(self, armis_link_suffix, parameter):
        """Get_device_data is used to get data using api.

        Args:
            self: Armis object.
            armis_link_suffix (String): will be containing the other part of link.
            parameter (json): will contain the json data to sends to parameter to get data from REST API.

        """
        try:

            response = requests.get(
                (self._link + armis_link_suffix), params=parameter, headers=self._header
            )
            if response.status_code == 200:
                logging.info("API connected successfully with Armis to fetch the data.")
                results = json.loads(response.text)

                if(results["data"]["count"] == 0):
                    raise ArmisDataNotFoundException(
                        "Armis Device Connector: Data not found."
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

                    body = json.dumps(data)
                    logging.info(
                        "Armis Device Connector: From %s length 1000",
                        self._data_device_from,
                    )
                    self._data_device_from = results["data"]["next"]
                    current_time = data[-1]["lastSeen"][:19]
                    if len(current_time) != 19:
                        if len(current_time) == 10:
                            current_time += "T00:00:00"
                            logging.info("Armis Device Connector: 'T:00:00:00' added as only date is available.")
                        else:
                            splited_time = current_time.split('T')
                            if len(splited_time[1]) == 5:
                                splited_time[1] += ":00"
                                logging.info("Armis Device Connector: ':00' added as seconds not available.")
                            elif len(splited_time[1]) == 2:
                                splited_time[1] += ":00:00"
                                logging.info("Armis Device Connector: ':00:00' added as only hour is available.")
                            current_time = "T".join(splited_time)

                    return body, current_time, total_data_length, count_per_frame_data
                else:
                    raise ArmisException(
                        "Armis Device Connector: There are no proper keys in data."
                    )

            elif response.status_code == 400:
                raise ArmisException(HTTP_ERRORS[400])

            elif response.status_code == 401 and self._retry_device_token <= 3:
                logging.info(
                    "Armis Device Connector: Retry number: {}".format(
                        str(self._retry_device_token)
                    )
                )
                self._retry_device_token += 1
                logging.error(HTTP_ERRORS[401])
                logging.info("Armis Device Connector: Generating access token again!")
                self._get_access_token_device("/access_token/")
                return self._get_device_data(armis_link_suffix, parameter)
            else:
                raise ArmisException(
                    "Armis Device Connector: Error while fetching data. status Code:{} error message:{}.".format(
                        response.status_code, response.text
                    )
                )

        except requests.exceptions.ConnectionError:
            logging.error(ERROR_MESSAGES["HOST_CONNECTION_ERROR"])
            raise ArmisException(
                "Armis Device Connector: Connection error while getting data from device api."
            )

        except requests.exceptions.RequestException as request_err:
            logging.error(request_err)
            raise ArmisException(
                "Armis Device Connector: Request error while getting data from Device api."
            )

        except ArmisException as err:
            logging.error(err)
            raise ArmisException(
                "Armis Device Connector: Error while getting data from device api."
            )

        except ArmisDataNotFoundException as err:
            logging.info(err)
            raise ArmisDataNotFoundException()

    def _fetch_device_data(
        self, type_data, state, table_name, is_table_not_exist, last_time=None
    ):
        """Fetch_device_data is used to push all the data into table.

        Args:
            self: Armis object.
            type_data (json): will contain the json data to use in the _get_links function.
            state (object): StateManager object.
            table_name (String): table name to store the data in microsoft sentinel.
            is_table_not_exist (bool): it is a flag that contains the value if table exists or not.
            last_time (String): it will contain latest time stamp.
        """
        try:
            self._get_access_token_device("/access_token/")
            if is_table_not_exist:
                aql_data = """{}""".format(type_data["aql"])
            else:
                aql_data = """{} after:{}""".format(type_data["aql"], last_time)
            type_data["aql"] = aql_data
            logging.info(
                "Armis Device Connector: aql data new " + str(type_data["aql"])
            )

            azuresentinel = AzureSentinel()
            while self._data_device_from is not None:
                parameter_device = {
                    "aql": type_data["aql"],
                    "from": self._data_device_from,
                    "orderBy": "lastSeen",
                    "length": 1000,
                    "fields": type_data["fields"],
                }
                (
                    body,
                    current_time,
                    total_data_length,
                    count_per_frame_data,
                ) = self._get_device_data("/search/", parameter_device)
                logging.info(
                    "Armis Device Connector: Total length of data is %s ",
                    total_data_length,
                )
                logging.info("Armis Device Connector:  Data collection is done successfully.")
                azuresentinel.post_data(customer_id, body, table_name)
                logging.info(
                    "Armis Device Connector: Collected %s device data into microsoft sentinel.",
                    count_per_frame_data,
                )
                state.post(str(current_time))
                logging.info(
                    "Armis Device Connector: Timestamp added at: " + str(current_time)
                )
                logging.info(
                    "Armis Device Connector: Timestamp added into the StateManager successfully."
                )

            if(str(is_avoid_duplicates).lower() == "true"):
                current_time = datetime.datetime.strptime(current_time, '%Y-%m-%dT%H:%M:%S')
                current_time += datetime.timedelta(seconds=1)
                current_time = current_time.strftime('%Y-%m-%dT%H:%M:%S')
                state.post(str(current_time))
                logging.info("Armis Device Connector: Last timestamp with plus one second that is added at: {}".format(
                    current_time)
                )
                logging.info("Armis Device Connector: "
                             + "Last timestamp is added with plus one second into the StateManager successfully.")

        except ArmisException as err:
            logging.error(err)
            raise ArmisException(
                "Armis Device Connector: Error while processing the data."
            )

        except ArmisDataNotFoundException:
            raise ArmisDataNotFoundException()

    def check_data_exists_or_not_device(self):
        """Check_data_exists_or_not is to check if the data is exists or not using the timestamp file.

        Args:
            self: Armis object.

        """
        device_field_list = ["accessSwitch", "category", "firstSeen", "id", "ipAddress", "lastSeen",
                             "macAddress", "manufacturer", "model", "name", "operatingSystem",
                             "operatingSystemVersion", "riskLevel", "sensor", "site", "tags", "type", "user",
                             "visibility", "serialNumber", "plcModule", "purdueLevel", "firmwareVersion"]
        try:
            parameter_devices = {
                "aql": "in:devices",
                "orderBy": "lastSeen",
                "fields": ','.join(device_field_list),
            }
            state_devices = StateManager(
                connection_string=connection_string, file_path="funcarmisdevicesfile"
            )
            last_time_devices = state_devices.get()
            if last_time_devices is None:
                logging.info(
                    "Armis Device Connector: The last run timestamp is not available for the devices!"
                )
                self._fetch_device_data(
                    parameter_devices,
                    state_devices,
                    armis_devices,
                    True,
                    last_time_devices,
                )
                logging.info("Armis Device Connector: Data ingestion initiated.")
            else:
                logging.info(
                    "Armis Device Connector: The last time point is available in devices: {}.".format(
                        last_time_devices
                    )
                )
                self._fetch_device_data(
                    parameter_devices,
                    state_devices,
                    armis_devices,
                    False,
                    last_time_devices,
                )
                logging.info(
                    "Armis Device Connector: Data added when logs was already in %s.",
                    armis_devices,
                )
            logging.info("Armis Device Connector: Device data added successfully !")
        except ArmisException as err:
            logging.error(err)
            raise ArmisException(
                "Armis Device Connector: Error occured during checking whether log table exist or not."
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
        timestamp_date = 'armis_device_time'
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
            "x-ms-date": rfc1123date,
            "time-generated-field": timestamp_date,
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
        "Armis Device Connector: Python timer trigger function ran at %s",
        utc_timestamp,
    )

    armis_obj = ArmisDevice()
    try:
        armis_obj.check_data_exists_or_not_device()
    except ArmisDataNotFoundException:
        pass

    utc_timestamp_final = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    logging.info(
        "Armis Device Connector: execution completed for device at %s.",
        utc_timestamp_final,
    )
    if mytimer.past_due:
        logging.info("Armis Device Connector: The timer is past due!")
