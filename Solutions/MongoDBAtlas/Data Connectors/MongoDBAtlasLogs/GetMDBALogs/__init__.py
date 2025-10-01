"""This __init__ file will be called once trigger is generated."""
from datetime import datetime, timezone
import logging
import base64
import json
import os
import time
import gzip
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

import requests
import azure.functions as func
from azure.core.exceptions import HttpResponseError
from azure.identity import ManagedIdentityCredential
from azure.monitor.ingestion import LogsIngestionClient
from dotenv import load_dotenv

from .job_state_table_store import JobStateTableStore


class ConfigStore:
    """External parameters required by the function application"""

    def __init__(self, **kwargs):
        """
        Initialize with keyword arguments or load from environment variables.
        Example:
            config = ConfigStore(client_id='abc', client_secret='xyz')
            or
            config = ConfigStore(client_id='ENV_CLIENT_ID',
                                 client_secret='ENV_CLIENT_SECRET', from_env=True)
        """
        self._config = {}
        self.from_env = kwargs.pop("from_env", False)

        for key, value in kwargs.items():
            if self.from_env:
                # Load value from environment variable using the name passed in `value`
                self._config[key] = os.getenv(value)
            else:
                # Use the value directly
                self._config[key] = value

    def get(self, key, default=None):
        """Retrieve a config value by key."""
        return self._config.get(key, default)

    def set(self, key, value):
        """Set or override a config value."""
        self._config[key] = value

    def all(self):
        """Return all configuration data as a dictionary."""
        return dict(self._config)

    def __getitem__(self, key):
        return self.get(key)

    def __repr__(self):
        return f"ConfigStore(keys={list(self._config.keys())})"


class Uploader:
    """
        Uploads pages of log messages to the Microsoft Sentinel Logs Ingestion API via a client.
        The pages are uploaded in parallel. The number of threads available to do this is configurable.
    """

    def __init__(self, config, upload_timeout=60):
        self.config = config
        self.azure_dcr_immutableid = config.get("azure_dcr_immutableid")
        azure_dce_endpoint = config.get("azure_dce_endpoint")
        self.azure_stream_name = config.get("azure_stream_name")
        azure_client_id = config.get("azure_client_id")
        thread_max = config.get("azure_max_upload_threads")
        if not thread_max.isdigit():
            raise ValueError(
                f"Invalid azure_max_upload_threads: '{thread_max}'")
        azure_max_upload_threads = int(thread_max)

        self.upload_chunk_count = 0
        self.upload_fail_count = 0
        self.jobs = []                     # holds futures
        self.executor = ThreadPoolExecutor(
            max_workers=azure_max_upload_threads)
        self.upload_timeout = upload_timeout

        credential = ManagedIdentityCredential(client_id=azure_client_id)
        self.client = LogsIngestionClient(
            endpoint=azure_dce_endpoint, credential=credential, logging_enable=True)

    def add_to_upload_list(self, chunk):
        future = self.executor.submit(
            self._post_data,
            client=self.client,
            rule_id=self.azure_dcr_immutableid,
            stream_name=self.azure_stream_name,
            logs=chunk,
        )
        self.jobs.append(future)

    def upload_list(self) -> dict:
        logging.info("Called upload_list")
        try:
            for index, future in enumerate(as_completed(self.jobs), start=1):
                try:
                    future.result(timeout=self.upload_timeout)
                    logging.info("job %s complete", index)
                except TimeoutError:
                    logging.error("job %s timed out after %s seconds",
                                  index, self.upload_timeout)
                    self.upload_fail_count += 1
                except Exception as e:
                    logging.exception("job %s failed: %s", index, e)
                    self.upload_fail_count += 1
        finally:
            self.jobs = []

        return {
            "upload_chunk_count": self.upload_chunk_count,
            "upload_fail_count": self.upload_fail_count,
        }

    def _post_data(self, client, rule_id, stream_name, logs):
        logging.info("Called _post_data (logs_count=%d)", len(logs))
        try:
            client.upload(rule_id=rule_id, stream_name=stream_name, logs=logs)
            self.upload_chunk_count += 1
        except HttpResponseError as e:
            logging.error("Upload failed (HttpResponseError): %s", e)
            self.upload_fail_count += 1
        except Exception as e:
            logging.exception("Upload failed (general): %s", e)
            self.upload_fail_count += 1


