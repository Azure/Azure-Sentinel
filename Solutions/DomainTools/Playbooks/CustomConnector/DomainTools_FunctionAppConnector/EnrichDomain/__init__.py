import json
import logging
from datetime import datetime
from hashlib import sha256
from hmac import new
from os import environ
from urllib.parse import urlencode, urlunparse

import azure.functions as func
import requests
import tldextract
from .utils import save_to_sentinel


DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
ENDPOINT = f"/v1/iris-enrich/"
DOMAINTOOLS_API_BASE_URL = "api.domaintools.com"
DEFAULT_HEADERS = {"accept": "application/json", "Content-Type": "application/json"}


custom_tuple = [
    ("Adsense", "adsense", "ad", dict),
    ("Contact Country Code", "admin_contact.country", "cons.cc", dict),
    ("Contact Name", "admin_contact.name", "cons.nm", dict),
    ("Contact Phone", "admin_contact.phone", "cons.ph", dict),
    ("Contact Street", "admin_contact.street", "cons.str", dict),
    ("Risk Score", "domain_risk.risk_score", "cr", int),
    ("Create Date", "create_date", "cre", dict),
    ("Domain", "domain", "domain", str),
    ("Admin Contact Email", "admin_contact.email", "empa", list),
    ("Billing Contact Email", "billing_contact.email", "empb", list),
    ("SOA Email", "soa_email", "ema", list),
    ("Registrant Contact Email", "registrant_contact.email", "empr", list),
    ("Technical Contact Email", "technical_contact.email", "empt", list),
    ("Whois Email", "additional_whois_email", "emw", list),
    ("Email Domain", "email_domain", "emd", list),
    ("Expiration Date", "expiration_date", "exp", dict),
    ("First Seen", "first_seen", "current_lifecycle_first_seen", dict),
    ("Google Analytics", "google_analytics", "ga", dict),
    ("Google Analytics 4", "ga4", "ga4", list),
    ("GTM Codes", "gtm_codes", "gtm_codes", list),
    ("Facebook Codes", "fb_codes", "fb_codes", list),
    ("Hotjar Codes", "hotjar_codes", "hotjar_codes", list),
    ("Baidu Codes", "baidu_codes", "baidu_codes", list),
    ("Yandex Codes", "yandex_codes", "yandex_codes", list),
    ("Matomo Codes", "matomo_codes", "matomo_codes", list),
    (
        "Statcounter Project Codes",
        "statcounter_project_codes",
        "statcounter_project_codes",
        list,
    ),
    (
        "Statcounter Security Codes",
        "statcounter_security_codes",
        "statcounter_security_codes",
        list,
    ),
    ("IP Address", "ip.address", "ip.ip", dict),
    ("IP ASN", "ip.asn", "ip.asn", list),
    ("IP Country", "ip.country_code", "ip.cc", dict),
    ("IP ISP", "ip.isp", "ip.isp", dict),
    ("MX Host", "mx.host", "mx.mx", dict),
    ("MX Domain", "mx.domain", "mx.mxd", dict),
    ("MX IP", "mx.ip", "mx.mip", list),
    ("Nameserver Host", "name_server.host", "ns.ns", dict),
    ("Nameserver Domain", "name_server.domain", "ns.nsd", dict),
    ("Nameserver IP", "name_server.ip", "ns.nip", list),
    ("Popularity Rank", "popularity_rank", "popularity_rank", int),
    ("Redirect Domain", "redirect_domain", "rdd", dict),
    ("Registrant Name", "registrant_name", "r_n", dict),
    ("Registrant Org", "registrant_org", "r_o", dict),
    ("Registrar", "registrar", "reg", dict),
    ("SSL Alt  Names", "ssl_info.alt_names", "ssl.alt_names", list),
    ("SSL Duration", "ssl_info.duration", "ssl.duration", dict),
    ("SSL Email", "ssl_info.email", "ssl.em", list),
    ("SSL Hash", "ssl_info.hash", "ssl.em", dict),
    ("SSL Hash", "ssl_info.hash", "ssl.sh", dict),
    (
        "SSL Issuer Common Name",
        "ssl_info.issuer_common_name",
        "ssl.issuer_common_name",
        dict,
    ),
    ("SSL Not After", "ssl_info.not_after", "ssl.not_after", dict),
    ("SSL Not Before", "ssl_info.not_before", "ssl.not_before", dict),
    ("SSL Subject", "ssl_info.subject", "ssl.s", dict),
    ("SSL Subject", "ssl_info.subject", "ssl.s", dict),
    ("SSL Subject Common Name", "ssl_info.common_name", "ssl.common_name", dict),
    ("SSL Organization", "ssl_info.organization", "ssl.so", dict),
    ("Server Type", "server_type", "server_type", dict),
    ("Status", "active", "active", bool),
    ("TLD", "tld", "tld", str),
    ("Tags", "tags", "tags", list),
    ("Website Title", "website_title", "title", dict),
]


