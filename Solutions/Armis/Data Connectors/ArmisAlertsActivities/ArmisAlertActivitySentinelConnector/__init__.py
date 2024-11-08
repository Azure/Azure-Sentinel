"""This __init__ file will be called once triggered is generated."""

import datetime
import logging
import time
import azure.functions as func
import json
from .sentinel import AzureSentinel
from .exports_store import ExportsTableStore
from Exceptions.ArmisExceptions import ArmisException, ArmisDataNotFoundException
from .utils import Utils
from . import consts
import inspect


class ArmisAlertsActivities(Utils):
    """This class will process the Alert Activity data and post it into the Microsoft sentinel."""

    def __init__(self):
        """__init__ method will initialize object of class."""
        super().__init__()
        self.data_alert_from = 0
        self.azuresentinel = AzureSentinel()
        self.total_alerts_posted = 0
        self.total_activities_posted = 0

    def get_alert_data(self, parameter):
        """get_alert_data is used to get data using api.

        Args:
            parameter (json): will contain the json data to sends to parameter to get data from REST API.

        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            results = self.make_rest_call(
                method="GET",
                url=consts.URL + consts.SEARCH_SUFFIX,
                params=parameter,
                headers=self.header,
                retry_401=consts.RETRY_COUNT_401,
            )
            if ("data" in results) and ("count" in results["data"]) and (results["data"].get("count") == 0):
                raise ArmisDataNotFoundException(consts.LOG_FORMAT.format(__method_name, "Alert Data not found."))

            if (("results" in results["data"]) and ("total" in results["data"]) and ("next" in results["data"])):
                count_per_frame_data = results["data"]["count"]
                data = results["data"]["results"]
                for i in data:
                    i["armis_alert_time"] = i["time"]

                logging.info(
                    consts.LOG_FORMAT.format(__method_name, "Alerts From {} length 1000".format(self.data_alert_from))
                )
                self.data_alert_from = results["data"]["next"]
                alert_time = self.get_formatted_time(data[-1]["time"][:19])

                return data, alert_time, count_per_frame_data
            else:
                logging.error(consts.LOG_FORMAT.format(__method_name, "There are no proper keys in alerts data."))
                raise ArmisException()

        except KeyError as err:
            logging.error(consts.LOG_FORMAT.format(__method_name, "Key error : {}.".format(err)))
            raise ArmisException()

        except ArmisException:
            raise ArmisException()

        except ArmisDataNotFoundException as err:
            logging.info(err)
            raise ArmisDataNotFoundException()
        except Exception as err:
            logging.error(consts.LOG_FORMAT.format(__method_name, "Error while fetching Alerts. : {}.".format(err)))
            raise ArmisException()

    def get_activity_data(self, activity_uuids):
        """Get armis activity data.

        Args:
            activity_uuids (list): list of activity uuid

        Returns:
            list: list of activity
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            parameters_activity = {
                "aql": "in:activity",
                "orderBy": "time",
                "from": 0,
                "length": consts.CHUNK_SIZE,
                "fields": ",".join(consts.ACTIVITY_FIELDS),
            }
            aql_formatted_ids = ",".join(str(activity_uuid) for activity_uuid in activity_uuids)
            parameters_activity["aql"] = "in:activity UUID:{}".format(aql_formatted_ids)
            results = self.make_rest_call(
                method="GET",
                url=consts.URL + consts.SEARCH_SUFFIX,
                params=parameters_activity,
                headers=self.header,
                retry_401=consts.RETRY_COUNT_401,
            )
            if ("data" in results) and ("count" in results["data"]) and (results["data"].get("count") == 0):
                logging.warning(consts.LOG_FORMAT.format(__method_name, "Activity Data not found."))
                return []
            if (("results" in results["data"]) and ("total" in results["data"]) and ("next" in results["data"])):
                data = results["data"]["results"]
                for i in data:
                    i["armis_activity_time"] = i["time"]
                return data
            else:
                logging.error(consts.LOG_FORMAT.format(__method_name, "There are no proper keys in activity data."))
                raise ArmisException()

        except KeyError as err:
            logging.error(consts.LOG_FORMAT.format(__method_name, "Key error : {}.".format(err)))
            raise ArmisException()

        except ArmisException:
            raise ArmisException()

        except Exception as err:
            logging.error(consts.LOG_FORMAT.format(__method_name, "Error while fetching Activity : {}.".format(err)))
            raise ArmisException()

    def post_alert_activity_data(self, alerts_data_to_post, activity_uuid_list, offset_to_post, checkpoint_table_object: ExportsTableStore):
        """Post alert and activity data to respective table in sentinel.

        Args:
            alerts_data_to_post (list): alerts data to post
            activity_uuid_list (list): list of activity uuids to post
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if alerts_data_to_post:
                if activity_uuid_list:
                    logging.info(consts.LOG_FORMAT.format(__method_name, "Fetching activities data."))
                    activity_data = self.get_activity_data(activity_uuid_list)
                    self.azuresentinel.post_data(
                        json.dumps(activity_data, indent=2), consts.ARMIS_ACTIVITIES_TABLE, "armis_activity_time"
                    )
                    self.total_activities_posted += len(activity_data)
                    logging.info(
                        consts.LOG_FORMAT.format(
                            __method_name, "Posted Activities count : {}.".format(len(activity_data))
                        )
                    )
                self.azuresentinel.post_data(
                    json.dumps(alerts_data_to_post, indent=2), consts.ARMIS_ALERTS_TABLE, "armis_alert_time"
                )
                self.total_alerts_posted += len(alerts_data_to_post)
                logging.info(
                    consts.LOG_FORMAT.format(
                        __method_name, "Posted Alerts count : {}.".format(len(alerts_data_to_post))
                    )
                )
                offset_to_post += len(alerts_data_to_post)
                logging.info(consts.LOG_FORMAT.format(__method_name, "Saving offset '{}' in checkpoint".format(offset_to_post)))
                checkpoint_table_object.merge("armisalertactivity", "alertactivitycheckpoint", {"offset": offset_to_post})
            return offset_to_post
        except ArmisException:
            raise ArmisException()
        except Exception as err:
            logging.error(
                consts.LOG_FORMAT.format(
                    __method_name, "Error while posting alerts and activity data : {}.".format(err)
                )
            )
            raise ArmisException()

    def process_alerts_data(self, alerts, offset_to_post, checkpoint_table_object: ExportsTableStore):
        """Process alerts data to fetch related activity.

        Args:
            alerts (list): list of alerts
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            activity_uuid_list = []
            alerts_data_to_post = []
            for alert in alerts:
                activity_uuids = alert.get("activityUUIDs", [])
                if len(activity_uuid_list) + len(activity_uuids) <= consts.CHUNK_SIZE:
                    activity_uuid_list.extend(activity_uuids)
                    alerts_data_to_post.append(alert)
                else:
                    offset_to_post = self.post_alert_activity_data(alerts_data_to_post, activity_uuid_list, offset_to_post, checkpoint_table_object)
                    alerts_data_to_post = []
                    activity_uuid_list = []
                    if len(activity_uuids) < consts.CHUNK_SIZE:
                        activity_uuid_list.extend(activity_uuids)
                        alerts_data_to_post.append(alert)
                    else:
                        logging.info(
                        consts.LOG_FORMAT.format(
                            __method_name, "Chunk size is greater than {}.".format(consts.CHUNK_SIZE))
                        )
                        for index in range(0, len(activity_uuids), consts.CHUNK_SIZE):
                            chunk_of_activity_uuids = activity_uuids[index: index + consts.CHUNK_SIZE]
                            activity_data = self.get_activity_data(chunk_of_activity_uuids)
                            self.azuresentinel.post_data(
                                json.dumps(activity_data, indent=2),
                                consts.ARMIS_ACTIVITIES_TABLE,
                                "armis_activity_time",
                            )
                            self.total_activities_posted += len(activity_data)
                            logging.info(
                                consts.LOG_FORMAT.format(
                                    __method_name, "Posted Activities count : {}.".format(len(activity_data))
                                )
                            )
                        self.azuresentinel.post_data(
                            json.dumps([alert], indent=2), consts.ARMIS_ALERTS_TABLE, "armis_alert_time"
                        )
                        logging.info(consts.LOG_FORMAT.format(__method_name, "Posted Alerts count : 1."))
                        self.total_alerts_posted += 1
                        offset_to_post += 1
                        logging.info(consts.LOG_FORMAT.format(__method_name, "Saving offset '{}' in checkpoint".format(offset_to_post)))
                        checkpoint_table_object.merge("armisalertactivity", "alertactivitycheckpoint", {"offset": offset_to_post})
            self.post_alert_activity_data(alerts_data_to_post, activity_uuid_list, offset_to_post, checkpoint_table_object)
        except ArmisException:
            raise ArmisException()

        except Exception as err:
            logging.error(
                consts.LOG_FORMAT.format(
                    __method_name, "Error while processing alerts and activity data : {}.".format(err)
                )
            )
            raise ArmisException()

    def fetch_alert_data(self, alert_parameter, is_checkpoint_not_exist, checkpoint_table_object: ExportsTableStore, last_time=None):
        """Fetch_alert_data is used to push all the data into table.

        Args:
            alert_parameter (json): will contain the json data to use in parameters.
            is_checkpoint_not_exist (bool): it is a flag that contains the value if checkpoint exists or not.
            last_time (String): it will contain checkpoint time stamp.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if is_checkpoint_not_exist:
                aql_data = "in:alerts"
            else:
                aql_data = """{} after:{}""".format("in:alerts", last_time)
            alert_parameter["aql"] = aql_data
            alert_parameter["length"] = 1000
            while self.data_alert_from is not None:
                alert_parameter.update({"from": self.data_alert_from})
                offset_to_post = self.data_alert_from
                logging.info(consts.LOG_FORMAT.format(__method_name, "Fetching alerts data with parameters = {}.".format(alert_parameter)))
                (
                    data,
                    alert_time,
                    count_per_frame_data,
                ) = self.get_alert_data(alert_parameter)
                self.process_alerts_data(data, offset_to_post, checkpoint_table_object)
                logging.info(
                    consts.LOG_FORMAT.format(
                        __method_name,
                        "Collected {} alert data from alerts api.".format(count_per_frame_data),
                    )
                )
            alert_time = datetime.datetime.strptime(alert_time, "%Y-%m-%dT%H:%M:%S")
            alert_time += datetime.timedelta(seconds=1)
            alert_time = alert_time.strftime("%Y-%m-%dT%H:%M:%S")
            logging.info(
                consts.LOG_FORMAT.format(
                    __method_name, "Saving offset '0' in checkpoint"
                )
            )
            logging.info(
                consts.LOG_FORMAT.format(
                    __method_name, "Adding last timestamp in checkpoint: {}".format(alert_time)
                )
            )
            checkpoint_table_object.merge("armisalertactivity", "alertactivitycheckpoint", {"time": alert_time, "offset": 0})
        except ArmisException:
            raise ArmisException()

        except ArmisDataNotFoundException:
            raise ArmisDataNotFoundException()

        except Exception as err:
            logging.error(consts.LOG_FORMAT.format(__method_name, "Error occurred : {}.".format(err)))
            raise ArmisException()

    def check_data_exists_or_not_alert(self):
        """Check_data_exists_or_not is to check if the data is exists or not using the timestamp file."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            parameter_alert = {
                "orderBy": "time",
                "fields": ",".join(consts.ALERT_FIELDS),
            }
            last_time_alerts = self.state_manager_obj.get()
            checkpoint_table = ExportsTableStore(connection_string=consts.CONNECTION_STRING, table_name=consts.CHECKPOINT_TABLE_NAME)

            if last_time_alerts is not None:
                logging.info(
                    consts.LOG_FORMAT.format(
                        __method_name, "The checkpoint file is available for alerts. time: {}.".format(last_time_alerts)
                    )
                )
                checkpoint_table.create()
                checkpoint_table.merge("armisalertactivity", "alertactivitycheckpoint", {"time": last_time_alerts, "offset": 0})
                self.state_manager_obj.delete()
                logging.info(
                    consts.LOG_FORMAT.format(
                        __method_name, "checkpoint file deleted from fileshare."
                    )
                )
                self.fetch_alert_data(
                    parameter_alert,
                    False,
                    checkpoint_table,
                    last_time_alerts,
                )
                return
            record = checkpoint_table.get("armisalertactivity", "alertactivitycheckpoint")
            fetch_data_from_scratch = False
            if not record:
                checkpoint_table.create()
                checkpoint_table.post("armisalertactivity", "alertactivitycheckpoint", {"offset": 0})
                fetch_data_from_scratch = True
            else:
                logging.info(consts.LOG_FORMAT.format(__method_name, "Fetching Entity from checkpoint table"))
                last_time_alerts = record.get("time")
                self.data_alert_from = record.get("offset") if record.get("offset") else 0
                logging.info(consts.LOG_FORMAT.format(
                    __method_name, "Checkpoint table: Last timestamp: {}, Offset: {}".format(
                        last_time_alerts, self.data_alert_from
                    )
                ))
                if last_time_alerts is None:
                    logging.info(consts.LOG_FORMAT.format(
                        __method_name, "time value not available in checkpoint table. Setting time as None."
                    ))
                    fetch_data_from_scratch = True
            self.fetch_alert_data(
                parameter_alert,
                fetch_data_from_scratch,
                checkpoint_table,
                last_time_alerts,
            )
            logging.info(
                consts.LOG_FORMAT.format(
                    __method_name,
                    "Total Posted alerts {}, Total Posted activities : {}.".format(
                        self.total_alerts_posted,
                        self.total_activities_posted,
                    ),
                )
            )
        except ArmisException:
            raise ArmisException()

        except ArmisDataNotFoundException:
            raise ArmisDataNotFoundException()

        except Exception as err:
            logging.error(
                consts.LOG_FORMAT.format(
                    __method_name, "Error occurred during checking whether checkpoint exist or not : {}.".format(err)
                )
            )
            raise ArmisException()


def main(mytimer: func.TimerRequest) -> None:
    """
    Start the execution.

    Args:
        mytimer (func.TimerRequest): This variable will be used to trigger the function.

    """
    __method_name = inspect.currentframe().f_code.co_name
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    logging.info(
        consts.LOG_FORMAT.format(__method_name, "Python timer trigger function ran at {}".format(utc_timestamp))
    )

    armis_obj = ArmisAlertsActivities()
    try:
        armis_obj.check_data_exists_or_not_alert()
    except ArmisDataNotFoundException:
        logging.warning(consts.LOG_FORMAT.format(__method_name, "Alert Data not found hence, stopping the execution."))

    utc_timestamp_final = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    logging.info(consts.LOG_FORMAT.format(__method_name, "execution completed at {}.".format(utc_timestamp_final)))
    if mytimer.past_due:
        logging.info(consts.LOG_FORMAT.format(__method_name, "The timer is past due!"))
