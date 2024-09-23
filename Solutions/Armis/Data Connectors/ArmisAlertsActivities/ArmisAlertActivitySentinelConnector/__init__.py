"""This __init__ file will be called once triggered is generated."""

import datetime
import logging
import azure.functions as func
import json
from .sentinel import AzureSentinel
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
            if results["data"]["count"] == 0:
                raise ArmisDataNotFoundException(consts.LOG_FORMAT.format(__method_name, "Alert Data not found."))

            if (
                "data" in results
                and "results" in results["data"]
                and "total" in results["data"]
                and "count" in results["data"]
                and "next" in results["data"]
            ):
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
            if results["data"]["count"] == 0:
                logging.warning(consts.LOG_FORMAT.format(__method_name, "Activity Data not found."))
                return []
            if (
                "data" in results
                and "results" in results["data"]
                and "total" in results["data"]
                and "count" in results["data"]
                and "next" in results["data"]
            ):
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

    def post_alert_activity_data(self, alerts_data_to_post, activity_uuid_list):
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
                self.post_alert_checkpoint(alerts_data_to_post[-1])
        except ArmisException:
            raise ArmisException()
        except Exception as err:
            logging.error(
                consts.LOG_FORMAT.format(
                    __method_name, "Error while posting alerts and activity data : {}.".format(err)
                )
            )
            raise ArmisException()

    def process_alerts_data(self, alerts):
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
                    self.post_alert_activity_data(alerts_data_to_post, activity_uuid_list)
                    alerts_data_to_post = []
                    activity_uuid_list = []
                    if len(activity_uuids) < consts.CHUNK_SIZE:
                        activity_uuid_list.extend(activity_uuids)
                        alerts_data_to_post.append(alert)
                    else:
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
                        self.total_alerts_posted += 1
                        logging.info(consts.LOG_FORMAT.format(__method_name, "Posted Alerts count : 1."))
                        self.post_alert_checkpoint(alert)
            self.post_alert_activity_data(alerts_data_to_post, activity_uuid_list)
        except ArmisException:
            raise ArmisException()

        except Exception as err:
            logging.error(
                consts.LOG_FORMAT.format(
                    __method_name, "Error while processing alerts and activity data : {}.".format(err)
                )
            )
            raise ArmisException()

    def fetch_alert_data(self, type_data, is_checkpoint_not_exist, last_time=None):
        """Fetch_alert_data is used to push all the data into table.

        Args:
            type_data (json): will contain the json data to use in parameters.
            is_checkpoint_not_exist (bool): it is a flag that contains the value if checkpoint exists or not.
            last_time (String): it will contain checkpoint time stamp.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if is_checkpoint_not_exist:
                aql_data = """{}""".format(type_data["aql"])
            else:
                aql_data = """{} after:{}""".format(type_data["aql"], last_time)
            type_data["aql"] = aql_data
            while self.data_alert_from is not None:
                parameter_alert = {
                    "aql": type_data["aql"],
                    "from": self.data_alert_from,
                    "orderBy": "time",
                    "length": 1000,
                    "fields": type_data["fields"],
                }
                logging.info(consts.LOG_FORMAT.format(__method_name, "Fetching alerts data."))
                (
                    data,
                    alert_time,
                    count_per_frame_data,
                ) = self.get_alert_data(parameter_alert)
                self.process_alerts_data(data)
                logging.info(
                    consts.LOG_FORMAT.format(
                        __method_name,
                        "Collected {} alert data from alerts api.".format(count_per_frame_data),
                    )
                )

            if str(consts.IS_AVOID_DUPLICATES).lower() == "true":
                alert_time = datetime.datetime.strptime(alert_time, "%Y-%m-%dT%H:%M:%S")
                alert_time += datetime.timedelta(seconds=1)
                alert_time = alert_time.strftime("%Y-%m-%dT%H:%M:%S")
                logging.info(
                    consts.LOG_FORMAT.format(
                        __method_name, "Last timestamp with plus one second that is added : {}".format(alert_time)
                    )
                )
                self.state_manager_obj.post(str(alert_time))
                logging.info(
                    consts.LOG_FORMAT.format(
                        __method_name,
                        "" + "Last timestamp is added with plus one second into the StateManager successfully.",
                    )
                )

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
                "aql": "in:alerts",
                "orderBy": "time",
                "fields": ",".join(consts.ALERT_FIELDS),
            }
            last_time_alerts = self.state_manager_obj.get()
            if last_time_alerts is None:
                logging.info(
                    consts.LOG_FORMAT.format(__method_name, "The checkpoint timestamp is not available for the alerts!")
                )
                self.fetch_alert_data(
                    parameter_alert,
                    True,
                    last_time_alerts,
                )
            else:
                logging.info(
                    consts.LOG_FORMAT.format(
                        __method_name, "The checkpoint is available for alerts: {}.".format(last_time_alerts)
                    )
                )
                self.fetch_alert_data(
                    parameter_alert,
                    False,
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
