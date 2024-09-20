"""This file has class and methods to push issue data into microsoft sentinel."""
import os
import datetime
import json
import logging
import base64
import hashlib
import hmac
import requests
from .scorecard_exceptions import NoDataError, SSIssueException


SECURITY_SCORECARD_ISSUE_TABLE_NAME = os.environ["SECURITY_SCORECARD_ISSUE_TABLE_NAME"]
shared_key = os.environ["WorkspaceKey"]
customer_id = os.environ["WorkspaceID"]


class AzureSentinel:
    """AzureSentinel is Used to post data to log analytics."""

    def build_signature(
        self,
        date,
        content_length,
        method,
        content_type,
        resource,
    ):
        """To build the signature."""
        x_headers = "x-ms-date:" + date
        string_to_hash = (
            method
            + "\n"
            + str(content_length)
            + "\n"
            + content_type
            + "\n"
            + x_headers
            + "\n"
            + resource
        )
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
        ).decode()
        authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
        return authorization

    # Build and send a request to the POST API
    def post_data(self, customer_id, body, log_type):
        """Build and send a request to the POST API."""
        method = "POST"
        content_type = "application/json"
        resource = "/api/logs"
        rfc1123date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        content_length = len(body)
        timestamp_date = "ss_time"
        try:
            signature = self.build_signature(
                rfc1123date,
                content_length,
                method,
                content_type,
                resource,
            )
        except SSIssueException as err:
            logging.error("SecurityScorecard Connector: Error occured: {}".format(err))
            raise SSIssueException(
                "SecurityScorecard Connector: Error while generating signature for log analytics."
            )

        uri = (
            "https://"
            + customer_id
            + ".ods.opinsights.azure.com"
            + resource
            + "?api-version=2016-04-01"
        )

        headers = {
            "content-type": content_type,
            "Authorization": signature,
            "Log-Type": log_type,
            "x-ms-date": rfc1123date,
            "time-generated-field": timestamp_date,
        }
        try:
            response = requests.post(uri, data=body, headers=headers)
            if not (response.status_code >= 200 and response.status_code <= 299):
                raise SSIssueException(
                    "SecurityScorecard Connector: Response code: {} from posting data to log analytics.".format(
                        response.status_code
                    )
                )

        except SSIssueException as err:
            logging.error(
                "SecurityScorecard Connector: Error while posting data : {}".format(err)
            )
            raise SSIssueException(
                "SecurityScorecard Connector: Error while posting data to microsoft sentinel."
            )


class CompanyWriter(object):
    """Represents a companyWriter object."""

    def __init__(self, company, state_manager_object):
        """__init__ method will initialize the object of companywriter class."""
        self.__company = company
        self.azuresentinel = AzureSentinel()
        self.state_manager_object = state_manager_object

    def save_checkpoint(self, portfolio_id=None, **config):
        """save_checkpoint method will save checkpoint for no data available."""
        new_from_date = ""
        try:
            chk_point_name = self.__company.domain
            from_date = config.get("from_date")
            todays_date = str(datetime.datetime.now().date())
            new_from_date = "%s|%s" % (from_date, todays_date)
            check_point_data_all_companies = self.state_manager_object.get()
            check_point_data_all_companies = json.loads(check_point_data_all_companies)
            if portfolio_id is None:
                check_point_data_all_companies[chk_point_name] = new_from_date
            else:
                check_point_data_all_companies[portfolio_id]["companies"][
                    chk_point_name
                ] = new_from_date
            self.state_manager_object.post(json.dumps(check_point_data_all_companies))
            logging.info(
                "SecurityScorecard Connector: checkpoint {} is saved of {} company when data is not available.".format(
                    chk_point_name, new_from_date
                )
            )
        except SSIssueException as err:
            logging.warn("SecurityScorecard Connector: error in checkpoint creation : {}".format(err))
            return

    def write_issues(self, portfolio_id=None, **config):
        """write_issues method will process the issues of a company."""
        chk_point_name = ""
        try:
            issues = self.__company.get_issues(**config)
        except NoDataError as err:
            logging.warn("SecurityScorecard Connector: Data {}".format(err))
            self.save_checkpoint(portfolio_id, **config)
            return
        except SSIssueException as err:
            logging.error("SecurityScorecard Connector: Error occurred  {}".format(err))
            raise err
        else:
            new_from_date = ""
            if not issues:
                return

            try:
                industry_name = self.__company.get_industry_name()
            except SSIssueException as err:
                logging.error("SecurityScorecard Connector: {}".format(err))

            max_date = '0001-01-01T00:00:00.000Z'
            for issue in issues:
                if issue["date"] > max_date:
                    max_date = issue["date"]
                issue["industry"] = industry_name
                issue["severity"] = config.get("level_issue_change", "NA")
                issue["portfolioId"] = config.get("portfolioId", "NA")
                issue["portfolioName"] = config.get("portfolioName", "NA")
            data = json.dumps(issues, indent=4)
            self.azuresentinel.post_data(
                customer_id, data, SECURITY_SCORECARD_ISSUE_TABLE_NAME
            )

            try:
                chk_point_name = self.__company.domain
                from_date = max_date[:10]
                from_date_data = str(
                    (
                        datetime.datetime.strptime(from_date, "%Y-%m-%d")
                        + datetime.timedelta(days=1)
                    ).date()
                )
                todays_date = str(datetime.datetime.now().date())
                new_from_date = "%s|%s" % (from_date_data, todays_date)
            except SSIssueException as err:
                logging.error("SecurityScorecard Connector: {}".format(err))
                return

            check_point_data_all_companies = self.state_manager_object.get()
            check_point_data_all_companies = json.loads(check_point_data_all_companies)
            if portfolio_id is None:
                check_point_data_all_companies[chk_point_name] = new_from_date
            else:
                check_point_data_all_companies[portfolio_id]["companies"][
                    chk_point_name
                ] = new_from_date
            self.state_manager_object.post(json.dumps(check_point_data_all_companies))
            logging.info(
                "SecurityScorecard Connector: checkpoint is saved with {} name and {} date".format(
                    chk_point_name, new_from_date
                )
            )
