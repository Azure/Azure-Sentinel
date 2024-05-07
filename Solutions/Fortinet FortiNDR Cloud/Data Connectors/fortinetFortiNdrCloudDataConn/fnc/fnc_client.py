from .api import FncApiClient, FncRestClient
from .global_variables import *
from .logger import FncClientLogger
from .metastream import FncMetastreamClient


class FncClient:
    @classmethod
    def get_api_client(
        cls,
        name: str,
        api_token: str = None,
        domain: str = CLIENT_DEFAULT_DOMAIN,
        rest_client: FncRestClient = None,
        logger: FncClientLogger = None
    ) -> FncApiClient:
        return FncApiClient(name=name, api_token=api_token, domain=domain, rest_client=rest_client, logger=logger)

    @classmethod
    def get_metastream_client(
        cls,
        name: str,
        account_code: str = None,
        access_key: str = None,
        secret_key: str = None,
        bucket: str = None,
        logger: FncClientLogger = None
    ) -> FncMetastreamClient:
        return FncMetastreamClient(name=name, account_code=account_code, access_key=access_key, secret_key=secret_key, bucket=bucket, logger=logger)
