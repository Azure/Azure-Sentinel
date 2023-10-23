"""This file contains methods for validations, checkpoint, pulling and pushing data."""
import sys
import datetime
import json
import inspect
import requests
import hashlib
from requests.auth import HTTPBasicAuth
from ..SharedCode import consts
from ..SharedCode.azure_sentinel import AzureSentinel


class BaseCollector:
    """This class contains methods to create object and helper methods."""

    def __init__(self, applogger, function_name, client_id, client_secret) -> None:
        """Initialize instance variable for class."""
        self.connection_string = consts.CONNECTION_STRING
        self.base_url = consts.BASE_URL
        self.client_id = client_id
        self.client_secretkey = client_secret
        self.start_time = consts.START_TIME
        self.applogger = applogger
        self.azuresentinel = AzureSentinel()
        self.session = requests.Session()
        self.session.headers["User-Agent"] = consts.USER_AGENT
        self.session.headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.function_name = function_name

    def validate_params(self, client_id_name, client_secret_name, snapshot=False):
        """To validate parameters of function app."""
        __method_name = inspect.currentframe().f_code.co_name
        required_params = {
            "BaseURL": self.base_url,
            client_id_name: self.client_id,
            client_secret_name: self.client_secretkey,
            "WorkspaceID": consts.WORKSPACE_ID,
            "WorkspaceKey": consts.WORKSPACE_KEY,
            "Detections_Table_Name": consts.DETECTIONS_TABLE_NAME,
            "Audits_Table_Name": consts.AUDITS_TABLE_NAME,
            "Entity_Scoring_Table_Name": consts.ENTITY_SCORING_TABLE_NAME,
            "Lockdown_Table_Name": consts.LOCKDOWN_TABLE_NAME,
            "Health_Table_Name": consts.HEALTH_TABLE_NAME,
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
            raise Exception(
                "Error Occurred while validating params. Required fields missing."
            )
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
            raise Exception(
                "Error Occurred while validating params. Invalid format for BaseURL."
            )

        if not snapshot:
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
                        raise Exception(
                            "Error Occurred while validating params. StartTime cannot be in the future."
                        )
                    self.start_time = datetime.datetime.strftime(
                        input_date, r"%Y-%m-%dT%H:%M:%SZ"
                    )
                else:
                    self.start_time = (
                        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
                        - datetime.timedelta(hours=24)
                    ).strftime(r"%Y-%m-%dT%H:%M:%SZ")
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
                raise Exception(
                    "Error Occurred while validating params. Invalid StartTime format."
                )

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
            "{}(method={}) : {} : Error occurred while fetching the access token from the response. "
            'Key "access_token" was not found in the API response.'.format(
                consts.LOGS_STARTS_WITH, __method_name, self.function_name
            )
        )
        raise Exception(
            "Error occurred while fetching the access token from the response. "
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
                    url=url,
                    auth=auth,
                    params=params,
                    data=data,
                    timeout=consts.API_TIMEOUT,
                )
            else:
                res = self.session.get(
                    url=url,
                    auth=auth,
                    params=params,
                    data=data,
                    timeout=consts.API_TIMEOUT,
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
                    "{}(method={}) : {} : API call: Unknown status code or empty "
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
            if res.status_code == 404:
                self.applogger.debug(
                    '{}(method={}) : {} : API call: Got {} Status Code : url="{}"'
                    ' response="{}"'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        url,
                        ex.response.status_code,
                        ex.response.text,
                    )
                )
                return {}
            else:
                self.applogger.error(
                    '{}(method={}) : {} : API call: Unsuccessful response: url="{}" status_code="{}"'
                    ' response="{}"'.format(
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
                if checkpoint.get("from", None):
                    field, checkpoint = "from", checkpoint.get("from")
                else:
                    field, checkpoint = "event_timestamp_gte", checkpoint.get(
                        "event_timestamp_gte"
                    )
            else:
                field, checkpoint = "event_timestamp_gte", self.start_time
                self.state.post(json.dumps({"event_timestamp_gte": self.start_time}))
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

    def _get_size_of_chunk_in_mb(self, chunk):
        """Get the size of chunk in MB."""
        return sys.getsizeof(chunk) / (1024 * 1024)

    def _create_chunks_and_post_to_sentinel(self, data, table_name, fields):
        """Create chunks and post to chunk to sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        chunk = []
        if self._get_size_of_chunk_in_mb(data) < 30:
            self.post_data_to_sentinel(data, table_name, fields)
            return
        for event in data:
            chunk.append(event)
            if self._get_size_of_chunk_in_mb(chunk) >= 30:
                if chunk[:-1]:
                    self.post_data_to_sentinel(chunk[:-1], table_name, fields)
                    next_checkpoint = chunk[-2].get("id")
                    self.save_checkpoint(next_checkpoint)
                    chunk = [event]
                    continue
                else:
                    id = chunk[0].get("id")
                    self.applogger.error(
                        '{}(method={}) : {} : event with id {} is too large to post into the sentinel hence skipping it.'.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            id,
                        )
                    )
                    chunk = []
                    continue
        if chunk:
            self.post_data_to_sentinel(chunk, table_name, fields)
    
    def pull_and_push_the_data(
        self,
        endpoint,
        checkpoint_field,
        checkpoint_value,
        table_name,
        fields=None,
        params=dict(),
    ):
        """To pull the data from vectra and push into sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        posted_event_count = 0
        iter_next = True
        params.update({"limit": consts.PAGE_SIZE, checkpoint_field: checkpoint_value})
        while iter_next:
            res = self.pull(url=self.base_url + endpoint, params=params)
            next_checkpoint = res.get("next_checkpoint", None)

            if endpoint == consts.DETECTIONS_ENDPOINT and len(res.get("events")):
                self.applogger.debug(
                    "{}(method={}) : {} : Trying to collect the additional information from"
                    " /detections endpoint for type=host.".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name
                    )
                )
                detection_ids_list = []
                for event in res.get("events"):
                    if event.get("type") == "host":
                        detection_ids_list.append(str(event.get("detection_id")))

                detection_id_set = set(detection_ids_list)
                detections_ids = ",".join(detection_id_set)
                next = True
                page = 1
                merge_json = {}

                if detections_ids:
                    while next:
                        url = self.base_url + "/api/v3.3/detections"
                        self.applogger.debug(
                            "{}(method={}) : {} : GET call to /detections endpoint with URL = {}".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.function_name,
                                url,
                            )
                        )
                        host_details = self.pull(
                            url=url, params={"id": detections_ids, "page": page}
                        )
                        if host_details.get("results"):
                            for each in host_details.get("results"):
                                merge_json[each.get("id")] = each
                        if not host_details.get("next"):
                            break
                        page += 1

                for event in res.get("events"):
                    if event.get("type") == "host" and merge_json.get(
                        event.get("detection_id"), {}
                    ):
                        temp_host = merge_json.get(event.get("detection_id"), {})
                        event["d_detection_details"] = [temp_host]
                        event["is_targeting_key_asset"] = str(
                            temp_host.get("is_targeting_key_asset", "")
                        )
                        event["src_host"] = [temp_host.get("src_host", {})]
                        event["normal_domains"] = temp_host.get("normal_domains", [])
                        event["src_ip"] = temp_host.get("src_ip", "")
                        event["summary"] = [temp_host.get("summary", {})]
                        event["grouped_details"] = temp_host.get("grouped_details", [])
                    elif event.get("type") == "account" and event.get("detail", {}):
                        event["d_detection_details"] = [event.get("detail", {})]
                    else:
                        event["d_detection_details"] = []
                    self.applogger.debug(
                        "{}(method={}) : {} :  Successfully modified events/detections"
                        " response for id={}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            event.get("id"),
                        )
                    )

            if res and len(res.get("events")):
                self._create_chunks_and_post_to_sentinel(res.get("events"), table_name, fields)
                posted_event_count += len(res.get("events"))
                iter_next = True if int(res.get("remaining_count")) > 0 else False
                params.update({"limit": consts.PAGE_SIZE, "from": next_checkpoint})
            else:
                iter_next = False
            if endpoint == consts.ENTITY_SCORING_ENDPOINT and (
                next_checkpoint is None or next_checkpoint == "null"
            ):
                break
            else:
                self.save_checkpoint(next_checkpoint)

        self.applogger.info(
            "{}(method={}) : {} : Posted total {} event(s) into MS Sentinel. No more events."
            " Stopping the collection.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                self.function_name,
                posted_event_count,
            )
        )

    def pull_and_push_the_snapshot_data(
        self,
        endpoint,
        table_name,
        hashed_events_list=list(),
        hash_field_list=[],
        fields=None,
    ):
        """To pull the snapshot type data from vectra and push into sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        posted_event_count = 0
        res = self.pull(url=self.base_url + endpoint)
        if res and len(res):
            if endpoint == consts.HEALTH_ENDPOINT:
                link_status_dict, aggregated_peak_traffic_dict = {}, {}
                connectivity_dict, trafficdrop_dict = {}, {}

                # for link_status
                for k, v in (
                    res.get("network", {})
                    .get("interfaces", {})
                    .get("sensors", {})
                    .items()
                ):
                    link_status = "UP"
                    for x, y in v.items():
                        if y.get("link", "") != "UP":
                            link_status = "Degraded"
                            break
                    link_status_dict[k] = link_status

                # for aggregated_peak_traffic
                for key, value in (
                    res.get("network", {}).get("traffic", {}).get("sensors", {}).items()
                ):
                    aggregated_peak_traffic_dict[key] = value.get(
                        "aggregated_peak_traffic_mbps", ""
                    )

                # for connectivity status and error
                for item in res.get("connectivity", {}).get("sensors", {}):
                    connectivity_dict[item.get("name", "")] = {
                        "status": item.get("status", ""),
                        "error": item.get("error", ""),
                    }

                # for traffic_drop status and error
                for item in res.get("trafficdrop", {}).get("sensors", {}):
                    trafficdrop_dict[item.get("name", "")] = {
                        "status": item.get("status", ""),
                        "error": item.get("error", ""),
                    }

                for i in range(len(res.get("sensors", {}))):
                    # adding d_link_status
                    res["sensors"][i]["d_link_status"] = link_status_dict.get(
                        res.get("sensors", {})[i].get("luid", ""), ""
                    )
                    # adding d_aggregated_peak_traffic
                    res["sensors"][i][
                        "d_aggregated_peak_traffic"
                    ] = aggregated_peak_traffic_dict.get(
                        res.get("sensors", {})[i].get("name", ""), ""
                    )
                    # adding d_connectivity_status
                    res["sensors"][i]["d_connectivity_status"] = connectivity_dict.get(
                        res.get("sensors", {})[i].get("name", ""), {}
                    ).get("status", "")
                    # adding d_connectivity_error
                    res["sensors"][i]["d_connectivity_error"] = connectivity_dict.get(
                        res.get("sensors", {})[i].get("name", ""), {}
                    ).get("error", "")
                    # adding d_trafficdrop_status
                    res["sensors"][i]["d_trafficdrop_status"] = trafficdrop_dict.get(
                        res.get("sensors", {})[i].get("name", ""), {}
                    ).get("status", "")
                    # adding d_trafficdrop_error
                    res["sensors"][i]["d_trafficdrop_error"] = trafficdrop_dict.get(
                        res.get("sensors", {})[i].get("name", ""), {}
                    ).get("error", "")

                list_res = [res]
                self.post_data_to_sentinel(list_res, table_name, fields)
                posted_event_count += 1
            else:
                for event in res:
                    temp_dict = {}
                    for field in hash_field_list:
                        temp_dict[field] = event.get(field)
                    hash_of_event = self.get_results_hash(temp_dict)
                    if hash_of_event not in hashed_events_list:
                        self.post_data_to_sentinel(event, table_name, fields)
                        posted_event_count += 1
                        hashed_events_list.append(hash_of_event)
                        self.save_checkpoint_snapshot(hashed_events_list)

        self.applogger.info(
            "{}(method={}) : {} : Posted total {} event(s) into MS Sentinel. No more events."
            " Stopping the collection.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                self.function_name,
                posted_event_count,
            )
        )

    def get_results_hash(self, data):
        """
        Method to generate hash digest.
        :data: Data to be hashed.
        :return: SHA512 hexdigest of data.
        """
        data = json.dumps(data, sort_keys=True)
        result = hashlib.sha512(data.encode())
        result_hash = result.hexdigest()
        return result_hash

    def get_checkpoint_snapshot(self):
        """Fetch snapshot hash from checkpoint file.

        Returns:
            List: hash_list
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            checkpoint = self.state.get()
            if checkpoint:
                checkpoint = json.loads(checkpoint)
                checkpoint = checkpoint.get("snapshot")
                self.applogger.info(
                    "{}(method={}) : {} : Checkpoint list fetched successfully.".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name
                    )
                )
            else:
                checkpoint = []
                self.state.post(json.dumps({"snapshot": checkpoint}))
                self.applogger.info(
                    "{}(method={}) : {} : Checkpoint list not found. Created new checkpoint list.".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name
                    )
                )
            return checkpoint
        except Exception as ex:
            self.applogger.error(
                '{}(method={}) : {} : Unexpected error while getting checkpoint list: err="{}"'.format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, str(ex)
                )
            )
            raise Exception(ex)

    def save_checkpoint_snapshot(self, value):
        """Post checkpoint snapshot into sentinel."""
        try:
            __method_name = inspect.currentframe().f_code.co_name
            self.state.post(json.dumps({"snapshot": value}))
            self.applogger.info(
                "{}(method={}) : {} : successfully saved checkpoint.".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name
                )
            )
        except Exception as ex:
            self.applogger.exception(
                '{}(method={}) : {} : Unexpected error while saving checkpoint: err="{}"'.format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, str(ex)
                )
            )
            raise Exception(ex)
