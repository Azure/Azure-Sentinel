"""This __init__ file will be called once trigger is generated."""

from datetime import datetime, timezone
import logging
import base64
import json
import os
import time
import gzip
from enum import Enum
from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor,
    as_completed,
    TimeoutError,
)
from typing import Type, Union

import requests
import azure.functions as func
from azure.core.exceptions import HttpResponseError
from azure.identity import ManagedIdentityCredential
from azure.monitor.ingestion import LogsIngestionClient
from dotenv import load_dotenv

from .job_state_table_store import JobStateTableStore

# Executor type configuration
# For future usage if CPU intensive work is added to the parallelized workers,
# allow switching to the Process Pool to avoid running into GIL.
EXECUTOR_TYPE: Type[Union[ThreadPoolExecutor, ProcessPoolExecutor]] = ThreadPoolExecutor
executor_model_env = os.getenv("EXECUTOR_MODEL")
if executor_model_env and executor_model_env.lower() == "multiprocessing":
    EXECUTOR_TYPE = ProcessPoolExecutor


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


def _upload_worker(azure_dce_endpoint, azure_client_id, rule_id, stream_name, logs):
    """
    Worker function to upload a single chunk of logs.
    This function is defined at the top level to be pickleable for multiprocessing.
    """
    logging.info("Called _upload_worker (logs_count=%d)", len(logs))
    try:
        credential = ManagedIdentityCredential(client_id=azure_client_id)
        client = LogsIngestionClient(
            endpoint=azure_dce_endpoint, credential=credential, logging_enable=True
        )
        client.upload(rule_id=rule_id, stream_name=stream_name, logs=logs)
        return True  # Success
    except HttpResponseError as e:
        logging.error("Upload failed (HttpResponseError): %s", e)
        return False  # Failure
    except Exception as e:
        logging.exception("Upload failed (general): %s", e)
        return False  # Failure


