import datetime
import logging
import os
import sys
import time
from collections import namedtuple

import msal
import requests
from requests_ratelimiter import LimiterSession
import azure.functions as func
from greynoise import GreyNoise
from .stixGen import GreyNoiseStixGenerator


REQUIRED_ENVIRONMENT_VARIABLES = [
    "GREYNOISE_KEY",
    "CLIENT_ID",
    "CLIENT_SECRET",
    "TENANT_ID",
    "WORKSPACE_ID",
    ]

GreyNoiseSetup = namedtuple("GreyNoiseSetup", ["api_key", "query", "tries", "size"])
MSALSetup = namedtuple("MSALSetup", ["tenant_id", "client_id", "client_secret", "workspace_id"])
class GreuNoiseSentinelUpdater(object):
    """Simple wrapper class to handle consuming IPs"""

    def __init__(self, greynoise_setup: GreyNoiseSetup,
                 msal_setup: MSALSetup):
        super(GreuNoiseSentinelUpdater, self).__init__()

        self.greynoise_query = greynoise_setup.query
        self.greynoise_size = greynoise_setup.size
        self.greynoise_tries = greynoise_setup.tries
        self.msal_tenant_id = msal_setup.tenant_id
        self.msal_client_id = msal_setup.client_id
        self.msal_client_secret = msal_setup.client_secret
        self.msal_workspace_id = msal_setup.workspace_id

        self.session = GreyNoise(
            api_key=greynoise_setup.api_key,
            integration_name="azuresentinel-consumer-v1.0",
        )
        self.gn_stix_generator = GreyNoiseStixGenerator()


    def get_token(self):
        """Gets an access token to access office service.
        Args:
            tenant_id (str): the tenant id
            client_id (str): the client id
            client_secret (str): the secret id for the client
        Returns:
            A token access key.
        """
        logging.info("Getting token for tenant: {0}".format(self.msal_tenant_id))
        try:
            context = msal.ConfidentialClientApplication(self.msal_client_id,
                                                        authority='https://login.microsofto'
                                                                'nline.com/' + self.msal_tenant_id,
                                                        client_credential=self.msal_client_secret)
            token = self.acquire_token(context)
            return token
        except requests.exceptions.RequestException as e:
            logging.info("Error getting token for tenant: {0}".format(self.msal_tenant_id))
            raise e


    def acquire_token(self, context):
        """Gets an access token to access ms graph TI Upload service.
        Args:
            context: the authentication context
        Returns:
            A token access key.
        """
        scope = "https://management.azure.com/.default"

        try:
            result = context.acquire_token_silent([scope],
                                                account=None)
            if not result:
                result = context.acquire_token_for_client(scopes=[
                    scope])

            if 'access_token' in result:
                bearer_token = result['access_token']
                return bearer_token
            else:
                error_code = result.get("error")
                error_message = result.get("error_description")
                logging.info("Error acquiring token for tenant with code: {0}".format(error_code))
                logging.info(error_message)
                raise ValueError(error_message)

        except requests.exceptions.RequestException as e:
            logging.info("Error acquiring token for tenant.")
            raise e
        
    def upload_indicators_to_sentinel(self, token: str, indicators: list):
        """Uploads a list of indicators to Azure Sentinel Threat Intelligence
        Endpoint Docs: # https://learn.microsoft.com/en-us/azure/sentinel/upload-indicators-api#request-body
            
        API Limits are 100 indicators per request and 100 requests per minute.
            Args:
                token (str): the access token
                indicators (list): the list of indicators to upload
            Returns:
                A response object."""
        
        session = LimiterSession(per_minute=90)

        url = "https://sentinelus.azure-api.net/{0}/threatintelligence:upload-indicators".format(self.msal_workspace_id)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(token)
        }
        params = {
            'api-version': '2022-07-01'
        }
        payload = {
            'SourceSystem': 'GreyNoise',
            'Value': indicators
        }

        try:
            response = session.request("POST", url, 
                                        headers=headers,
                                        params=params,
                                        json=payload)
            response.raise_for_status()
        except requests.HTTPError as e:
            logging.error('Did you add the Azure Sentinel Contributor role to your service principal?')
            logging.error(e.response.text)
            logging.error('Cannot upload indicators to Azure Sentinel, exiting.')
            sys.exit(1)
            
        return response.json()


    def consume_ips(self):
        logging.info(
            "Starting consumption of GreyNoise indicators with query %s"
            % (self.greynoise_query)
        )
        total_addresses = 0
        tries = int(self.greynoise_tries)
        scroll = ""
        complete = False

        # MS Graph TI Upload API limits are 100 indicators per request and 100 requests per minute.
        # Get MSAL token
        token = self.get_token()
        while not complete:
            try:
                if self.greynoise_size <= 2000:
                    payload = self.session.query(
                        query=self.greynoise_query,
                        size=self.greynoise_size,
                        scroll=scroll,
                    )
                else:
                    payload = self.session.query(
                        query=self.greynoise_query, 
                        scroll=scroll,
                        size=2000
                    )

                # this protects from bad / invalid queries
                # and exists out before proceeding
                if payload["count"] == 0:
                    logging.info("GreyNoise Query return no results, exiting")
                    sys.exit(1)

                # Loop to generate STIX objects and upload to Sentinel
                stix_objects = []
                counter = 0
                for gn_object in payload["data"]:
                    stix_object = self.gn_stix_generator.generate_indicator(gn_object)

                    stix_objects.append(stix_object)
                    counter += 1
                    if counter == 100:
                        # send batch to sentinel
                        self.upload_indicators_to_sentinel(token, stix_objects)
                        # reset counter and stix_objects
                        counter = 0
                        stix_objects = []
                        logging.debug("Sent 100 GreyNoise indicators to Sentinel" )


                # the scroll is for pagination but does not always exist because
                # we have consumed all the IPs
                scroll = payload.get("scroll")
                complete = payload["complete"]

                addresses = len(payload["data"])
                total_addresses += addresses

                logging.info(
                    "Sent %s GreyNoise indicators to Sentinel for a total of %s addresses"
                    % (addresses, total_addresses)
                )

                # this is a hacky workaround to deal with an edge case on the API where if
                # you limit the results on a query, the complete flag doesn't flip to
                # true correctly
                if (
                    self.greynoise_size != ""
                    and int(self.greynoise_size) < int(payload["count"])  # noqa: W503
                    and int(self.greynoise_size) == int(total_addresses)  # noqa: W503
                ):
                    break

            except Exception as reqErr:
                logging.error("Contacting greynoise API failed: %s" % str(reqErr))
                if tries != 0:
                    tries -= 1
                    logging.error("Trying again in 10 seconds using same scroll...")
                    time.sleep(10)
                else:
                    logging.error(
                        "Exiting program. Max tries met. With time %s and last scroll: %s"
                        % (time, scroll)
                    )
                    sys.exit(3)

        logging.info(
            "Ingest process completed.  Inserted %s Indicators into redis."
            % total_addresses
        )


