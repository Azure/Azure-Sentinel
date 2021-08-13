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

def await_result(func, *args, **kwargs):
    """If func returns an awaitable, raise that this runner can't handle it."""
    result = func(*args, **kwargs)
    if hasattr(result, "__await__"):
        raise TypeError(
            "Policy {} returned awaitable object in non-async pipeline.".format(func)
        )
    return result

def to_rest_request(pipeline_transport_request):
    from ..rest import HttpRequest as RestHttpRequest
    return RestHttpRequest(
        method=pipeline_transport_request.method,
        url=pipeline_transport_request.url,
        headers=pipeline_transport_request.headers,
        files=pipeline_transport_request.files,
        data=pipeline_transport_request.data
    )

def to_rest_response(pipeline_transport_response):
    from .transport._requests_basic import RequestsTransportResponse
    from ..rest._requests_basic import RestRequestsTransportResponse
    from ..rest import HttpResponse
    if isinstance(pipeline_transport_response, RequestsTransportResponse):
        response_type = RestRequestsTransportResponse
    else:
        response_type = HttpResponse
    response = response_type(
        request=to_rest_request(pipeline_transport_response.request),
        internal_response=pipeline_transport_response.internal_response,
    )
    response._connection_data_block_size = pipeline_transport_response.block_size  # pylint: disable=protected-access
    return response

def get_block_size(response):
    try:
        return response._connection_data_block_size  # pylint: disable=protected-access
    except AttributeError:
        return response.block_size

def get_internal_response(response):
    try:
        return response._internal_response  # pylint: disable=protected-access
    except AttributeError:
        return response.internal_response
