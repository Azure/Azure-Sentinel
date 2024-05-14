import os.path
from datetime import datetime, timedelta, timezone
from typing import Iterator, List

from fnc.global_variables import CLIENT_DEFAULT_USER_AGENT, DEFAULT_DATE_FORMAT, METASTREAM_DEFAULT_BUCKET, METASTREAM_SUPPORTED_EVENT_TYPES
from fnc.utils import datetime_to_utc_str, str_to_utc_datetime

from ..errors import ErrorMessages, ErrorType, FncClientError
from ..logger import BasicLogger, FncClientLogger
from .s3_client import MetastreamContext, S3Client


class FncMetastreamClient:
    user_agent: str
    account_code: str
    access_key: str
    secret_key: str
    bucket: str
    logger: FncClientLogger

    def __init__(self,
                 name: str,
                 account_code: str = None,
                 access_key: str = None,
                 secret_key: str = None,
                 bucket: str = None,
                 logger: FncClientLogger = None):
        name = f'{name}-metastream' if name else 'metastream'
        user_agent = f"{CLIENT_DEFAULT_USER_AGENT}-{name}"
        self.logger = logger or BasicLogger(name=user_agent)

        self.get_logger().info(f"Initializing {user_agent}.")

        if not all([account_code, access_key, secret_key]):
            missing = []
            if not access_key:
                missing.append('access_key')
            if not secret_key:
                missing.append('secret_key')
            if not account_code:
                missing.append('account_code')

            raise FncClientError(
                error_type=ErrorType.CLIENT_VALIDATION_ERROR,
                error_message=ErrorMessages.CLIENT_REQUIRED_ARGUMENT_MISSING,
                error_data={'args': missing, 'client': 'FncMetastreamClient'}
            )

        self.user_agent = f'{user_agent}-{account_code}'
        self.account_code = account_code
        self.access_key = access_key
        self.secret_key = secret_key
        if not bucket:
            self.get_logger().info("No bucket was provided. We will use the default.")
        self.bucket = bucket or METASTREAM_DEFAULT_BUCKET

        self.get_logger().info(f"{user_agent} successfully initialized.")

    def get_logger(self):
        return self.logger

    def _get_customer_prefix(self) -> str:
        """returns the bucket key prefix up to the account_code"""
        return f'v1/customer/cust-{self.account_code}'

    def _validate(self, event_types: List[str], start_date: datetime, end_date: datetime = None):
        self.get_logger().debug("Validating metastream events fetch request's arguments.")

        failed = []
        if not all(e in METASTREAM_SUPPORTED_EVENT_TYPES for e in event_types):
            failed.append(f'Invalid event types. The event_types must be of the following: {", ".join(METASTREAM_SUPPORTED_EVENT_TYPES)}')

        if not end_date:
            d = start_date.date() if isinstance(start_date, datetime) else start_date
            if (datetime.now(timezone.utc).date() - d).days > 7:
                failed.append("Only events within last 7 days can be searched.")

            if (datetime.now(timezone.utc).date() - d).days < 1:
                failed.append("Only events for a whole day within last 7 days can be searched.")
        else:
            delta = end_date - start_date
            if delta > timedelta(days=1):
                failed.append("The search window must be less than 24 hours.")

            if start_date > end_date:
                failed.append("The search window must be at least 1 second.")

        if failed:
            raise FncClientError(
                error_type=ErrorType.EVENTS_FETCH_VALIDATION_ERROR,
                error_message=ErrorMessages.EVENTS_FETCH_VALIDATION_ERROR,
                error_data={'failed': failed}
            )
        else:
            self.get_logger().info("The arguments for the metastream events fetch request has been successfully validated.")

    def _basename(self, prefix):
        return os.path.basename(prefix.rstrip('/'))

    def _prefix_to_datetime(self, date_prefix: str) -> datetime:
        """
        Converts a S3 bucket key prefix to a datetime.
        :param date_prefix: assumes the last element is a date in YYYYMMDD format
        :return: UTC datetime
        """
        date_str = self._basename(date_prefix)
        if date_str.startswith("date_partition="):
            date_str = date_str[15:]
        try:
            return str_to_utc_datetime(datetime_str=date_str, format="%Y%m%d")
        except ValueError as e:
            raise FncClientError(
                error_type=ErrorType.EVENTS_UNKNOWN_DATE_PREFIX_FORMAT,
                error_message=ErrorMessages.EVENTS_UNKNOWN_DATE_PREFIX_FORMAT,
                error_data={'date_prefix': date_str, 'error': e},
                exception=e
            ) from e

    def _get_prefixes(self, s3: S3Client, event_type: str, start_day: datetime = None, end_day: datetime = None, context: MetastreamContext = None):
        if not s3:
            self.get_logger().warning("Prefixes for the S3 buckets cannot be retrieved due to: The client to connect to AWS S3 bucket was not provided.")
            return

        if not start_day:
            self.get_logger().warning("Prefixes for the S3 buckets cannot be retrieved due to: The start day was not provided.")
            return

        self.get_logger().debug(f"Processing buckets for customer prefix: '{self._get_customer_prefix()}'")

        start_day = start_day.replace(hour=0, minute=0, second=0,
                                      microsecond=0, tzinfo=timezone.utc)

        for sensor_prefix in s3.fetch_common_prefixes(self._get_customer_prefix()):
            sensor = self._basename(sensor_prefix)
            if sensor in ['devices', 'signals']:
                continue
            self.get_logger().debug(f"Processing sensor '{sensor}'")

            for date_prefix in s3.fetch_common_prefixes(sensor_prefix):
                d = self._prefix_to_datetime(date_prefix=date_prefix)
                if not end_day:
                    # We are pulling a full single day
                    if start_day != d:
                        continue
                else:
                    # We are pulling a indow of time
                    if start_day > d or end_day < d:
                        continue

                self.get_logger().debug(f"Processing date prefix '{d}'")

                for event_type_prefix in s3.fetch_common_prefixes(date_prefix):
                    e_type = self._basename(event_type_prefix)
                    if e_type != event_type:
                        continue

                    yield event_type_prefix

    def _get_events_from_prefix(
        self, s3: S3Client, prefix: str = None,
        limit: int = 0, num_events: int = 0,
        start_date: datetime = None, end_date: datetime = None
    ):
        if limit and num_events >= limit:
            return

        for obj in s3.fetch_file_objects(f'{prefix}v1/'):
            obj_time = obj.get('LastModified').time()

            if start_date and start_date > obj.get('LastModified'):
                continue

            if end_date:
                end_time = end_date.time()
                if obj_time > end_time:
                    continue

            events = s3.fetch_gzipped_json_lines_file(
                obj.get('Key'))

            if limit:
                self.get_logger().debug(f"{limit - num_events} events reported from {obj.get('Key')}")
                yield events[:limit - num_events]
                num_events += len(events)
                if num_events >= limit:
                    return
            else:
                self.get_logger().debug(f"{len(events)} events reported from {obj.get('Key')}")
                yield events

    def fetch_events_by_day(self, day: datetime, event_type: str, limit: int = 0, context: MetastreamContext = None) -> Iterator[List[dict]]:
        """fetches events from metastream for an entire day.  See README.md for full details"""
        self.get_logger().info(f"Fetching {event_type} events for {day.date()}.")

        try:
            self._validate(event_types=[event_type], start_date=day.date())
        except FncClientError as e:
            self.get_logger().error(f'Events cannot be fetched due to: {str(e)}')
            raise e

        start_day = day.replace(hour=0, minute=0, second=0,
                                microsecond=0, tzinfo=timezone.utc)

        num_events = 0

        self.get_logger().info("Fetching events")
        with S3Client(self.bucket, self.access_key, self.secret_key, self.user_agent, context=context) as s3:
            for event_type_prefix in self._get_prefixes(s3=s3, event_type=event_type, start_day=start_day, context=context):
                for events in self._get_events_from_prefix(
                    s3=s3, prefix=event_type_prefix,
                    limit=limit, num_events=num_events
                ):
                    num_events += len(events)
                    yield events

    def fetch_events(self,
                     event_type: str,
                     start_date: datetime = datetime.now(
                         timezone.utc) - timedelta(minutes=5),
                     end_date: datetime = None,
                     limit: int = 0,
                     context: MetastreamContext = None) -> Iterator[List[dict]]:
        """fetches events from metastream.  See README.md for full details"""
        # Ensure Dates are in UTC
        end_date_str = datetime_to_utc_str(datetime_obj=end_date, format=DEFAULT_DATE_FORMAT)
        start_date_str = datetime_to_utc_str(datetime_obj=start_date, format=DEFAULT_DATE_FORMAT)
        start_date = str_to_utc_datetime(datetime_str=start_date_str, format=DEFAULT_DATE_FORMAT)
        end_date = str_to_utc_datetime(datetime_str=end_date_str, format=DEFAULT_DATE_FORMAT)

        checkpoint = end_date or datetime.now(tz=timezone.utc).replace(microsecond=0)
        checkpoint_str = datetime_to_utc_str(datetime_obj=checkpoint, format=DEFAULT_DATE_FORMAT)

        if context:
            context.update_checkpoint(checkpoint=checkpoint_str)

        event_types = [event_type]

        self.get_logger().info(f"Fetching {event_type} events between {start_date_str} and {checkpoint}.")

        try:
            self._validate(event_types=event_types, start_date=start_date, end_date=checkpoint)
        except FncClientError as e:
            self.get_logger().error(f'Events cannot be fetched due to: {str(e)}')
            raise e

        num_events = 0
        cut_off = checkpoint - timedelta(seconds=1)

        start_day = start_date.replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        end_day = cut_off.replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

        with S3Client(self.bucket, self.access_key, self.secret_key, self.user_agent, context=context) as s3:
            for event_type_prefix in self._get_prefixes(
                s3=s3, event_type=event_type,
                start_day=start_day, end_day=end_day,
                context=context
            ):
                for events in self._get_events_from_prefix(
                    s3=s3, prefix=event_type_prefix,
                    limit=limit, num_events=num_events,
                    start_date=start_date, end_date=cut_off
                ):
                    num_events += len(events)
                    yield events

    def fetch_event_types(self):
        return METASTREAM_SUPPORTED_EVENT_TYPES

    def get_splitted_context(self, start_date_str: str = None) -> tuple[MetastreamContext, MetastreamContext]:
        checkpoint = datetime.now(tz=timezone.utc).replace(microsecond=0)

        h_context = MetastreamContext()
        context = MetastreamContext()

        if start_date_str:
            start_date = str_to_utc_datetime(datetime_str=start_date_str, format=DEFAULT_DATE_FORMAT)
            sd = start_date.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
            history = {
                'start_date': datetime_to_utc_str(sd, DEFAULT_DATE_FORMAT),
                'end_date': datetime_to_utc_str(checkpoint, DEFAULT_DATE_FORMAT),
            }
            h_context.update_history(history=history)
            h_context.update_checkpoint(history['start_date'])

        context.update_checkpoint(checkpoint=history['end_date'])

        return h_context, context

    def poll_history(
        self, context: MetastreamContext = None,
        event_type: str = None,
        interval: timedelta = timedelta(days=1)
    ) -> Iterator[List[dict]]:
        # Raise Exception if No Context with History is passed
        if not context or not context.get_history(event_type):
            self.get_logger().error("A splitted context with the history time window is required to pull history")
            raise FncClientError(
                error_type=ErrorType.MISSING_CONTEXT,
                error_message=ErrorMessages.METASTREAM_MISSING_CONTEXT
            )

        if not event_type or event_type not in METASTREAM_SUPPORTED_EVENT_TYPES:
            failed = (f'Invalid event types. The event_types must be of the following: {", ".join(METASTREAM_SUPPORTED_EVENT_TYPES)}')
            raise FncClientError(
                error_type=ErrorType.EVENTS_FETCH_VALIDATION_ERROR,
                error_message=ErrorMessages.EVENTS_FETCH_VALIDATION_ERROR,
                error_data={'failed': failed}
            )
        try:
            if interval > timedelta(days=1):
                interval = timedelta(days=1)

            # Get the history time window
            now = datetime.now(tz=timezone.utc)
            history = context.get_history(event_type)

            # If the there is no history to pull we return
            if not history:
                self.get_logger().info(
                    f"No history to be polled for {event_type}. ")
                return

            start_date_str = history.get('start_date', None)
            end_date_str = history.get('end_date', None)

            start_date = str_to_utc_datetime(start_date_str)
            end_date = str_to_utc_datetime(end_date_str)

            if start_date + interval < end_date:
                end_date = start_date + interval
                if start_date.day != end_date.day:
                    end_date = end_date.replace(hour=0, minute=0, second=0,
                                                microsecond=0, tzinfo=timezone.utc)

                end_date_str = datetime_to_utc_str(datetime_obj=end_date, format=DEFAULT_DATE_FORMAT)

            # If the there is no history to pull we return
            if end_date == start_date:
                self.get_logger().info(
                    f"No history to be polled for {event_type} (start_date= {start_date_str} and end_date= {end_date_str}). ")
                return

            if (
                not start_date or not end_date or
                end_date > now or start_date > now or
                end_date < start_date
            ):
                self.get_logger().warning(
                    f"Polling history was called with invalid data (start_date= {start_date_str} and end_date= {end_date_str}). The call will be ignored.")
                return

            self.get_logger().info(f"Polling history from {start_date_str} to {end_date_str}")

            for events in self.fetch_events(
                context=context, event_type=event_type,
                start_date=start_date, end_date=end_date
            ):
                yield events

            history['start_date'] = context.get_checkpoint()
            context.update_history(history=history, event_type=event_type)
            context.update_checkpoint(checkpoint=None)
        except FncClientError as e:
            self.get_logger().error("The events history polling process failed.")
            raise e
        except Exception as e:
            self.get_logger().error("The events history polling process failed.")
            raise FncClientError(
                error_type=ErrorType.GENERIC_ERROR,
                error_message=ErrorMessages.GENERIC_ERROR_MESSAGE,
                error_data={'error': e}
            )
