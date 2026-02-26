"""Init file for Dossier Required Source Function."""

import inspect
import json
from .list_of_sources import DossierListSources
from ..SharedCode.infoblox_exception import InfobloxException
from ..SharedCode.logger import applogger
from ..SharedCode import consts


def main(name: str) -> str:
    """Dossier fetch required source main function.

    Args:
        name (str): The input name to be processed.

    Returns:
        str: A JSON string representing the lookup source list.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        json_data = json.loads(name)
        target_type = json_data.get("type")
        target = json_data.get("target")
        dossier_job_obj = DossierListSources(target_type, target)
        lookup_source_list = dossier_job_obj.required_lookup_sources()
        lookup_source_str = json.dumps(lookup_source_list)
        return lookup_source_str
    except KeyError as key_error:
        applogger.error(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DOSSIER_REQUIRED_SOURCE_FUNCTION_NAME,
                "Key error : Error-{}".format(key_error),
            )
        )
        raise InfobloxException()
    except InfobloxException:
        raise InfobloxException()
    except Exception as error:
        applogger.error(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DOSSIER_REQUIRED_SOURCE_FUNCTION_NAME,
                "Unexpected error : Error-{}".format(error),
            )
        )
        raise InfobloxException()