class AzureSentinel:
    """Microsoft Sentinel client used to post data to log analytics."""

    def __init__(self, config):
        self.config = config
        self.tenant_id = config.get("tenant_id")

        self.azure_main_storage = config.get("azure_main_storage")
        self.upload_chunk_size = 1024 * 1024  # 1MB of data

        connection_string = self.azure_main_storage
        self.table_name = "JobState"
        self.job_state_table_store = JobStateTableStore(
            connection_string, self.table_name)

    def _upload_in_chunks(self, logs, max_bytes=1 * 1024 * 1024) -> dict:
        """
        Splits a list of logs into smaller arrays of logs each ≤ max_bytes in size.
        It performs a size check assuming each object is serialized to a JSON formatted string when uploaded
        to the Log Ingestion API.

        :param logs: list of JSON-serializable log entries
        :param max_bytes: maximum size per chunk in bytes (default 1MB)
        :return: dict with upload statistics
        """
        uploader = Uploader(self.config)
        current_chunk = []
        current_size = 2  # accounts for '[' and ']'

        for item in logs:
            # Serialize each item once
            item_str = json.dumps(item, ensure_ascii=False)
            item_size = len(item_str.encode("utf-8"))

            # Add 1 byte if not the first element (comma separator in JSON array)
            if current_chunk:
                item_size += 1

            if current_size + item_size <= max_bytes:
                current_chunk.append(item)
                current_size += item_size
            else:
                # Flush the current chunk
                if current_chunk:
                    uploader.add_to_upload_list(current_chunk)

                # Start a new chunk with this item
                current_chunk = [item]
                current_size = 2 + len(item_str.encode("utf-8"))

        # Flush the last chunk
        if current_chunk:
            uploader.add_to_upload_list(current_chunk)

        # Start uploads
        return uploader.upload_list()

    def upload_data_to_log_analytics_table(self, log_entries) -> dict:
        """Authenticates with Azure before calling the LogIngestionAPI to upload logs."""

        return self._upload_in_chunks(log_entries, self.upload_chunk_size)

    def get_last_update_time(self):
        """upserts a row with last_time_stamp in JobStatus table"""

        table_entity_dict = self.job_state_table_store.get(
            pk="LastRead", rk="RowKey")
        if table_entity_dict is None:
            logging.info(
                "Did not find table %s when retrieving a row. Will create table instead.", self.table_name)
            self.job_state_table_store.create()
            return None
        data = table_entity_dict["data"]
        data_dict = json.loads(data)
        last_time_stamp = data_dict["lastTimeStamp"]
        return last_time_stamp

    def put_last_update_time(self, last_update_time):
        """Updates JobStatus table with last_update_time."""
        data = {
            "lastTimeStamp": last_update_time
        }
        self.job_state_table_store.upsert(
            pk="LastRead", rk="RowKey", data=json.dumps(data))
        logging.info("LastTimeStamp updated to %s",
                     last_update_time)


class FilterType(str, Enum):
    """Permissable filter options for log messages"""
    NONE = 'none'
    ALL = 'all'
    EXCLUDE = 'exclude'
    INCLUDE = 'include'


