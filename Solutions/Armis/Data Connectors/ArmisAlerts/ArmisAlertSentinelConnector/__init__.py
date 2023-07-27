"""This __init__ file will be called once triggered is generated."""
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
armis_alerts = os.environ["ArmisAlertsTableName"]
is_avoid_duplicates = os.environ["AvoidDuplicates"]

HTTP_ERRORS = {
    400: "Armis Alert Connector: Bad request: Missing aql parameter.",
    401: "Armis Alert Connector: Authentication error: Authorization information is missing or invalid.",
}
ERROR_MESSAGES = {
    "ACCESS_TOKEN_NOT_FOUND": "Armis Alert Connector: Access token not found. please check Key.",
    "HOST_CONNECTION_ERROR": "Armis Alert Connector: Invalid host while verifying 'armis account'",
}

body = ""


class ArmisAlert:
    """This class will process the Alert data and post it into the Microsoft sentinel."""

    def __init__(self):
        """__init__ method will initialize object of class."""
        self._link = url
        self._header = {}
        self._secret_key = API_KEY
        self._data_alert_from = 0
        self._retry_alert_token = 1

    def _get_access_token_alert(self, armis_link_suffix):
        """
        _get_access_token_alert method will fetch the access token using api and set it in header for further use.

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
                    logging.info("Armis Alert Connector: Getting access token.")
                    _access_token = json.loads(response.text)["data"]["access_token"]
                    self._header.update({"Authorization": _access_token})
                elif response.status_code == 400:
                    raise ArmisException(
                        "Armis Alert Connector: Please check either armis URL or armis secret key is wrong."
                    )

                else:
                    raise ArmisException(
                        "Armis Alert Connector: Error while generating the access token. error code: {}.".format(
                            response.status_code
                        )
                    )

            except ArmisException as err:
                logging.error(err)
                raise ArmisException(
                    "Armis Alert Connector: Error while generating the access token."
                )

        else:
            raise ArmisException(
                "Armis Alert Connector: The secret key or link has not been initialized."
            )

    def _get_alert_data(self, armis_link_suffix, parameter):
        """_get_alert_data is used to get data using api.

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
                        "Armis Alert Connector: Data not found."
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
                        i["armis_alert_time"] = i["time"]

                    body = json.dumps(data, indent=2)
                    logging.info(
                        "Armis Alert Connector: From %s length 1000",
                        self._data_alert_from,
                    )
                    self._data_alert_from = results["data"]["next"]
                    current_time = data[-1]["time"][:19]
                    if len(current_time) != 19:
                        if len(current_time) == 10:
                            current_time += "T00:00:00"
                            logging.info("Armis Alert Connector: 'T:00:00:00' added as only date is available.")
                        else:
                            splited_time = current_time.split('T')
                            if len(splited_time[1]) == 5:
                                splited_time[1] += ":00"
                                logging.info("Armis Alert Connector: ':00' added as seconds not available.")
                            elif len(splited_time[1]) == 2:
                                splited_time[1] += ":00:00"
                                logging.info("Armis Alert Connector: ':00:00' added as only hour is available.")
                            current_time = "T".join(splited_time)

                    return body, current_time, total_data_length, count_per_frame_data
                else:
                    raise ArmisException(
                        "Armis Alert Connector: There are no proper keys in data."
                    )

            elif response.status_code == 400:
                raise ArmisException(HTTP_ERRORS[400])

            elif response.status_code == 401 and self._retry_alert_token <= 3:
                logging.info(
                    "Armis Alert Connector: Retry number: {}".format(
                        str(self._retry_alert_token)
                    )
                )
                self._retry_alert_token += 1
                logging.error(HTTP_ERRORS[401])
                logging.info("Armis Alert Connector: Generating access token again!")
                self._get_access_token_alert("/access_token/")
                return self._get_alert_data(armis_link_suffix, parameter)
            else:
                raise ArmisException(
                    "Armis Alert Connector: Error while fetching data. status code:{} error message:{}.".format(
                        response.status_code, response.text
                    )
                )

        except requests.exceptions.ConnectionError:
            logging.error(ERROR_MESSAGES["HOST_CONNECTION_ERROR"])
            raise ArmisException(
                "Armis Alert Connector:Connection error while getting data from alert api."
            )

        except requests.exceptions.RequestException as request_err:
            logging.error(request_err)
            raise ArmisException(
                "Armis Alert Connector:Request error while getting data from alert api."
            )

        except ArmisException as err:
            logging.error(err)
            raise ArmisException(
                "Armis Alert Connector: Error while getting data from alert api."
            )

        except ArmisDataNotFoundException as err:
            logging.info(err)
            raise ArmisDataNotFoundException()

    def _fetch_alert_data(
        self, type_data, state, table_name, is_table_not_exist, last_time=None
    ):
        """Fetch_alert_data is used to push all the data into table.

        Args:
            self: Armis object.
            type_data (json): will contain the json data to use in the _get_links function.
            state (object): StateManager object.
            table_name (String): table name to store the data in microsoft sentinel.
            is_table_not_exist (bool): it is a flag that contains the value if table exists or not.
            last_time (String): it will contain latest time stamp.
        """
        try:
            self._get_access_token_alert("/access_token/")
            if is_table_not_exist:
                aql_data = """{}""".format(type_data["aql"])
            else:
                aql_data = """{} after:{}""".format(type_data["aql"], last_time)
            type_data["aql"] = aql_data
            logging.info("Armis Alert Connector: aql data new " + str(type_data["aql"]))

            azuresentinel = AzureSentinel()
            while self._data_alert_from is not None:
                parameter_alert = {
                    "aql": type_data["aql"],
                    "from": self._data_alert_from,
                    "orderBy": "time",
                    "length": 1000,
                    "fields": type_data["fields"],
                }
                (
                    body,
                    current_time,
                    total_data_length,
                    count_per_frame_data,
                ) = self._get_alert_data("/search/", parameter_alert)
                logging.info(
                    "Armis Alert Connector: Total length of data is %s ",
                    total_data_length,
                )
                logging.info("Armis Alert Connector:  Data collection is done successfully.")
                azuresentinel.post_data(customer_id, body, table_name)
                logging.info(
                    "Armis Alert Connector: Collected %s alert data into microsoft sentinel.",
                    count_per_frame_data,
                )
                state.post(str(current_time))
                logging.info(
                    "Armis Alert Connector: Timestamp added at: " + str(current_time)
                )
                logging.info(
                    "Armis Alert Connector: Timestamp added into the StateManager successfully."
                )

            if(str(is_avoid_duplicates).lower() == "true"):
                current_time = datetime.datetime.strptime(current_time, '%Y-%m-%dT%H:%M:%S')
                current_time += datetime.timedelta(seconds=1)
                current_time = current_time.strftime('%Y-%m-%dT%H:%M:%S')
                state.post(str(current_time))
                logging.info("Armis Alert Connector: Last timestamp with plus one second that is added at: {}".format(
                    current_time)
                )
                logging.info("Armis Alert Connector: "
                             + "Last timestamp is added with plus one second into the StateManager successfully.")

        except ArmisException as err:
            logging.error(err)
            raise ArmisException(
                "Armis Alert Connector: Error while processing the data."
            )

        except ArmisDataNotFoundException:
            raise ArmisDataNotFoundException()

    def check_data_exists_or_not_alert(self):
        """Check_data_exists_or_not is to check if the data is exists or not using the timestamp file.

        Args:
            self: Armis object.

        """
        alert_field_list = ["alertId", "type", "title", "description", "severity", "time", "status",
                            "deviceIds", "activityUUIDs"]
        try:
            parameter_alert = {
                "aql": "in:alerts",
                "orderBy": "time",
                "fields": ','.join(alert_field_list),
            }
            state_alerts = StateManager(
                connection_string=connection_string, file_path="funcarmisalertsfile"
            )
            last_time_alerts = state_alerts.get()
            if last_time_alerts is None:
                logging.info(
                    "Armis Alert Connector: The last run timestamp is not available for the alerts!"
                )
                self._fetch_alert_data(
                    parameter_alert,
                    state_alerts,
                    armis_alerts,
                    True,
                    last_time_alerts,
                )
                logging.info("Armis Alert Connector: Data ingestion initiated.")
            else:
                logging.info(
                    "Armis Alert Connector: The last time point is available in alerts: {}.".format(
                        last_time_alerts
                    )
                )
                self._fetch_alert_data(
                    parameter_alert,
                    state_alerts,
                    armis_alerts,
                    False,
                    last_time_alerts,
                )
                logging.info(
                    "Armis Alert Connector: Data added when logs was already in %s.",
                    armis_alerts,
                )
            logging.info("Armis Alert Connector: Alerts data added successfully !")
        except ArmisException as err:
            logging.error(err)
            raise ArmisException(
                "Armis Alert Connector: Error occured during checking whether log table exist or not."
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
        timestamp_date = 'armis_alert_time'
        try:
            signature = self.build_signature(
                rfc1123date,
                content_length,
                method,
                content_type,
                resource,
            )
        except ArmisException as err:
            logging.error("Armis Alert Connector: Error occured: {}".format(err))
            raise ArmisException(
                "Armis Alert Connector: Error while generating signature for log analytics."
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
                    "Armis Alert Connector: Data posted successfully to microsoft sentinel."
                )
            else:
                raise ArmisException(
                    "Armis Alert Connector: Response code: {} from posting data to log analytics.".format(
                        response.status_code
                    )
                )

        except ArmisException as err:
            logging.error(err)
            raise ArmisException(
                "Armis Alert Connector: Error while posting data to microsoft sentinel."
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
        "Armis Alert Connector: Python timer trigger function ran at %s",
        utc_timestamp,
    )

    armis_obj = ArmisAlert()
    try:
        armis_obj.check_data_exists_or_not_alert()
    except ArmisDataNotFoundException:
        pass

    utc_timestamp_final = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    logging.info(
        "Armis Alert Connector: execution completed for alerts at %s.",
        utc_timestamp_final,
    )
    if mytimer.past_due:
        logging.info("Armis Alert Connector: The timer is past due!")
