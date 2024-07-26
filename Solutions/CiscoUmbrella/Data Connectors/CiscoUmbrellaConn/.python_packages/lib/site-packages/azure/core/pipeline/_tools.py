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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any
    from azure.core.rest import HttpResponse as RestHttpResponse

def await_result(func, *args, **kwargs):
    """If func returns an awaitable, raise that this runner can't handle it."""
    result = func(*args, **kwargs)
    if hasattr(result, "__await__"):
        raise TypeError(
            "Policy {} returned awaitable object in non-async pipeline.".format(func)
        )
    return result

def is_rest(obj):
    # type: (Any) -> bool
    """Return whether a request or a response is a rest request / response.

    Checking whether the response has the object content can sometimes result
    in a ResponseNotRead error if you're checking the value on a response
    that has not been read in yet. To get around this, we also have added
    a check for is_stream_consumed, which is an exclusive property on our new responses.
    """
    return hasattr(obj, "is_stream_consumed") or hasattr(obj, "content")

def handle_non_stream_rest_response(response):
    # type: (RestHttpResponse) -> None
    """Handle reading and closing of non stream rest responses.
    For our new rest responses, we have to call .read() and .close() for our non-stream
    responses. This way, we load in the body for users to access.
    """
    try:
        response.read()
        response.close()
    except Exception as exc:
        response.close()
        raise exc
