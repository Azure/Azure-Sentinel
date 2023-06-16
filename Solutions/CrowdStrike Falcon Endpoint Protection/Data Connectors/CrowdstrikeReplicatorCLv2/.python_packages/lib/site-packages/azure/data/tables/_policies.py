# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import time
from typing import Any, TYPE_CHECKING, Dict
from wsgiref.handlers import format_date_time
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore

from azure.core.pipeline.policies import (
    HeadersPolicy,
    SansIOHTTPPolicy,
    RetryPolicy,
)
from azure.core.exceptions import AzureError, ServiceRequestError, ClientAuthenticationError

from ._common_conversion import _transform_patch_to_cosmos_post
from ._models import LocationMode

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineRequest


def set_next_host_location(settings, request):
    # type: (Dict[str, Any], PipelineRequest) -> None
    """
    A function which sets the next host location on the request, if applicable.
    """
    if request.http_request.method not in ['GET', 'HEAD']:
        return
    try:
        if settings["retry_secondary"] and settings["hosts"] and all(settings["hosts"].values()):
            url = urlparse(request.http_request.url)
            # If there's more than one possible location, retry to the alternative
            if settings["mode"] == LocationMode.PRIMARY:
                settings["mode"] = LocationMode.SECONDARY
            else:
                settings["mode"] = LocationMode.PRIMARY
            updated = url._replace(netloc=settings["hosts"].get(settings["mode"]))
            request.http_request.url = updated.geturl()
    except KeyError:
        pass


class StorageHeadersPolicy(HeadersPolicy):

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        super(StorageHeadersPolicy, self).on_request(request)

        # Add required date headers
        current_time = format_date_time(time.time())
        request.http_request.headers["x-ms-date"] = current_time
        request.http_request.headers["Date"] = current_time


class StorageHosts(SansIOHTTPPolicy):
    def __init__(self, hosts=None, **kwargs):  # pylint: disable=unused-argument
        self.hosts = hosts
        super(StorageHosts, self).__init__()

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        request.context.options["hosts"] = self.hosts
        parsed_url = urlparse(request.http_request.url)

        # Detect what location mode we're currently requesting with
        location_mode = LocationMode.PRIMARY
        for key, value in self.hosts.items():
            if parsed_url.netloc == value:
                location_mode = key

        # See if a specific location mode has been specified, and if so, redirect
        use_location = request.context.options.pop("use_location", None)
        if use_location:
            # Lock retries to the specific location
            request.context.options["retry_to_secondary"] = False
            if use_location not in self.hosts:
                raise ValueError(
                    "Attempting to use undefined host location {}".format(use_location)
                )
            if use_location != location_mode:
                # Update request URL to use the specified location
                updated = parsed_url._replace(netloc=self.hosts[use_location])
                request.http_request.url = updated.geturl()
                location_mode = use_location

        request.context.options["location_mode"] = location_mode


