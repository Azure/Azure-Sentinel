import logging
import requests
from datetime import datetime, timedelta, timezone
from json import dumps
from os import environ
import azure.functions as func
from .state_manager import StateManager
from .utils import save_to_sentinel

customer_id = environ.get("WorkspaceID")
shared_key = environ.get("WorkspaceKey")
connection_string = environ.get("AzureWebJobsStorage")
fetch_blocked_domains = environ.get("FetchBlockedDomains")
fetch_suspicious_domains = environ.get("FetchSuspiciousDomains")
fetch_malicious_domains = environ.get("FetchMaliciousDomains")
fetch_permitted_domains = environ.get("FetchPermittedDomains")
hyas_api_key = environ.get("ApiKey")
table_name = environ.get("TableName")
log_analytics_uri = (
    f"https://{customer_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01"
)
state = StateManager(connection_string)

LAST_X_DAYS = 0
PAGE_SIZE = 1000
OUTPUT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
INPUT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
HYAS_URL = "https://api.hyas.com/dns-log-report/v2/logs"


def get_from_and_to_date(date_format=INPUT_DATE_FORMAT):
    """
    Returns the 'from' and 'to' dates as formatted strings based on the given date_format.

    Args:
        date_format (str): Optional. The format string for the output dates. Default is INPUT_DATE_FORMAT.

    Returns:
        tuple: A tuple containing the 'from' and 'to' dates as formatted strings.
    """
    current_date_time = datetime.utcnow().replace(second=0, microsecond=0)
    last_run_date_time = state.get()
    logging.debug(last_run_date_time)
    if last_run_date_time is not None:
        from_date_time = datetime.strptime(last_run_date_time, date_format)
    else:
        from_date_time = current_date_time - timedelta(days=LAST_X_DAYS)

    return format(from_date_time, date_format), format(current_date_time, date_format)


def call_hyas_protect_api():
    """
    Calls the HYAS Protect API to fetch logs based on specified filters and saves them to Sentinel.

    Returns:
        None
    """
    if (
        fetch_blocked_domains == "No"
        and fetch_suspicious_domains == "No"
        and fetch_malicious_domains == "No"
        and fetch_permitted_domains == "No"
    ):
        logging.info("All fetch domains variables are set to 'No'. Returning None.")
        return

    (
        from_datetime,
        to_datetime,
    ) = get_from_and_to_date()  # "2023-03-22 10:50:00", "2023-06-20 10:50:00"
    from_date = datetime.strptime(from_datetime, INPUT_DATE_FORMAT).strftime(
        OUTPUT_DATE_FORMAT
    )
    to_date = datetime.strptime(to_datetime, INPUT_DATE_FORMAT).strftime(
        OUTPUT_DATE_FORMAT
    )
    applied_filters = [
        {
            "id": "datetime",
            "isRange": True,
            "rangeValue": {
                "start": from_date,
                "end": to_date,
                "timeType": "range",
            },
        }
    ]
    if fetch_blocked_domains == "Yes":
        applied_filters.append({"id": "reputation", "value": "blocked"})

    if fetch_suspicious_domains == "Yes":
        applied_filters.append({"id": "reputation", "value": "suspicious"})

    if fetch_malicious_domains == "Yes":
        applied_filters.append({"id": "reputation", "value": "malicious"})

    if fetch_permitted_domains == "Yes":
        applied_filters.append({"id": "reputation", "value": "permitted"})

    data = {"applied_filters": applied_filters}
    total_count, page_size, page_number, records_fetched = 1, PAGE_SIZE, 0, 0
    while records_fetched < total_count:
        # Prepare the paging parameters
        data["paging"] = {
            "order": "desc",
            "page_number": page_number,
            "page_size": page_size,
            "page_type": "standard",
            "sort": "datetime",
        }

        # Make the API call
        response = requests.post(
            HYAS_URL,
            headers={"Content-Type": "application/json", "X-API-Key": hyas_api_key},
            data=dumps(data),
        )
        if response.status_code in range(200, 299):
            result = response.json()
            logs = result["logs"]
            records_fetched += len(logs)
            page_number += 1
            total_count = result["total_count"]
            sentinel_logs = [hyas_dict(log) for log in logs]
            sentinel_resp = save_to_sentinel(
                log_analytics_uri,
                customer_id,
                shared_key,
                dumps(sentinel_logs),
                table_name,
            )
            if sentinel_resp in range(200, 299):
                logging.info(
                    f"HYAS Protect logs from {from_date} to {to_date} with filter {str(data)} saved in sentinel successfully."
                )
            state.post(to_datetime)
        else:
            if response.status_code in [401, 403]:
                logging.error("Invalid HYAS API KEY.")
            logging.info(response.content)
            logging.info(
                f"Unable to fetch logs from Hyas Protect API. Response code: {response.status_code}"
            )
            break
        if records_fetched >= total_count:
            break
        
        

