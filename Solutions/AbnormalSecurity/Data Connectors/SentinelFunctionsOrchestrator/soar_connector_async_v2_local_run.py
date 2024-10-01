import logging
import os
import asyncio
import time
from datetime import datetime, timedelta
from .soar_connector_async_v2 import get_cases, get_threats
from .utils import get_context, TIME_FORMAT

def find_duplicates(arr):
    from collections import Counter

    counts = Counter(arr)
    return [item for item, count in counts.items() if count > 1]


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    os.environ["ABNORMAL_SECURITY_REST_API_TOKEN"] = "121"
    os.environ["API_HOST"] = "http://localhost:3000"
    os.environ["ABNORMAL_LAG_ON_BACKEND_SEC"] = "10"
    os.environ["ABNORMAL_FREQUENCY_MIN"] = "1"
    os.environ["ABNORMAL_LIMIT_MIN"] = "2"

    stored_threat_time = datetime.now() - timedelta(minutes=3)
    stored_cases_time = datetime.now() - timedelta(minutes=3)
    output_threats_queue = asyncio.Queue()
    output_cases_queue = asyncio.Queue()
    try:
        while True:
            threats_ctx = get_context(stored_date_time=stored_threat_time.strftime(TIME_FORMAT))
            logging.info(
                f"Filtering messages in range {threats_ctx.CLIENT_FILTER_TIME_RANGE.start} : {threats_ctx.CLIENT_FILTER_TIME_RANGE.end}"
            )
            asyncio.run(get_threats(ctx=threats_ctx, output_queue=output_threats_queue))

            stored_threat_time = threats_ctx.CURRENT_TIME
            logging.info(f"Sleeping for {threats_ctx.FREQUENCY.total_seconds()} seconds\n\n")


            cases_ctx = get_context(stored_date_time=stored_cases_time.strftime(TIME_FORMAT))
            logging.info(
                f"Filtering messages in range {cases_ctx.CLIENT_FILTER_TIME_RANGE.start} : {cases_ctx.CLIENT_FILTER_TIME_RANGE.end}"
            )
            asyncio.run(get_cases(ctx=cases_ctx, output_queue=output_cases_queue))

            stored_cases_time = cases_ctx.CURRENT_TIME
            logging.info(f"Sleeping for {cases_ctx.FREQUENCY.total_seconds()} seconds\n\n")
            time.sleep(cases_ctx.FREQUENCY.total_seconds())




    except KeyboardInterrupt:
        pass

    idlist = []
    while not output_threats_queue.empty():
        current = output_threats_queue.get_nowait()
        logging.info(current)
        idlist.append(current[1]["abxMessageId"])

    idset = set(idlist)
    maxid = max(idlist)
    duplicates = find_duplicates(idlist)
    missedids = list(filter(lambda x: x not in idset, list(range(1, maxid + 1))))

    logging.info("\n\n\nSummary of the operation")

    logging.info("Ingested values", idlist)
    logging.info(f"Max ID: {maxid}")
    logging.info(f"Duplicates: {duplicates}")
    logging.info(f"Missed IDs: {missedids}")

    assert len(idset) == len(idlist), "Duplicates threats exist"
    assert len(duplicates) == 0, "There are duplicates threats"
    assert len(missedids) == 0, "There are missed threats IDs"



    idlist = []
    while not output_cases_queue.empty():
        current = output_cases_queue.get_nowait()
        logging.info(current)
        idlist.append(current[1]["caseId"])

    idset = set(idlist)
    maxid = max(idlist)
    duplicates = find_duplicates(idlist)
    missedids = list(filter(lambda x: x not in idset, list(range(1, maxid + 1))))

    logging.info("\n\n\nSummary of the operation")

    logging.info("Ingested values", idlist)
    logging.info(f"Max ID: {maxid}")
    logging.info(f"Duplicates: {duplicates}")
    logging.info(f"Missed IDs: {missedids}")

    assert len(idset) == len(idlist), "Duplicate cases exist"
    assert len(duplicates) == 0, "There are duplicates cases"
    assert len(missedids) == 0, "There are missed cases IDs"
