from fnc.global_variables import CLIENT_DEFAULT_DOMAIN

from .api import FncApiClient, FncRestClient
from .logger import FncClientLogger
from .metastream import FncMetastreamClient


class FncClient:
    api_client_mask = None
    api_client: FncApiClient = None
    metastream_client_mask = None
    metastream_client: FncMetastreamClient = None

    @staticmethod
    def get_api_client(
        name: str,
        api_token: str = None,
        domain: str = CLIENT_DEFAULT_DOMAIN,
        rest_client: FncRestClient = None,
        logger: FncClientLogger = None
    ) -> FncApiClient:
        mask = hash(f"{api_token}-{domain}")

        if FncClient.api_client_mask and FncClient.api_client_mask == mask:
            # If there is an API client for the same api_token and domain we return it
            return FncClient.api_client

        if FncClient.api_client_mask:
            # If there is already a client for a different api_token and/or domain we recreate the client
            FncClient.api_client.get_logger().info(
                "The used api_token and/or domain are being updated. The FncApiClient will be recreated."
            )

        FncClient.api_client_mask = mask
        FncClient.api_client = FncApiClient(name=name, api_token=api_token, domain=domain, rest_client=rest_client, logger=logger)

        return FncClient.api_client

    @staticmethod
    def get_metastream_client(
        name: str,
        account_code: str = None,
        access_key: str = None,
        secret_key: str = None,
        bucket: str = None,
        logger: FncClientLogger = None
    ) -> FncMetastreamClient:
        mask = hash(f"{account_code}-{access_key}-{secret_key}-{bucket}")

        if FncClient.metastream_client_mask and FncClient.metastream_client_mask == mask:
            # If there is a Metastream client for the credentials and bucket we return it
            return FncClient.metastream_client

        if FncClient.metastream_client_mask:
            # If there is already a metastream client for a different credentials and/or bucket we recreate the client
            FncClient.metastream_client.get_logger().info(
                "The client's credentials and/or bucket are being updated. The FncMetastreamClient will be recreated."
            )

        FncClient.metastream_client_mask = mask
        FncClient.metastream_client = FncMetastreamClient(name=name, account_code=account_code,
                                                          access_key=access_key, secret_key=secret_key, bucket=bucket, logger=logger)
        return FncClient.metastream_client
