import azure.functions as func
from shared_code import configurations, utils
from shared_code.customized_logger.customized_json_logger import (
    get_customized_json_logger,
)
from shared_code.models.oat import OATFileMessage
from shared_code.services.oat_service import download_oat_file, oat_file_handler
from shared_code.trace_utils.trace import trace_manager

API_TOKENS = configurations.get_api_tokens()

logger = get_customized_json_logger()


def main(oatFileMsg: func.QueueMessage) -> None:
    try:
        message = OATFileMessage.parse_obj(oatFileMsg.get_json())
        if message.task_id:
            trace_manager.task_id = message.task_id
        else:
            logger.info(f'No task id from msg, create new: {trace_manager.task_id}.')

        logger.info(
            f'Start to process oat_file_msg, clp id: {message.clp_id}, package id: {message.package_id}, pipeline id: {message.pipeline_id}.'
        )

        account_token = utils.find_token_by_clp(message.clp_id, API_TOKENS)
        if not account_token:
            logger.warning(
                f'Account token not found, clp: {message.clp_id}, stop current job.'
            )
            return
        
        if utils.check_token_is_expired(account_token):
            logger.error(f"token is expired, clp: {message.clp_id}")
            return

        oat_file = download_oat_file(
            account_token, message.package_id, message.pipeline_id
        )
        if oat_file is None:
            logger.warning(f'Got no oat file, stop processing, queue msg: {message}')
            return

        oat_file_handler(message.clp_id, message.package_id, oat_file)
        logger.info(
            f'Successfully processed oat_file_msg:, clp id: {message.clp_id}, package id: {message.package_id}, pipeline id: {message.pipeline_id}.'
        )
    except Exception as e:
        logger.exception(f'Internal error. Exception: {e}.')
        raise