def extract_domain(url):
    try:
        extract_result = tldextract.extract(url)
        domain = f"{extract_result.domain}.{extract_result.suffix}"
        return domain
    except Exception as ex:
        logging.info(f"Error in domain tldextract: {ex}")
        return ""


def table_results(custom_tuple, api_resp_json, asim=False):
    try:
        table_data = {}
        for i in custom_tuple:
            title, key, query, key_type = i
            if key_type not in [list, dict]:
                if "." in key:
                    keys = key.split(".")
                    data = api_resp_json[keys[0]]
                    if key_type is int:
                        table_data[title] = (
                            data.get(keys[1]) if data.get(keys[1]) else ""
                        )
                else:
                    table_data[title] = api_resp_json.get(key)
            else:
                if "." in key:
                    keys = key.split(".")
                    data = api_resp_json[keys[0]]
                    if isinstance(data, list):
                        if key_type is dict:
                            l1 = []
                            for x in data:
                                l1.append(x.get(keys[1]))
                            l2 = []
                            for z in l1:
                                l2.append(str(z.get("value")))
                            table_data[title] = ", ".join(l2)
                        else:
                            l1 = []
                            for x in data:
                                for y in x.get(keys[1]):
                                    l1.append(y)
                            l2 = []
                            for z in l1:
                                l2.append(str(z.get("value")))
                            table_data[title] = ", ".join(l2)
                    elif isinstance(data, dict):
                        if key_type is dict:
                            k1 = data.get(keys[1])
                            table_data[title] = k1.get("value") if k1 else ""
                        else:
                            l1 = []
                            k1 = data.get(keys[1])
                            if k1:
                                for x in k1:
                                    l1.append(x)
                                l2 = []
                                for z in l1:
                                    l2.append(str(z.get("value")))
                                table_data[title] = ", ".join(l2)
                            else:
                                table_data[title] = ""

                else:
                    if key == "tags":
                        data = api_resp_json.get(key)
                        labels = [z.get("label") for z in data]
                        table_data[title] = ", ".join(labels)
                    else:
                        data = api_resp_json.get(key)
                        if data:
                            if key_type is list:
                                l1 = []
                                for x in data:
                                    l1.append(x)
                                l2 = []
                                for z in l1:
                                    l2.append(str(z.get("value")))
                                table_data[title] = ", ".join(l2)
                            else:
                                table_data[title] = data.get("value")
                        else:
                            table_data[title] = ""
        if asim:
            return table_data
        else:
            table_formatted_data = []
            if table_data:
                table_formatted_data = [
                    {"key": k, "value": v} for k, v in table_data.items()
                ]
            return table_formatted_data
    except Exception as ex:
        logging.error(str(ex))


