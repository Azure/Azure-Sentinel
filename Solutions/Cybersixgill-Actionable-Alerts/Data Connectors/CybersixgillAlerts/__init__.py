# import datetime
from datetime import datetime, timedelta, timezone
from copy import deepcopy
from json import dumps
from re import match
import logging

from os import environ
import azure.functions as func
from .state_manager import StateManager
from .utils import remove_patterns, save_to_sentinel

from sixgill.sixgill_actionable_alert_client import SixgillActionableAlertClient

customer_id = environ['WorkspaceID'] 
shared_key = environ['WorkspaceKey']
connection_string = environ['AzureWebJobsStorage']
client_id = environ['ClientID']
client_secret = environ['ClientSecret']
logAnalyticsUri = environ.get('logAnalyticsUri')
CHANNEL_ID = "cea9a52effad4bc5e905a5a653f5cf9b"
LAST_X_DAYS = 90
PAGE_SIZE = 5


# https://docs.microsoft.com/azure/azure-monitor/logs/data-collector-api#python-sample
if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Invalid Log Analytics Uri.")

state = StateManager(connection_string)

def get_from_and_to_date(date_format="%Y-%m-%d %H:%M:%S"):
    current_date_time = datetime.utcnow().replace(second=0, microsecond=0)
    last_run_date_time = state.get()
    logging.debug(last_run_date_time)
    if last_run_date_time is not None:
        from_date_time = datetime.strptime(last_run_date_time, date_format)
    else:
        from_date_time = current_date_time - timedelta(days=LAST_X_DAYS)
    
    return format(from_date_time, date_format), format(current_date_time, date_format)



def main(mytimer: func.TimerRequest) -> None:
    logging.info(str(environ))
    utc_timestamp = datetime.utcnow().replace(
        tzinfo=timezone.utc).isoformat()
    
    if mytimer.past_due:
        logging.info('The timer is past due!')
        return

    from_date_time, to_date_time = get_from_and_to_date()
    logging.info(from_date_time)
    logging.info(to_date_time)

    actionable_alerts_client = SixgillActionableAlertClient(
        client_id, client_secret, CHANNEL_ID)
    start = 0
    logging.info("Going in")
    while True:
        actionable_alerts = actionable_alerts_client.get_actionable_alerts_bulk(
            from_date=from_date_time, limit=PAGE_SIZE, offset=start, sort_order="asc"
        )
        logging.info(f"start={start}, offset={PAGE_SIZE}")
        logging.info(actionable_alerts)
        start = start + PAGE_SIZE
        if not actionable_alerts:
            logging.info("Empty response from API")
            break
        else:
            logging.info(f"# of actionable alerts received : {len(actionable_alerts)}")
        for actionable_alert in actionable_alerts:
            alert_id = actionable_alert.get("id")
            portal_url = f"https://portal.cybersixgill.com/#/?actionable_alert={alert_id}"
            if "status" not in actionable_alert:
                actionable_alert["status"] = {
                    "status": "treatment_required",
                    "name": "Treatment Required",
                    "user": "",
                }
            # Sub alerts logic
            alert_info = actionable_alerts_client.get_actionable_alert(alert_id)
            # Merging assets to a single list 
            if "matched_assets" in alert_info and isinstance(alert_info["matched_assets"], dict):
                assets = []
                for _, v in alert_info["matched_assets"].items():
                    assets.extend(v)
                logging.info(assets)
                actionable_alert["assets"] = assets # list(set(assets))
            threat_actor = alert_info.get("es_item", {}).get(
                "creator_plain_text"
            ) or alert_info.get("es_item", {}).get("creator")
            threat_actor = threat_actor or ""
            actionable_alert["threat_actor"] = threat_actor
            if threat_actor:
                actor_source = alert_info.get("es_item", {}).get("site")
                actionable_alert["threat_source"] = actor_source
            else:
                actionable_alert["threat_source"] = ""

            sub_alerts = actionable_alert.pop("sub_alerts", [])
            for sub_alert in filter(None, sub_alerts):
                unique_id = f'{alert_id}__{int(sub_alert.get("aggregate_alert_id"))}'
                # Merging assets to a single list 
                sub_alert_assets = []
                if "matched_assets" in sub_alert and isinstance(sub_alert["matched_assets"], dict):
                    for _, v in sub_alert["matched_assets"].items():
                        sub_alert_assets.extend(v)

                sub_item = deepcopy(actionable_alert)
                sub_item.update(sub_alert)
                sub_item["assets"] = sub_alert_assets
                sub_item["unique_id"] = unique_id
                sub_item["parent_id"] = alert_id
                sub_item["portal_url"] = portal_url
                sub_item = remove_patterns(sub_item)
                logging.info(sub_item)
                save_to_sentinel(logAnalyticsUri,  customer_id, shared_key ,dumps(sub_item))

            # Sub alerts logic ends
            actionable_alert["parent_id"] = None
            actionable_alert["organization_name"] = alert_info.get(
                "additional_info", {}
            ).get("organization_name")
            content = alert_info.get("es_item", {}).get("highlight", {}).get("content")
            content = content[0] if isinstance(content, list) else content
            existing_content = str(actionable_alert["content"])
            logging.info(f"creating alert with id={alert_id}")
            actionable_alert["_time"] = actionable_alert["date"]
            actionable_alert["alert_creation_date"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            actionable_alert["portal_url"] = portal_url
            actionable_alert["content"] = str(content) if content else existing_content
            actionable_alert["matched_assets"] = alert_info.get("matched_assets")
            actionable_alert["sub_alerts_count"] = len(sub_alerts)
            if threat_actor:
                actor_source = alert_info.get("es_item", {}).get("site")
                actionable_alert["threat_source"] = actor_source
                actionable_alert[
                    "actor_url_with_context"
                ] = f"https://portal.cybersixgill.com/#/actor/{threat_actor}/{actor_source}"
                actionable_alert[
                    "actor_url_without_context"
                ] = f"https://portal.cybersixgill.com/#/actor/{threat_actor}/"
            actionable_alert = remove_patterns(actionable_alert)
            logging.debug(actionable_alert)
            save_to_sentinel(logAnalyticsUri,  customer_id, shared_key,dumps(actionable_alert))


    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    state.post(to_date_time)
