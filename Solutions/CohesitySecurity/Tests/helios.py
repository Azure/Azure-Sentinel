#!/usr/bin/env python3

import requests


def get_alert_details(alert_id, apiKey):
    api_url = "https://helios.cohesity.com/mcm/alerts?maxAlerts=10&alertIdList=" + alert_id
    headers = {"Content-Type": "application/json"}
    headers["authority"] = "helios.cohesity.com"
    headers["apiKey"] = apiKey
    response = requests.get(api_url, headers=headers)
    return response.json()[0]
