# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------


class Configuration(object):
    """Provides the home for all of the configurable policies in the pipeline.

    A new Configuration object provides no default policies and does not specify in what
    order the policies will be added to the pipeline. The SDK developer must specify each
    of the policy defaults as required by the service and use the policies in the
    Configuration to construct the pipeline correctly, as well as inserting any
    unexposed/non-configurable policies.

    :ivar headers_policy: Provides parameters for custom or additional headers to be sent with the request.
    :ivar proxy_policy: Provides configuration parameters for proxy.
    :ivar redirect_policy: Provides configuration parameters for redirects.
    :ivar retry_policy: Provides configuration parameters for retries in the pipeline.
    :ivar custom_hook_policy: Provides configuration parameters for a custom hook.
    :ivar logging_policy: Provides configuration parameters for logging.
    :ivar http_logging_policy: Provides configuration parameters for HTTP specific logging.
    :ivar user_agent_policy: Provides configuration parameters to append custom values to the
     User-Agent header.
    :ivar authentication_policy: Provides configuration parameters for adding a bearer token Authorization
     header to requests.
    :keyword polling_interval: Polling interval while doing LRO operations, if Retry-After is not set.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_config.py
            :start-after: [START configuration]
            :end-before: [END configuration]
            :language: python
            :caption: Creates the service configuration and adds policies.
    """

    def __init__(self, **kwargs):
        # Headers (sent with every request)
        self.headers_policy = None

        # Proxy settings (Currently used to configure transport, could be pipeline policy instead)
        self.proxy_policy = None

        # Redirect configuration
        self.redirect_policy = None

        # Retry configuration
        self.retry_policy = None

        # Custom hook configuration
        self.custom_hook_policy = None

        # Logger configuration
        self.logging_policy = None

        # Http logger configuration
        self.http_logging_policy = None

        # User Agent configuration
        self.user_agent_policy = None

        # Authentication configuration
        self.authentication_policy = None

        # Polling interval if no retry-after in polling calls results
        self.polling_interval = kwargs.get("polling_interval", 30)


class ConnectionConfiguration(object):
    """HTTP transport connection configuration settings.

    Common properties that can be configured on all transports. Found in the
    Configuration object.

    :keyword int connection_timeout: A single float in seconds for the connection timeout. Defaults to 300 seconds.
    :keyword int read_timeout: A single float in seconds for the read timeout. Defaults to 300 seconds.
    :keyword bool connection_verify: SSL certificate verification. Enabled by default. Set to False to disable,
     alternatively can be set to the path to a CA_BUNDLE file or directory with certificates of trusted CAs.
    :keyword str connection_cert: Client-side certificates. You can specify a local cert to use as client side
     certificate, as a single file (containing the private key and the certificate) or as a tuple of both files' paths.
    :keyword int connection_data_block_size: The block size of data sent over the connection. Defaults to 4096 bytes.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_config.py
            :start-after: [START connection_configuration]
            :end-before: [END connection_configuration]
            :language: python
            :dedent: 4
            :caption: Configuring transport connection settings.
    """

    def __init__(self, **kwargs):
        self.timeout = kwargs.pop('connection_timeout', 300)
        self.read_timeout = kwargs.pop('read_timeout', 300)
        self.verify = kwargs.pop('connection_verify', True)
        self.cert = kwargs.pop('connection_cert', None)
        self.data_block_size = kwargs.pop('connection_data_block_size', 4096)
