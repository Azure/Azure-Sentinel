"""This __init__ file will be called once triggered is generated."""
import os
import json
import datetime
import logging
from collections import OrderedDict
import azure.functions as func
from .scorecard_exceptions import (
    APIKeyNotProvidedError,
    DomainNotProvidedError,
    BaseURLNotProvidedError,
    SSFactorException,
)
from .state_manager import StateManager
from .scorecard import ScoreCardHelperClass
from .writers import CompanyWriter

SECURITY_SCORECARD_SECRET_KEY = os.environ["SecurityScorecardKey"]
BASE_URL = os.environ["BASE_URL"]
connection_string = os.environ["AzureWebJobsStorage"]
DOMAIN = os.environ["DOMAIN"]
LEVEL_FACTOR_CHANGE = os.environ["LEVEL_FACTOR_CHANGE"]
PORTFOLIO_IDS_STR = os.environ["PORTFOLIO_IDS_STR"]
DIFF_OVERRIDE_OWN_FACTOR = os.environ["DIFF_OVERRIDE_OWN_FACTOR"]
DIFF_OVERRIDE_PORTFOLIO_FACTOR = os.environ["DIFF_OVERRIDE_PORTFOLIO_FACTOR"]


def main(mytimer: func.TimerRequest) -> None:
    """Start the execution.

    Args:
        mytimer (func.TimerRequest): This variable will be used to trigger the function.
    """
    utc_now_time = datetime.datetime.utcnow()
    utc_timestamp = utc_now_time.replace(tzinfo=datetime.timezone.utc).isoformat()
    logging.info(
        "SecurityScorecard Connector: Python timer trigger function ran at %s",
        utc_timestamp,
    )
    portfolio_ids = []
    portfolios = []
    try:
        # remove whitespace from environment variables
        secret_key = SECURITY_SCORECARD_SECRET_KEY.strip()
        base_url = BASE_URL.strip()
        domain = DOMAIN.strip()
        level_factor_change = LEVEL_FACTOR_CHANGE.strip()
        portfolio_ids_str = PORTFOLIO_IDS_STR.strip()
        diff_override_own_factor = str(DIFF_OVERRIDE_OWN_FACTOR).strip().lower()
        diff_override_portfolio_factor = str(DIFF_OVERRIDE_PORTFOLIO_FACTOR).strip().lower()

        # Validation of Secret Key, URL and Domain
        if not secret_key:
            raise APIKeyNotProvidedError()
        if not domain:
            raise DomainNotProvidedError()
        if not base_url:
            raise BaseURLNotProvidedError()

        # Creating list of portfolioIds and getting data of portfolios
        if portfolio_ids_str:
            portfolio_ids = [
                portfolio_id.strip()
                for portfolio_id in portfolio_ids_str.split(",")
                if portfolio_id.strip()
            ]
            portfolios = list(
                filter(
                    lambda portfolio: portfolio_ids.__contains__(portfolio.get("id")),
                    ScoreCardHelperClass(base_url, secret_key).get_portfolios(),
                )
            )
            logging.info(
                "SecurityScorecard Connector: Total {} portfolio ids are provided.".format(
                    len(portfolio_ids)
                )
            )
        if not portfolios:
            logging.info(
                "SecurityScorecard Connector: Portfolio ids not provided or portfolio id is not available in the API."
            )

        # Object to save the data of checkpoints
        state_manager_object = StateManager(
            connection_string=connection_string, file_path="funcstimestamp"
        )
        state_manager_data = state_manager_object.get()
        state_manager_json = json.loads(state_manager_data)
        to_date = utc_now_time.date()
        from_date_sm = str(to_date - datetime.timedelta(days=1))
        from_date_factor = "%s|%s" % (from_date_sm, from_date_sm)
        new_statemanager_data = {}
        new_statemanager_data = {
            domain: state_manager_json.get(domain) or from_date_factor
        }
        company_pname_pids = {}

        # Creating statemanager data with latest checkpoints
        for portfolio in portfolios:
            portfolio_id = portfolio.get("id")
            portfolio_name = portfolio.get("name")
            companies = ScoreCardHelperClass(base_url, secret_key).get_portfolio_data(
                portfolio_id
            )
            porfolio_companies = {
                company.get("domain"): state_manager_json.get(portfolio_id, {})
                .get("companies", {})
                .get(company.get("domain"))
                or from_date_factor
                for company in companies
            }
            new_statemanager_data[portfolio_id] = {
                "portfolio_name": portfolio_name,
                "companies": porfolio_companies,
            }
            for company, from_date in porfolio_companies.items():
                from_date_portfolio_companies = from_date.split('|')[0]
                company_pname_pids[from_date_portfolio_companies] = (
                    company_pname_pids.get(from_date_portfolio_companies) or []
                )
                company_pname_pids[from_date_portfolio_companies].append(
                    {
                        "company": company,
                        "portfolio_id": portfolio_id,
                        "portfolio_name": portfolio_name,
                        "check_date": from_date.split('|')[1],
                    }
                )

        state_manager_object.post(json.dumps(new_statemanager_data))

        # Sorting companies by date
        company_to_fetch_data = dict(OrderedDict(sorted(company_pname_pids.items())))
        from_date_factor = (new_statemanager_data[domain]).split('|')[0]
        check_date = (new_statemanager_data[domain]).split('|')[1]
        config = {
                "level_factor_change": level_factor_change,
                "to_date": str(to_date),
                "from_date_factor": str(
                    (
                        datetime.datetime.strptime(from_date_factor, "%Y-%m-%d")
                        - datetime.timedelta(days=1)
                    ).date()
                ),
                "diff_override_own_factor": diff_override_own_factor,
                "diff_override_portfolio_factor": diff_override_portfolio_factor,
            }
        if check_date != str(to_date):
            # Fetching data of domain Factors and writing it into the Microsoft Sentinel
            scorecard_obj = ScoreCardHelperClass(base_url, secret_key, domain)
            writer_obj = CompanyWriter(scorecard_obj, state_manager_object)
            logging.info(
                "SecurityScorecard Connector: Writting Factors data into the Microsoft Sentinel!"
            )
            writer_obj.write_factors(**config)
            logging.info(
                "SecurityScorecard Connector: Factors data successfully ingested!"
            )
        else:
            logging.info("SecurityScorecard Connector: skipped domain company.")
        # Fetching data of portfolio companies and writing it into the Microsoft Sentinel
        for from_date_company in company_to_fetch_data.keys():
            date_wise_company_list = company_to_fetch_data.get(from_date_company) or []
            for company_data in date_wise_company_list:
                company_name = company_data.get("company")
                company_pid = company_data.get("portfolio_id")
                company_pname = company_data.get("portfolio_name")
                if company_data.get('check_date') == str(to_date):
                    logging.info(
                        "SecurityScorecard Connector: skipped the company : {}".format(
                            company_name
                        )
                    )
                    continue
                config.update(
                    {
                        "from_date_factor": str(
                            (
                                datetime.datetime.strptime(
                                    from_date_company, "%Y-%m-%d"
                                )
                                - datetime.timedelta(days=1)
                            ).date()
                        ),
                        "portfolioId": company_pid,
                        "portfolioName": company_pname,
                    }
                )
                logging.info(
                    "SecurityScorecard Connector: configuration for {} company is {}".format(
                        company_name, config
                    )
                )
                company_obj = ScoreCardHelperClass(base_url, secret_key, company_name)
                writer_obj = CompanyWriter(company_obj, state_manager_object)
                logging.info(
                    "SecurityScorecard Connector: Writting Factors data into the Microsoft Sentinel!"
                )
                writer_obj.write_factors(company_pid, **config)
                logging.info(
                    "SecurityScorecard Connector: Factors data successfully ingested!"
                )

    except APIKeyNotProvidedError:
        raise APIKeyNotProvidedError(
            "SecurityScorecard Connector: Secret Key is not Provided."
        )

    except DomainNotProvidedError:
        raise DomainNotProvidedError(
            "SecurityScorecard Connector: Domain is not Provided."
        )

    except BaseURLNotProvidedError:
        raise BaseURLNotProvidedError(
            "SecurityScorecard Connector: Base URL is not Provided."
        )

    except SSFactorException as err:
        raise SSFactorException("SecurityScorecard Connector: {}".format(err))

    utc_timestamp_final = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    logging.info(
        "SecurityScorecard Connector: execution completed for alerts at %s.",
        utc_timestamp_final,
    )
    if mytimer.past_due:
        logging.info("SecurityScorecard Connector: The timer is past due!")
