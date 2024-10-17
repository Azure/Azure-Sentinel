"""Get mimecast cg data and ingest to custom table in sentinel."""

import inspect
import json
import time
from random import randrange
import gzip
import aiohttp
import asyncio
from aiohttp.client_exceptions import (
    ClientError,
    ServerTimeoutError,
    ClientResponseError,
)
from ..SharedCode import consts
from ..SharedCode.mimecast_exception import MimecastException, MimecastTimeoutException
from ..SharedCode.logger import applogger
from ..SharedCode.state_manager import StateManager
from ..SharedCode.utils import Utils
from ..SharedCode.sentinel import post_data_async
from tenacity import RetryError


class MimecastCGToSentinel(Utils):
    """Class for ingest cg the data from mimecast to sentinel."""

    def __init__(self, start_time) -> None:
        """Initialize MimecastDLPToSentinel object."""
        super().__init__(consts.SEG_CG_FUNCTION_NAME)
        self.check_environment_var_exist(
            [
                {"Base_Url": consts.BASE_URL},
                {"WorkspaceID": consts.WORKSPACE_ID},
                {"WorkspaceKey": consts.WORKSPACE_KEY},
                {"Mimecast_Client_ID": consts.MIMECAST_CLIENT_ID},
                {"Mimecast_Client_Secret": consts.MIMECAST_CLIENT_SECRET},
            ]
        )
        self.authenticate_mimecast_api()
        self.start = start_time
        self.checkpoint_obj = StateManager(
            consts.CONN_STRING, "Checkpoint-SEG-CG", consts.FILE_SHARE_NAME
        )

    async def get_mimecast_cg_data_in_sentinel(self):
        """Get mimecast cg data and ingest data to sentinel, initialization method."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Start fetching cg endpoint data using batch and async",
                )
            )
            await self.get_batch_data_urls_from_api()
        except MimecastTimeoutException:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Mimecast: 9:00 mins executed hence breaking.",
                )
            )
            return
        except MimecastException:
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()

    async def get_batch_data_urls_from_api(self):
        """Retrieve a list of URLs from the Mimecast CG API and processes them.

        This function retrieve a list of URLs from the Mimecast CG API by making a GET request to the
        SEG_CG endpoint. It iterate through the response pages and retrieves the URLs from each page.
        The function then process the URLs and ingest data in sentinel by calling the `process_s3_bucket_urls` method.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            checkpoint_data = self.get_checkpoint_data(self.checkpoint_obj)
            next_page = None
            if checkpoint_data:
                next_page = checkpoint_data.get("nextPage")
            else:
                checkpoint_data = {}
            url = "{}{}".format(consts.BASE_URL, consts.ENDPOINTS["SEG_CG"])

            params = {"type": consts.SEG_CG_TYPES, "pageSize": consts.ASYNC_PAGE_SIZE}
            page = 1
            while True:
                if int(time.time()) >= self.start + consts.FUNCTION_APP_TIMEOUT_SECONDS:
                    raise MimecastTimeoutException()
                if next_page:
                    params["nextPage"] = next_page
                applogger.debug(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Params = {}, url = {}, page {}".format(params, url, page),
                    )
                )
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Iterating page {}".format(page),
                    )
                )
                response = self.make_rest_call(method="GET", url=url, params=params)
                next_page = response.get("@nextPage")
                values = response.get("value")
                if not values:
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "No more data to fetch",
                        )
                    )
                    break

                url_list = [val.get("url") for val in values]

                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Found {} urls in response in page {}".format(
                            len(url_list), page
                        ),
                    )
                )
                result = await self.process_s3_bucket_urls(url_list, page)
                applogger.debug(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Next token = {}".format(next_page),
                    )
                )
                if result:
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Complete processing s3 bucket urls for page {}".format(
                                page
                            ),
                        )
                    )
                    checkpoint_data.update({"nextPage": next_page})
                    self.post_checkpoint_data(self.checkpoint_obj, checkpoint_data)
                else:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "An error occurred while fetching data,"
                            "Please ensure that the Sentinel credentials are correct",
                        )
                    )
                    raise MimecastException()
                page += 1

        except MimecastTimeoutException:
            raise MimecastTimeoutException()
        except RetryError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.MAX_RETRY_ERROR_MSG.format(
                        error, error.last_attempt.exception()
                    ),
                )
            )
            raise MimecastException()
        except MimecastException:
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()

    async def process_s3_bucket_urls(self, url_list, page):
        """Process a list of S3 bucket URLs.

        Args:
            url_list (List[str]): A list of S3 bucket URLs.
            page (int): page number

        Returns:
            bool: True if all tasks are completed.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                for index, url in enumerate(url_list):
                    task = asyncio.create_task(
                        self.fetch_unzip_and_ingest_s3_url_data(index + 1, session, url)
                    )
                    tasks.append(task)
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "{} tasks created for page {}".format(len(tasks), page),
                    )
                )
                results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = 0
            for result in results:
                if result is True:
                    success_count += 1
            if success_count == 0 and len(url_list) > 0:
                return False
            if success_count == len(url_list):
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "All tasks are completed successfully for page {}".format(page),
                    )
                )
            else:
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "{} tasks failed for page {}".format(
                            (len(url_list) - success_count), page
                        ),
                    )
                )
            return True
        except MimecastException:
            raise MimecastException()
        except aiohttp.ClientError as session_err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.CLIENT_ERROR_MSG.format(
                        "Error creating aiohttp.ClientSession: {} for page {}".format(
                            session_err, page
                        )
                    ),
                )
            )
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(
                        "{} for page {}".format(err, page)
                    ),
                )
            )
            raise MimecastException()

    def handle_corrupt_data(self, index, obj, corrupt_data):
        """Handle corrupt data by appending it to the corrupt_data list.

        Args:
            index (int): The index of the task.
            obj: The object to be handled.
            corrupt_data (list): A list to store corrupt data.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            corrupt_data.append(str(obj))
        except TypeError as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.TYPE_ERROR_MSG.format(
                        "{}, for task = {}".format(err, index)
                    ),
                )
            )

    async def decompress_and_make_json(self, index, response):
        """Decompress and convert the content of a response to a list of JSON objects.

        Args:
            index (int): The task index.
            response (aiohttp.ClientResponse): The response object.

        Returns:
            list: A list of JSON objects.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Read zip, Decompress zip and make json from events for task {}".format(
                        index
                    ),
                )
            )
            gzipped_content = await response.read()
            decompressed_data = gzip.decompress(gzipped_content)
            decompressed_content = decompressed_data.decode("utf-8", errors="replace")
            json_objects = []
            corrupt_data = []
            for obj in decompressed_content.splitlines():
                try:
                    obj = obj.strip()
                    if obj:
                        json_objects.append(json.loads(obj))
                except json.JSONDecodeError:
                    self.handle_corrupt_data(index, obj, corrupt_data)
                    continue
            if corrupt_data:
                curent_corrupt_data_obj = StateManager(
                    consts.CONN_STRING,
                    "Corrupt-Data-Cloud-Gateway_{}".format(str(int(time.time()))),
                    consts.FILE_SHARE_NAME,
                )
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Posting corrupted data into checkpoint file for task: {}".format(
                            index
                        ),
                    )
                )
                self.post_checkpoint_data(curent_corrupt_data_obj, corrupt_data)
            return json_objects
        except MimecastException:
            raise MimecastException()
        except aiohttp.ClientError as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.CLIENT_ERROR_MSG.format(
                        "Error reading response: {}, for task = {}".format(err, index)
                    ),
                )
            )
            raise MimecastException()
        except gzip.BadGzipFile as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "gzip file is corrupted or Invalid: {}, for task = {}".format(
                        err, index
                    ),
                )
            )
            raise MimecastException()
        except UnicodeDecodeError as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Error decoding decompressed data: {}, for task = {}".format(
                        err, index
                    ),
                )
            )
            raise MimecastException()
        except (OSError, IOError) as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Error decompressing data: {}, for task = {}".format(err, index),
                )
            )
            raise MimecastException()
        except json.JSONDecodeError as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.JSON_DECODE_ERROR_MSG.format(
                        "Error parsing JSON: {}, for task = {}".format(err, index)
                    ),
                )
            )
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_TASK_MSG.format(err, index),
                )
            )
            raise MimecastException()

    async def fetch_unzip_and_ingest_s3_url_data(
        self, index, session: aiohttp.ClientSession, url
    ):
        """Fetch, unzip, and ingest data from a given S3 URL.

        Args:
            index (int): The index of the task.
            session (aiohttp.ClientSession): The session to use for making the HTTP request.
            url (str): The URL of the S3 file.

        Returns:
            bool: True if the data was successfully ingested, False otherwise.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            for _ in range(consts.MAX_RETRIES_ASYNC):
                try:
                    response = await self.make_async_call(session, url, index)
                    response_json = await self.decompress_and_make_json(index, response)
                    if len(response_json) > 0:
                        applogger.info(
                            self.log_format.format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.azure_function_name,
                                "Data len = {}, Ingesting data to sentinel for task = {}".format(
                                    len(response_json), index
                                ),
                            )
                        )
                        mapping_dict = consts.FILE_PREFIX_MC_TYPE
                        for data in response_json:
                            data["type"] = mapping_dict.get(data.get("type"))

                        await post_data_async(
                            index,
                            json.dumps(response_json),
                            session,
                            consts.TABLE_NAME["SEG_CG"],
                        )
                        return True
                    return False
                except MimecastException:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Retry.. , for task = {}".format(index),
                        )
                    )
                    time.sleep(randrange(2, 10))
                    continue
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Max retries exceeded, for task = {}".format(index),
                )
            )
            raise MimecastException()
        except MimecastException:
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_TASK_MSG.format(err, index),
                )
            )
            raise MimecastException()

    async def make_async_call(self, session, url, index):
        """Make an asynchronous call to the given URL using the provided session.

        Args:
            session (aiohttp.ClientSession): The session to use for making the HTTP request.
            url (str): The URL to make the call to.
            index (int): The index of the task.

        Returns:
            aiohttp.ClientResponse: The response object if the call is successful.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.debug(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Get Call, for task = {}".format(index),
                )
            )
            response = await session.get(url)

            if response.status >= 200 and response.status <= 299:
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Success, Status code : {} for task = {}".format(
                            response.status, index
                        ),
                    )
                )
                return response
            elif response.status == 429:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Too Many Requests, Status code : {} for task = {}".format(
                            response.status, index
                        ),
                    )
                )
                raise MimecastException()
            else:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Unexpected Error = {}, Status code : {} for task = {}".format(
                            response.text, response.status, index
                        ),
                    )
                )
                raise MimecastException()
        except MimecastException:
            raise MimecastException()
        except ClientResponseError as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Client response error: {} - {}, for task = {}".format(
                        err.status, err.message, index
                    ),
                )
            )
            raise MimecastException()
        except ServerTimeoutError as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Server timeout error: {}, for task = {}".format(err, index),
                )
            )
            raise MimecastException()
        except ClientError as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Client error: {}, for task = {}".format(err, index),
                )
            )
            raise MimecastException()
        except asyncio.TimeoutError as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Request timeout error: {}, for task = {}".format(err, index),
                )
            )
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_TASK_MSG.format(err, index),
                )
            )
            raise MimecastException()
