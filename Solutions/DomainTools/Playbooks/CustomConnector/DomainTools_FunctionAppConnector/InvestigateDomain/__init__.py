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

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
ENDPOINT = f"/v1/iris-investigate/"
DOMAINTOOLS_API_BASE_URL = "api.domaintools.com"
DEFAULT_HEADERS = {"accept": "application/json", "Content-Type": "application/json"}
max_pivot = 200


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


def generate_link(query, value):
    return (
        f"<a href=https://iris.domaintools.com/investigate/search/?q={query}:{value}>{value}</a>"
        if value
        else ""
    )


def table_results(custom_tuple, api_resp_json, max_pivot):
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
                            generate_link(query, data.get(keys[1]))
                            if data.get(keys[1])
                            else f"<a href=https://iris.domaintools.com/investigate/search/?q={query}:{ data.get(keys[1])}>{data.get(keys[1])}</a>"
                            if data.get(keys[1]) == 0
                            else ""
                        )
                else:
                    table_data[title] = generate_link(query, api_resp_json.get(key))
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
                                l2.append(
                                    generate_link(query, z.get("value"))
                                    if 0 < z.get("count") <= max_pivot
                                    else str(z.get("value"))
                                )
                            table_data[title] = ", ".join(l2)
                        else:
                            l1 = []
                            for x in data:
                                for y in x.get(keys[1]):
                                    l1.append(y)
                            l2 = []
                            for z in l1:
                                l2.append(
                                    generate_link(query, z.get("value"))
                                    if 0 < z.get("count") <= max_pivot
                                    else str(z.get("value"))
                                )
                            table_data[title] = ", ".join(l2)
                    elif isinstance(data, dict):
                        if key_type is dict:
                            k1 = data.get(keys[1])
                            if k1:
                                table_data[title] = (
                                    generate_link(query, k1.get("value"))
                                    if 0 < k1.get("count") <= max_pivot
                                    else k1.get("value")
                                )
                            else:
                                table_data[title] = ""
                        else:
                            l1 = []
                            k1 = data.get(keys[1])
                            if k1:
                                for x in k1:
                                    l1.append(x)
                                l2 = []
                                for z in l1:
                                    l2.append(
                                        generate_link(query, z.get("value"))
                                        if 0 < z.get("count") <= max_pivot
                                        else z.get("value")
                                    )
                                table_data[title] = ", ".join(l2)
                            else:
                                table_data[title] = ""

                else:
                    if key == "tags":
                        data = api_resp_json.get(key)
                        labels = [generate_link(query, z.get("label")) for z in data]
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
                                    l2.append(
                                        generate_link(query, z.get("value"))
                                        if 0 < z.get("count") <= max_pivot
                                        else z.get("value")
                                    )
                                table_data[title] = ", ".join(l2)
                            else:
                                table_data[title] = (
                                    generate_link(query, data.get("value"))
                                    if 0 < data.get("count") <= max_pivot
                                    else data.get("value")
                                )
                        else:
                            table_data[title] = ""

        table_formatted_data = []
        if table_data:
            table_formatted_data = [
                {"key": k, "value": v} for k, v in table_data.items()
            ]
        return table_formatted_data
    except Exception as ex:
        logging.error(str(ex))


def do_hmac_request(
    api_username,
    api_key,
    params=None,
):
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


def get_pivot_values(data, max_pivot, key=None, nested=False):
    pivot_values = []
    if nested:
        for obj in data:
            for nested_obj in obj.get(key):
                if 0 < nested_obj.get("count") <= max_pivot:
                    pivot_values.append(nested_obj.get("value"))
    elif key:
        for obj in data:
            if 0 < obj.get(key).get("count") <= max_pivot:
                pivot_values.append(obj.get(key).get("value"))
    else:
        for obj in data:
            if 0 < obj.get("count") <= max_pivot:
                pivot_values.append(obj.get("value"))
    return pivot_values


def get_pivot_data(results, api_username, api_key, max_pivot):
    pivot_results = []
    for result in results:
        ip_addresses = get_pivot_values(result.get("ip"), max_pivot, "address")
        registrant_name = (
            result.get("registrant_name").get("value")
            if 0 < result.get("registrant_name").get("count") <= max_pivot
            else ""
        )
        registrant_org = (
            result.get("registrant_org").get("value")
            if 0 < result.get("registrant_org").get("count") <= max_pivot
            else ""
        )
        nameserver_host = get_pivot_values(result.get("name_server"), max_pivot, "host")
        nameserver_ip = get_pivot_values(
            result.get("name_server"), max_pivot, "ip", True
        )
        mx_ip = get_pivot_values(result.get("mx"), max_pivot, "ip", True)
        mx_host = get_pivot_values(result.get("mx"), max_pivot, "host")
        ssl_email = get_pivot_values(result.get("ssl_email"), max_pivot)
        soa_email = get_pivot_values(result.get("soa_email"), max_pivot)
        ssl_hash = get_pivot_values(result.get("ssl_info"), max_pivot, "hash")
        ssl_hash = get_pivot_values(result.get("ssl_info"), max_pivot, "hash")
        email_domains = get_pivot_values(result.get("email_domain"), max_pivot)

        pivots = {
            "ip": ip_addresses,
            "registrant": [registrant_name],
            "registrant_org": [registrant_org],
            "nameserver_host": nameserver_host,
            "nameserver_ip": nameserver_ip,
            "mx_ip": mx_ip,
            "mx_host": mx_host,
            "ssl_email": ssl_email,
            "ssl_hash": ssl_hash,
            "email": soa_email,
            "email_domain": email_domains,
        }
        for k, v in pivots.items():
            for pivot_value in v:
                if pivot_value:
                    pivot_resp = call_pivot_api(k, pivot_value, api_username, api_key)
                    if pivot_resp:
                        pivot_results.append(pivot_resp)
    return pivot_results



