#!/usr/bin/env python

import os
import sys
import datetime
import logging
import re
import azure.functions as func
from .sentinel_connector import AzureSentinelConnector
from .state_manager import StateManager

# BHE client import
from .bhe_client import *

# Log Analytics Workspace Info
WORKSPACE_ID = os.environ['WorkspaceID']
SHARED_KEY = os.environ['WorkspaceKey']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
LOG_TYPE = 'bloodhoundEnterprise'

# Azure Blob storage connection string
file_storage_connection_string = os.environ['AzureWebJobsStorage']

# Validate Log Analytics URI
if not logAnalyticsUri or str(logAnalyticsUri).isspace():
    logAnalyticsUri = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'
pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Invalid Log Analytics Uri.")

# BHE instance info
bhe_domain = os.environ['BHEDomain']
token_id = os.environ['BHETokenId']
token_key = os.environ['BHETokenKey']

def stream_events(last_data_stream, timestamp_now):
        
        # Connection to BHE domain
        credentials = Credentials(token_id, token_key)
        client = BHEClient(scheme='https', host=bhe_domain, port=443, credentials=credentials)

        sentinel = AzureSentinelConnector(workspace_id=WORKSPACE_ID, logAnalyticsUri = logAnalyticsUri, shared_key=SHARED_KEY, log_type=LOG_TYPE, queue_size=10000, bulks_number=10)

        # Check if BHE domain is reachable and creds are working
        try:
            status_code = client.get_api_version().status_code
        except:
            logging.info("BHE Cannot reach domain: %s" % bhe_domain)
            raise ValueError("Cannot reach domain: %s" % bhe_domain)
        else:
            if status_code == 200:
                logging.info("BHE API creds validated")
            else:
                logging.info("BHE Cannot log in using API keys. Status code: %s" % status_code)
                raise ValueError("Cannot log in using API keys. Status code: %s" % status_code)


        # Get available domains
        domains = client.get_domains()
        logging.info("BHE Number of domains %s" % len(domains))

        for domain in domains:
            if domain['collected']:
                # Get paths for domain
                attack_paths = client.get_paths(domain)
                logging.info(("BHE Processing %s attack paths for domain %s" % (len(attack_paths), domain['name'])))

                for attack_path in attack_paths:
                    logging.info("BHE Processing attack path %s for domain %s" % (attack_path.id, domain['name']))

                    # Add attack path principals to kv store
                    path_principals = client.get_path_principals(attack_path)

                    for principal_set in path_principals.impacted_principals:

                        # Create generic record
                        path_record = {
                                "domain_id": path_principals.domain_id,
                                "domain_name": path_principals.domain_name,
                                "path_id": path_principals.id,
                                "path_title": path_principals.title,
                                "group": None,
                                "principal": None,
                                "non_tier_zero_principal": None,
                                "tier_zero_principal": None,
                                "user": None,
                                "data_type": 'path_principals'
                            }
                        
                        # Populate generic record and insert
                        if (path_principals.id.startswith('LargeDefault')):
                            path_record['group'] = principal_set['Group']
                            path_record['principal'] = principal_set['Principal']

                            sentinel.send(path_record)

                        elif 'Tier Zero Principal' in principal_set:
                            path_record['non_tier_zero_principal'] = principal_set['Non Tier Zero Principal']
                            path_record['tier_zero_principal'] = principal_set['Tier Zero Principal']

                            sentinel.send(path_record)

                        else:
                            path_record['user'] = principal_set['User']

                            sentinel.send(path_record)

                    path_events = client.get_path_timeline(
                        path = attack_path,
                        from_timestamp = last_data_stream,
                        to_timestamp = timestamp_now
                    )

                    for path_event in path_events:
                        path_event['domain_id'] = domain['id']
                        path_event['domain_impact_value'] = domain['impactValue']
                        path_event['domain_name'] = domain['name']
                        path_event['domain_type'] = domain['type']
                        path_event['data_type'] = 'paths'

                        sentinel.send(path_event)

                    logging.info("BHE Processing attack path %s done" % attack_path.id)

        # Get posture data
        posture_events = client.get_posture(
            from_timestamp = last_data_stream,
            to_timestamp = timestamp_now
        )

        logging.info("BHE Processing %s events of posture data" % len(posture_events))

        # Create posture events in Sentinel
        for posture_event in posture_events:

            # Lookup domain name and type
            domain = next(x for x in domains if x['id'] == posture_event['domain_sid'])

            posture_event['domain_id'] = domain['id']
            posture_event['domain_impact_value'] = domain['impactValue']
            posture_event['domain_name'] = domain['name']
            posture_event['domain_type'] = domain['type']
            posture_event['exposure'] = str(int(float(posture_event["exposure_index"]) * 100))
            posture_event['data_type'] = 'posture'

            sentinel.send(posture_event)

        logging.info("BHE Flushing the Sentinel queue")
        
        sentinel.flush()
        
        logging.info("BHE Streaming events done")

def generate_date():
    tformat = '%Y-%m-%dT%H:%M:%S.%f'
    current_time = datetime.datetime.now(datetime.timezone.utc).strftime(tformat)[:-3] + 'Z'
    state = StateManager(connection_string=file_storage_connection_string)
    past_time = state.get()
    if past_time is not None:
        logging.info("BHE The last time point is: {}".format(past_time))
    else:
        logging.info("BHE There is no last data stream, getting event from the beginning of time")
        past_time = "1970-01-01T00:00:00.000Z"
    return (past_time, current_time)

def update_date():
    current_time = datetime.datetime.now(datetime.timezone.utc).strftime(tformat)[:-3] + 'Z'
    state = StateManager(connection_string=file_storage_connection_string)
    logging.info("BHE Setting last time point to: {}".format(current_time))
    state.post(current_time)

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    
    last_data_stream, timestamp_now = generate_date()

    logging.info("BHE Last data stream %s" % last_data_stream)

    stream_events(last_data_stream = last_data_stream, timestamp_now = timestamp_now)

    update_date()
    
    
    