class Uploader:
    """
    Uploads pages of log messages to the Microsoft Sentinel Logs Ingestion API via a client.
    The pages are uploaded in parallel with a given executor, or creates a new one.
    """

    def __init__(self, config, executor, upload_timeout=60):
        self.config = config
        self.azure_dcr_immutableid = config.get("azure_dcr_immutableid")
        self.azure_dce_endpoint = config.get("azure_dce_endpoint")
        self.azure_stream_name = config.get("azure_stream_name")
        self.azure_client_id = config.get("azure_client_id")
        thread_max = config.get("azure_max_upload_threads")
        if not thread_max.isdigit():
            raise ValueError(f"Invalid azure_max_upload_threads: '{thread_max}'")
        azure_max_upload_threads = int(thread_max)

        self.upload_chunk_count = 0
        self.upload_fail_count = 0
        self.jobs = []  # holds futures
        self.executor = executor
        self.upload_timeout = upload_timeout

    def add_to_upload_list(self, chunk):
        future = self.executor.submit(
            _upload_worker,
            self.azure_dce_endpoint,
            self.azure_client_id,
            self.azure_dcr_immutableid,
            self.azure_stream_name,
            chunk,
        )
        self.jobs.append(future)
        return future

    def upload_list(self) -> dict:
        logging.info("Called upload_list")
        try:
            for index, future in enumerate(as_completed(self.jobs), start=1):
                try:
                    future.result(timeout=self.upload_timeout)
                    logging.info("job %s complete", index)
                except TimeoutError:
                    logging.error(
                        "job %s timed out after %s seconds", index, self.upload_timeout
                    )
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
            connection_string, self.table_name
        )
        self.last_read_pk = "LastRead"

    def _process_and_chunk_logs(self, logs, max_bytes=1 * 1024 * 1024) -> dict:
        """
        Splits a list of logs into smaller arrays of logs each ≤ max_bytes in size.
        It performs a size check assuming each object is serialized to a JSON formatted string when uploaded
        to the Log Ingestion API.

        :param logs: list of JSON-serializable log entries
        :param max_bytes: maximum size per chunk in bytes (default 1MB)
        :return: dict with upload statistics
        """
        chunks = []
        current_chunk = []
        current_size = 2  # accounts for '[' and ']'
        chunking_start_time = int(time.time())
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
                    chunks.append(current_chunk)

                # Start a new chunk with this item
                current_chunk = [item]
                current_size = 2 + len(item_str.encode("utf-8"))

        # Flush the last chunk
        if current_chunk:
            chunks.append(current_chunk)

        chunking_end_time = int(time.time())
        logging.info(
            "Time spent chunking logs: %d", chunking_end_time - chunking_start_time
        )

        return chunks

    def upload_data_to_log_analytics_table(self, log_entries) -> dict:
        """Authenticates with Azure before calling the LogIngestionAPI to upload logs."""

        return self._upload_in_chunks(log_entries, self.upload_chunk_size)

    def get_last_update_time(self, cluster_id):
        """
        Gets the last timestamp in the JobStatus table for a specific cluster_id.
        Each cluster has its own row: PartitionKey="LastRead", RowKey=cluster_id
        """
        logging.info("[Cluster %s] Retrieving LastTimeStamp", cluster_id)
        table_entity_dict = self.job_state_table_store.get(
            pk=self.last_read_pk, rk=cluster_id
        )
        if table_entity_dict is None:
            logging.info(
                "[Cluster %s] Did not find row in table %s (first run for this cluster).",
                cluster_id,
                self.table_name,
            )
            return None

        data = table_entity_dict.get("data")
        if data is None:
            return None

        data_dict = json.loads(data)
        last_time_stamp = data_dict.get("lastTimeStamp")

        return last_time_stamp

    def put_last_update_time(self, cluster_id, last_update_time):
        """
        Updates JobStatus table with last_update_time for a specific cluster_id.
        Each cluster has its own row: PartitionKey="LastRead", RowKey=cluster_id
        """

        logging.info(
            "[Cluster %s] Updating LastTimeStamp to %s", cluster_id, last_update_time
        )
        data = {"lastTimeStamp": last_update_time}

        try:
            self.job_state_table_store.upsert(
                pk=self.last_read_pk, rk=cluster_id, data=json.dumps(data)
            )
            logging.info(
                "[Cluster %s] LastTimeStamp updated to %s", cluster_id, last_update_time
            )
        except Exception as e:
            # Table might not exist, create it and retry
            logging.info(
                "[Cluster %s] Failed to upsert entry, table might not exist. Will create table and retry: %s",
                cluster_id,
                e,
            )
            self.job_state_table_store.create()
            self.job_state_table_store.upsert(
                pk=self.last_read_pk, rk=cluster_id, data=json.dumps(data)
            )
            logging.info(
                "[Cluster %s] LastTimeStamp updated to %s (after creating table)"
            )


class FilterType(str, Enum):
    """Permissible filter options for log messages"""

    NONE = "none"
    ALL = "all"
    EXCLUDE = "exclude"
    INCLUDE = "include"