def call_pivot_api(param_name, pivot_value, api_username, api_key):
    try:
        params={param_name: pivot_value}
        results = []
        while True:
            response = do_hmac_request(api_username, api_key, params)
            results.extend(response.json().get('response',{}).get('results',[]))
            if response.json().get("response").get("position"):
                params['position'] = response.json().get("response").get("position")
            else:
                break
        # resp = do_hmac_request(api_username, api_key, params)
        if results:
            data = {}
            data["pivot_type"] = param_name
            data["pivot_value"] = pivot_value
            data["pivot_results"] = []
            for res in results:
                data["pivot_results"].append(
                    {
                        "domain": res.get("domain"),
                        "risk_score": res.get("domain_risk", {}).get("risk_score"),
                    }
                )
            data["pivot_results"] = sorted(
                data["pivot_results"], key=lambda x: x["risk_score"], reverse=True
            )
            return data
    except Exception as ex:
        logging.info(ex)
    return []



def extract_domain(url):
    try:
        extract_result = tldextract.extract(url)
        domain = f"{extract_result.domain}.{extract_result.suffix}"
        return domain
    except Exception as ex:
        logging.info(f"Error in domain tldextract: {ex}")
        return ""


def modified_resp(
    responses: list,
    api_username,
    api_key,
    malicious_tags,
    max_pivot,
    include_pivots=False,
):
    results = []
    for x in responses:
        op = {}
        api_tags = [z.get("label") for z in x.get("tags", [])]
        op["domain"] = x.get("domain")
        op["custom_table"] = table_results(custom_tuple, x, max_pivot)
        if include_pivots:
            op["pivot"] = get_pivot_data([x], api_username, api_key, max_pivot)
        op["malicious_tags"] = [tag for tag in api_tags if tag in malicious_tags]
        results.append(op)
    return results


def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f"Resource Requested: {func.HttpRequest}")

    try:
        api_key = environ["APIKey"]
        api_username = environ["APIUsername"]
        domain = req.params.get("domain")
        active = req.params.get("active")
        create_date = req.params.get("create_date")
        expiration_date = req.params.get("expiration_date")
        guided_pivots = req.params.get("guided_pivots", False)
        max_pivot = req.params.get("max_pivot", 0)
        malicious_tags = req.params.get("malicious_tags", [])
        from_playbook = req.params.get("from_playbook")
        create_date_within = req.params.get("create_date_within")
        first_seen_within = req.params.get("first_seen_within")
        if not domain:
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                domain = req_body.get("domain")
                active = req_body.get("active")
                create_date = req_body.get("create_date")
                create_date_within = req_body.get("create_date_within")
                first_seen_within = req_body.get("first_seen_within")
                expiration_date = req_body.get("expiration_date")
                guided_pivots = req_body.get("guided_pivots", False)
                max_pivot = req_body.get("max_pivot", 200)
                malicious_tags = req_body.get("malicious_tags", [])
                from_playbook = req_body.get("from_playbook", False)

        domains_list = [extract_domain(x) for x in domain]
        params = {}
        if active:
            params["active"] = active
        if create_date:
            params["create_date"] = create_date
        if expiration_date:
            params["expiration_date"] = expiration_date
        if create_date_within:
            params["create_date_within"] = create_date_within
        if first_seen_within:
            params["first_seen_within"] = first_seen_within
        api_response = []
        api_results = []
        for batch in chunk_list(domains_list, 100):
            params['domain'] = ",".join(batch)
            response = do_hmac_request(api_username, api_key, params)
            if response.ok:
                api_response.append(response.json()["response"])
                api_results.extend(response.json()["response"]["results"])
            else:
                api_response.append(response.json())

        if api_results:
            if from_playbook:
                if guided_pivots:
                    output = {}
                    output["response"] = api_response
                    output["custom_response"] = modified_resp(
                        api_results,
                        api_username,
                        api_key,
                        malicious_tags,
                        max_pivot,
                        True,
                    )
                else:
                    output = {}
                    output["response"] = api_response
                    output["custom_response"] = modified_resp(
                        api_results,
                        api_username,
                        api_key,
                        malicious_tags,
                        max_pivot,
                        False,
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
