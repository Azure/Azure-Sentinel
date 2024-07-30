"""Init for Dossier Job Result function."""

import inspect
from .get_dossier_result import DossierGetResult
from ..SharedCode.logger import applogger
from ..SharedCode import consts


def main(name: str) -> str:
    """Dossier job result main function.

    Args:
        name (str): The name used to retrieve dossier data.

    Returns:
        str: The result of the dossier data retrieval.
    """
    __method_name = inspect.currentframe().f_code.co_name
    applogger.info(
        consts.LOG_FORMAT.format(
            consts.LOGS_STARTS_WITH,
            __method_name,
            consts.DOSSIER_GET_RESULT_FUNCTION_NAME,
            "Dossier Job Result function started with job_id = {}".format(name),
        )
    )
    job_id = name
    result = ""
    dossier_get_result = DossierGetResult()
    result = dossier_get_result.get_job_result_and_ingest_in_sentinel(job_id)
    return result
