import azure.functions as func
import os

from azure.storage.queue import QueueClient, TextBase64EncodePolicy


def main(msg: func.QueueMessage) -> None:
    queue_client = QueueClient.from_connection_string(
        os.environ['AzureWebJobsStorage'],
        'oat-queue',
        message_encode_policy=TextBase64EncodePolicy(),
    )
    queue_client.send_message(msg.get_body().decode(), visibility_timeout=3600)
