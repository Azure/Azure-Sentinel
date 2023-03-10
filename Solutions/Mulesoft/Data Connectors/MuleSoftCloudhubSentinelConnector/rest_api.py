import logging
import requests


def get_alerts(username, password, app_name, env_id, start_time, end_time, limit=1000):
    #mock_url = "https://anypoint.mulesoft.com/mocking/api/v1/sources/exchange/assets/f1e97bc6-315a-4490-82a7-23abe036327a.anypoint-platform/cloudhub-api/1.0.20/m/v2/alerts?offset=0"
    url = 'https://anypoint.mulesoft.com/cloudhub/api/v2/alerts'
    params = {
        "resource": app_name,
        "limit": limit
    }
    headers = {'X-ANYPNT-ENV-ID': env_id}
    alerts = requests.get(url=url, headers=headers, auth=(username, password), params=params).json()
    filtered_alerts = []
    if type(alerts) == list:
        filtered_alerts = list(filter(lambda alert: start_time <= alert["createdAt"] <= end_time, alerts))
        if len(filtered_alerts) == 0:
            logging.info("No new alerts were added.")
    else:
        if "message" in alerts:
            logging.error(alerts["message"])
        else:
            logging.info("List of alerts are empty.")
    return filtered_alerts


def get_logs(username, password, env_id, start_time, end_time):
    #mock_domain_url = "https://anypoint.mulesoft.com/mocking/api/v1/sources/exchange/assets/f1e97bc6-315a-4490-82a7-23abe036327a.anypoint-platform/cloudhub-api/1.0.20/m/v2/applications?retrieveStatistics=false&period=3600000&retrieveLogLevels=true&retrieveTrackingSettings=true&retrieveIpAddresses=true"
    domain_url = "https://anypoint.mulesoft.com/cloudhub/api/v2/applications"
    headers = {'X-ANYPNT-ENV-ID': env_id,
               "content-type": "application/json"}
    body = {"startTime": start_time,
            "endTime": end_time}
    domains_json = requests.get(url=domain_url, headers=headers, data=body, auth=(username, password)).json()
    logs = []
    if len(domains_json) == 0:
        logging.info("List of domains are empty.")
    else:
        if type(domains_json) is list:
            domains = list(map(lambda application: application["domain"], domains_json))
            for domain in domains:
                #mock_log_url = "https://anypoint.mulesoft.com/mocking/api/v1/sources/exchange/assets/f1e97bc6-315a-4490-82a7-23abe036327a.anypoint-platform/cloudhub-api/1.0.20/m/v2/applications/" + domain + "/logs"
                log_url = "https://anypoint.mulesoft.com/cloudhub/api/v2/applications/" + domain + "/logs"
                logs += requests.post(url=log_url, headers=headers, auth=(username, password)).json()
                if any(type(log) == str for log in logs):
                    logs = []
                    logging.info("List of logs are empty.")
        else:
            logging.error(domains_json["message"])
    return logs