class MongoDbConnection:
    """Connection object for MongoDB Atlas API"""

    def __init__(self, config, timeout=30):
        # Mongo DB Atlas connection parameters
        self.config = config
        self.mdba_client_id = config.get("mdba_client_id")
        self.mdba_client_secret = config.get("mdba_client_secret")
        self.mdba_group_id = config.get("mdba_group_id")
        self.mdba_cluster_id = config.get("mdba_cluster_id")
        self.mdba_token_url = "https://cloud.mongodb.com/api/oauth/token"
        self.mdba_access_token = None
        self.timeout = timeout  # timeout in seconds
        self.filtered_categories = []
        self.skipped_entries = 0
        self.included_entries = 0
        self.malformed_entries = 0
        self.total_size_downloaded = 0
        self.azure_sentinel_stats = {}
        self.access_ids_to_filter = None
        self.network_ids_to_filter = None
        self.query_ids_to_filter = None

        self.mdba_access_logs_filter_type = config.get(
            "mdba_access_logs_filter_type")
        if self.mdba_access_logs_filter_type not in (None, FilterType.NONE):
            self.filtered_categories.append("ACCESS")
            access_list_input = config.get("mbda_access_list")
            self.access_ids_to_filter = self.parse_ids_list(
                access_list_input, self.mdba_access_logs_filter_type)

        self.mdba_network_logs_filter_type = config.get(
            "mdba_network_logs_filter_type")
        if self.mdba_network_logs_filter_type not in (None, FilterType.NONE):
            self.filtered_categories.append("NETWORK")
            network_list_input = config.get("mdba_network_list")
            self.network_ids_to_filter = self.parse_ids_list(
                network_list_input, self.mdba_network_logs_filter_type)

        self.mdba_query_logs_filter_type = config.get(
            "mdba_query_logs_filter_type")
        if self.mdba_query_logs_filter_type not in (None, FilterType.NONE):
            self.filtered_categories.append("QUERY")
            query_list_input = config.get("mbda_query_list")
            self.query_ids_to_filter = self.parse_ids_list(
                query_list_input, self.mdba_query_logs_filter_type)

    def _encode_credentials(self):
        credentials = f"{self.mdba_client_id}:{self.mdba_client_secret}"
        return base64.b64encode(credentials.encode()).decode()

    def get_access_token(self):
        """Retrieves an access token via OAuth from MongoDB"""

        if self.mdba_access_token:
            return self.mdba_access_token

        headers = {
            "Authorization": f"Basic {self._encode_credentials()}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "client_credentials"
        }

        response = requests.post(
            self.mdba_token_url, headers=headers, data=data, timeout=self.timeout)

        if response.status_code == 200:
            self.mdba_access_token = response.json().get("access_token")
            return self.mdba_access_token
        else:
            logging.error(
                "Failed to get access token: %s %s", response.status_code, response.text)
            raise Exception(
                f"Failed to get access token: {response.status_code} {response.text}"
            )

    def _simplify_datetime_object(self, obj):

        if isinstance(obj, dict) and "$date" in obj:
            try:
                dt = datetime.fromisoformat(
                    obj["$date"].replace("Z", "+00:00"))
                dt_utc = dt.astimezone(timezone.utc)
                return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            except Exception:
                return obj
        return obj

    def _transform_log(self, log_entry):

        transformed = {}
        for key, value in log_entry.items():
            new_key = {
                "s": "severity",
                "c": "category",
                "t": "TimeGenerated"
            }.get(key, key)

            # Special handling for TimeGenerated field (t: {$date: "..."})
            if new_key == "TimeGenerated" and isinstance(value, dict) and "$date" in value:
                value = self._simplify_datetime_object(value)

            transformed[new_key] = value
        return transformed

    def parse_ids_list(self, input_str: str, filter_type: str, max_count: int = 10) -> list[int]:
        """
        Parse a comma-separated string into a list of positive integers.
        Removes spaces/quotes and validates count and positivity.

        Special rule:
        - If the result is an empty list, return ([], True) meaning "do not filter".

        :param input_str: Comma-separated string of numbers, e.g. "1, 2, '3'"
        :param max_count: Maximum number of allowed entries (default: 10)
        :return: list of ints
        :raises ValueError: If invalid, non-numeric, <=0, or too many entries
        """
        result = []
        items = input_str.split(",") if input_str else []

        for item in items:
            cleaned = item.strip().strip("'\"")
            if not cleaned:  # skip empty chunks
                continue
            if not cleaned.isdigit():
                raise ValueError(f"Invalid number: '{cleaned}'")
            num = int(cleaned)
            if num <= 0:
                raise ValueError(f"Number must be positive: {num}")
            result.append(num)

        if len(result) > max_count:
            raise ValueError(
                f"Too many numbers provided. Maximum allowed is {max_count}.")

        if len(result) == 0 and filter_type in (FilterType.INCLUDE, FilterType.EXCLUDE):
            raise ValueError(
                "Filtering requires at least one number."
            )

        return result

    def _should_skip_entry(self, raw_entry: dict) -> bool:
        """Return True if this entry should be skipped based on category and filtering rules."""

        category = raw_entry.get("c", "").upper()
        entry_id = raw_entry.get("id", "")

        # Skip if category not allowed
        if category not in self.filtered_categories:
            return True

        # Category-specific filtering rules
        filter_rules = {
            "ACCESS": (self.mdba_access_logs_filter_type, self.access_ids_to_filter),
            "NETWORK": (self.mdba_network_logs_filter_type, self.network_ids_to_filter),
            "QUERY": (self.mdba_query_logs_filter_type, self.query_ids_to_filter)
        }

        # Apply filtering if category matches a rule
        if category in filter_rules:
            filter_type, filter_ids = filter_rules[category]
            if filter_type == FilterType.INCLUDE and entry_id not in filter_ids:
                return True
            if filter_type == FilterType.EXCLUDE and entry_id in filter_ids:
                return True

        return False

    def get_cluster_logs(self, start_date, end_date) -> dict:
        """
        Retrieves logs from MongoDB Atlas API within a time frame.
        :param start_date: time in seconds since epoch of earliest log message to retrieve.
        :param end_date: time in seconds since epoch of latest log message to retrieve.
        :return JSON object of response status and either log_entries containing all matched log entries or error
        """

        mdba_access_token = self.get_access_token()

        mongodb_url = (
            f"https://cloud.mongodb.com/api/atlas/v2/groups/{self.mdba_group_id}/clusters/{self.mdba_cluster_id}/logs/"
            f"mongodb.gz?startDate={start_date}&endDate={end_date}"
        )

        headers = {
            "Authorization": f"Bearer {mdba_access_token}",
            "Accept": "application/vnd.atlas.2023-02-01+gzip"
        }

        logging.info("mongodb_url: %s", mongodb_url)

        try:
            log_entries = []

            with requests.get(mongodb_url, headers=headers, stream=True, timeout=self.timeout) as response:
                response.raise_for_status()
                logging.info("retrieved response from MongoDB")

                # wrap response.raw (a file-like object) with gzip for streaming decompression
                with gzip.GzipFile(fileobj=response.raw) as gz:
                    for raw_line in gz:
                        self.total_size_downloaded += len(raw_line)
                        # every ~10 MB
                        if self.total_size_downloaded % (10 * 1024 * 1024) < len(raw_line):
                            logging.info(
                                "downloaded so far: %s bytes", self.total_size_downloaded)

                        line = raw_line.decode("utf-8").strip()
                        if not line:
                            continue

                        try:
                            raw_entry = json.loads(line)

                            if self._should_skip_entry(raw_entry):
                                self.skipped_entries += 1
                                continue

                            transformed = self._transform_log(raw_entry)
                            log_entries.append(transformed)
                            self.included_entries += 1

                        except json.JSONDecodeError:
                            self.malformed_entries += 1
                            continue

            return {
                "status": response.status_code,
                "logs": log_entries
            }

        except requests.Timeout:
            logging.error("get_cluster_logs timeout")
            return {"status": "timeout", "error": "The request timed out."}
        except requests.HTTPError as e:
            logging.error("get_cluster_logs http error: %s", str(e))
            return {"status": response.status_code, "error": str(e)}
        except Exception as e:
            logging.error("get_cluster_logs  exception %s", e, exc_info=True)
            return {"status": "error", "error": str(e)}

    def check_for_mdba_log_activity(self):
        """Retrieves logs from MongoDB and sends them to Sentinel"""

        current_time_in_seconds = int(time.time())
        azure_sentinel = AzureSentinel(self.config)

        last_update_time = azure_sentinel.get_last_update_time()
        logging.info("last_update_time: %s, current_time_in_seconds: %s",
                     last_update_time, current_time_in_seconds)

        if last_update_time is None:
            # The first time through, do not retrieve logs. Just record when next log retrieval should start.
            azure_sentinel.put_last_update_time(current_time_in_seconds)
            return
        else:
            start_time = last_update_time + 1

        result = self.get_cluster_logs(start_time, current_time_in_seconds)

        # Check the result
        if result.get("status") == 200:
            logs = result["logs"]

            if len(logs) > 0:
                logging.info(
                    "Calling azure_sentinel.upload_data_to_log_analytics_table with %s rows", len(logs))
                self.azure_sentinel_stats = azure_sentinel.upload_data_to_log_analytics_table(
                    logs)
            else:
                logging.warning("MongoDbConnection. No logs retrieved.")

            azure_sentinel.put_last_update_time(current_time_in_seconds)
        else:
            logging.error(
                "MongoDbConnection.check_for_mdba_log_activity error retrieving logs: %s", result)

    def get_monitoring_statistics(self) -> dict:
        """Health monitoring statistics"""

        return {
            "included_entries": self.included_entries,
            "skipped_entries": self.skipped_entries,
            "malformed_entries": self.malformed_entries,
            "total_size_downloaded": self.total_size_downloaded,
            "azure_sentinel_stats": self.azure_sentinel_stats
        }


