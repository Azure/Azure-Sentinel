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


try:
    import configparser
    from configparser import NoOptionError
except ImportError:
    import ConfigParser as configparser  # type: ignore
    from ConfigParser import NoOptionError  # type: ignore

from typing import TYPE_CHECKING, Optional, Dict, List, Any, Callable, Union  # pylint: disable=unused-import

from .pipeline import Pipeline
from .universal_http.requests import (
    RequestHTTPSenderConfiguration
)
from .pipeline.universal import (
    UserAgentPolicy,
    HTTPLogger,
)

if TYPE_CHECKING:
    from .pipeline import AsyncPipeline

class Configuration(RequestHTTPSenderConfiguration):
    """Client configuration.

    :param str baseurl: REST API base URL.
    :param str filepath: Path to existing config file (optional).
    """

    def __init__(self, base_url, filepath=None):
        # type: (str, Optional[str]) -> None

        super(Configuration, self).__init__(filepath)
        # Service
        self.base_url = base_url

        # User-Agent as a policy
        self.user_agent_policy = UserAgentPolicy()

        # HTTP logger policy
        self.http_logger_policy = HTTPLogger()

        # The pipeline. We don't know until a ServiceClient use this configuration if it will be sync or async
        # We instantiate with a default empty Pipeline for mypy mostly, trying to use a pipeline from a pure
        # configuration object doesn't make sense.
        self.pipeline = Pipeline()  # type: Union[Pipeline, AsyncPipeline]

        # If set to True, ServiceClient will own the sessionn
        self.keep_alive = False

        # Potential credentials pre-declared
        self.credentials = None

        if filepath:
            self.load(filepath)

    @property
    def user_agent(self):
        # type: () -> str
        """The current user agent value."""
        return self.user_agent_policy.user_agent

    def add_user_agent(self, value):
        # type: (str) -> None
        """Add value to current user agent with a space.

        :param str value: value to add to user agent.
        """
        self.user_agent_policy.add_user_agent(value)

    @property
    def enable_http_logger(self):
        return self.http_logger_policy.enable_http_logger

    @enable_http_logger.setter
    def enable_http_logger(self, value):
        self.http_logger_policy.enable_http_logger = value
