"""File for driver code cofense to sentinel."""
import inspect
import time
from datetime import datetime, timezone
import asyncio
import aiohttp
import json
from .sentinel import MicrosoftSentinel
from .cofense_to_sentinel_mapping import map_indicator_fields
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.cofense_intelligence_exception import CofenseIntelligenceException
from ..SharedCode.utils import Utils
from ..SharedCode.manage_checkpoints import ManageCheckpoints
from ..SharedCode.state_manager import StateManager


class CofenseIntelligence(Utils, ManageCheckpoints):
    """Class for pulls data from cofenseintelligence and create indicator on sentinel."""

    def __init__(self) -> None:
        """Initialize instance variable for class."""
        Utils.__init__(self, consts.COFENSE_TO_SENTINEL)
        ManageCheckpoints.__init__(
            self, "cofense_to_sentinel", consts.COFENSE_TO_SENTINEL
        )
        self.validate_params()
        self.proxy = self.create_proxy()

    def save_failed_indicators_data_to_checkpoint(self, indicators_data, file_name):
        """Save failed indicators data to checkpoint.

        Args:
            indicators_data (list): Failed indicators data.
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            state_manager_obj = StateManager(
                consts.CONNECTION_STRING, file_path=file_name
            )
            checkpoint_data = state_manager_obj.get(consts.COFENSE_TO_SENTINEL)
            if checkpoint_data is None or checkpoint_data == "":
                state_manager_obj.post(json.dumps(indicators_data))
                applogger.info(
                    "{}(method={}) : {} : checkpoint file created and {} failed indicators posted sucessfully.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        len(indicators_data),
                    )
                )
            else:
                json_checkpoint = json.loads(checkpoint_data)
                json_checkpoint.extend(indicators_data)
                state_manager_obj.post(json.dumps(json_checkpoint))
                applogger.info(
                    "{}(method={}) : {} : Updated checkpoint with {} failed indicators sucessfully.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        len(indicators_data),
                    )
                )
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : error while posting checkpoint data for failed indicators :{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    error,
                )
            )
            raise CofenseIntelligenceException()

    async def post_data_to_threat_intelligence(self, indicators_data):
        """Create the asynchronous tasks for indicators ingestion to Microsoft Sentinel Threat Intelligence.

        Args:
            indicators_data (dict): Indicators Data

        Returns:
            dict: Dictionary containing the success_count and failure_count
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            failed_indicators = []
            microsoft_sentinel_obj = MicrosoftSentinel()
            tasks = []
            async with aiohttp.ClientSession() as session:
                for indicator in indicators_data.get("data", {}).get("indicators", []):
                    mapped_data = map_indicator_fields(indicator)
                    tasks.append(
                        asyncio.create_task(
                            microsoft_sentinel_obj.create_indicator(
                                mapped_data, session
                            )
                        )
                    )
                results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = 0
            failed_count = 0
            for i in results:
                if i is None:
                    success_count += 1
                else:
                    failed_count += 1
                    failed_indicators.append(i)
            applogger.info(
                "{}(method={}) : {} : Total_Invocations: {}, Successful Indicators Posting: {},\
                    Failed Indicators Posting: {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.COFENSE_TO_SENTINEL,
                    len(results),
                    success_count,
                    failed_count,
                )
            )
            return {
                "success_count": success_count,
                "failure_count": failed_count,
                "failed_indicators": failed_indicators,
            }
        except CofenseIntelligenceException:
            applogger.error(
                "{}(method={}) : {} : Indicator Creation Failed.".format(
                    consts.LOGS_STARTS_WITH, __method_name, consts.COFENSE_TO_SENTINEL
                )
            )
            raise CofenseIntelligenceException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Indicator Creation Failed, Error: {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.COFENSE_TO_SENTINEL,
                    error,
                )
            )
            raise CofenseIntelligenceException()

    async def get_cofense_data_post_to_sentinel(self):
        """Fetch data and Indicators mapping."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            total_indicators = 0
            total_success_indicators = 0
            total_fail_indicators = 0
            get_indicator_url = "{}{}".format(
                consts.COFENSE_BASE_URL, consts.ENDPOINTS["search_indicators"]
            )
            params = {"resultsPerPage": consts.COFENSE_PAGE_SIZE}
            checkpoint_since_last_published = self.get_checkpoint_data(
                "sinceLastPublished"
            )
            checkpoint_page = self.get_checkpoint_data("page")
            if checkpoint_since_last_published:
                applogger.info(
                    "{}(method={}) : {} :SincelastPublished Checkpoint found:{}.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.COFENSE_TO_SENTINEL,
                        checkpoint_since_last_published,
                    )
                )
                params["sinceLastPublished"] = checkpoint_since_last_published
            else:
                applogger.info(
                    "{}(method={}) : {} :SincelastPublished Checkpoint not found,\
                        Fetching data of last 15 days.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.COFENSE_TO_SENTINEL,
                    )
                )
                now = datetime.now(timezone.utc)
                midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
                params["sinceLastPublished"] = (
                    int(midnight.timestamp()) - consts.FIFTEEN_DAYS
                )
                applogger.info(
                    "{}(method={}) : {} :Updating Initial SincelastPublished Checkpoint {}.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.COFENSE_TO_SENTINEL,
                        params["sinceLastPublished"],
                    )
                )
                self.post_data_to_checkpoint(
                    "sinceLastPublished", params["sinceLastPublished"]
                )
            if checkpoint_page is not None:
                applogger.info(
                    "{}(method={}) : {} :Page Checkpoint found:{}.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.COFENSE_TO_SENTINEL,
                        checkpoint_page,
                    )
                )
                params["page"] = checkpoint_page
            failed_indicators_file_name = str(
                int(datetime.now(timezone.utc).timestamp())
            )
            while True:
                indicators_data = self.get_cofense_data(
                    url=get_indicator_url,
                    params=params,
                    endpoint_name="get indicators",
                    proxies=self.proxy,
                )
                applogger.info(
                    "{}(method={}) : {} : Indicators fetched successfully.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.COFENSE_TO_SENTINEL,
                    )
                )
                if len(indicators_data.get("data", {}).get("indicators", [])) == 0:
                    applogger.info(
                        "{}(method={}) : {} : No indicators found.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.COFENSE_TO_SENTINEL,
                        )
                    )
                    break

                total_indicators += len(
                    indicators_data.get("data", {}).get("indicators", [])
                )
                response = await self.post_data_to_threat_intelligence(indicators_data)
                total_success_indicators += response["success_count"]
                total_fail_indicators += response["failure_count"]
                if response["failure_count"] > 0:
                    applogger.info(
                        "{}(method={}) : {} : {} indicators failed, adding the indicators to retry_queue.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.COFENSE_TO_SENTINEL,
                            response["failure_count"],
                        )
                    )
                    self.save_failed_indicators_data_to_checkpoint(
                        response["failed_indicators"], failed_indicators_file_name
                    )
                next_page = (
                    indicators_data.get("data", {})
                    .get("page", {})
                    .get("currentPage", 0)
                    + 1
                )
                if next_page == indicators_data.get("data", {}).get("page", {}).get(
                    "totalPages", 0
                ):
                    break
                params["page"] = next_page
                applogger.info(
                    "{}(method={}) : {} : Updating page checkpoint: {}.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.COFENSE_TO_SENTINEL,
                        next_page,
                    )
                )
                self.post_data_to_checkpoint("page", next_page)
            applogger.info(
                "{}(method={}) : {} : Total collected indicators from cofense : {}, "
                "successfully posted indicators into sentinel: {}, "
                "failed indicators while posting : {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.COFENSE_TO_SENTINEL,
                    total_indicators,
                    total_success_indicators,
                    total_fail_indicators,
                )
            )
            self.post_data_to_checkpoint("sinceLastPublished", int(time.time()))
            self.post_data_to_checkpoint("page", 0)
            applogger.info(
                "{}(method={}) : {} : Updated page and LastPublished checkpoint Successfully.".format(
                    consts.LOGS_STARTS_WITH, __method_name, consts.COFENSE_TO_SENTINEL
                )
            )
        except CofenseIntelligenceException:
            raise CofenseIntelligenceException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : error occured :{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    error,
                )
            )
            raise CofenseIntelligenceException()
