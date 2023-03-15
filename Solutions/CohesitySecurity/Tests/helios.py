#!/usr/bin/env python3

"""
This module provides functions for interacting with the Helios cluster.
"""

import datetime
import requests
import time


def create_headers(api_key):
    """
    This function creates headers for an HTTP request to the Helios API.

    Args:
        api_key (str): The API key to authenticate the request.

    Returns:
        A dictionary containing the headers for the HTTP request.
    """
    headers = {
        "Content-Type": "application/json",
        "authority": "helios.cohesity.com",
        "apiKey": api_key
    }
    return headers


def get_alerts_details(alert_ids, api_key):
    """
    This function retrieves details for a batch of alerts, specified by a list of alert IDs.

    Args:
        alert_ids (list): A list of alert IDs to retrieve details for.
        api_key (str): The API key to authenticate the request.

    Returns:
        A dictionary containing the details for the alerts.
    """
    max_alerts = len(alert_ids)
    assert max_alerts > 0
    alert_ids = ",".join(alert_ids)
    api_url = "https://helios.cohesity.com/mcm/alerts?maxAlerts=" + str(max_alerts) + "&alertIdList=" + alert_ids
    headers = create_headers(api_key)
    response = requests.get(api_url, headers=headers)
    return response.json() if response.json() else None


def get_alert_details(alert_id, api_key):
    """
    This function retrieves details for a single alert, specified by an alert ID.

    Args:
        alert_id (str): The ID of the alert to retrieve details for.
        api_key (str): The API key to authenticate the request.

    Returns:
        A dictionary containing the details for the alert.
    """
    api_url = "https://helios.cohesity.com/mcm/alerts?maxAlerts=1&alertIdList=" + alert_id
    headers = create_headers(api_key)
    response = requests.get(api_url, headers=headers)
    return response.json()[0] if response.json() else None


def get_alerts(api_key, start_days_ago, end_days_ago):
    """
    This function retrieves a list of alert IDs for a specified time range.

    Args:
        api_key (str): The API key to authenticate the request.
        start_days_ago (int): The number of days in the past to start retrieving alerts from.
        end_days_ago (int): The number of days in the past to stop retrieving alerts at.

    Returns:
        A list of alert IDs for the specified time range.
    """
    def get_days_ago_timestamp(days_ago):
        days_ago = datetime.datetime.now() - datetime.timedelta(days=days_ago)
        days_ago_timestamp = int(time.mktime(days_ago.timetuple()) * 1000000)
        return str(days_ago_timestamp)

    api_url = "https://helios.cohesity.com/mcm/alerts?alertCategoryList=kSecurity&startDateUsecs=" + get_days_ago_timestamp(start_days_ago) + "&endDateUsecs=" + get_days_ago_timestamp(end_days_ago)
    headers = create_headers(api_key)
    response = requests.get(api_url, headers=headers)
    return [jsObj["id"] for jsObj in response.json()]


__all__ = [
    'get_alert_details',
    'get_alerts',
    'get_alerts_details',
]
