import json
from botocore.config import Config as BotoCoreConfig
from aiobotocore.session import get_session
from gzip_stream import AsyncGZIPDecompressedStream
import re
import aiohttp
import logging
import azure.functions as func
import urllib.parse
from ..CommonCode.sentinel_connector import AzureSentinelConnectorAsync
from ..CommonCode.constants import (
    AZURE_TENANT_ID,
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET,
    DCE_ENDPOINT,
    DCR_ID,
    FLOW_LOGS_CUSTOM_TABLE,
    AUDIT_LOGS_CUSTOM_TABLE,
    LOGS_TO_CONSUME,
    AWS_KEY,
    AWS_SECRET,
    AWS_REGION_NAME,
    LINE_SEPARATOR,
    ALL_TRAFFIC,
    FLOW_EVENTS,
    AUDIT_EVENTS,
)


# Defining the S3 Client object based on AWS Credentials
def _create_s3_client():
    s3_session = get_session()
    boto_config = BotoCoreConfig(
        region_name=AWS_REGION_NAME,
        retries={"max_attempts": 10, "mode": "standard"},
        read_timeout=0,
        tcp_keepalive=True,
    )
    return s3_session.create_client(
        "s3",
        region_name=AWS_REGION_NAME,
        aws_access_key_id=AWS_KEY,
        aws_secret_access_key=AWS_SECRET,
        config=boto_config,
    )


def fileToBeFiltered(file_path):
    if LOGS_TO_CONSUME == ALL_TRAFFIC:
        return False

    if "auditable" in file_path:
        return FLOW_EVENTS in LOGS_TO_CONSUME
    else:
        return AUDIT_EVENTS in LOGS_TO_CONSUME


async def _generate_sentinel_connectors(session):
    stream_names = []
    sentinel_connectors = {}
    if LOGS_TO_CONSUME == ALL_TRAFFIC:
        stream_names.append(FLOW_LOGS_CUSTOM_TABLE)
        stream_names.append(AUDIT_LOGS_CUSTOM_TABLE)

    elif LOGS_TO_CONSUME == AUDIT_EVENTS:
        stream_names.append(AUDIT_LOGS_CUSTOM_TABLE)
    else:
        stream_names.append(FLOW_LOGS_CUSTOM_TABLE)

    for stream in stream_names:
        sentinel_connectors[stream] = AzureSentinelConnectorAsync(
            session,
            DCE_ENDPOINT,
            DCR_ID,
            stream,
            AZURE_CLIENT_ID,
            AZURE_CLIENT_SECRET,
            AZURE_TENANT_ID,
        )

    return sentinel_connectors


async def main(msg: func.QueueMessage):
    try:
        total_events = 0
        accumulated_file_size = 0
        sqs_ids_seen_so_far = 0
        # stores the connection objects that can be reused when uploading events to specific tables
        sentinel_connectors = {}
        # initialize sentinel_connectors
        async with aiohttp.ClientSession() as session:
            sentinel_connectors = await _generate_sentinel_connectors(session)

        # msg should contain a list of links to s3
        result = {"id": msg.id, "body": msg.get_body()}
        # body should be a list of dicts, where each dict has link, bucket_name, sqs_message_id
        body = json.loads(result["body"].decode("ascii").replace("'", '"'))

    except ValueError:
        pass
    else:
        for obj in body:
            link = obj.get("link")
            bucket = obj.get("bucket_name")
            messageId = obj.get("sqs_message_id")
            file_size = obj.get("file_size", 0)
            accumulated_file_size += file_size

            if fileToBeFiltered(link):
                continue

            sqs_ids_seen_so_far += 1
            stream_name = (
                AUDIT_LOGS_CUSTOM_TABLE
                if "auditable" in link
                else FLOW_LOGS_CUSTOM_TABLE
            )

            file_stats = {
                "Trigger": "Queue",
                "stream_name": stream_name,
                "Type": "file_stats",
                "link": link,
                "bucket": bucket,
                "sqs_message_id": messageId,
                "file_size_bytes": file_size,
            }
            logging.info(json.dumps(file_stats))

            async with _create_s3_client() as client:
                async with aiohttp.ClientSession() as session:

                    if link:
                        sentinel_connector = sentinel_connectors[stream_name]
                        if (
                            sentinel_connector is not None
                        ):  # in case, user selected auditable only but flow event is being processed from sqs
                            total_events += await process_file(
                                bucket, link, client, sentinel_connector
                            )

        # ensure data is flushed at the end in case queue limit of 4000 is not reached
        for connector in sentinel_connectors.keys():
            await sentinel_connectors[connector].flush()
        event_stats = {
            "Trigger": "Queue",
            "Type": "event_stats",
            "total_events": total_events,
            "sqs_ids_seen_so_far": sqs_ids_seen_so_far,
            "aggregated_file_size": accumulated_file_size,
        }
        logging.info(json.dumps(event_stats))


async def process_file(bucket, s3_path, client, sentinel_connector):

    event_count = 0
    s3_path = urllib.parse.unquote(s3_path)

    response = await client.get_object(Bucket=bucket, Key=s3_path)
    s = ""

    async for decompressed_chunk in AsyncGZIPDecompressedStream(response["Body"]):
        s += decompressed_chunk.decode(errors="ignore")
        lines = re.split(r"{0}".format(LINE_SEPARATOR), s)
        for n, line in enumerate(lines):
            if n < len(lines) - 1:
                if line:
                    try:
                        event = json.loads(line)
                        event_count += 1
                    except ValueError as e:
                        logging.error(
                            "[QueueTrigger] Error while loading json Event at s value {}. Error: {}".format(
                                line, str(e)
                            )
                        )
                        continue
                    await sentinel_connector.send(event)
        s = line

    if s:
        try:
            event = json.loads(line)
        except ValueError as e:
            logging.error(
                "[QueueTrigger] Error while loading json Event at s value {}. Error: {}".format(
                    line, str(e)
                )
            )
        await sentinel_connector.send(event)

    return event_count