def configuration_set_up():
    """environment variable configuration"""

    load_dotenv()  # take environment variables

    config = ConfigStore(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        azure_web_job_storage=os.getenv("AzureWebJobsStorage"),
        azure_client_id=os.getenv("AZURE_CLIENT_ID"),
        azure_client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        azure_dce_endpoint=os.getenv("DCE_ENDPOINT"),
        azure_dcr_immutableid=os.getenv("DCR_IMMUTABLEID"),
        azure_stream_name=os.getenv("STREAM_NAME"),
        azure_main_storage=os.getenv("AZURE_MAIN_STORAGE"),
        azure_max_upload_threads=os.getenv("AZURE_MAX_UPLOAD_THREADS"),
        mdba_client_id=os.getenv("MDBA_CLIENT_ID"),
        mdba_client_secret=os.getenv("MDBA_CLIENT_SECRET"),
        mdba_group_id=os.getenv("MDBA_GROUP_ID"),
        mdba_cluster_id=os.getenv("MDBA_CLUSTER_ID"),
        mdba_access_logs_filter_type=os.getenv("MDBA_ACCESS_LOGS_FILTER_TYPE"),
        mbda_access_list=os.getenv("MDBA_ACCESS_LIST"),
        mdba_network_logs_filter_type=os.getenv(
            "MDBA_NETWORK_LOGS_FILTER_TYPE"),
        mdba_network_list=os.getenv("MDBA_NETWORK_LIST"),
        mdba_query_logs_filter_type=os.getenv("MDBA_QUERY_LOGS_FILTER_TYPE"),
        mdba_query_list=os.getenv("MDBA_QUERY_LIST"),
    )

    mdba_client_id = config.get("mdba_client_id")
    mdba_group_id = config.get("mdba_group_id")
    mdba_cluster_id = config.get("mdba_cluster_id")
    mdba_access_logs_filter_type = config.get("mdba_access_logs_filter_type")
    mbda_access_list = config.get("mbda_access_list")
    mdba_network_logs_filter_type = config.get("mdba_network_logs_filter_type")
    mdba_network_list = config.get("mdba_network_list")
    mdba_query_logs_filter_type = config.get("mdba_query_logs_filter_type")
    mdba_query_list = config.get("mdba_query_list")

    logging.debug("config.mdba_client_id: %s", mdba_client_id)
    logging.debug("config.mdba_group_id: %s", mdba_group_id)
    logging.debug("config.mdba_cluster_id: %s", mdba_cluster_id)
    logging.debug("config.mdba_access_logs_filter_type: %s",
                  mdba_access_logs_filter_type)
    logging.debug("config.mbda_access_list: %s", mbda_access_list)
    logging.debug("config.mdba_network_logs_filter_type: %s",
                  mdba_network_logs_filter_type)
    logging.debug("config.mdba_network_list: %s", mdba_network_list)
    logging.debug("config.mdba_query_logs_filter_type: %s",
                  mdba_query_logs_filter_type)
    logging.debug("config.mdba_query_list: %s", mdba_query_list)

    tenant_id = config.get("tenant_id")
    azure_web_job_storage = config.get("azure_web_job_storage")
    azure_client_id = config.get("azure_client_id")
    azure_dce_endpoint = config.get("azure_dce_endpoint")
    azure_dcr_immutableid = config.get("azure_dcr_immutableid")
    azure_stream_name = config.get("azure_stream_name")
    azure_main_storage = config.get("azure_main_storage")
    azure_max_upload_threads = config.get("azure_max_upload_threads")

    logging.debug("config.tenant_id: %s", tenant_id)
    logging.debug("config.azure_web_job_storage: %s", azure_web_job_storage)
    logging.debug("config.azure_client_id: %s", azure_client_id)
    logging.debug("config.azure_dce_endpoint: %s", azure_dce_endpoint)
    logging.debug("config.azure_dcr_immutableid: %s", azure_dcr_immutableid)
    logging.debug("config.azure_stream_name: %s", azure_stream_name)
    logging.debug("config.azure_main_storage: %s", azure_main_storage)
    logging.info("config.azure_max_upload_threads: %s",
                 azure_max_upload_threads)

    return config


