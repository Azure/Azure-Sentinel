"""This file contains implementation to ingest Dataminr RTAP alert data into sentinel."""
import os
import json
import inspect
from .sentinel import MicrosoftSentinel
from shared_code.consts import (
    LOGS_STARTS_WITH,
    RELATEDALERTS_TABLE_NAME,
    VULNERABILITY_PRODUCTS_TABLE_NAME,
    VULNERABILITY_PRODUCTS_RELATEDALERTS_TABLE_NAME,
)
from shared_code.dataminrpulse_exception import DataminrPulseException
from shared_code.logger import applogger

alerts_table = os.environ.get("AlertsTableName")
related_alerts_table = RELATEDALERTS_TABLE_NAME.format(alerts_table)
vulnerabilities_products_table = VULNERABILITY_PRODUCTS_TABLE_NAME.format(alerts_table)
vulnerabilities_products_related_alerts_table = (
    VULNERABILITY_PRODUCTS_RELATEDALERTS_TABLE_NAME.format(alerts_table)
)


class DataminrPulse:
    """This class contains methods to get data from request body pushed via Dataminr RTAP and ingest into Sentinel."""

    def __init__(self) -> None:
        """Initialize instance variables for class."""
        self.logs_starts_with = LOGS_STARTS_WITH
        self.microsoftsentinel = MicrosoftSentinel()
        self.error_logs = "{}(method={}) {}"
        self.check_environment_var_existance()

    def check_environment_var_existance(self):
        """To verify that all required environment variables are exist.

        Raises:
            DataminrPulseException: raise exception if any of the required environment variable is not set.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.debug(
                "{}(method={}) Checking environment variables are exist or not.".format(
                    self.logs_starts_with, __method_name
                )
            )
            if alerts_table is None:
                raise DataminrPulseException(
                    "AlertsTableName is not set in the environment please set the environment variable."
                )
            applogger.debug(
                "{}(method={}) All custom environment variable exists.".format(
                    self.logs_starts_with, __method_name
                )
            )
        except DataminrPulseException as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise DataminrPulseException(err)
        except Exception as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise DataminrPulseException(err)

    def extract_products_from_vulnerability(
        self, alert_index, vulnerabilities, log_type
    ):
        """Extract products data from vulnerabilities and ingested in seperate log analytics table.

        Args:
            alert_index (str): alert_id of alert data.
            vulnerabilities (list): vulnerabilities list of alert data.
            log_type (str): Table name in which vulnerability_products data will be ingested.

        Raises:
            DataminrPulseException: raises DataminrPulseException when any error occurs.

        Returns:
            list: returns updated vulnerabilities list.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            for vulnerability in vulnerabilities:
                vuln_id = vulnerability.get("id")
                products = vulnerability.get("products")
                if products:
                    data = {
                        "index": alert_index,
                        "vulnerabilities_id": vuln_id,
                        "vulnerabilities_products": products,
                    }
                    body = json.dumps(data)
                    status_code = self.microsoftsentinel.post_data(body, log_type)
                    if status_code >= 200 and status_code <= 299:
                        applogger.debug(
                            "{}(method={}) products for vulnerability id={}, alert id={} posted successfully.".format(
                                self.logs_starts_with,
                                __method_name,
                                vuln_id,
                                alert_index,
                            )
                        )
                    vulnerability.pop("products")
            return vulnerabilities
        except KeyError as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise DataminrPulseException(err)
        except Exception as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise DataminrPulseException(err)

    def prepare_embeded_labels_data(self, alert_index, embeded_labels, log_type):
        """Prepare Embeded Labels data.

        Args:
            alert_index (str): index of alert data recived via RTAP.
            embeded_labels(list): list of embeded labels data of a alert.
            log_type (str): Table name in which vulnerability_products data will be ingested.

        Raises:
            DataminrPulseException: raises DataminrPulseException when any error occurs.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            for cybermetadata in embeded_labels:
                data = cybermetadata.get("data")
                if data:
                    vulnerabilities = data.get("vulnerabilities")
                    if vulnerabilities:
                        updated_vulnerabilities = (
                            self.extract_products_from_vulnerability(
                                alert_index,
                                vulnerabilities,
                                log_type,
                            )
                        )
                        data.update({"vulnerabilities": updated_vulnerabilities})
                cybermetadata.update({"data": data})
            return embeded_labels
        except KeyError as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise DataminrPulseException(err)
        except Exception as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise DataminrPulseException(err)

    def prepare_rawtoredirecturl(self, alerts_data):
        """
        Prepare a data for subfield rawToRedirectedUrls in alert_data.

        Args:
            alerts_data (json): alert data received via Dataminr RTAP.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if alerts_data.get("internalOnly"):
                internal_only = alerts_data.get("internalOnly")
                redirect_link = internal_only.get("redirectLinks")
                if redirect_link:
                    redirect_urls = redirect_link.get("rawToRedirectedUrls")
                    if redirect_urls:
                        alerts_data["internalOnly"]["redirectLinks"][
                            "rawToRedirectedUrls"
                        ] = [redirect_urls]
        except KeyError as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise DataminrPulseException(err)
        except Exception as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise DataminrPulseException(err)

    def post_related_alerts(self, related_alerts, alert_id):
        """Post related alerts in seperate table obtained in alerts data received via DataminrPulse RTAP.

        Args:
            related_alerts (list): alerts related to provided alert_id.
            alert_id (_type_): id  of an alert whose related alerts are going to be ingested.

        Raises:
            DataminrPulseException: raises when any error occurs.

        Returns:
            list: returns list of related_alerts_id.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            count = 0
            related_alert_ids = []
            applogger.info(
                "{}(method={}) Received total {} alerts data related to id={} via RTAP.".format(
                    self.logs_starts_with,
                    __method_name,
                    len(related_alerts),
                    alert_id,
                )
            )
            for alert in related_alerts:
                alert.update({"alert_relatedTo": alert_id})
                self.prepare_rawtoredirecturl(alert)
                embeded = alert.get("_embedded")
                if embeded:
                    embeded_labels = embeded.get("labels")
                    if embeded_labels:
                        updated_embeded_labels = self.prepare_embeded_labels_data(
                            alert.get("index"),
                            embeded_labels,
                            vulnerabilities_products_related_alerts_table,
                        )
                        alert.update({"_embedded": {"labels": updated_embeded_labels}})
                related_alert_ids.append(alert.get("index"))
                body = json.dumps(alert)
                status_code = self.microsoftsentinel.post_data(
                    body, related_alerts_table
                )
                if status_code >= 200 and status_code <= 299:
                    count += 1
            applogger.info(
                "{}(method={}) Posted total {} alerts data related to id={} successfully.".format(
                    self.logs_starts_with,
                    __method_name,
                    count,
                    alert_id,
                )
            )
            return related_alert_ids
        except DataminrPulseException as err:
            raise DataminrPulseException(err)
        except Exception as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise DataminrPulseException(err)

    def prepare_alerts(self, alert_data):
        """Prepare alerts data for ingesting in Sentinel.

        Args:
            alert_data (json): Alert data received via Dataminr RTAP.

        Raises:
            DataminrPulseException: raises when any error occurs.

        Returns:
            alert_data(json): returns prepared alert data
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            self.prepare_rawtoredirecturl(alert_data)
            embeded = alert_data.get("_embedded")
            if embeded:
                embeded_labels = embeded.get("labels")
                if embeded_labels:
                    updated_embeded_labels = self.prepare_embeded_labels_data(
                        alert_data.get("index"),
                        embeded_labels,
                        vulnerabilities_products_table,
                    )
                    alert_data.update({"_embedded": {"labels": updated_embeded_labels}})
            if alert_data.get("relatedAlerts"):
                related_alerts = self.post_related_alerts(
                    alert_data.get("relatedAlerts"), alert_data.get("index")
                )
                alert_data.update({"relatedAlerts": related_alerts})
        except DataminrPulseException as err:
            raise DataminrPulseException(err)
        except Exception as error:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, error)
                )
            )
            raise DataminrPulseException(error)

    def send_alert_data_to_sentinel(self, data):
        """To process alerts data received via DataminrPulse RTAP and ingest into Sentinel.

        Raises:
            DataminrPulseException: raises when any error occurs.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if type(data) == dict:
                self.prepare_alerts(data)
                body = json.dumps(data)
                applogger.debug(
                    "{}(method={}) Posting the RTAP alerts from DataminrPulseAlertsSentinelConnector".format(
                        self.logs_starts_with, __method_name
                    )
                )
                self.microsoftsentinel.post_data(
                    body,
                    alerts_table,
                )
                applogger.info(
                    "{}(method={}) Alert data is ingested into Sentinel.".format(
                        self.logs_starts_with, __method_name
                    )
                )
            else:
                applogger.info(
                    "{}(method={}) Total alerts recived via RTAP are {}.".format(
                        self.logs_starts_with, __method_name, len(data)
                    )
                )
                count = 0
                for alert in data:
                    self.prepare_alerts(alert)
                    count += 1
                body = json.dumps(data)
                applogger.debug(
                    "{}(method={}) Posting the RTAP alert data from DataminrPulseAlertsSentinelConnector".format(
                        self.logs_starts_with, __method_name
                    )
                )
                self.microsoftsentinel.post_data(
                    body,
                    alerts_table,
                )
                applogger.info(
                    "{}(method={}) Total {} alerts ingested in Sentinel.".format(
                        self.logs_starts_with, __method_name, count
                    )
                )
            return "Data ingetsed successfully to Sentinel log analytics workspace."
        except DataminrPulseException as err:
            raise DataminrPulseException(err)
        except Exception as error:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, error)
                )
            )
            raise DataminrPulseException(error)
