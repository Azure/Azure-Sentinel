"""Utility methods."""
import inspect
from . import consts
from .logger import applogger
from .netskope_exception import NetskopeException


def get_event_alert_type_subtype():
    """To get event alert type subtype."""
    __method_name = inspect.currentframe().f_code.co_name
    try:
        events_alerts_subtype = consts.SHARE_NAME
        if events_alerts_subtype in consts.EVENTS_LIST:
            return {"type_of_data": "events", "sub_type": events_alerts_subtype}
        return {"type_of_data": "alerts", "sub_type": events_alerts_subtype}
    except Exception as error:
        applogger.error(
            "{}(method={}) : Error while getting alerts, events type or subtype. Error-{}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                error,
            )
        )
        raise NetskopeException()