def checkEnvironmentVariables(env):
    # the following checks will ensure required environment variables are set
    # and any others will have some type of defaulting
    unset_environment_variables = []

    for env_var in REQUIRED_ENVIRONMENT_VARIABLES:
        if not env.get(env_var, False):
            unset_environment_variables.append(env_var)

    if unset_environment_variables:
        logging.error(
            "The following required environment variables are unset: %s"
            % str(unset_environment_variables)
        )
        sys.exit(2)

def build_query_string(env):
    classifications = env.get("GREYNOISE_CLASSIFICATIONS", "malicious")
    logging.info("Building query string for %s" % classifications)

    # a user can accidentally set the environment to an empty string
    if len(classifications) == 0:
        return '(classification:malicious)'
    
    classifications = classifications.split(",")
    length_of_classifications = len(classifications)
    
    classification_string = "("
    for item in classifications:
        length_of_classifications -= 1
        classification_string += "classification:" + item
        if length_of_classifications > 0:
            classification_string += " OR "
    
    classification_string += ")"
    return classification_string


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    env = os.environ.copy()

    checkEnvironmentVariables(env)

    # SET VARS
    query_time = "1"
    size = "50000"

    # our classifications are formatted for greynoise
    classifications = build_query_string(env)


     # obtain our query for greynoise
    try:
        query_time = int(query_time)
        if query_time > 90 or query_time < 1:
            logging.error("Time input is not a valid integer between 1 and 90")
            sys.exit(1)
        else:
            if query_time == 1:
                logging.info("Using default query time of 1 day")
            else:
                logging.info("Using custom query time of %s day(s)" % str(query_time))
            query_time = "last_seen:%sd" % query_time
    except ValueError:
        logging.error("Input for time is not valid")
        sys.exit(1)

    # build our query
    query = classifications + " " + query_time  

    if size != "":
        logging.info("Querying GreyNoise API")
        try:
            size = int(size)
            if size > 500000 or size < 1:
                logging.error("Size input is not a valid integer between 1 and 500000")
                sys.exit(1)
            else:
                logging.info("Limiting results to %s" % str(size))

        except ValueError:
            logging.error("Input for size is not valid")
            sys.exit(1)
    else:
        logging.info("No size limited provided, returning all indicators available")

     # set up everything required to pass into the updater
    greynoise_setup = GreyNoiseSetup(
        env.get("GREYNOISE_KEY"), query, env.get("GREYNOISE_MAX_TRIES", 3), size
    )
    msal_setup = MSALSetup(
        env.get("TENANT_ID"), env.get("CLIENT_ID"), env.get("CLIENT_SECRET"), env.get("WORKSPACE_ID")
    )

    g = GreuNoiseSentinelUpdater(greynoise_setup, msal_setup)
    g.consume_ips()

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
