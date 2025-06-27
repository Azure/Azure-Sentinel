import logging
from typing import Dict
import requests

from connections.exceptions import ApiResponseException

TIMEOUT = 30


class ZeroFoxClient:
    def __init__(self, user, token) -> None:
        self.credentials = {"username": user, "password": token}
        self._base_url = "https://api.zerofox.com"

    def cti_request(
        self,
        method: str,
        url_suffix: str,
        params=None,
        timeout=TIMEOUT,
    ):

        headers = self._get_cti_request_header()
        url = f"{self._base_url}/cti/{url_suffix}"

        response = self._http_request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=None,
            timeout=timeout,
            ok_code=200,
        )
        yield response["results"]

        while response["next"]:
            response = self._http_request(
                method="GET",
                headers=headers,
                timeout=timeout,
                ok_code=200,
                url=response["next"],
            )
            yield response["results"]

    def _http_request(
        self,
        method,
        url: str,
        ok_code: int = 200,
        timeout: float = TIMEOUT,
        **kwargs,
    ):
        """Wrap request method for handling status codes."""
        response = requests.request(
            method=method,
            url=url,
            timeout=timeout,
            **kwargs,
        )
        if response.status_code != ok_code:
            logging.error(f"Failed to {method} {url}. Response: {response.text}")
            raise ApiResponseException(method, url=url, res=response)
        if response.status_code == requests.codes["no_content"]:
            return None
        return response.json()

    def _get_new_access_token(self):
        url_suffix: str = "auth/token/"
        response_content: Dict = self._http_request(
            method="POST",
            ok_code=200,
            url=f"{self._base_url}/{url_suffix}",
            data=self.credentials,
        )
        return response_content.get("access", "")

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
        logging.debug("Access token retrieved")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
