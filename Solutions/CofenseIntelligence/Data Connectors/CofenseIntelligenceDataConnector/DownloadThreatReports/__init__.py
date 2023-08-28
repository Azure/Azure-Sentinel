"""Download Report Module."""
import logging
import inspect
import requests
import azure.functions as func
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.utils import Utils
from ..SharedCode.cofense_intelligence_exception import CofenseIntelligenceException


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Download the file and return as http response.

    Args:
        req (func.HttpRequest): _description_

    Returns:
        func.HttpResponse: _description_
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        logging.info("Python HTTP trigger function recieved a request.")
        utils_obj = Utils(consts.DOWNLOAD_THREAT_REPORTS)
        utils_obj.validate_params()
        proxy = utils_obj.create_proxy()
        url = req.params.get("url")
        splitted_url = url.rsplit("/", 1)
        file_format = splitted_url[1]
        level_two_split = splitted_url[0].rsplit("/", 1)
        file_name = level_two_split[1]
        response = requests.get(
            url=url,
            auth=(consts.COFENSE_USERNAME, consts.COFENSE_PASSWORD),
            timeout=10,
            proxies=proxy,
        )
        if response.status_code == 200:
            applogger.info(
                "{}(method={}) : {} : Request Success : threat id - {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DOWNLOAD_THREAT_REPORTS,
                    file_name,
                )
            )
            download_file_name = "{}.{}".format(file_name, file_format)
            if file_format == "html":
                return func.HttpResponse(
                    response.content,
                    mimetype="text/html",
                    headers={
                        "Content-Disposition": f'attachment; filename="{download_file_name}"'
                    },
                )
            elif file_format == "pdf":
                return func.HttpResponse(
                    response.content,
                    mimetype="application/pdf",
                    headers={
                        "Content-Disposition": f'attachment; filename="{download_file_name}"'
                    },
                )
            return func.HttpResponse("Wrong File Format.")
        elif response.status_code == 401:
            applogger.error(
                "{}(method={}) : {} : Error occured : Authentication Failure. "
                "Provide valid Cofense Username and Cofense Password in Function App:{}'s "
                "configuration and try again.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DOWNLOAD_THREAT_REPORTS,
                    consts.FUNCTION_APP_NAME,
                )
            )
            return func.HttpResponse(
                "Authentication Error: Wrong Credentials. "
                "Provide valid Cofense Username and Cofense Password in Function App:{}'s "
                "configuration and try again.".format(consts.FUNCTION_APP_NAME)
            )
        elif response.status_code == 429:
            applogger.error(
                "{}(method={}) : {} : Error occured : Rate Limit Exceeded.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DOWNLOAD_THREAT_REPORTS,
                )
            )
            return func.HttpResponse(
                "Rate Limit Exceeded, Please Try again after some Time."
            )
        applogger.error(
            "{}(method={}) : {} : Unknown Error, Response from API-{}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DOWNLOAD_THREAT_REPORTS,
                response.text,
            )
        )
        return func.HttpResponse(response.text, mimetype="text/html")
    except requests.exceptions.RequestException as connect_error:
        if consts.IS_PROXY_REQUIRED == "Yes":
            applogger.error(
                "{}(method={}) : {} : Proxy parameters are invalid or Proxy is unreachable,"
                " Please verify in Function App:{}'s configuration and try again, Error-{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DOWNLOAD_THREAT_REPORTS,
                    consts.FUNCTION_APP_NAME,
                    connect_error,
                )
            )
            return func.HttpResponse(
                "Proxy parameters are invalid or Proxy is unreachable. "
                "Please verify in Function App:{}'s configuration and try again.".format(
                    consts.FUNCTION_APP_NAME
                )
            )
        applogger.error(
            "{}(method={}) : {} : HTTP Request Error, Error-{}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DOWNLOAD_THREAT_REPORTS,
                connect_error,
            )
        )
        return func.HttpResponse("HTTP Request Error, Error-{}.".format(connect_error))
    except CofenseIntelligenceException as cofense_error:
        param_type = "Proxy "
        if (
            str(cofense_error)
            == "Error Occurred while validating params. Required fields missing."
        ):
            param_type = "Required "
        applogger.error(
            "{}(method={}) : {} : {}Parameters are missing,"
            " Please verify in Function App:{}'s configuration and try again.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DOWNLOAD_THREAT_REPORTS,
                param_type,
                consts.FUNCTION_APP_NAME,
            )
        )
        return func.HttpResponse(
            "{}Parameters are missing, "
            "Please verify in Function App:{}'s configuration and try again.".format(
                param_type, consts.FUNCTION_APP_NAME
            )
        )

    except Exception as error:
        applogger.error(
            "{}(method={}) : {} : Error occured : {}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DOWNLOAD_THREAT_REPORTS,
                error,
            )
        )
        return func.HttpResponse("Error : {}".format(error))
