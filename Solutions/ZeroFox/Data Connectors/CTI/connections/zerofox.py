from typing import Dict
import requests
import json


class ZeroFoxClient:
    def __init__(self, user, token) -> None:
        self.credentials = {"username": user, "password": token}
        self._base_url = "https://api.zerofox.com"

    def cti_request(
        self,
        method: str,
        url_suffix: str,
        params=None,
        data=None,
        error_handler=None,
    ):
        """
        :param method: HTTP request type
        :param url_suffix: The suffix of the URL
        :param params: The request's query parameters
        :param data: The request's body parameters
        :param version: api prefix to consider, default is to use version '1.0'
        :param res_type: Selects the decoder of the response. It can be
        `json` (default), `xml`, `text`, `content`, `response`
        :param empty_response: Indicates if the response data is empty or not
        :param error_handler: Function that receives the response and manage
        the error
        :return: Returns the content of the response received from the API.
        """
        headers = self._get_cti_request_header()

        response = self._http_request(
            method=method,
            url_suffix=f"/cti/{url_suffix}",
            headers=headers,
            params=params,
            data=data,
            empty_valid_codes=(200, 201),
            error_handler=error_handler,
        )

        for result in response["results"]:
            yield result
        while response["next"]:
            response = self._http_request(
                method="GET",
                headers=headers,
                full_address=response["next"],
            )
            for result in response["results"]:
                yield result

    def _client_error_handler(self, res: requests.Response):
        err_msg = f"Error in API call [{res.status_code}] - {res.reason}"
        try:
            # Try to parse json error response
            error_entry = res.json()
            err_msg += f"\n{json.dumps(error_entry)}"
            raise Exception(err_msg)
        except ValueError:
            err_msg += f"\n{res.text}"
            raise Exception(err_msg)

    def _http_request(
        self,
        method,
        url_suffix="",
        full_address=None,
        headers=None,
        auth=None,
        json_data=None,
        params=None,
        data=None,
        files=None,
        timeout=None,
        ok_codes=None,
        return_empty_response=False,
        retries=0,
        error_handler=None,
        empty_valid_codes=None,
        **kwargs,
    ):
        try:
            # Replace params if supplied
            address = full_address if full_address else f"{self._base_url}{url_suffix}"
            if not timeout:
                timeout = 10

            # Execute
            res = requests.request(
                method,
                address,
                params=params,
                data=data,
                json=json_data,
                files=files,
                headers=headers,
                auth=auth,
                timeout=timeout,
                **kwargs,
            )
            # Handle error responses gracefully
            if not self._is_status_code_valid(res, ok_codes):
                if error_handler:
                    error_handler(res)
                else:
                    self._client_error_handler(res)

            if not empty_valid_codes:
                empty_valid_codes = [204]
            is_response_empty_and_successful = res.status_code in empty_valid_codes
            if is_response_empty_and_successful and return_empty_response:
                return res

            try:
                return res.json()
            except ValueError as exception:
                raise Exception(
                    f"Failed to parse object from response: {res.content}",
                    exception,
                    res,
                )
        except requests.exceptions.ConnectTimeout as exception:
            err_msg = (
                "Connection Timeout Error - potential reasons might be that the Server URL parameter"
                " is incorrect or that the Server is not accessible from your host."
            )
            raise Exception(err_msg, exception)
        except requests.exceptions.SSLError as exception:
            # in case the "Trust any certificate" is already checked
            err_msg = (
                "SSL Certificate Verification Failed - try selecting 'Trust any certificate' checkbox in"
                " the integration configuration."
            )
            raise Exception(err_msg, exception)
        except requests.exceptions.ProxyError as exception:
            err_msg = (
                "Proxy Error - if the 'Use system proxy' checkbox in the integration configuration is"
                " selected, try clearing the checkbox."
            )
            raise Exception(err_msg, exception)
        except requests.exceptions.ConnectionError as exception:
            # Get originating Exception in Exception chain
            error_class = str(exception.__class__)
            err_type = f"""<{error_class[error_class.find("'") + 1 : error_class.rfind("'")]}>"""
            err_msg = (
                "Verify that the server URL parameter"
                " is correct and that you have access to the server from your host."
                f"\nError Type: {err_type}\n"
                "Error Number: [{exception.errno}]\n"
                "Message: {exception.strerror}\n"
            )
            raise Exception(err_msg, exception)
        except requests.exceptions.RetryError as exception:
            try:
                reason = f"Reason: {exception.args[0].reason.args[0]}"
            except Exception:  # noqa: disable=broad-except
                reason = ""
            err_msg = f"Max Retries Error- Request attempts with {retries} retries failed. \n{reason}"
            raise Exception(err_msg, exception)

    def _is_status_code_valid(self, response: requests.Response, codes):
        return codes is None or response.status_code in codes

    def _get_new_access_token(self):
        url_suffix: str = "/auth/token/"
        try:
            response_content: Dict = self._http_request(
                method="POST",
                url_suffix=url_suffix,
                data=self.credentials,
            )
            return response_content.get("access", "")
        except Exception as e:
            raise e

    def get_cti_authorization_token(self) -> str:
        """
        :return: returns the authorization token for the CTI feed
        """
        token = self._get_new_access_token()
        if not token:
            raise Exception("Unable to retrieve token.")
        return token

    def _get_cti_request_header(self):
        token: str = self.get_cti_authorization_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
