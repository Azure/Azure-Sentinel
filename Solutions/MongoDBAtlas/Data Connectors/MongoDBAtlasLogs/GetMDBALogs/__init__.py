"""This __init__ file will be called once trigger is generated."""
from datetime import datetime, timezone
import logging
import base64
import json
import os
import time
import gzip
from io import BytesIO
from typing import Tuple

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


class AzureSentinel:
    """Microsoft Sentinel client used to post data to log analytics."""

    def __init__(self, config):
        self.config = config
        self.tenant_id = config.get("tenant_id")

        self.azure_dce_endpoint = config.get("azure_dce_endpoint")
        self.azure_dcr_immutableid = config.get("azure_dcr_immutableid")
        self.azure_stream_name = config.get("azure_stream_name")
        self.azure_client_id = config.get("azure_client_id")
        self.azure_main_storage = config.get("azure_main_storage")
        self.upload_chunk_size = 1024 * 1024  # 1MB of data

        connection_string = self.azure_main_storage
        self.table_name = "JobState"
        self.job_state_table_store = JobStateTableStore(
            connection_string, self.table_name)

    def _upload_in_chunks(self, client, logs, max_bytes=1 * 1024 * 1024):
        """
        Splits a JSON array into smaller JSON arrays each ≤ max_bytes in size.

        :param logs: list of JSON-serializable log entries
        :param max_bytes: maximum size per chunk in bytes (default 1MB)
        """
        current_chunk = []

        for item in logs:
            # Test adding the item to the current chunk
            test_chunk = current_chunk + [item]
            chunk_str = json.dumps(test_chunk, ensure_ascii=False)
            chunk_size = len(chunk_str.encode("utf-8"))

            if chunk_size <= max_bytes:
                current_chunk.append(item)
            else:
                # Save current chunk and start a new one
                if current_chunk:
                    try:
                        logging.debug(
                            "Calling client.upload rule_id=%s, stream_name=%s", self.azure_dcr_immutableid, self.azure_stream_name)
                        client.upload(rule_id=self.azure_dcr_immutableid,
                                      stream_name=self.azure_stream_name, logs=current_chunk)
                    except HttpResponseError as e:
                        logging.error("Upload failed: %s", e)

                current_chunk = [item]

        # Add the last chunk if it has data
        if current_chunk:
            logging.debug(
                "Calling client.upload rule_id=%s, stream_name=%s", self.azure_dcr_immutableid, self.azure_stream_name)
            client.upload(rule_id=self.azure_dcr_immutableid,
                          stream_name=self.azure_stream_name, logs=current_chunk)

    def upload_data_to_log_analytics_table(self, json_log):
        """Authenticates with Azure before calling the LogIngestionAPI to upload logs."""

        credential = ManagedIdentityCredential(client_id=self.azure_client_id)

        client = LogsIngestionClient(
            endpoint=self.azure_dce_endpoint, credential=credential, logging_enable=True)

        self._upload_in_chunks(client, json_log, self.upload_chunk_size)

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
        filtered_categories_input = config.get("mdba_category_list")
        allowed_categories = {"ACCESS", "NETWORK", "QUERY"}
        self.filtered_categories = self._parse_categories(
            filtered_categories_input, allowed_categories)

        network_list_input = config.get("mdba_network_list")
        self.network_ids_to_include, self.filter_by_network_id = self.parse_network_ids(
            network_list_input)

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

    def _parse_categories(self, input_str: str, allowed_categories: set) -> list:
        """
        Parse a comma-separated string into a list of categories.
        Removes spaces and quotes, validates against allowed_categories.

        :param input_str: Comma-separated string of categories, e.g. "ACCESS, 'NETWORK', QUERY"
        :param allowed_categories: Set of allowed categories, e.g. {"ACCESS", "NETWORK", "QUERY"}
        :return: List of validated categories
        :raises ValueError: If a category is not in allowed_categories or if no valid values are found
        """
        result = []
        items = input_str.split(",")

        for item in items:
            cleaned = item.strip().strip("'\"")  # remove spaces and quotes
            if not cleaned:  # skip blanks
                continue
            if cleaned not in allowed_categories:
                raise ValueError(f"Invalid category: '{cleaned}'")
            result.append(cleaned)

        if not result:
            raise ValueError("No valid categories provided.")

        return result

    def parse_network_ids(self, input_str: str, max_count: int = 10) -> Tuple[list[int], bool]:
        """
        Parse a comma-separated string into a list of positive integers.
        Removes spaces/quotes and validates count and positivity.

        Special rule:
        - If the result is an empty list, return ([], True) meaning "do not filter".

        :param input_str: Comma-separated string of numbers, e.g. "1, 2, '3'"
        :param max_count: Maximum number of allowed entries (default: 10)
        :return: Tuple (list of ints, bool indicating do-filter if list is empty)
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

        return result, (len(result) > 0)

    def get_cluster_logs(self, start_date, end_date):
        """
        Retrieves logs from MongoDB Atlas API within a time frame.
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
            with requests.get(mongodb_url, headers=headers, stream=True, timeout=self.timeout) as response:
                response.raise_for_status()

                buffer = BytesIO()
                for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB
                    buffer.write(chunk)
                buffer.seek(0)

                with gzip.GzipFile(fileobj=buffer) as gz:
                    ndjson_data = gz.read().decode("utf-8")

                json_lines = []
                skipped_entries = 0
                included_entries = 0
                malformed_entries = 0

                for line in ndjson_data.splitlines():
                    if not line.strip():
                        continue

                    try:
                        raw_entry = json.loads(line)

                        # Skip early if "c" field isn't in the allowed categories
                        if raw_entry.get("c", "").upper() not in self.filtered_categories:
                            skipped_entries += 1
                            continue

                        # Skip early if "c" field is NETWORK and filtering is required and the "id" field is not in the list of network ids to include
                        if raw_entry.get("c", "").upper() == "NETWORK":
                            if self.filter_by_network_id is True and raw_entry.get("id", "").upper() not in self.network_ids_to_include:
                                skipped_entries += 1
                                continue

                        transformed = self._transform_log(raw_entry)
                        json_lines.append(transformed)
                        included_entries += 1

                    except json.JSONDecodeError:
                        malformed_entries += 1
                        continue  # skip malformed lines

                logging.info("MongoDB API returned %s matching entries, %s non matching entries, %s malformed enties",
                             included_entries, skipped_entries, malformed_entries)

                return {
                    "status": response.status_code,
                    "logs": json_lines
                }

        except requests.Timeout:
            logging.error("get_cluster_logs timeout")
            return {"status": "timeout", "error": "The request timed out."}
        except requests.HTTPError as e:
            logging.error("get_cluster_logs http error: %s", str(e))
            return {"status": response.status_code, "error": str(e)}
        except Exception as e:
            logging.error("get_cluster_logs  exeption %s", e)
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
                azure_sentinel.upload_data_to_log_analytics_table(logs)
            else:
                logging.warning("MongoDbConnection. No logs retrieved.")

            azure_sentinel.put_last_update_time(current_time_in_seconds)
        else:
            logging.error(
                "MongoDbConnection.check_for_mdba_log_activity error retrieving logs: %s", result)


