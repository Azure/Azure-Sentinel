from datetime import datetime
import logging
import requests
import config

from requests.auth import HTTPBasicAuth

from models import Email, Event, Model


def _build_url(model: Model, *args, **kwargs) -> str:
    """
    Build the URL based on the base url from config, the resource url from the model and any provided *args and
    **kwargs. *args are appended to the base resource separated by /. **kwargs are added as url parameters
    with key=value
    """
    url_parts = []
    for part in args:
        url_parts.append('/')
        url_parts.append(str(part))

    if kwargs:
        url_parts.append('?')
        for k, v in kwargs.items():
            if v is not None and v is not False:
                url_parts += [k, '=', str(v), '&']

    if len(url_parts) != 0 and url_parts[-1] == '&':
        url_parts.pop()

    return ''.join([config.BASE_URL, model.RESOURCE_URL] + url_parts)


def _list(cls: Model, *args, **kwargs):
    url = _build_url(cls, *args, **kwargs)

    response = requests.get(url,
                            auth=HTTPBasicAuth(config.API_KEY, config.API_SECRET),
                            headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                            verify=config.VERIFY_CERTIFICATE)

    if (response.status_code >= 400):
        error_message = response.json()
        if (response.json().get('data') is not None):
            if (response.json()['data'].get('message') is not None):
                error_message = response.json()['data']['message']
            else:
                error_message = response.json()['data']
        logging.error(error_message)
        raise Exception(error_message)

    items = []
    for item in response.json()['data']:
        items.append(cls.from_json(item))

    return items


def _get(cls: Model, *args, **kwargs):
    url = _build_url(cls, *args, **kwargs)

    response = requests.get(url,
                            auth=HTTPBasicAuth(config.API_KEY, config.API_SECRET),
                            headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                            verify=config.VERIFY_CERTIFICATE)

    if (response.status_code >= 400):
        error_message = response.json()
        if (response.json().get('data') is not None):
            if (response.json()['data'].get('message') is not None):
                error_message = response.json()['data']['message']
            else:
                error_message = response.json()['data']
        logging.error(error_message)
        raise Exception(error_message)

    return response.json()['data']

def _url_format_time(time: datetime) -> str:
    if time is None:
        return None

    return str(time.timestamp())


def events_list(page: int = 1, limit: int = 20, as_partner=False, direction='asc', after=None, after_id: int = None):
    """
    Returns an array of Event
    """
    return _list(Event,
                 page=page, limit=limit,
                 partner=as_partner,
                 after=_url_format_time(after),
                 direction=direction,
                 after_id=after_id)


def emails_list(page: int = 1, limit: int = 20, as_partner=False, direction='desc', after=None, cohort_id=None,
                signature_id=None, email_ids=None, enrich=False):
    """
    Returns an array of Email
    """
    return _list(Email,
                 page=page, limit=limit,
                 partner=as_partner,
                 direction=direction,
                 after=_url_format_time(after),
                 cohort=cohort_id,
                 signature=signature_id,
                 email_ids=email_ids,
                 enrich=enrich)


def emails_get(email_id: int):
    """
    Returns the Email corresponding to the provided email_id
    """
    email_json = _get(Email, email_id)

    return Email.from_json(email_json, full=True)
