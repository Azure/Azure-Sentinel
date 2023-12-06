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
from .poller import NoPolling as _NoPolling

from ..serialization import Model
from ..async_client import ServiceClientAsync
from ..pipeline import ClientRawResponse

class AsyncPollingMethod(object):
    """ABC class for polling method.
    """
    def initialize(self, client, initial_response, deserialization_callback):
        raise NotImplementedError("This method needs to be implemented")

    async def run(self):
        raise NotImplementedError("This method needs to be implemented")

    def status(self):
        raise NotImplementedError("This method needs to be implemented")

    def finished(self):
        raise NotImplementedError("This method needs to be implemented")

    def resource(self):
        raise NotImplementedError("This method needs to be implemented")


class AsyncNoPolling(_NoPolling):
    """An empty async poller that returns the deserialized initial response.
    """
    async def run(self):
        """Empty run, no polling.

        Just override initial run to add "async"
        """
        pass


async def async_poller(client, initial_response, deserialization_callback, polling_method):
    """Async Poller for long running operations.

    :param client: A msrest service client. Can be a SDK client and it will be casted to a ServiceClient.
    :type client: msrest.service_client.ServiceClient
    :param initial_response: The initial call response
    :type initial_response: msrest.universal_http.ClientResponse or msrest.pipeline.ClientRawResponse
    :param deserialization_callback: A callback that takes a Response and return a deserialized object. If a subclass of Model is given, this passes "deserialize" as callback.
    :type deserialization_callback: callable or msrest.serialization.Model
    :param polling_method: The polling strategy to adopt
    :type polling_method: msrest.polling.PollingMethod
    """

    try:
        client = client if isinstance(client, ServiceClientAsync) else client._client
    except AttributeError:
        raise ValueError("Poller client parameter must be a low-level msrest Service Client or a SDK client.")
    response = initial_response.response if isinstance(initial_response, ClientRawResponse) else initial_response

    if isinstance(deserialization_callback, type) and issubclass(deserialization_callback, Model):
        deserialization_callback = deserialization_callback.deserialize

    # Might raise a CloudError
    polling_method.initialize(client, response, deserialization_callback)

    await polling_method.run()
    return polling_method.resource()
