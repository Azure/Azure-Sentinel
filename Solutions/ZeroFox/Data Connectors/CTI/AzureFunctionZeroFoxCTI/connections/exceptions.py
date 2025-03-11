import json

import requests


class ApiResponseException(Exception):
    """Represents event where response status code was not as expected."""

    def __init__(self, method, url, res: requests.Response):
        """Construct exception based on endpoint address and response."""
        err_msg = f"Error in {method} API call to endpoint {url}\n\
              [{res.status_code}] - {res.reason}"
        try:
            # Try to parse json error response
            error_entry = res.json()
            err_msg += f"\n{json.dumps(error_entry)}"
        except ValueError:
            err_msg += f"\n{res.text}"
        super().__init__(err_msg)
