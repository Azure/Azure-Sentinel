import logging
import azure.functions as func

from requests.exceptions import HTTPError
from shared_code.models.oat import OATQueueMessage
from shared_code.services.oat_service import get_search_data

from shared_code import utils, configurations
from shared_code.exceptions import GeneralException
from shared_code.data_collector import LogAnalytics
from shared_code.transform_utils import transform_oat_log

WORKSPACE_ID = configurations.get_workspace_id()
WORKSPACE_KEY = configurations.get_workspace_key()
API_TOKENS = configurations.get_api_tokens()
XDR_HOST_URL = configurations.get_xdr_host_url()
OAT_LOG_TYPE = configurations.get_oat_log_type()


def _transfrom_logs(clp_id, detections, raw_logs):
    maps = {detection['uuid']: detection for detection in detections}
    for log in raw_logs:
        if log['uuid'] in maps:
            maps[log['uuid']].update(log)

    return [transform_oat_log(clp_id, log) for log in maps.values()]


def main(msg: func.QueueMessage) -> None:
    try:
        message = OATQueueMessage.parse_obj(msg.get_json())
        clp_id = message.clp_id
        detections = message.detections
        post_data = message.post_data

        token = utils.find_token_by_clp(clp_id, API_TOKENS)

        if not token:
            raise GeneralException(f'Token not found for clp: {clp_id}')

        # get workbench detail
        raw_logs = get_search_data(token, post_data)

        # transform data
        transfromed_logs = _transfrom_logs(clp_id, detections, raw_logs)

        # send to log analytics
        log_analytics = LogAnalytics(WORKSPACE_ID, WORKSPACE_KEY, OAT_LOG_TYPE)
        log_analytics.post_data(transfromed_logs)
        logging.info(f'Send oat data successfully. count: {len(transfromed_logs)}.')

    except HTTPError as e:
        logging.exception(f'Fail to get search data! Exception: {e}')
        raise
    except:
        logging.exception('Internal error.')
        raise