def hyas_dict(log: dict):
    """
    Converts a dictionary representing HYAS Protect log data into a standardized format.

    Args:
        log (dict): The dictionary containing the HYAS Protect log data.

    Returns:
        dict: The converted log data in a standardized format.
    """
    return {
        "Reputation": log.get("reputation"),
        "DateTime": log.get("datetime"),
        "Domain": log.get("domain"),
        "DeviceName": log.get("devicename"),
        "ProcessName": log.get("processname"),
        "Nameserver": log.get("nameserver"),
        "Verdict": log.get("verdict"),
        "VerdictSource": log.get("verdictSource"),
        "VerdictStatus": log.get("verdictStatus"),
        "Registrar": log.get("registrar"),
        "PolicyName": log.get("policy", {}).get("policy_name"),
        "PolicyID": log.get("policy", {}).get("policy_id"),
        "RegistrarVerdict": log.get("markup", {}).get("registrar", {}).get("verdict"),
        "FQDNVerdict": log.get("markup", {}).get("fqdn", {}).get("verdict"),
        "DomainVerdict": log.get("markup", {}).get("domain", {}).get("verdict"),
        "IPVerdict": log.get("markup", {}).get("ip", {}).get("verdict"),
        "CNameVerdict": log.get("markup", {}).get("cname", {}).get("verdict"),
        "NameserverIPVerdict": log.get("markup", {})
        .get("nameserver_ip", {})
        .get("verdict"),
        "NameserverVerdict": log.get("markup", {}).get("nameserver", {}).get("verdict"),
        "TLDVerdict": log.get("markup", {}).get("tld", {}).get("verdict"),
        "TTL": log.get("ttl"),
        "Tags": ",".join(str(x) for x in log.get("tags", [])),
        "LogID": log.get("log_id"),
        "ClientID": log.get("client_id"),
        "ClientName": log.get("client_name"),
        "ClientIP": log.get("client_ip"),
        "Domain2TLD": log.get("domain_2tld"),
        "DomainTLD": log.get("domain_tld"),
        "Nameserver2TLD": log.get("nameserver_2tld"),
        "NameserverTLD": log.get("nameserver_tld"),
        "NameserverIP": log.get("nameserver_ip", {}).get("ip"),
        "NameserverCountryISOCode": log.get("nameserver_ip", {}).get(
            "country_iso_code"
        ),
        "NameserverCountryName": log.get("nameserver_ip", {}).get("country_name"),
        "ARecord": ",".join(str(x) for x in log.get("a_record", [])),
        "CName": ",".join(x for x in log.get("c_name", [])),
        "CName2TLD": ",".join(x for x in log.get("c_name_2tld", [])),
        "CNameTLD": ",".join(x for x in log.get("c_name_tld", [])),
        "ThreatLevel": log.get("threat_level"),
        "QueryType": log.get("query_type"),
        "ResponseCode": log.get("response_code"),
        "ResponseName": log.get("response_name"),
        "ResponseDescription": log.get("response_description"),
        "ResolverMode": log.get("resolver_mode"),
        "ReasonLists": ",".join(str(x) for x in log.get("reason", {}).get("lists", [])),
        "ReasonType": log.get("reason", {}).get("type"),
        "DomainAge": log.get("domain_age"),
        "DomainCategory": ",".join(x for x in log.get("domain_category", [])),
        "DomainCreationDate": log.get("domain_creation_date"),
        "DomainExpiresDate": log.get("domain_expires_date"),
        "DomainUpdatedDate": log.get("domain_updated_date"),
    }



def main(mytimer: func.TimerRequest) -> None:
    """
    The main function for the timer trigger.

    Args:
        mytimer (func.TimerRequest): The TimerRequest object containing information about the timer trigger.

    Returns:
        None
    """
    if mytimer.past_due:
        logging.info("The timer is past due!")
        return
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    call_hyas_protect_api()
    logging.info("Python timer trigger function ran at %s", utc_timestamp)

