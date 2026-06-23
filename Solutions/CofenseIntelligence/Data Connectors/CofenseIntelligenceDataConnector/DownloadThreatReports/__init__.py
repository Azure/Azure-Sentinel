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

        # Prefer accepting a threat/report ID rather than a full URL to avoid SSRF.
        # Acceptable params: 'id' or 'threat_id' (report identifier). Optional: 'format' ('pdf' or 'html').
        threat_id = req.params.get("id") or req.params.get("threat_id") or req.params.get("report_id")
        if not threat_id:
            return func.HttpResponse("Missing 'id' (threat/report identifier) parameter.", status_code=400)

        file_format = (req.params.get("format") or "pdf").lower()
        if file_format not in ("pdf", "html"):
            return func.HttpResponse("Invalid format. Supported: pdf, html.", status_code=400)

        # Construct the trusted Cofense URL server-side using the configured base URL
        base = consts.COFENSE_BASE_URL.rstrip('/')
        url = f"{base}/{threat_id}/{file_format}"
        parsed = urllib.parse.urlparse(url)

        # Safety checks on the constructed URL
        if parsed.scheme.lower() != "https":
            applogger.error(
                "{}(method={}) : {} : Configured COFENSE_BASE_URL is not HTTPS: {}".format(
                    consts.LOGS_STARTS_WITH, __method_name, consts.DOWNLOAD_THREAT_REPORTS, consts.COFENSE_BASE_URL
                )
            )
            return func.HttpResponse("Server misconfiguration: COFENSE_BASE_URL must be HTTPS.", status_code=500)

        hostname = parsed.hostname
        if not hostname:
            return func.HttpResponse("Invalid configured Cofense base URL.", status_code=500)

        # As a final safety check, ensure the constructed hostname matches expected Cofense host
        if not _is_allowed_cofense_host(hostname):
            applogger.error(
                "{}(method={}) : {} : Configured COFENSE_BASE_URL host not allowed: {}".format(
                    consts.LOGS_STARTS_WITH, __method_name, consts.DOWNLOAD_THREAT_REPORTS, hostname
                )
            )
            return func.HttpResponse("Server misconfiguration: unexpected Cofense host.", status_code=500)

        # Prevent requests to private/local addresses (defense-in-depth even for constructed URL)
        if _is_address_private(hostname):
            applogger.error(
                "{}(method={}) : {} : Rejected download request. Constructed destination resolves to private/local address: {}".format(
                    consts.LOGS_STARTS_WITH, __method_name, consts.DOWNLOAD_THREAT_REPORTS, hostname
                )
            )
            return func.HttpResponse(
                "Constructed destination resolves to a private or local address and is not allowed.",
                status_code=403,
            )

        # File name for logging and content-disposition
        file_name = threat_id

        # Make the authenticated request to the trusted Cofense URL but DO NOT follow redirects
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