def do_hmac_request(api_username, api_key, params=None):
    try:
        signer = DTSigner(api_username, api_key)
        timestamp = datetime.utcnow().strftime(DATE_TIME_FORMAT)

        query = {
            "api_username": api_username,
            "signature": signer.sign(timestamp, ENDPOINT),
            "timestamp": timestamp,
            "app_partner": "Microsoft",
            "app_name": "Sentinel",
            "app_version": "1.0",
        }
        full_url = urlunparse(
            ("https", DOMAINTOOLS_API_BASE_URL, ENDPOINT, "", urlencode(query), None)
        )
        response = requests.get(full_url, params=params, headers=DEFAULT_HEADERS)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logging.info(f"Request failed: {e}")
        return response


class DTSigner:
    def __init__(self, api_username: str, api_key: str) -> None:
        self.api_username = api_username
        self.api_key = api_key

    def sign(self, timestamp: str, uri: str) -> str:
        """
        Generates a digital signature for the given timestamp and URI.

        Args:
            timestamp (str): The timestamp to include in the signature.
            uri (str): The URI to include in the signature.

        Returns:
            str: The generated digital signature.
        """
        params = "".join([self.api_username, timestamp, uri])
        return new(
            self.api_key.encode("utf-8"), params.encode("utf-8"), digestmod=sha256
        ).hexdigest()
    


def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]



def modified_resp(responses: list):
    results = []
    for x in responses:
        op = {}
        op["domain"] = x.get("domain")
        op["custom_table"] = table_results(custom_tuple, x)
        results.append(op)
    return results


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f"Resource Requested: {func.HttpRequest}")

    try:
        api_key = environ["APIKey"]
        api_username = environ["APIUsername"]
        workspace_id = req.params.get("workspace_id")
        workspace_key = req.params.get("workspace_key")
        domain = req.params.get("domain")
        from_playbook = req.params.get("from_playbook", False)
        asim = req.params.get("asim", False)
        if not domain:
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                domain = req_body.get("domain")
                from_playbook = req_body.get("from_playbook", False)
                asim = req_body.get("asim", False)
                workspace_id = req_body.get("workspace_id")
                workspace_key = req_body.get("workspace_key")

        domains_list = [extract_domain(x) for x in domain]
        api_response = []
        api_results = []
        for batch in chunk_list(domains_list, 500):
            params = {"domain": ",".join(batch)}
            response = do_hmac_request(api_username, api_key, params)
            if response.ok:
                api_response.append(response.json()["response"])
                api_results.extend(response.json()["response"]["results"])
            else:
                api_response.append(response.json())
        if api_results:
            if from_playbook:
                output = {}
                output["response"] = api_response
                output["custom_response"] = modified_resp(
                    api_results
                )
            elif asim:
                sentinel_logs = [
                    table_results(custom_tuple, log, True)
                    for log in api_results
                ]
                sentinel_resp = save_to_sentinel(
                    f"https://{workspace_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01",
                    workspace_id,
                    workspace_key,
                    json.dumps(sentinel_logs),
                    "DomainToolsDomainEnrichment",
                )
                if sentinel_resp in range(200, 299):
                    logging.info(
                        f"Data saved in DomainToolsDomainEnrichment custom table successfully."
                    )
                    return func.HttpResponse(
                        json.dumps({"status": "success"}),
                        headers={"Content-Type": "application/json"},
                        status_code=200,
                    )
                return func.HttpResponse(
                    json.dumps({"status": "error"}),
                    headers={"Content-Type": "application/json"},
                    status_code=200,
                )

            else:
                output = api_response
        else:
            output = api_response
        return func.HttpResponse(
            json.dumps(output),
            headers={"Content-Type": "application/json"},
            status_code=200,
        )

    except KeyError as ke:
        logging.error(f"Invalid Settings. {ke.args} configuration is missing.")
        return func.HttpResponse(
            "Invalid Settings. Configuration is missing.", status_code=500
        )
    except Exception as ex:
        logging.error(f"Exception Occured: {str(ex)}")
        return func.HttpResponse("Internal Server Exception", status_code=500)
