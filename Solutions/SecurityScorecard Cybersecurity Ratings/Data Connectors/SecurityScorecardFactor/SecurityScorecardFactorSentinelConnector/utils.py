"""Utils module is for helping methods."""
import requests


def make_rest_call(url, secret_key):
    """Connect to SecurityScorecard api and returns json data.

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
    params = {'timing': 'daily'}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def format_date_string(date_string):
    """format_date_string function will format date string."""
    return date_string.replace('T', ' ')[:19]


def get_value_from_dict_list(iterable, key, value):
    """get_value_from_dict_list method will check the key exists and matches with the value \
    in a iterable of dicts, and returns it if present.

    :param iterable:
    :param key: str, Key to check
    :param value: str, value to check
    :return: dict if present else None
    """
    for item in iterable:
        if key in item.keys() and item[key] == value:
            return item

    return None
