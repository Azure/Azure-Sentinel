"""File for driver code DataminrPulse to sentinel."""
import inspect
from datetime import datetime, timezone
import asyncio
import aiohttp
import json
from .sentinel import MicrosoftSentinel
from .dataminr_pulse_to_threat_intelligence_mapping import map_indicator_fields
from ..shared_code import consts
from ..shared_code.logger import applogger
from ..shared_code.dataminrpulse_exception import DataminrPulseException
from ..shared_code.state_manager import StateManager
from .get_logs_data import get_logs_data
from ..shared_code.validate_params import validate_params


class DataMinrPulseThreatIntelligence:
    """Class for pulls data from dataminr_pulse log table and create indicator on sentinel."""

    def __init__(self) -> None:
        """Initialize instance variable for class."""
        self.state_manager_obj = StateManager(
            consts.CONN_STRING, "time_generated_checkpoint"
        )
        validate_params(consts.DATAMINR_PULSE_THREAT_INTELLIGENCE)

    def save_failed_indicators_data_to_checkpoint(self, indicators_data, file_name):
        """Save failed indicators data to checkpoint.

        Args:
            indicators_data (list): Failed indicators data.
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            state_manager_obj = StateManager(consts.CONN_STRING, file_path=file_name)
            checkpoint_data = state_manager_obj.get(
                consts.DATAMINR_PULSE_THREAT_INTELLIGENCE
            )
            if checkpoint_data is None or checkpoint_data == "":
                state_manager_obj.post(json.dumps(indicators_data))
                applogger.info(
                    "{}(method={}) : {} : checkpoint file created and {} failed indicators posted successfully.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                        len(indicators_data),
                    )
                )
            else:
                json_checkpoint = json.loads(checkpoint_data)
                json_checkpoint.extend(indicators_data)
                state_manager_obj.post(json.dumps(json_checkpoint))
                applogger.info(
                    "{}(method={}) : {} : Updated checkpoint with {} failed indicators successfully.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                        len(indicators_data),
                    )
                )
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : error while posting checkpoint data for failed indicators :{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                    error,
                )
            )
            raise DataminrPulseException()

    async def post_data_to_threat_intelligence(self, dataminr_data):
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
            conn = aiohttp.TCPConnector(limit_per_host=30)
            failed_mapping_count = 0
            async with aiohttp.ClientSession(connector=conn) as session:
                for data in dataminr_data:
                    try:
                        mapped_data = map_indicator_fields(data)
                    except DataminrPulseException as error:
                        applogger.warning(
                            "{}(method={}) : {} : Exception in mapping. Skipping this Indicator, Index-{}, Error:{}.".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                                data.get("index_s", ""),
                                error
                            )
                        )
                        failed_mapping_count += 1
                        continue
                    for indicator_data in mapped_data:
                        tasks.append(
                            asyncio.create_task(
                                microsoft_sentinel_obj.create_indicator(indicator_data, session)
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
                    Failed Indicators Posting: {}, Failed Indicators due to mapping: {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                    (len(results)+failed_mapping_count),
                    success_count,
                    failed_count,
                    failed_mapping_count,
                )
            )
            return {
                "success_count": success_count,
                "failure_count": failed_count,
                "failed_mapping_count": failed_mapping_count,
                "failed_indicators": failed_indicators,
            }
        except DataminrPulseException:
            applogger.error(
                "{}(method={}) : {} : Indicator Creation Failed.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                )
            )
            raise DataminrPulseException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Indicator Creation Failed, Error: {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                    error,
                )
            )
            raise DataminrPulseException()

    def batch(self, iterable, n):
        """Yield data in batches of given size from list.

        Args:
            iterable (list): list to make batch of
            n (number): size of batches

        Yields:
            list: data in batches of size n
        """
        length_of_list = len(iterable)
        for ndx in range(0, length_of_list, n):
            yield iterable[ndx:min(ndx + n, length_of_list)]

    async def get_dataminr_pulse_data_post_to_sentinel(self):
        """Fetch data and Indicators mapping."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            total_indicators = 0
            total_success_indicators = 0
            total_fail_indicators = 0
            total_failed_mapping = 0
            checkpoint_time_generated = self.state_manager_obj.get(
                consts.DATAMINR_PULSE_THREAT_INTELLIGENCE
            )
            if checkpoint_time_generated:
                applogger.info(
                    "{}(method={}) : {} :TimeGenerated Checkpoint found:{}.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                        checkpoint_time_generated,
                    )
                )
            else:
                checkpoint_time_generated = str(datetime.now(tz=timezone.utc))
                applogger.info(
                    "{}(method={}) : {} :TimeGenerated Checkpoint not found,\
                        Fetching data from current Time, {}.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                        checkpoint_time_generated
                    )
                )
                self.state_manager_obj.post(checkpoint_time_generated)
            logs_data = get_logs_data(checkpoint_time_generated)
            if len(logs_data) == 0:
                applogger.info(
                    "{}(method={}) : {} :No logs data found,\
                        Stopping Execution.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                    )
                )
                return
            failed_indicators_file_name = str(
                int(datetime.now(timezone.utc).timestamp())
            )
            for data in self.batch(logs_data, 100):
                response = await self.post_data_to_threat_intelligence(data)
                total_indicators += response["success_count"] + response["failure_count"] + response["failed_mapping_count"]
                total_success_indicators += response["success_count"]
                total_fail_indicators += response["failure_count"]
                total_failed_mapping += response["failed_mapping_count"]
                self.state_manager_obj.post(data[-1]["TimeGenerated"])
                applogger.info(
                    "{}(method={}) : {} :Posting TimeGenerated in Checkpoint, data : {}.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                        data[-1]["TimeGenerated"],
                    )
                )
                if response["failure_count"] > 0:
                    applogger.info(
                        "{}(method={}) : {} : {} indicators failed, adding the indicators to retry_queue.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                            response["failure_count"],
                        )
                    )
                    self.save_failed_indicators_data_to_checkpoint(
                        response["failed_indicators"], failed_indicators_file_name
                    )
            applogger.info(
                "{}(method={}) : {} : Total collected Data from DataminrPulse : {}, "
                "successfully posted indicators into sentinel: {}, "
                "failed indicators while posting : {}., failed indicators due to mapping: {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                    total_indicators,
                    total_success_indicators,
                    total_fail_indicators,
                    total_failed_mapping,
                )
            )
        except DataminrPulseException:
            raise DataminrPulseException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : error occurred :{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DATAMINR_PULSE_THREAT_INTELLIGENCE,
                    error,
                )
            )
            raise DataminrPulseException()
