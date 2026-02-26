"""This file has helper class to call securityscorecard apis to pull data."""
from .utils import make_rest_call, format_date_string, get_value_from_dict_list
from .scorecard_exceptions import NoDataError


class ScoreCardHelperClass:
    """Represents a scorecard object."""

    def __init__(self, base_url, access_key, domain=None):
        """__init__ method will initialize the object of scorecardhelper class."""
        self.__base_url = base_url
        self.__access_key = access_key
        self.domain = domain

    def get_issues(self, **config):
        """get_issues method will get the issues data of a company."""
        try:
            issue_types_url = "{}/metadata/issue-types".format(self.__base_url)
            issue_types = make_rest_call(
                url=issue_types_url, secret_key=self.__access_key
            )
            json_issue_type = issue_types["entries"]
        except Exception:
            raise NoDataError(
                "SecurityScorecard Connector: Issue type data is not available"
            )

        from_date, to_date = "{}T00:00:00Z".format(
            config.get("from_date")
        ), "{}T00:00:00Z".format(config.get("to_date"))
        issue_level_url = (
            "{}/companies/{}/history/events?date_from={}&date_to={}".format(
                self.__base_url, self.domain, from_date, to_date
            )
        )
        issue_level = make_rest_call(
            url=issue_level_url,
            secret_key=self.__access_key,
        )
        json_issue_level_entries = issue_level.get("entries", [])
        if not json_issue_level_entries:
            raise NoDataError(
                "SecurityScorecard Connector: Issue level data is not available"
            )

        return list(
            map(
                lambda entry: {
                    "body": "Issue",
                    "Factor": entry.get("factor", "None"),
                    "eventID": entry.get("id", "No_id"),
                    "subject": self.domain,
                    "date": format_date_string(entry.get("date", "no_date")),
                    "issueType": entry.get("issue_type", "no_issueType"),
                    "findingsCount": entry.get("issue_count", "no_issue_count"),
                    "groupStatus": entry.get("group_status"),
                    "issueName": "{}".format(
                        get_value_from_dict_list(
                            json_issue_type, "key", entry.get("issue_type")
                        )["title"]
                        if get_value_from_dict_list(
                            json_issue_type, "key", entry.get("issue_type")
                        )
                        else "not found"
                    ),
                    "totalScoreImpact": entry.get("total_score_impact"),
                    "severity_value": entry.get("severity"),
                    "detail_url": entry.get("detail_url"),
                    "ss_time": entry.get("date", ""),
                },
                filter(
                    lambda each: each["issue_type"] != "breach",
                    json_issue_level_entries,
                ),
            )
        )

    def get_portfolios(self):
        """get_portfolios method will get the portfolios."""
        portfolio_url = "{}/portfolios".format(self.__base_url)
        portfolio = make_rest_call(
            portfolio_url,
            self.__access_key,
        )
        return portfolio.get("entries", [])

    def get_portfolio_data(self, portfolio_id):
        """get_portfolio_data method will get the companies of a portfolio."""
        portfolio_data_url = "{}/portfolios/{}/companies".format(
            self.__base_url, portfolio_id
        )
        companies = make_rest_call(
            portfolio_data_url,
            self.__access_key,
        )
        return companies.get("entries", [])

    def get_industry_name(self):
        """get_industry_name method will get the industry name of a company."""
        industry_url = "{}/companies/{}".format(self.__base_url, self.domain)
        company = make_rest_call(
            industry_url,
            self.__access_key,
        )
        return company.get("industry", "")
