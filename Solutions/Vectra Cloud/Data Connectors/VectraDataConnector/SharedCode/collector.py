"""This file contains methods for validations, checkpoint, pulling and pushing data."""
import datetime
import json
import inspect
import requests
from requests.auth import HTTPBasicAuth
from ..SharedCode import consts
from ..SharedCode.azure_sentinel import AzureSentinel


class BaseCollector:
    """This class contains methods to create object and helper methods."""

    def __init__(self, applogger, function_name) -> None:
        """Initialize instance variable for class."""
        self.connection_string = consts.CONNECTION_STRING
        self.base_url = consts.BASE_URL
        self.client_id = consts.CLIENT_ID
        self.client_secretkey = consts.CLIENT_SECRET
        self.start_time = consts.START_TIME
        self.applogger = applogger
        self.azuresentinel = AzureSentinel()
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "Vectra-Sentinel"
        self.session.headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.function_name = function_name

    def validate_params(self):
        """To validate parameters of function app."""
        __method_name = inspect.currentframe().f_code.co_name
        required_params = {
            "BaseURL": self.base_url,
            "ClientId": self.client_id,
            "ClientSecretKey": self.client_secretkey,
            "WorkspaceID": consts.WORKSPACE_ID,
            "WorkspaceKey": consts.WORKSPACE_KEY,
            "Account_Detection_Table_Name": consts.ACCOUNT_DETECTION_TABLE_NAME,
            "Audits_Table_Name": consts.AUDITS_TABLE_NAME,
            "Entity_Scoring_Table_Name": consts.ENTITY_SCORING_TABLE_NAME,
        }
        missing_required_field = False
        for label, params in required_params.items():
            if not params:
                missing_required_field = True
                self.applogger.error(
                    '{}(method={}) : {} : "{}" field is not configured. field_value="{}"'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        label,
                        params,
                    )
                )
        if missing_required_field:
            raise Exception("Error Occurred while validating params. Required fields missing.")
        if not self.base_url.startswith("https://"):
            self.applogger.error(
                '{}(method={}) : {} : "BaseURL" must start with ”https://” schema followed '
                'by hostname. BaseURL="{}"'.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    self.base_url,
                )
            )
            raise Exception("Error Occurred while validating params. Invalid format for BaseURL.")

        try:
            if self.start_time:
                input_date = datetime.datetime.strptime(
                    self.start_time, r"%m/%d/%Y %H:%M:%S"
                )
                now = datetime.datetime.utcnow()
                if input_date > now:
                    self.applogger.error(
                        '{}(method={}) : {} : "StartTime" should not be in future. StartTime="{}"'.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            self.start_time,
                        )
                    )
                    raise Exception("Error Occurred while validating params. StartTime cannot be in the future.")
                self.start_time = datetime.datetime.strftime(
                    input_date, r"%Y-%m-%dT%H:%M:%SZ"
                )
            else:
                self.start_time = (
                    datetime.datetime.utcnow()
                    .replace(tzinfo=datetime.timezone.utc)
                    .strftime(r"%Y-%m-%dT%H:%M:%SZ")
                )
        except ValueError:
            self.applogger.error(
                '{}(method={}) : {} : "StartTime" should be in "MM/DD/YYYY HH:MM:SS" (UTC) '
                'format. StartTime="{}"'.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    self.start_time,
                )
            )
            raise Exception("Error Occurred while validating params. Invalid StartTime format.")

    def validate_connection(self):
        """To validate the connection with vectra and generate access token."""
        __method_name = inspect.currentframe().f_code.co_name
        res = self.pull(
            url=self.base_url + consts.OAUTH2_ENDPOINT,
            auth=HTTPBasicAuth(self.client_id, self.client_secretkey),
            data={"grant_type": "client_credentials"},
            method="POST",
        )
        if res and res.get("access_token"):
            self.session.headers["Authorization"] = "bearer {}".format(
                res.get("access_token")
            )
            self.applogger.info(
                "{}(method={}) : {} : Validation successful.".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name
                )
            )
            return
        self.applogger.error(
            '{}(method={}) : {} : Error occurred while fetching the access token from the response. '
            'Key "access_token" was not found in the API response.'.format(
                consts.LOGS_STARTS_WITH, __method_name, self.function_name
            )
        )
        raise Exception(
            'Error occurred while fetching the access token from the response. '
            'Key "access_token" was not found in the API response.'
        )

    def pull(self, url, params=None, data=None, auth=None, method="GET"):
        """
        Do GET call to fetch Data from Vectra API.

        :return: retrieved response obj
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            if method == "POST":
                res = self.session.post(
                    url=url, auth=auth, params=params, data=data, timeout=consts.API_TIMEOUT
                )
            else:
                res = self.session.get(
                    url=url, auth=auth, params=params, data=data, timeout=consts.API_TIMEOUT
                )
            res.raise_for_status()
            if res and res.status_code in [200, 201]:
                self.applogger.debug(
                    '{}(method={}) : {} : API call: Response received successfully. url="{}" params="{}"'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        url,
                        params,
                    )
                )
                return res.json()
            else:
                self.applogger.error(
                    '{}(method={}) : {} : API call: Unknown status code or empty '
                    'response: url="{}" status_code="{}" response="{}"'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        url,
                        res.status_code,
                        res.text,
                    )
                )
                raise Exception("Received unknown status code or empty response.")
        except requests.exceptions.HTTPError as ex:
            self.applogger.error(
                '{}(method={}) : {} : API call: Unsuccessful response: url="{}" status_code="{}" response="{}"'.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    url,
                    ex.response.status_code,
                    ex.response.text,
                )
            )
            raise Exception("HTTP Error Occurred while getting response from api.")
        except Exception as ex:
            self.applogger.error(
                '{}(method={}) : {} : API call: Unexpected error while API call url="{}" error="{}"'.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    url,
                    str(ex),
                )
            )
            raise Exception("Error Occurred while getting response from api.")

    def get_checkpoint_field_and_value(self):
        """Fetch last data from checkpoint file.

        Returns:
            None/json: last_data
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            field = None
            checkpoint = self.state.get()
            if checkpoint:
                checkpoint = json.loads(checkpoint)
                field, checkpoint = "from", checkpoint.get("from")
            else:
                field, checkpoint = "event_timestamp_gte", self.start_time
            self.applogger.info(
                '{}(method={}) : {} : Checkpoint field="{}" and value="{}"'.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    field,
                    checkpoint,
                )
            )
            return field, checkpoint
        except Exception as ex:
            self.applogger.error(
                '{}(method={}) : {} : Unexpected error while getting checkpoint: err="{}"'.format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, str(ex)
                )
            )
            raise Exception(ex)

    def save_checkpoint(self, value):
        """Post checkpoint into sentinel."""
        try:
            __method_name = inspect.currentframe().f_code.co_name
            self.state.post(json.dumps({"from": value}))
            self.applogger.info(
                '{}(method={}) : {} : successfully saved checkpoint. from="{}"'.format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, value
                )
            )
        except Exception as ex:
            self.applogger.exception(
                '{}(method={}) : {} : Unexpected error while saving checkpoint: err="{}"'.format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, str(ex)
                )
            )
            raise Exception(ex)

    def post_data_to_sentinel(self, data, table_name, fields):
        """To post data into sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        if fields:
            for event in data:
                for field in fields:
                    event[field] = [event.get(field)]
        data = json.dumps(data)
        status_code = self.azuresentinel.post_data(data, table_name)
        if status_code in consts.SENTINEL_ACCEPTABLE_CODES:
            self.applogger.info(
                '{}(method={}) : {} : Successfully posted the data in the table="{}"'.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    table_name,
                )
            )
        else:
            self.applogger.error(
                '{}(method={}) : {} : Data is not posted in the table="{}" status_code="{}"'.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    table_name,
                    status_code,
                )
            )
            raise Exception(
                "Error Occurred while posting data into Microsoft Sentinel Log Analytics Workspace."
            )

    def pull_and_push_the_data(
        self, endpoint, checkpoint_field, checkpoint_value, table_name, fields=None
    ):
        """To pull the data from vectra and push into sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        iter_next = True
        params = {"limit": 1000, checkpoint_field: checkpoint_value}
        while iter_next:
            res = self.pull(url=self.base_url + endpoint, params=params)
            next_checkpoint = res.get("next_checkpoint")
            if res and len(res.get("events")):
                self.post_data_to_sentinel(
                    res.get("events"), table_name, fields
                )
                iter_next = True if int(res.get("remaining_count")) > 0 else False
                params = {"limit": 1000, "from": next_checkpoint}
            else:
                self.applogger.info(
                    "{}(method={}) : {} : Stopping the collection.".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name
                    )
                )
                iter_next = False
            self.save_checkpoint(next_checkpoint)
