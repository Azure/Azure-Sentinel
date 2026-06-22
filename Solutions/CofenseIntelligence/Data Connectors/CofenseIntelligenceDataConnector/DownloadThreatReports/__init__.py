"""Download Report Module."""
import logging
import inspect
import requests
import azure.functions as func
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.utils import Utils
from ..SharedCode.cofense_intelligence_exception import CofenseIntelligenceException
import urllib.parse
import socket
import ipaddress


def _is_address_private(hostname: str) -> bool:
    """Resolve hostname and check if any resolved IP is private/local.

    Returns True if any address is in a private, loopback or link-local range.
    If resolution fails, be conservative and treat as not private (fail open is dangerous).
    """
    try:
        # If hostname is an IP literal, check directly
        try:
            ip = ipaddress.ip_address(hostname)
            return ip.is_private or ip.is_loopback or ip.is_link_local
        except ValueError:
            # Not an IP literal; resolve DNS
            infos = socket.getaddrinfo(hostname, None)
            for family, _, _, _, sockaddr in infos:
                addr = sockaddr[0]
                try:
                    ip = ipaddress.ip_address(addr)
                    if ip.is_private or ip.is_loopback or ip.is_link_local:
                        return True
                except ValueError:
                    continue
    except Exception:
        # If DNS resolution fails for any reason, be conservative and disallow the host by marking as private
        return True
    return False


def _is_allowed_cofense_host(hostname: str) -> bool:
    """Allow only hosts that belong to configured Cofense base url.

    This enforces an allowlist: the request host must be the same as or a subdomain
    of the configured COFENSE_BASE_URL host.
    """
    if not hostname:
        return False
    try:
        base_host = urllib.parse.urlparse(consts.COFENSE_BASE_URL).hostname
        if not base_host:
            return False
        # Exact match or subdomain
        hostname = hostname.lower()
        base_host = base_host.lower()
        return hostname == base_host or hostname.endswith("." + base_host)
    except Exception:
        return False


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

        # Validate input URL -- do NOT accept arbitrary user-supplied destinations.
        url = req.params.get("url")
        if not url:
            return func.HttpResponse("Missing 'url' parameter.", status_code=400)

        parsed = urllib.parse.urlparse(url)
        # Only allow HTTPS
        if parsed.scheme.lower() != "https":
            return func.HttpResponse("Only HTTPS destinations are allowed.", status_code=400)

        hostname = parsed.hostname
        if not hostname:
            return func.HttpResponse("Invalid URL provided.", status_code=400)

        # Enforce allowlist: only Cofense configured base host (or its subdomains) are permitted
        if not _is_allowed_cofense_host(hostname):
            applogger.error(
                "{}(method={}) : {} : Rejected download request. Destination not in allowlist: {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DOWNLOAD_THREAT_REPORTS,
                    hostname,
                )
            )
            return func.HttpResponse(
                "Destination host is not allowed.", status_code=403
            )

        # Prevent requests to private/local addresses
        if _is_address_private(hostname):
            applogger.error(
                "{}(method={}) : {} : Rejected download request. Destination resolves to private/local address: {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DOWNLOAD_THREAT_REPORTS,
                    hostname,
                )
            )
            return func.HttpResponse(
                "Destination resolves to a private or local address and is not allowed.",
                status_code=403,
            )

        # Extract filename and format from path safely
        path_parts = parsed.path.rsplit("/", 1)
        if len(path_parts) < 2 or not path_parts[1]:
            return func.HttpResponse("Invalid file path in URL.", status_code=400)
        file_format = path_parts[1]
        level_two_split = path_parts[0].rsplit("/", 1)
        file_name = level_two_split[1] if len(level_two_split) > 1 else level_two_split[0]

        # Make the request but DO NOT follow redirects automatically to avoid leaking credentials
        response = requests.get(
            url=url,
            auth=(consts.COFENSE_USERNAME, consts.COFENSE_PASSWORD),
            timeout=10,
            proxies=proxy,
            allow_redirects=False,
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
