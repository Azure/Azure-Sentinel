"""This file has helper class to call securityscorecard apis to pull data."""
from .utils import make_rest_call, format_date_string
from .scorecard_exceptions import NoDataError


class ScoreCardHelperClass:
    """Represents a scorecard object."""

    def __init__(self, base_url, access_key, domain=None):
        """__init__ method will initialize the object of scorecardhelper class."""
        self.__base_url = base_url
        self.__access_key = access_key
        self.domain = domain

    def generate_overall_score(self, today_values, yesterday_values):
        """generate_overall_score method will generate the overall score of a company."""
        diff = today_values["score"] - yesterday_values["score"]

        return {
            "body": "OverAll",
            "src": "OverallScore",
            "subject": self.domain,
            "dateYesterday": format_date_string(yesterday_values.get("date", "")),
            "dateToday": format_date_string(today_values.get("date", "")),
            "scoreYesterday": yesterday_values.get("score", ""),
            "scoreToday": today_values.get("score", ""),
            "scoreChange": diff,
            'diff': diff,
            "ss_time": today_values.get("date", ""),
        }

    def get_overall_score(self, **config):
        """get_overall_score method will get the overall score of a company."""
        from_date, to_date = config.get("from_date_factor"), config.get("to_date")
        overall_score_url = "{}/companies/{}/history/score?from={}&to={}".format(
            self.__base_url, self.domain, from_date, to_date
        )
        scores = make_rest_call(
            url=overall_score_url,
            secret_key=self.__access_key,
        )
        json_response_entries = scores.get("entries", [])
        if not json_response_entries:
            raise NoDataError("SecurityScorecard Connector: No data available")
        rv = []

        for value in range(len(json_response_entries) - 1):
            yesterday_values = json_response_entries[value]
            today_values = json_response_entries[value + 1]
            rv.append(self.generate_overall_score(today_values, yesterday_values))
        return rv

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