class TablesRetryPolicy(RetryPolicy):
    """A retry policy.

    The retry policy in the pipeline can be configured directly, or tweaked on a per-call basis.

    :keyword bool retry_to_secondary: Whether to allow retrying to the secondary fail-over host
     location. Default value is False.

    :keyword int retry_total: Total number of retries to allow. Takes precedence over other counts.
     Default value is 10.

    :keyword int retry_connect: How many connection-related errors to retry on.
     These are errors raised before the request is sent to the remote server,
     which we assume has not triggered the server to process the request. Default value is 3.

    :keyword int retry_read: How many times to retry on read errors.
     These errors are raised after the request was sent to the server, so the
     request may have side-effects. Default value is 3.

    :keyword int retry_status: How many times to retry on bad status codes. Default value is 3.

    :keyword float retry_backoff_factor: A backoff factor to apply between attempts after the second try
     (most errors are resolved immediately by a second try without a delay).
     In fixed mode, retry policy will always sleep for {backoff factor}.
     In 'exponential' mode, retry policy will sleep for: `{backoff factor} * (2 ** ({number of total retries} - 1))`
     seconds. If the backoff_factor is 0.1, then the retry will sleep
     for [0.0s, 0.2s, 0.4s, ...] between retries. The default value is 0.8.

    :keyword int retry_backoff_max: The maximum back off time. Default value is 120 seconds (2 minutes).

    :keyword RetryMode retry_mode: Fixed or exponential delay between attemps, default is exponential.

    :keyword int timeout: Timeout setting for the operation in seconds, default is 604800s (7 days).
    """

    def __init__(self, **kwargs):
        super(TablesRetryPolicy, self).__init__(**kwargs)
        self.retry_to_secondary = kwargs.get('retry_to_secondary', False)

    def is_retry(self, settings, response):
        """Is this method/status code retryable? (Based on allowlists and control
        variables such as the number of total retries to allow, whether to
        respect the Retry-After header, whether this header is present, and
        whether the returned status code is on the list of status codes to
        be retried upon on the presence of the aforementioned header)
        """
        should_retry = super(TablesRetryPolicy, self).is_retry(settings, response)
        status = response.http_response.status_code
        if status == 404 and settings['mode'] == LocationMode.SECONDARY:
            # Response code 404 should be retried if secondary was used.
            return True
        return should_retry

    def configure_retries(self, options):
        """Configures the retry settings.

        :param options: keyword arguments from context.
        :return: A dict containing settings and history for retries.
        :rtype: dict
        """
        config = super(TablesRetryPolicy, self).configure_retries(options)
        config["retry_secondary"] = options.pop("retry_to_secondary", self.retry_to_secondary)
        config["mode"] = options.pop("location_mode", LocationMode.PRIMARY)
        config["hosts"] = options.pop("hosts", None)
        return config

    def update_context(self, context, retry_settings):
        """Updates retry history in pipeline context.

        :param context: The pipeline context.
        :type context: ~azure.core.pipeline.PipelineContext
        :param retry_settings: The retry settings.
        :type retry_settings: dict
        """
        super(TablesRetryPolicy, self).update_context(context, retry_settings)
        context['location_mode'] = retry_settings['mode']

    def update_request(self, request, retry_settings):  # pylint:disable=no-self-use
        """Updates the pipeline request before attempting to retry.

        :param PipelineRequest request: The outgoing request.
        :param dict(str, Any) retry_settings: The current retry context settings.
        """
        set_next_host_location(retry_settings, request)

    def send(self, request):
        """Sends the PipelineRequest object to the next policy. Uses retry settings if necessary.

        :param request: The PipelineRequest object
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: Returns the PipelineResponse or raises error if maximum retries exceeded.
        :rtype: :class:`~azure.core.pipeline.PipelineResponse`
        :raises: ~azure.core.exceptions.AzureError if maximum retries exceeded.
        :raises: ~azure.core.exceptions.ClientAuthenticationError if authentication
        """
        retry_active = True
        response = None
        retry_settings = self.configure_retries(request.context.options)
        absolute_timeout = retry_settings['timeout']
        is_response_error = True

        while retry_active:
            try:
                start_time = time.time()
                self._configure_timeout(request, absolute_timeout, is_response_error)
                response = self.next.send(request)
                if self.is_retry(retry_settings, response):
                    retry_active = self.increment(retry_settings, response=response)
                    if retry_active:
                        self.update_request(request, retry_settings)
                        self.sleep(retry_settings, request.context.transport, response=response)
                        is_response_error = True
                        continue
                break
            except ClientAuthenticationError:  # pylint:disable=try-except-raise
                # the authentication policy failed such that the client's request can't
                # succeed--we'll never have a response to it, so propagate the exception
                raise
            except AzureError as err:
                if self._is_method_retryable(retry_settings, request.http_request):
                    retry_active = self.increment(retry_settings, response=request, error=err)
                    if retry_active:
                        self.update_request(request, retry_settings)
                        self.sleep(retry_settings, request.context.transport)
                        if isinstance(err, ServiceRequestError):
                            is_response_error = False
                        else:
                            is_response_error = True
                        continue
                raise err
            finally:
                end_time = time.time()
                if absolute_timeout:
                    absolute_timeout -= (end_time - start_time)

        self.update_context(response.context, retry_settings)
        return response


class CosmosPatchTransformPolicy(SansIOHTTPPolicy):
    """Policy to transform PATCH requests into POST requests with the "X-HTTP-Method":"MERGE" header set."""

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        if request.http_request.method == "PATCH":
            _transform_patch_to_cosmos_post(request.http_request)
