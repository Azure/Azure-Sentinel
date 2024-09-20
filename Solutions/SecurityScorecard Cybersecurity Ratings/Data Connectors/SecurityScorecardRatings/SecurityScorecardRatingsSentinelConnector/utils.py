"""Utils module is for helping methods."""
import requests


def make_rest_call(url, secret_key):
    """Connect to securityScorecard api and returns json data.

    :param url: str
    :param secret_key: str
    :return: json
    """
    headers = {
        "Accept": "application/json; charset=utf-8",
        'Authorization': 'Token {}'.format(secret_key),
        "X-SSC-Application-Name": "Microsoft Sentinel",
        "X-SSC-Application-Version": "1.0",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def format_date_string(date_string):
    """format_date_string function will format date string."""
    return date_string.replace('T', ' ')[:19]
