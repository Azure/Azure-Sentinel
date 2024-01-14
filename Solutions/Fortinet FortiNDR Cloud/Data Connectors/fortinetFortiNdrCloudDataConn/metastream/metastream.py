import os.path
from datetime import datetime, timedelta, timezone, date
from typing import List

from globalVariables import SUPPORTED_EVENT_TYPES, BUCKETS
from .s3_client import S3Client, Context
from .auth_client import Auth
from .errors import InputError, ServerError

def _validate_start_date(start_date: datetime, checkpoint: datetime):
    if start_date > checkpoint:
        raise InputError(message="start_date must be at least 1 second in the past")

    delta = checkpoint - start_date
    if delta > timedelta(days=1):
        raise InputError(message="start_date must be within the last 24 hours")


def _validate_day(day: date):
    if (datetime.now(timezone.utc).date() - day).days > 7:
        raise InputError(message="day must be within 7 days")


def _validate_event_types(event_types):
    if not all(e in SUPPORTED_EVENT_TYPES for e in event_types):
        raise InputError(f'event_types must be of the following: {", ".join(SUPPORTED_EVENT_TYPES)}')


def _validate_limit(limit: int):
    if limit < 1 or limit > 10_000:
        raise InputError('limit must be between 1 and 10,000')


def _basename(prefix):
    return os.path.basename(prefix.rstrip('/'))


def _prefix_to_datetime(date_prefix: str) -> datetime:
    """
    Converts a S3 bucket key prefix to a datetime.
    :param date_prefix: assumes the last element is a date in YYYYMMDD format
    :return: UTC datetime
    """
    date = _basename(date_prefix)
    if date.startswith("date_partition="):
        date = date[15:]
    try:
        return datetime.strptime(date + '+0000', "%Y%m%d%z")
    except ValueError:
        raise ServerError(message=f'unknown format for date_prefix: {date_prefix}', code=0) from None


def _ts_to_datetime(timestamp: str) -> datetime:
    """Converts an ISO 8601 formatted timestamp to a datetime"""
    if not timestamp:
        return datetime.min
    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')


def _get_customer_prefix(account_code: str, env: str) -> str:
    """returns the bucket key prefix up to the account_code"""
    if env.lower() == "uat":
        account_code = f'uat-{account_code}'
    return f'v1/customer/cust-{account_code}'


def _get_bucket(env: str):
    if env.lower() == "production":
        return BUCKETS["production"]
    else:
        return BUCKETS["uat"]


def _fetch_account_code(env: str, account_code: str = None, api_token: str = None) -> str:
    """returns account_code if given or else attempts to fetch the account code from the auth API"""
    if not any([account_code, api_token]):
        raise InputError(f"one of 'account_code' or 'api_token' is required")
    if account_code:
        return account_code

    with Auth(api_token, env) as auth:
        user = auth.user()
        account_uuid = user.get("account_uuid")
        account = auth.account(account_uuid)
        account_code = account.get("code")
        if account_code is None:
            raise InputError("unable to get account code from auth")
        return account_code


def _create_user_agent_extra(name, account_code):
    user_agent_extra = f'integrations-{name}-{account_code}'
    return user_agent_extra


def fetch_events(name: str, event_types: List[str], account_code: str = None, api_token: str = None,
                 start_date: datetime = datetime.now(timezone.utc) - timedelta(minutes=5),
                 access_key: str = None, secret_key: str = None, limit: int = 0, env: str = "production",
                 context: Context = None):
    """fetches events from metastream.  See README.md for full details"""
    checkpoint = datetime.now(tz=timezone.utc).replace(microsecond=0)
    if context:
        context.checkpoint = checkpoint

    account_code = _fetch_account_code(env, account_code, api_token)
    _validate_event_types(event_types)
    _validate_start_date(start_date, checkpoint)

    start_day = start_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

    if not event_types:
        event_types = SUPPORTED_EVENT_TYPES

    num_events = 0
    cut_off = checkpoint - timedelta(seconds=1)

    user_agent_extra = _create_user_agent_extra(name, account_code)

    with S3Client(_get_bucket(env), access_key, secret_key, user_agent_extra, context=context) as s3:
        for sensor_prefix in s3.fetch_common_prefixes(_get_customer_prefix(account_code, env)):
            if _basename(sensor_prefix) in ['devices', 'signals']:
                continue

            for date_prefix in s3.fetch_common_prefixes(sensor_prefix):
                if start_day > _prefix_to_datetime(date_prefix):
                    continue

                for event_type_prefix in s3.fetch_common_prefixes(date_prefix):
                    if _basename(event_type_prefix) not in event_types:
                        continue

                    for obj in s3.fetch_file_objects(f'{event_type_prefix}v1/'):
                        if start_date > obj.get('LastModified'):
                            continue
                        if obj.get('LastModified') > cut_off:
                            continue

                        events = s3.fetch_gzipped_json_lines_file(obj.get('Key'))
                        if limit:
                            yield events[:limit - num_events]
                            num_events += len(events)
                            if num_events >= limit:
                                return
                        else:
                            yield events


