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
import datetime
import email.utils
from ...utils._utils import _FixedOffset, case_insensitive_dict


def _parse_http_date(text):
    """Parse a HTTP date format into datetime."""
    parsed_date = email.utils.parsedate_tz(text)
    return datetime.datetime(*parsed_date[:6], tzinfo=_FixedOffset(parsed_date[9] / 60))


def parse_retry_after(retry_after):
    """Helper to parse Retry-After and get value in seconds.

    :param str retry_after: Retry-After header
    :rtype: int
    """
    try:
        delay = int(retry_after)
    except ValueError:
        # Not an integer? Try HTTP date
        retry_date = _parse_http_date(retry_after)
        delay = (retry_date - datetime.datetime.now(retry_date.tzinfo)).total_seconds()
    return max(0, delay)


def get_retry_after(response):
    """Get the value of Retry-After in seconds.

    :param response: The PipelineResponse object
    :type response: ~azure.core.pipeline.PipelineResponse
    :return: Value of Retry-After in seconds.
    :rtype: float or None
    """
    headers = case_insensitive_dict(response.http_response.headers)
    retry_after = headers.get("retry-after")
    if retry_after:
        return parse_retry_after(retry_after)
    for ms_header in ["retry-after-ms", "x-ms-retry-after-ms"]:
        retry_after = headers.get(ms_header)
        if retry_after:
            parsed_retry_after = parse_retry_after(retry_after)
            return parsed_retry_after / 1000.0
    return None
