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

    def generate_factors(self, today_values, yesterday_values, json_factor_entries):
        """generate_factors method will generate factors using factors data."""
        rv = []
        for factor in today_values.get('factors', []):
            name = factor['name']
            other = get_value_from_dict_list(today_values['factors'], 'name', name)
            diff = factor['score'] - other['score'] if other else 0
            matched_factor = get_value_from_dict_list(json_factor_entries, 'key', name)
            try:
                factor_description = matched_factor.get('description', '')
                factor_name = matched_factor.get('name', '')
            except KeyError:
                factor_description = 'data is not there'
                factor_name = 'Not Available'
            except AttributeError:
                factor_description = 'data is not there'
                factor_name = 'Not Available'

            rv.append({
                'body': 'Factor',
                'Factor': name,
                'Factor Name': factor_name,
                'subject': self.domain,
                'dateYesterday': format_date_string(yesterday_values.get('date', '')),
                'dateToday': format_date_string(today_values.get('date', '')),
                'scoreYesterday': other['score'] if other else 0,
                'scoreToday': factor['score'],
                'scoreChange': diff,
                'diff': diff,
                'factorDescription': "{}".format(factor_description),
                "ss_time": today_values.get("date", ""),
            })

        return rv

    def get_factors(self, **config):
        """get_factors method will pull the factors score of a company."""
        factor_meta_url = '{}/metadata/factors'.format(self.__base_url)
        factor_meta = make_rest_call(url=factor_meta_url, secret_key=self.__access_key)
        json_factor_entries = factor_meta.get("entries", [])

        from_date, to_date = config.get("from_date_factor"), config.get("to_date")
        factor_url = "{}/companies/{}/history/factors/score?from={}&to={}".format(
            self.__base_url, self.domain, from_date, to_date
        )
        factors = make_rest_call(
            url=factor_url,
            secret_key=self.__access_key,
        )
        json_response_entries = factors.get("entries", [])
        if not json_response_entries:
            raise NoDataError("SecurityScorecard Connector: No data available")
        rv = []

        for value in range(len(json_response_entries) - 1):
            yesterday_values = json_response_entries[value]
            today_values = json_response_entries[value + 1]
            rv.extend(self.generate_factors(today_values, yesterday_values, json_factor_entries))
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
