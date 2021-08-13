# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time

from azure.core.pipeline.policies import AsyncRetryPolicy
from azure.core.exceptions import (
    AzureError,
    ClientAuthenticationError,
    ServiceRequestError
)

from .._models import LocationMode
from .._policies import set_next_host_location


class AsyncTablesRetryPolicy(AsyncRetryPolicy):
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
     In fixed mode, retry policy will alwasy sleep for {backoff factor}.
     In 'exponential' mode, retry policy will sleep for: `{backoff factor} * (2 ** ({number of total retries} - 1))`
     seconds. If the backoff_factor is 0.1, then the retry will sleep
     for [0.0s, 0.2s, 0.4s, ...] between retries. The default value is 0.8.

    :keyword int retry_backoff_max: The maximum back off time. Default value is 120 seconds (2 minutes).

    :keyword RetryMode retry_mode: Fixed or exponential delay between attemps, default is exponential.

    :keyword int timeout: Timeout setting for the operation in seconds, default is 604800s (7 days).
    """

    def __init__(self, **kwargs):
        super(AsyncTablesRetryPolicy, self).__init__(**kwargs)
        self.retry_to_secondary = kwargs.get('retry_to_secondary', False)

    def is_retry(self, settings, response):
        """Is this method/status code retryable? (Based on whitelists and control
        variables such as the number of total retries to allow, whether to
        respect the Retry-After header, whether this header is present, and
        whether the returned status code is on the list of status codes to
        be retried upon on the presence of the aforementioned header)
        """
        should_retry = super(AsyncTablesRetryPolicy, self).is_retry(settings, response)
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
        config = super(AsyncTablesRetryPolicy, self).configure_retries(options)
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
        super(AsyncTablesRetryPolicy, self).update_context(context, retry_settings)
        context['location_mode'] = retry_settings['mode']

    def update_request(self, request, retry_settings):  # pylint: disable=no-self-use
        """Updates the pipeline request before attempting to retry.

        :param PipelineRequest request: The outgoing request.
        :param dict(str, Any) retry_settings: The current retry context settings.
        """
        set_next_host_location(retry_settings, request)

    async def send(self, request):
        """Uses the configured retry policy to send the request to the next policy in the pipeline.

        :param request: The PipelineRequest object
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: Returns the PipelineResponse or raises error if maximum retries exceeded.
        :rtype: ~azure.core.pipeline.PipelineResponse
        :raise: ~azure.core.exceptions.AzureError if maximum retries exceeded.
        :raise: ~azure.core.exceptions.ClientAuthenticationError if authentication fails
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
                response = await self.next.send(request)
                if self.is_retry(retry_settings, response):
                    retry_active = self.increment(retry_settings, response=response)
                    if retry_active:
                        self.update_request(request, retry_settings)
                        await self.sleep(retry_settings, request.context.transport, response=response)
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
                        await self.sleep(retry_settings, request.context.transport)
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