def fetch_events_by_day(name: str, day: datetime, event_type: str, account_code: str, api_token: str = None,
                        access_key: str = None, secret_key: str = None, limit: int = 0, env: str = "production",
                        context: Context = None) -> List[dict]:
    """fetches events from metastream for an entire day.  See README.md for full details"""
    account_code = _fetch_account_code(env, account_code, api_token)
    _validate_day(day.date())
    start_day = day.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

    user_agent_extra = _create_user_agent_extra(name, account_code)
    num_events = 0
    with S3Client(_get_bucket(env), access_key, secret_key, user_agent_extra, context=context) as s3:
        for sensor_prefix in s3.fetch_common_prefixes(_get_customer_prefix(account_code, env)):
            if _basename(sensor_prefix) in ['devices', 'signals']:
                continue

            for date_prefix in s3.fetch_common_prefixes(sensor_prefix):
                if start_day != _prefix_to_datetime(date_prefix):
                    continue

                for event_type_prefix in s3.fetch_common_prefixes(date_prefix):
                    if _basename(event_type_prefix) != event_type:
                        continue

                    for obj in s3.fetch_file_objects(f'{event_type_prefix}v1/'):
                        events = s3.fetch_gzipped_json_lines_file(obj.get('Key'))
                        if limit:
                            yield events[:limit - num_events]
                            num_events += len(events)
                            if num_events >= limit:
                                return
                        else:
                            yield events


def fetch_detections_by_day(name: str, day: date, account_code: str, access_key: str = None, secret_key: str = None,
                            limit: int = 0, env: str = "production", context: Context = None) -> List[dict]:
    """fetches events from metastream for an entire day.  See README.md for full details"""
    _validate_day(day)

    user_agent_extra = _create_user_agent_extra(name, account_code)
    num_events = 0
    with S3Client(_get_bucket(env), access_key, secret_key, user_agent_extra, context=context) as s3:
        for sensor_prefix in s3.fetch_common_prefixes(_get_customer_prefix(account_code, env)):
            if _basename(sensor_prefix) != 'signals':
                continue

            for date_prefix in s3.fetch_common_prefixes(sensor_prefix):
                if day != _prefix_to_datetime(date_prefix).date():
                    continue

                for obj in s3.fetch_file_objects(date_prefix):
                    if not _basename(obj.get('Key', '')).startswith('detection_none'):
                        continue
                    events = s3.fetch_gzipped_json_lines_file(obj.get('Key'))
                    if limit:
                        yield events[:limit - num_events]
                        num_events += len(events)
                        if num_events >= limit:
                            return
                    else:
                        yield events


def fetch_detections(name: str, account_code: str, start_date: datetime, access_key: str = None, secret_key: str = None,
                     limit: int = 0, env: str = "production", context: Context = None):
    """fetches events from metastream.  See README.md for full details"""
    checkpoint = datetime.now(tz=timezone.utc).replace(microsecond=0)
    if context:
        context.checkpoint = checkpoint

    _validate_start_date(start_date, checkpoint)

    start_day = start_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

    num_events = 0
    cut_off = checkpoint - timedelta(seconds=1)

    user_agent_extra = _create_user_agent_extra(name, account_code)

    with S3Client(_get_bucket(env), access_key, secret_key, user_agent_extra, context=context) as s3:
        for sensor_prefix in s3.fetch_common_prefixes(_get_customer_prefix(account_code, env)):
            if _basename(sensor_prefix) != 'signals':
                continue

            for date_prefix in s3.fetch_common_prefixes(sensor_prefix):
                if start_day > _prefix_to_datetime(date_prefix):
                    continue

                for obj in s3.fetch_file_objects(date_prefix):
                    if not _basename(obj.get('Key', '')).startswith('detection_none'):
                        continue
                    if start_date > obj.get('LastModified'):
                        continue
                    if obj.get('LastModified') > cut_off:
                        continue

                    events = s3.fetch_gzipped_json_lines_file(obj.get('Key'))
                    if limit:
                        yield events[:limit - num_events]
                        num_events += len(events)
                        if num_events >= limit:
                            return
                    else:
                        yield events


def fetch_event_types():
    return SUPPORTED_EVENT_TYPES