class MongoDbConnection:
    """Connection object for MongoDB Atlas API"""

    def __init__(self, config, timeout=30):
        # Mongo DB Atlas connection parameters
        self.config = config
        self.mdba_client_id = config.get("mdba_client_id")
        self.mdba_client_secret = config.get("mdba_client_secret")

        # Debugging: Log credentials at the moment of object creation
        client_id_to_log = self.mdba_client_id
        client_secret_to_log = (
            (self.mdba_client_secret[:4] + "...") if self.mdba_client_secret else "None"
        )
        logging.info(
            f"MongoDbConnection initialized with Client ID: '{client_id_to_log}' and Client Secret starting with: '{client_secret_to_log}'"
        )

        self.mdba_group_id = config.get("mdba_group_id")
        self.mdba_cluster_ids = config.get("mdba_cluster_ids")
        self.mdba_token_url = "https://cloud.mongodb.com/api/oauth/token"
        self.mdba_access_token = None
        self.timeout = timeout  # timeout in seconds
        self.filtered_categories = []
        self.skipped_entries = 0
        self.included_entries = 0
        self.malformed_entries = 0
        self.total_size_downloaded = 0
        self.cluster_size_downloaded = {}
        self.azure_sentinel_stats = {}
        self.access_ids_to_filter = None
        self.network_ids_to_filter = None
        self.query_ids_to_filter = None

        self.mdba_access_logs_filter_type = config.get("mdba_access_logs_filter_type")
        if self.mdba_access_logs_filter_type not in (None, FilterType.NONE):
            self.filtered_categories.append("ACCESS")
            access_list_input = config.get("mdba_access_list")
            self.access_ids_to_filter = self.parse_ids_list(
                access_list_input, self.mdba_access_logs_filter_type
            )

        self.mdba_network_logs_filter_type = config.get("mdba_network_logs_filter_type")
        if self.mdba_network_logs_filter_type not in (None, FilterType.NONE):
            self.filtered_categories.append("NETWORK")
            network_list_input = config.get("mdba_network_list")
            self.network_ids_to_filter = self.parse_ids_list(
                network_list_input, self.mdba_network_logs_filter_type
            )

        self.mdba_query_logs_filter_type = config.get("mdba_query_logs_filter_type")
        if self.mdba_query_logs_filter_type not in (None, FilterType.NONE):
            self.filtered_categories.append("QUERY")
            query_list_input = config.get("mdba_query_list")
            self.query_ids_to_filter = self.parse_ids_list(
                query_list_input, self.mdba_query_logs_filter_type
            )

    def _encode_credentials(self):
        credentials = f"{self.mdba_client_id}:{self.mdba_client_secret}"
        return base64.b64encode(credentials.encode()).decode()

    def get_access_token(self):
        """Retrieves an access token via OAuth from MongoDB"""

        if self.mdba_access_token:
            return self.mdba_access_token

        headers = {
            "Authorization": f"Basic {self._encode_credentials()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {"grant_type": "client_credentials"}

        response = requests.post(
            self.mdba_token_url, headers=headers, data=data, timeout=self.timeout
        )

        if response.status_code == 200:
            self.mdba_access_token = response.json().get("access_token")
            return self.mdba_access_token
        else:
            logging.error(
                "Failed to get access token: %s %s", response.status_code, response.text
            )
            raise Exception(
                f"Failed to get access token: {response.status_code} {response.text}"
            )

    def _simplify_datetime_object(self, obj):

        if isinstance(obj, dict) and "$date" in obj:
            try:
                dt = datetime.fromisoformat(obj["$date"].replace("Z", "+00:00"))
                dt_utc = dt.astimezone(timezone.utc)
                return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            except Exception:
                return obj
        return obj

    def _transform_log(self, log_entry, cluster_id):

        transformed = {}
        for key, value in log_entry.items():

            # TimeGenerated kept in Pascal case to match with Sentinel usage
            new_key = {"s": "severity", "c": "category", "t": "TimeGenerated"}.get(
                key, key
            )

            # Special handling for TimeGenerated field (t: {$date: "..."})
            if (
                new_key == "TimeGenerated"
                and isinstance(value, dict)
                and "$date" in value
            ):
                value = self._simplify_datetime_object(value)

            transformed[new_key] = value
            # clusterId kept as camel case to stay consistent with other MongoDB fields
            transformed["clusterId"] = cluster_id

        return transformed

    def parse_ids_list(
        self, input_str: str, filter_type: str, max_count: int = 10
    ) -> list[int]:
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
                f"Too many numbers provided. Maximum allowed is {max_count}."
            )

        if len(result) == 0 and filter_type in (FilterType.INCLUDE, FilterType.EXCLUDE):
            raise ValueError("Filtering requires at least one number.")

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
            "QUERY": (self.mdba_query_logs_filter_type, self.query_ids_to_filter),
        }

        # Apply filtering if category matches a rule
        if category in filter_rules:
            filter_type, filter_ids = filter_rules[category]
            if filter_type == FilterType.INCLUDE and entry_id not in filter_ids:
                return True
            if filter_type == FilterType.EXCLUDE and entry_id in filter_ids:
                return True

        return False

    def get_cluster_logs(self, cluster_id, start_date, end_date) -> dict:
        """
        Retrieves logs from MongoDB Atlas API within a time frame for a specific cluster.
        :param cluster_id: the MongoDB cluster ID to fetch logs from.
        :param start_date: time in seconds since epoch of earliest log message to retrieve.
        :param end_date: time in seconds since epoch of latest log message to retrieve.
        :return JSON object of response status and either log_entries containing all matched log entries or error
        """

        mdba_access_token = self.get_access_token()

        mongodb_url = (
            f"https://cloud.mongodb.com/api/atlas/v2/groups/{self.mdba_group_id}/clusters/{cluster_id}/logs/"
            f"mongodb.gz?startDate={start_date}&endDate={end_date}"
        )

        headers = {
            "Authorization": f"Bearer {mdba_access_token}",
            "Accept": "application/vnd.atlas.2023-02-01+gzip",
        }

        logging.info("[Cluster %s] mongodb_url: %s", cluster_id, mongodb_url)

        try:
            log_entries = []
            cluster_bytes = 0

            with requests.get(
                mongodb_url, headers=headers, stream=True, timeout=self.timeout
            ) as response:
                response.raise_for_status()
                logging.info("[Cluster %s] Retrieved response from MongoDB", cluster_id)

                # wrap response.raw (a file-like object) with gzip for streaming decompression
                with gzip.GzipFile(fileobj=response.raw) as gz:
                    for raw_line in gz:
                        line_size = len(raw_line)
                        self.total_size_downloaded += line_size
                        cluster_bytes += line_size
                        # every ~10 MB
                        if self.total_size_downloaded % (10 * 1024 * 1024) < line_size:
                            logging.info(
                                "[Cluster %s] Downloaded so far: %s bytes",
                                cluster_id,
                                self.total_size_downloaded,
                            )

                        line = raw_line.decode("utf-8").strip()
                        if not line:
                            continue

                        try:
                            raw_entry = json.loads(line)

                            if self._should_skip_entry(raw_entry):
                                self.skipped_entries += 1
                                continue

                            transformed = self._transform_log(raw_entry, cluster_id)
                            log_entries.append(transformed)
                            self.included_entries += 1

                        except json.JSONDecodeError:
                            self.malformed_entries += 1
                            continue
            self.cluster_size_downloaded[cluster_id] = cluster_bytes
            logging.info("[Cluster %s] Downloaded %d bytes", cluster_id, cluster_bytes)
            return {"status": response.status_code, "logs": log_entries}

        except requests.Timeout:
            logging.error("get_cluster_logs timeout")
            return {"status": "timeout", "error": "The request timed out."}
        except requests.HTTPError as e:
            logging.error("get_cluster_logs http error: %s", str(e))
            return {"status": response.status_code, "error": str(e)}
        except Exception as e:
            logging.error("get_cluster_logs  exception %s", e, exc_info=True)
            return {"status": "error", "error": str(e)}

    def submit_cluster_fetch_jobs(self, executor, azure_sentinel):
        """
        Submits fetch jobs for all clusters to the executor.
        Determines individual time ranges for each cluster and submits fetch futures.

        :param executor: The executor pool to submit jobs to.
        :param azure_sentinel: The AzureSentinel instance for timestamp management.
        :return: dict with future_to_cluster mapping, cluster_time_ranges, and current_time.
        """
        current_time_in_seconds = int(time.time())
        cluster_time_ranges = {}

        for cluster_id in self.mdba_cluster_ids:
            last_update_time = azure_sentinel.get_last_update_time(cluster_id)
            logging.info(
                f"[Cluster %s] last_update_time: %s, current_time_in_seconds: %s",
                cluster_id,
                last_update_time,
                current_time_in_seconds,
            )

            if last_update_time is None:
                # First time through, do not retrieve logs and initialize timestamp only
                azure_sentinel.put_last_update_time(cluster_id, current_time_in_seconds)
                logging.info(
                    "[Cluster %s] First run. Timestamp initialized to %s",
                    cluster_id,
                    current_time_in_seconds,
                )
            else:
                # Each cluster gets its own time range based on its last update
                start_time = last_update_time + 1
                cluster_time_ranges[cluster_id] = (start_time, current_time_in_seconds)

        # Early exit if there are no logs to retrieve
        if not cluster_time_ranges:
            logging.info("No clusters ready for log retrieval yet (first run).")
            return {
                "future_to_cluster": {},
                "cluster_time_ranges": {},
                "current_time_in_seconds": current_time_in_seconds,
            }

        logging.info(
            "Submitting parallel log fetch jobs for %d clusters",
            len(cluster_time_ranges),
        )

        # Submit all cluster log fetch jobs with their respective time ranges
        future_to_cluster = {
            executor.submit(
                self.get_cluster_logs, cluster_id, start_time, end_time
            ): cluster_id
            for cluster_id, (start_time, end_time) in cluster_time_ranges.items()
        }

        return {
            "future_to_cluster": future_to_cluster,
            "cluster_time_ranges": cluster_time_ranges,
            "current_time_in_seconds": current_time_in_seconds,
        }

    def _process_fetch_results(
        self,
        future,
        cluster_id,
        uploader,
        azure_sentinel,
        current_time_in_seconds,
        cluster_upload_futures,
        cluster_fetch_stats,
    ):
        """
        Process a completed fetch future for a cluster.
        If successful, immediately queues upload job for the fetched logs.

        :param future: The completed fetch future.
        :param cluster_id: The cluster this fetch belongs to.
        :param uploader: The Uploader instance to queue uploads.
        :param azure_sentinel: The AzureSentinel instance for timestamp updates.
        :param current_time_in_seconds: Timestamp to use for updates.
        :param cluster_upload_futures: Dict to store upload futures per cluster.
        :param cluster_fetch_stats: Dict to store fetch stats.
        """

        try:
            result = future.result(timeout=self.timeout)
            cluster_fetch_stats[cluster_id] = result

            if result.get("status") == 200:
                logs = result.get("logs", [])
                logging.info(
                    "[Cluster %s] Successfully fetched %d logs.", cluster_id, len(logs)
                )

                # Immediately chunk and queue uploads for this cluster's logs
                if logs:
                    chunks = azure_sentinel._process_and_chunk_logs(logs)
                    logging.info(
                        "[Cluster %s] Queueing %d upload chunks.",
                        cluster_id,
                        len(chunks),
                    )
                    cluster_upload_futures[cluster_id] = []
                    for chunk in chunks:
                        upload_future = uploader.add_to_upload_list(chunk)
                        cluster_upload_futures[cluster_id].append(upload_future)
                else:
                    # No logs fetched, simple update timestamp
                    azure_sentinel.put_last_update_time(
                        cluster_id, current_time_in_seconds
                    )
                    logging.info(
                        "[Cluster %s] No logs. Last timestamp updated to %s",
                        cluster_id,
                        current_time_in_seconds,
                    )
            else:
                logging.error(
                    "[Cluster %s] Failed to fetch logs: %s",
                    cluster_id,
                    result.get("error", "Unknown error"),
                )
        except TimeoutError:
            logging.error("[Cluster %s] Timed out fetching logs", cluster_id)
            cluster_fetch_stats[cluster_id] = {
                "status": "timeout",
                "error": "Request timed out",
            }
        except Exception as e:
            logging.exception("[Cluster %s] Exception fetching logs: %s", cluster_id, e)
            cluster_fetch_stats[cluster_id] = {"status": "error", "error": str(e)}

    def _process_upload_results(
        self, cluster_upload_futures, uploader, azure_sentinel, current_time_in_seconds
    ):
        """
        Wait for all upload jobs to complete and update timestamps for successful clusters.

        :param cluster_upload_futures: Dict mapping cluster_id to list of upload futures.
        :param azure_sentinel: The AzureSentinel instance for timestamp management.
        :param current_time_in_seconds: The Timestamp to use for updates
        :return: Tuple of (upload_chunk_count, upload_fail_count)
        """

        upload_chunk_count = 0
        upload_fail_count = 0

        total_upload_futures = sum(
            len(futures) for futures in cluster_upload_futures.values()
        )
        logging.info("Waiting for %d upload jobs to finish", total_upload_futures)

        for cluster_id, upload_futures in cluster_upload_futures.items():
            cluster_upload_success = True
            for upload_future in upload_futures:
                try:
                    success = upload_future.result(timeout=uploader.upload_timeout)
                    if success:
                        upload_chunk_count += 1
                        logging.debug("[Cluster %s] Upload chunk complete.", cluster_id)
                    else:
                        upload_fail_count += 1
                        cluster_upload_success = False
                        logging.warning(
                            "[Cluster %s] Upload chunk failed (handled in worker).",
                            cluster_id,
                        )
                except TimeoutError:
                    logging.error("[Cluster %s] Upload timed out.", cluster_id)
                    upload_fail_count += 1
                    cluster_upload_success = False
                except Exception as e:
                    logging.exception(
                        "[Cluster %s] Upload failed with unexpected exception: %s",
                        cluster_id,
                        e,
                    )
                    upload_fail_count += 1
                    cluster_upload_success = False

            # Only update timestamp if all uploads for this cluster succeeded
            if cluster_upload_success and len(upload_futures) > 0:
                azure_sentinel.put_last_update_time(cluster_id, current_time_in_seconds)
                logging.info(
                    "[Cluster %s] All uploads succeeded. Timestamp updated to %s.",
                    cluster_id,
                    current_time_in_seconds,
                )
            elif not cluster_upload_success:
                logging.warning(
                    "[Cluster %s] Some uploads failed. Timestamp not updated - will retry on next run.",
                    cluster_id,
                )

        return upload_chunk_count, upload_fail_count

    def check_for_mdba_log_activity(self):
        """
        Retrieves logs from MongoDB and sends them to Sentinel

        Orchestrates the complete log fetch and upload workflow:
        - Submit fetch jobs for all clusters to executor.
        - As fetch jobs complete, queue upload jobs for that cluster.
        - Wait for all upload jobs to complete.
        - Update last timestamps for clusters that have successfully completed all uploads.
        """

        azure_sentinel = AzureSentinel(self.config)
        # Set max workers to be at most 20 -> 10 max clusters for each fetch + upload
        max_workers = min(len(self.mdba_cluster_ids) + 10, 20)
        cluster_fetch_stats = {}
        cluster_upload_futures = {}

        with EXECUTOR_TYPE(max_workers=max_workers) as executor:
            uploader = Uploader(self.config, executor=executor)

            # Submit all fetch jobs
            fetch_info = self.submit_cluster_fetch_jobs(executor, azure_sentinel)
            future_to_cluster = fetch_info["future_to_cluster"]
            current_time_in_seconds = fetch_info["current_time_in_seconds"]

            if not future_to_cluster:
                logging.info("No fetch jobs to process.")
                return

            logging.info("Processing %d fetch jobs", len(future_to_cluster))

            # Process fetch results as they complete and immediately queue uploads
            for future in as_completed(future_to_cluster):
                cluster_id = future_to_cluster[future]
                self._process_fetch_results(
                    future,
                    cluster_id,
                    uploader,
                    azure_sentinel,
                    current_time_in_seconds,
                    cluster_upload_futures,
                    cluster_fetch_stats,
                )

            # Wait for all upload jobs to complete and update timestamps on successful clusters
            upload_chunk_count, upload_fail_count = self._process_upload_results(
                cluster_upload_futures,
                uploader,
                azure_sentinel,
                current_time_in_seconds,
            )

        # Store upload stats
        self.azure_sentinel_stats = {
            "upload_chunk_count": upload_chunk_count,
            "upload_fail_count": upload_fail_count,
        }

        # Log upload summary
        logging.info(
            "Upload complete: %d chunks succeeded, %d chunks failed",
            upload_chunk_count,
            upload_fail_count,
        )
        for cluster_id, stats in cluster_fetch_stats.items():
            logging.info(
                "[Cluster %s] Fetch results: %s", cluster_id, stats.get("status")
            )

    def get_monitoring_statistics(self) -> dict:
        """Health monitoring statistics"""

        return {
            "included_entries": self.included_entries,
            "skipped_entries": self.skipped_entries,
            "malformed_entries": self.malformed_entries,
            "total_size_downloaded": self.total_size_downloaded,
            "cluster_size_downloaded": self.cluster_size_downloaded,
            "azure_sentinel_stats": self.azure_sentinel_stats,
        }


