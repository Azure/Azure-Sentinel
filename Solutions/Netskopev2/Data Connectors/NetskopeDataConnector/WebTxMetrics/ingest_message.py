"""Module to Ingest metrics in sentinel."""
import json
import requests
from requests.exceptions import InvalidURL, ConnectionError
import inspect
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.netskope_exception import NetskopeException
from .sentinel import post_data


def ingest_backlog_unacked_message():
    """Fetch and Ingest WebTx Metrics to Sentinel."""
    __method_name = inspect.currentframe().f_code.co_name
    try:
        headers = {"Netskope-Api-Token": consts.NETSKOPE_TOKEN}
        parameters = {"hours": consts.HOURS}
        res = requests.get(
            consts.WEBTX_METRICS_URL.format(hostname=consts.NETSKOPE_HOSTNAME), headers=headers, params=parameters
        )
        if res.status_code == 200:
            json_data = res.json()
            if len(json_data['result']) == 0:
                applogger.info(
                    "{}(method={}) : {} : Empty data was returned by the api.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.NETSKOPE_WEBTX,
                    )
                )
                return
            subscription = list(json_data["result"]["subscription/backlog_message_count"].keys())[0]
            partition_key = list(json_data["result"]["subscription/backlog_message_count"][subscription].keys())[0]
            backlog_message = json_data["result"]["subscription/backlog_message_count"][subscription][partition_key]
            oldest_unacked_message = json_data["result"]["subscription/oldest_unacked_message_age"][subscription][
                partition_key
            ]
            data_to_post = []
            for key in backlog_message:
                data_to_post.append(
                    {
                        "timestamp": key,
                        "backlog_message_count": backlog_message[key],
                        "oldest_unacked_message_age": oldest_unacked_message[key],
                    }
                )
            post_data(json.dumps(data_to_post), consts.LOG_TYPE)
            applogger.info(
                "{}(method={}) : {} : WebTx metrics posted.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_WEBTX,
                )
            )
        elif res.status_code == 401:
            applogger.error(
                "{}(method={}) : {} : Not authorized to use this feature.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_WEBTX,
                )
            )
            raise NetskopeException()
        elif res.status_code == 403:
            applogger.error(
                "{}(method={}) : {} : Netskope token is not valid. Token is either expired or invalid.Please "
                "provide a V2 token with the api/v2/events/metrics/transactionevents endpoint's permission.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_WEBTX,
                )
            )
            raise NetskopeException()
        else:
            applogger.error(
                "{}(method={}) : {} : Error while fetching metrics status code {}.".format(
                    consts.LOGS_STARTS_WITH, __method_name, consts.NETSKOPE_WEBTX, res.status_code
                )
            )
            raise NetskopeException()
    except InvalidURL as error:
        applogger.error(
            "{}(method={}) : {} : InvalidURL: {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.NETSKOPE_WEBTX,
                error,
            )
        )
        raise NetskopeException()
    except ConnectionError as error:
        applogger.error(
            "{}(method={}) : {} : ConnectionError: {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.NETSKOPE_WEBTX,
                error,
            )
        )
        raise NetskopeException()
    except KeyError as error:
        applogger.error(
            "{}(method={}) : {} : KeyError: {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.NETSKOPE_WEBTX,
                error,
            )
        )
        raise NetskopeException()
    except NetskopeException:
        applogger.error(
            "{}(method={}) : {} : Error occured while fetching and ingesting Netskope WebTxMetrics.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.NETSKOPE_WEBTX,
            )
        )
        raise NetskopeException()
    except Exception as error:
        applogger.error(
            "{}(method={}) : {} : Error: {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.NETSKOPE_WEBTX,
                error,
            )
        )
        raise NetskopeException()
