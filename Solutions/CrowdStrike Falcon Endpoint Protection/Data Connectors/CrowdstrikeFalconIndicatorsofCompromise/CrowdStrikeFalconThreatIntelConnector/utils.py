import requests
import json
from datetime import datetime, timedelta
import logging
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.fileshare import ShareClient
from azure.storage.fileshare import ShareFileClient

CONFIDENCE_MAPPING = {"high": 85, "medium": 60, "low": 30}

STIX_PATTERN_MAPPING = {
    "hash_md5": "file:hashes.MD5",
    "hash_sha256": "file:hashes.'SHA-256'",
    "hash_sha1": "file:hashes.'SHA-1'",
    "url": "url:value",
    "domain": "domain-name:value",
    "ip_address": "ipv4-addr:value",
    "mutex_name": "mutex:name",
    "password": "user-account:credential",
    "file_name": "file:name",
    "email_address": "email-addr:value",
    "username": "user-account:account_login",
    "persona_name": "user-account:display_name",
    "ip_address_block": "ipv4-addr:value",
    "coin_address": "x-wallet-addr:value",
    "bitcoin_address": "x-wallet-addr:value",
}


class UnauthorizedTokenException(Exception):
    pass


class InvalidCredentialsException(Exception):
    pass


class APIError(Exception):
    pass


class StateManager:
    def __init__(self, connection_string, share_name, file_path):
        self.share_cli = ShareClient.from_connection_string(
            conn_str=connection_string, share_name=share_name
        )
        self.file_cli = ShareFileClient.from_connection_string(
            conn_str=connection_string, share_name=share_name, file_path=file_path
        )

    def post(self, marker_text: str):
        try:

            self.file_cli.upload_file(marker_text)

        except ResourceNotFoundError:
            self.share_cli.create_share()
            self.file_cli.upload_file(marker_text)

    def get(self):
        try:
            logging.info("Looking for marker.")
            marker = self.file_cli.download_file().readall().decode()
            logging.info(f"Marker found '{marker}'.")
            return marker
        except ResourceNotFoundError:
            logging.info("No marker found.")
            return None


class CrowdStrikeTokenRetriever:
    def __init__(
        self, crowdstrike_base_url, crowdstrike_client_id, crowdstrike_client_secret
    ):
        self.crowdstrike_base_url = crowdstrike_base_url
        self.crowdstrike_client_id = crowdstrike_client_id
        self.crowdstrike_client_secret = crowdstrike_client_secret
        self.token_exp = datetime.now()
        self.token = self.get_token()

    def get_token(self):

        # if token is within 60 seconds of expiring, generate a new token.
        if (self.token_exp - datetime.now()).total_seconds() < 60:
            logging.info("generating new crowdstrike token")
            response = requests.post(
                f"{self.crowdstrike_base_url}/oauth2/token",
                data={"grant_type": "client_credentials"},
                auth=(self.crowdstrike_client_id, self.crowdstrike_client_secret),
            )

            if response.status_code != 201:
                raise InvalidCredentialsException(response.text)

            # calculate expiration date
            self.token_exp = datetime.now() + timedelta(
                seconds=json.loads(response.content)["expires_in"]
            )
            logging.info(f"expiration time: {self.token_exp}")
            self.token = json.loads(response.content)["access_token"]

        return self.token


class AADTokenRetriever:
    def __init__(self, aad_client_id, aad_client_secret, tenant_id):
        self.aad_client_id = aad_client_id
        self.aad_client_secret = aad_client_secret
        self.tenant_id = tenant_id
        self.token_exp = datetime.now()
        self.token = self.get_token()

    def get_token(self):

        # if token is within 60 seconds of expiring, generate a new token.
        if (self.token_exp - datetime.now()).total_seconds() < 60:
            logging.info("generating new aad token")
            url = (
                f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            )
            payload = {
                "grant_type": "client_credentials",
                "client_id": self.aad_client_id,
                "client_secret": self.aad_client_secret,
                "scope": "https://management.azure.com/.default",
            }
            response = requests.post(url=url, data=payload)

            if response.status_code != 200:
                raise InvalidCredentialsException(response.text)

            # calculate expiration date
            self.token_exp = datetime.now() + timedelta(
                seconds=json.loads(response.content)["expires_in"]
            )
            logging.info(f"expiration time: {self.token_exp}")
            self.token = json.loads(response.content)["access_token"]

        return self.token