def _parse_cluster_ids(raw_cluster_ids):
    logging.info("Parsing ClusterIds from: %s", repr(raw_cluster_ids))
    cluster_ids = [
        cid.strip()
        for cid in raw_cluster_ids.replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace(" ", "\n")
        .split("\n")
        if cid.strip()
    ]
    if not cluster_ids:
        raise ValueError("MDBA_CLUSTER_ID must contain at least one cluster ID")

    logging.info("Parsed cluster IDs: %s", cluster_ids)

    return cluster_ids


from azure.keyvault.secrets import SecretClient


def configuration_set_up():
    """environment variable configuration"""

    load_dotenv()  # take environment variables

    # Fetch the secret from Key Vault
    key_vault_uri = os.getenv("KEY_VAULT_URI")
    secret_name = os.getenv("MDBA_SECRET_NAME")
    azure_client_id = os.getenv("AZURE_CLIENT_ID")

    mdba_client_secret = None
    if key_vault_uri and secret_name and azure_client_id:
        try:
            credential = ManagedIdentityCredential(client_id=azure_client_id)
            secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)
            retrieved_secret = secret_client.get_secret(secret_name)
            mdba_client_secret = retrieved_secret.value
            logging.info("Successfully retrieved secret from Key Vault.")
        except Exception as e:
            logging.error(f"Failed to retrieve secret from Key Vault: {e}")
            # Depending on requirements, you might want to raise the exception
            # raise e
    else:
        logging.warning(
            "Key Vault URI, Secret Name, or Azure Client ID is not configured. Trying to fall back to direct environment variable."
        )
        mdba_client_secret = os.getenv("MDBA_CLIENT_SECRET")

    config = ConfigStore(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        azure_web_job_storage=os.getenv("AzureWebJobsStorage"),
        azure_client_id=azure_client_id,
        azure_client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        azure_dce_endpoint=os.getenv("DCE_ENDPOINT"),
        azure_dcr_immutableid=os.getenv("DCR_IMMUTABLEID"),
        azure_stream_name=os.getenv("STREAM_NAME"),
        azure_main_storage=os.getenv("AZURE_MAIN_STORAGE"),
        azure_max_upload_threads=os.getenv("AZURE_MAX_UPLOAD_THREADS"),
        mdba_client_id=os.getenv("MDBA_CLIENT_ID"),
        mdba_client_secret=mdba_client_secret,
        mdba_group_id=os.getenv("MDBA_GROUP_ID"),
        mdba_cluster_ids=_parse_cluster_ids(os.getenv("MDBA_CLUSTER_ID")),
        mdba_access_logs_filter_type=os.getenv("MDBA_ACCESS_LOGS_FILTER_TYPE"),
        mdba_access_list=os.getenv("MDBA_ACCESS_LIST"),
        mdba_network_logs_filter_type=os.getenv("MDBA_NETWORK_LOGS_FILTER_TYPE"),
        mdba_network_list=os.getenv("MDBA_NETWORK_LIST"),
        mdba_query_logs_filter_type=os.getenv("MDBA_QUERY_LOGS_FILTER_TYPE"),
        mdba_query_list=os.getenv("MDBA_QUERY_LIST"),
    )

    mdba_client_id = config.get("mdba_client_id")
    mdba_group_id = config.get("mdba_group_id")
    mdba_access_logs_filter_type = config.get("mdba_access_logs_filter_type")
    mdba_access_list = config.get("mdba_access_list")
    mdba_network_logs_filter_type = config.get("mdba_network_logs_filter_type")
    mdba_network_list = config.get("mdba_network_list")
    mdba_query_logs_filter_type = config.get("mdba_query_logs_filter_type")
    mdba_query_list = config.get("mdba_query_list")

    logging.debug("config.mdba_client_id: %s", mdba_client_id)
    logging.debug("config.mdba_group_id: %s", mdba_group_id)
    logging.debug(
        "config.mdba_access_logs_filter_type: %s", mdba_access_logs_filter_type
    )
    logging.debug("config.mdba_access_list: %s", mdba_access_list)
    logging.debug(
        "config.mdba_network_logs_filter_type: %s", mdba_network_logs_filter_type
    )
    logging.debug("config.mdba_network_list: %s", mdba_network_list)
    logging.debug("config.mdba_query_logs_filter_type: %s", mdba_query_logs_filter_type)
    logging.debug("config.mdba_query_list: %s", mdba_query_list)

    tenant_id = config.get("tenant_id")
    azure_web_job_storage = config.get("azure_web_job_storage")
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
    logging.info("config.azure_max_upload_threads: %s", azure_max_upload_threads)

    return config


