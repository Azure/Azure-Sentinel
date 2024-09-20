import azure.functions as func
import json
import os
import logging

from azure.storage.queue import QueueClient, TextBase64EncodePolicy


def main(wbPoisonMsg: func.QueueMessage) -> None:
    queue_client = QueueClient.from_connection_string(
        os.environ['AzureWebJobsStorage'],
        'workbench-queue',
        message_encode_policy=TextBase64EncodePolicy(),
    )
    queue_client.send_message(wbPoisonMsg.get_body().decode(), visibility_timeout=3600)
