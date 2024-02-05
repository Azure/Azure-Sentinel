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
organization_id = environ['OrganizationID']
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
            from_date=from_date_time, limit=PAGE_SIZE, offset=start, sort_order="asc",
            organization_id=organization_id
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
            alert_info = actionable_alerts_client.get_actionable_alert(alert_id, organization_id=organization_id)
            # Merging assets to a single list 
            if "matched_assets" in alert_info and isinstance(alert_info["matched_assets"], dict):
                assets = []
                for _, v in alert_info["matched_assets"].items():
                    assets.extend(v)
                logging.info(assets)
                actionable_alert["assets"] = assets # list(set(assets))
            cve_id = alert_info.get('additional_info').get('cve_id')
            es_id = alert_info.get('es_id')
            es_item = alert_info.get("es_item", {})
            threat_actor = ""
            if cve_id:
                actionable_alert['cve_url'] = f'https://portal.cybersixgill.com/#/cve/{cve_id}'
                additional_info = alert_info.get("additional_info", {})
                content = additional_info.get("cve_description", "")
                actionable_alert['cve'] = cve_id
                actionable_alert['cybersixgillcvss31'] = additional_info.get("nvd", {}).get("v3", {}).get("current", -1)
                actionable_alert['cybersixgillcvss20'] = additional_info.get("nvd", {}).get("v2", {}).get("current", -1)
                actionable_alert['cybersixgilldvescore'] = additional_info.get("score", {}).get("current")
                attributes = []
                for attribute in additional_info.get("attributes", []):
                    if attribute.get("value"):
                        attributes.append(additional_info.get("description"))
                attributes = '\n\n-----------\n\n'.join(attributes)
                actionable_alert['alert_attributes'] = attributes
            elif es_id == "Not Applicable":
                alert_content = actionable_alerts_client.get_actionable_alert_content(actionable_alert_id=alert_info.get('id'),
                                                                            fetch_only_current_item=True)
                content_item = {}
                content_items = alert_content.get('items')
                if content_items:
                    for item in content_items:
                        additional_keywords = item.get('Additional Keywords')  # for Github Alert
                        alert_actor = item.get('Actor')  # For Compromised Alerts
                        alert_detection = item.get('Detection time')  # For Phishing Alerts
                        breach_date = item.get('breach_date')
                        if additional_keywords is not None:
                            content_item['Repository name'] = "Repository name: " + item.get("Repository name", "")
                            content_item['Customer Keywords'] = "Customer Keywords: " + item.get("Customer Keywords", "")
                            content_item['GitURL'] = "GitURL: " + item.get("URL", "")
                        elif alert_actor is not None:
                            content_item['Actor'] = "Actor: " + alert_actor
                            content_item['BIN'] = "BIN: " + item.get("BIN", "")
                            content_item['Site'] = "Site: " + item.get("Site", "")
                            content_item['Text'] = "Text: " + item.get("Text", "")
                        elif alert_detection is not None:
                            content_item['Detection time'] = "Detection time: " + alert_detection
                            content_item['IP addresses'] = "IP addresses: " + item.get("IP addresses", "")
                            content_item['Suspicious domain'] = "Suspicious domain: " + item.get("Suspicious domain", "")
                            content_item['Triggered domain'] = "Triggered domain: " + item.get("Triggered domain", "")
                        elif breach_date is not None:
                            content_item['Already Seen'] = "Already Seen: " + item.get("already_seen", "")
                            content_item['Breach Date'] = "Breach Date: " + breach_date
                            content_item['Description'] = "Description: " + item.get("description", "")
                            content_item['Email'] = "Email: " + item.get("email", "")
                            content_item['Created Time'] = "Created Time: " + item.get("create_time", "")
                content = "\n".join(content_item.values())
            else:
                content_item = {}
                aggregate_alert_id = alert_info.get('aggregate_alert_id')
                if not isinstance(aggregate_alert_id, int):
                    aggregate_alert_id = None
                content = actionable_alerts_client.get_actionable_alert_content(actionable_alert_id=alert_id,
                                                                            aggregate_alert_id=aggregate_alert_id,
                                                                            fetch_only_current_item=True)
                # get item full content
                content = content.get('items')
                if content:
                    if content[0].get('_id'):
                        es_items = content[0].get('_source')
                        if es_items:
                            content_item['title'] = es_items.get('title')
                            content_item['content'] = es_items.get('content')
                            content_item['creator'] = es_items.get('creator')
                            threat_actor = es_items.get('creator')

            actionable_alert["threat_actor"] = threat_actor
            actionable_alert["threat_source"] = es_item.get("site") if isinstance(es_item, dict) else ""

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
            # content = alert_info.get("es_item", {}).get("highlight", {}).get("content")
            # content = content[0] if isinstance(content, list) and content else content
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
                actor_source = es_item.get("site") if isinstance(es_item, dict) else ""
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