def main(mytimer: func.TimerRequest = None) -> None:
    """
    Start the execution.

    Args:
        mytimer (func.TimerRequest): This variable will be used to trigger the function.

    """
    utc_timestamp_start = datetime.now()

    # Log the selected executor model
    if EXECUTOR_TYPE == ProcessPoolExecutor:
        logging.info("Using ProcessPoolExecutor for concurrency.")
    else:
        logging.info("Using ThreadPoolExecutor for concurrency.")

    logging.info(
        "MongoDB Atlas Connector: Python timer trigger function ran at %s",
        utc_timestamp_start,
    )

    config = configuration_set_up()

    conn = MongoDbConnection(config)

    try:
        conn.check_for_mdba_log_activity()
    except Exception as e:
        logging.error("An error occurred: %s", e)

    utc_timestamp_final = datetime.now()
    time_diff = (utc_timestamp_final - utc_timestamp_start).total_seconds()
    time_diff_str = f"{time_diff:.3f}"
    stats = conn.get_monitoring_statistics()
    included_entries = stats.get("included_entries", 0)
    skipped_entries = stats.get("skipped_entries", 0)
    malformed_entries = stats.get("malformed_entries", 0)
    total_entries = included_entries + skipped_entries + malformed_entries
    total_size_downloaded = stats.get("total_size_downloaded", 0)
    cluster_size_downloaded = stats.get("cluster_size_downloaded", {})
    azure_sentinel_stats = stats.get("azure_sentinel_stats")
    upload_chunk_count = azure_sentinel_stats.get("upload_chunk_count", 0)
    upload_fail_count = azure_sentinel_stats.get("upload_fail_count", 0)

    logging.info(
        "MongoDBAtlasLogs connector monitoring. start time utc: %s, end time utc: %s, execution time(seconds): %s, total_entries: %s, matching entries: %s, non matching entries: %s, malformed entries: %s, total_size_downloaded: %s, upload_chunk_count: %s, upload_fail_count: %s",
        utc_timestamp_start.isoformat(),
        utc_timestamp_final.isoformat(),
        time_diff_str,
        total_entries,
        included_entries,
        skipped_entries,
        malformed_entries,
        total_size_downloaded,
        upload_chunk_count,
        upload_fail_count,
    )

    if cluster_size_downloaded:
        for cluster, downloaded in cluster_size_downloaded.items():
            logging.info("[Cluster %s] Total size downloaded: %s", cluster, downloaded)

    if mytimer and "mytimer" in locals():
        if mytimer.past_due:
            logging.info("MongoDB Atlas Connector: The timer is past due.")