def main(mytimer: func.TimerRequest) -> None:
    """
    Start the execution.

    Args:
        mytimer (func.TimerRequest): This variable will be used to trigger the function.

    """
    utc_timestamp_start = datetime.now()
    logging.info(
        "MongoDB Atlas Connector: Python timer trigger function ran at %s", utc_timestamp_start
    )

    config = configuration_set_up()

    conn = MongoDbConnection(config)

    try:
        conn.check_for_mdba_log_activity()
    except Exception as e:
        print(f"An error occurred: {e}")
        pass

    utc_timestamp_final = datetime.now()
    time_diff = (utc_timestamp_final -
                 utc_timestamp_start).total_seconds()
    time_diff_str = f"{time_diff:.3f}"
    stats = conn.get_monitoring_statistics()
    included_entries = stats.get("included_entries", 0)
    skipped_entries = stats.get("skipped_entries", 0)
    malformed_entries = stats.get("malformed_entries", 0)
    total_entries = included_entries + skipped_entries + malformed_entries
    total_size_downloaded = stats.get("total_size_downloaded", 0)
    azure_sentinel_stats = stats.get("azure_sentinel_stats")
    upload_chunk_count = azure_sentinel_stats.get("upload_chunk_count", 0)
    upload_fail_count = azure_sentinel_stats.get("upload_fail_count", 0)

    logging.info("MongoDBAtlasLogs connector monitoring. start time utc: %s, end time utc: %s, execution time(seconds): %s, total_entries: %s, matching entries: %s, non matching entries: %s, malformed entries: %s, total_size_downloaded: %s, upload_chunk_count: %s, upload_fail_count: %s",
                 utc_timestamp_start.isoformat(), utc_timestamp_final.isoformat(), time_diff_str, total_entries, included_entries, skipped_entries, malformed_entries, total_size_downloaded, upload_chunk_count, upload_fail_count)

    if 'mytimer' in locals():
        if mytimer.past_due:
            logging.info("MongoDB Atlas Connector: The timer is past due.")