def configuration_set_up():
    # environment variable configuration
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
        mdba_client_id=os.getenv("MDBA_CLIENT_ID"),
        mdba_client_secret=os.getenv("MDBA_CLIENT_SECRET"),
        mdba_group_id=os.getenv("MDBA_GROUP_ID"),
        mdba_cluster_id=os.getenv("MDBA_CLUSTER_ID"),
        mdba_network_list=os.getenv("MDBA_NETWORK_LIST"),
        mdba_category_list=os.getenv("MDBA_CATEGORY_LIST")
    )

    mdba_client_id = config.get("mdba_client_id")
    mdba_group_id = config.get("mdba_group_id")
    mdba_cluster_id = config.get("mdba_cluster_id")

    logging.debug("config.mdba_client_id: %s", mdba_client_id)
    logging.debug("config.mdba_group_id: %s", mdba_group_id)
    logging.debug("config.mdba_cluster_id: %s", mdba_cluster_id)

    tenant_id = config.get("tenant_id")
    azure_web_job_storage = config.get("azure_web_job_storage")
    azure_client_id = config.get("azure_client_id")
    azure_dce_endpoint = config.get("azure_dce_endpoint")
    azure_dcr_immutableid = config.get("azure_dcr_immutableid")
    azure_stream_name = config.get("azure_stream_name")
    azure_main_storage = config.get("azure_main_storage")
    mdba_network_list = config.get("mdba_network_list")
    mdba_category_list = config.get("mdba_category_list")

    logging.debug("config.tenant_id: %s", tenant_id)
    logging.debug("config.azure_web_job_storage: %s", azure_web_job_storage)
    logging.debug("config.azure_client_id: %s", azure_client_id)
    logging.debug("config.azure_dce_endpoint: %s", azure_dce_endpoint)
    logging.debug("config.azure_dcr_immutableid: %s", azure_dcr_immutableid)
    logging.debug("config.azure_stream_name: %s", azure_stream_name)
    logging.debug("config.azure_main_storage: %s", azure_main_storage)
    logging.debug("config.mdba_network_list: %s", mdba_network_list)
    logging.debug("config.mdba_category_list: %s", mdba_category_list)

    return config


def main(mytimer: func.TimerRequest) -> None:
    # def main() -> None:
    """
    Start the execution.

    Args:
        mytimer (func.TimerRequest): This variable will be used to trigger the function.

    """
    logging.info(
        "MongoDB Atlas Connector: Python timer trigger function ran at %s",
        datetime.now().isoformat()
    )

    config = configuration_set_up()

    conn = MongoDbConnection(config)

    try:
        conn.check_for_mdba_log_activity()
    except Exception as e:
        print(f"An error occurred: {e}")
        pass

    utc_timestamp_final = datetime.now().isoformat()

    logging.info(
        "MongoDB Atlas Connector: Execution completed at %s.",
        utc_timestamp_final,
    )
    if 'mytimer' in locals():
        if mytimer.past_due:
            logging.info("MongoDB Atlas Connector: The timer is past due.")


# if __name__ == "__main__":
#     main()
