from azure.identity import ClientSecretCredential
from azure.monitor.ingestion import LogsIngestionClient


class SentinelApiConnector:
    def __init__(
        self,
        *,
        data_collection_endpoint: str,
        dcr_immutable_id: str,
        dcr_stream_name: str,
        tenant_id: str,
        client_id: str,
        client_secret: str,
    ):
        self.dcr_immutable_id = dcr_immutable_id
        self.dcr_stream_name = dcr_stream_name
        
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )
        
        self.client = LogsIngestionClient(
            endpoint=data_collection_endpoint,
            credential=credential,
            logging_enable=True,
        )

    def post(self, json_body: list) -> None:
        if not isinstance(json_body, list):
            json_body = [json_body] if isinstance(json_body, dict) else list(json_body)
        
        if not json_body:
            return
        
        self.client.upload(
            rule_id=self.dcr_immutable_id,
            stream_name=self.dcr_stream_name,
            logs=json_body,
        )
