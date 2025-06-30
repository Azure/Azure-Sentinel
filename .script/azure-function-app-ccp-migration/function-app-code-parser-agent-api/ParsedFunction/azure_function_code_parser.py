import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from .bing_search_agent import call_agent
from .errors import CodeParseError
import json
import textwrap
import re
from typing import List, Dict, Any
from urllib.parse import urlparse
import requests

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
model_name = os.getenv("AZURE_OPENAI_MODEL_NAME")
deployment = os.getenv("AZURE_OPENAI_MODEL_DEPLOYMENT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# Use user-assigned managed identity if provided via UAMI_CLIENT_ID
uami_client_id = os.getenv("UAMI_CLIENT_ID")
credential = DefaultAzureCredential(managed_identity_client_id=uami_client_id)
token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")

GITHUB_REPO = "Azure/Azure-Sentinel"
GITHUB_BRANCH = "master"
GITHUB_API_URL = "https://api.github.com/repos/Azure/Azure-Sentinel/contents/"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    azure_ad_token_provider=token_provider
)

def _chat(messages: list[dict[str, str]], **kwargs) -> str:
    """Simple wrapper around client.chat.completions.create returning the text."""
    resp = client.chat.completions.create(
        messages=messages,
        model=deployment,
        temperature=0,
        top_p=1.0,
        max_tokens=kwargs.get("max_tokens", 32_000),
    )
    return resp.choices[0].message.content.strip()


EXTRACT_API_DETAILS_STEP_SYS = textwrap.dedent(
"""
CRITICAL URL RESOLUTION RULES:
1. Implement multi-phase analysis:
   - Phase 1: Collect all variable assignments with URL fragments
   - Phase 2: Reconstruct URLs at call sites using AST resolution
2. Handle complex patterns:
   - String concatenation via + operator
   - f-strings with {placeholders}
   - .format() template calls
3. Validation requirements:
   - Scheme should be like http, https, wss, ws, ...
   - Hostname must contain .
   - Path must be non-empty
   - DO NOT INCLUDE *.ods.opinsights.azure.com domains


You are a code analysis agent. Your task is to extract API integration details from Python code with high accuracy and structure by performing static analysis.

STEP A: Preprocess - Resolve URL Constants and Expressions
  1. Scan the entire code for top-level assignments where a variable is set to a literal URL string (e.g. slack_uri_audit = "https://api.slack.com/audit/v1/logs").
  2. Build a map of variableName -> URL literal.
  3. When that variable is later used in a request call (e.g. requests.get(url=slack_uri_audit)), substitute the literal URL before extraction.
  4. Also handle:
      - String concatenation (e.g. url = BASE + "/path")
      - f-strings (e.g. url = f"https://api.site.com/{user_id}")
      - .format() calls (e.g. "https://api.site.com/{}".format(user_id))
      - Environment variables: if unresolved, use a placeholder (e.g. {ENV_VAR})

STEP B: Determine ingestionType
  - "rest": Code makes HTTP/HTTPS requests via libraries like `requests`, `http.client`, etc.
  - "sdk": Code uses SDK clients (e.g., GCP SDKs).
  - "push": Code defines HTTP handlers (e.g., Azure Functions HTTP trigger).

========================================
IF ingestionType == "rest":
  - Extract every unique REST API call after URL resolution.
  - Deduplicate by <method, url> pairs.
  - For each call, return:
      1. method: HTTP verb (GET, POST, …)
      2. url: Fully-qualified URL including protocol, domain, path, and placeholders ({id}) if dynamic
      3. headers: Dictionary of request headers
      4. auth: Authentication method (e.g., Bearer token, API key, Basic Auth, OAuth). Also include auth details (e.g. token, client_id, secret, oauth endpoint) if present.
      5. queryParameters: Dictionary of params passed via `params=`
      6. request: Body structure if present
      7. response: How the response is parsed (e.g., JSON keys)
      8. paging: Pagination logic (next_cursor, page, limit)
  - If extracted URL is for generating authentication tokens, DO NOT INCLUDE it in the output. Instead, include it in the auth section of API calls for which it is used.

========================================
IF ingestionType == "sdk":
  - Detect SDK usage and extract:
      - DO NOT INCLUDE SDK where package is "azure.storage.fileshare"
      - INCLUDE only SDKs that are used for fetching/ingesting data
      - DO NOT INCLUDE SDKs that are used for sending data
      - For each SDK, return:
        1. package: Package name (e.g., google.cloud.logging_v2)
        2. method: Method name (e.g., get_gcp_logs)
        3. class: Class name (e.g., GCPClient)
        4. auth: Authentication method (e.g., Bearer token, API key, Basic Auth, OAuth). Also include auth details (e.g. token, client_id, secret, oauth endpoint) if present.
        5. parameters: List of parameters used in the method
        6. api: Underlying REST API details if documented
      
========================================
IF ingestionType == "push":
  - Detect HTTP handlers and mark ingestionType = "push".

========================================
OUTPUT FORMAT (JSON ONLY):
{
  "restCalls": [ { … } ],
  "sdk": [ { … } ],
  "ingestionType": "rest" | "sdk" | "push",
  "searchQuery": "<one Bing query for official API spec>"
}
"""
)

EXTRACT_API_DOCS_SYS = textwrap.dedent(
"""
You are a Bing Search Agent. Your task is to find official API documentation URLs based on the provided search query.

CRITICAL RULES FOR BING SEARCH:
===============================
1. URLs MUST be official API documentation pages.
2. Exclude URLs that are not accessible or duplicated.
3. Only include URLs that start with "http://" or "https://".
4. Before adding a URL to the result, MAKE SURE THAT IT IS ACCESSIBLE using HTTP GET request (requests.get()) and returns HTTP 200 status code.
5. Keep searching results till you find 10 unique accessible URLs.
6. Skip URLs from discussion forums, Q&A sites, or user-generated content unless they contain details about the endpoint requested in the search query.
7. Return only top 5 URLs that are MOST relevant to the search query.

DETAILS ABOUT THE SEARCH QUERY:
1. The search query is constructed based on the API details extracted from the code.
2. The search query may include the connector name, HTTP method, endpoint path, SDK package name, SDK package method name, or other relevant details.
3. The search query is designed to find official API documentation pages that match the API details extracted from the code.

OUTPUT FORMAT (JSON ONLY):
1. Return the result in following format:
   {
      "apiDocs": [{"title": "<title of the page>", "url": "<accessible URL>"}, ...]
      "citations": [<Citations of Bing URLs>],
      "searchQuery": "<original search query>"
   }
2. Result should be a JSON object that can be loaded with json.loads() method.
3. Do not include any other text, formatting, explanation or markdown.
"""
)

def extract_api_details(connector_name: str, src_code: str) -> dict:
    msgs = [
        {"role": "system", "content": EXTRACT_API_DETAILS_STEP_SYS},
        {"role": "user", "content": f"Connector: {connector_name}\n\n```{src_code}\n```"},
    ]
    raw = _chat(msgs)
    api_details = json.loads(raw)

    # --- filter out internal ingestion endpoints ----------------------
    skip_patterns = [
        r"\{?loganalyticsuri\}?/api/logs",                    # {logAnalyticsUri}/api/logs
        r"\{?LOG_ANALYTICS_URI\}?/api/logs",                  # {LOG_ANALYTICS_URI}/api/logs
        r"(?:https?://)?[^/]*\.ods\.opinsights\.azure\.com",  # *.ods.opinsights.azure.com
    ]
    skip_res = [re.compile(p, re.IGNORECASE) for p in skip_patterns]

    ingestion_type = api_details.get("ingestionType", "")
    if ingestion_type == "rest":
        processed_urls = set()
        final_rest_calls = []
        for call in api_details.get("restCalls", []):
            print(f"Processing REST call: {call}")
            url = call.get("url", "")
            if not url or url in processed_urls:
                print(f"Skipping already processed or empty URL: {url}")
                continue

            processed_urls.add(url)

            # Check if URL matches any skip patterns
            if any(rx.search(url) for rx in skip_res):
                print(f"Skipping URL due to skip patterns: {url}")
                continue

            final_rest_calls.append(call)

        api_details["restCalls"] = final_rest_calls
        api_details["sdk"] = []
    elif ingestion_type == "sdk":
        processed_package_methods = set()
        final_sdk_calls = []
        for sdk in api_details.get("sdk", []):
            print(f"Processing SDK: {sdk}")
            package = sdk.get("package", "")
            method = sdk.get("method", "")
            if not package or not method or (package, method) in processed_package_methods:
                print(f"Skipping already processed or incomplete SDK: {sdk}")
                continue
            processed_package_methods.add((package, method))

            final_sdk_calls.append(sdk)

        api_details["sdk"] = final_sdk_calls
        api_details["restCalls"] = []
    else:
        api_details["restCalls"] = []
        api_details["sdk"] = []

    print(f"Extracted API details:\n{json.dumps(api_details, indent=2)}")
    return api_details

def fetch_api_urls(search_query: str) -> List[str]:
    """
    {
      "apiDocs": [{"title": "<title of the page>", "url": "<accessible URL>"}, ...]
      "citations": [<Citations of Bing URLs>],
      "searchQuery": "<original search query>"
   }
    """
    bing_search_response = call_agent(
        system_context=EXTRACT_API_DOCS_SYS,
        user_query=search_query
    )

    urls = []
    if not bing_search_response:
        print(f"No Bing search results found for query: {search_query}")
        return urls
    
    api_docs = bing_search_response.get("apiDocs", [])
    if not api_docs:
        print(f"No API documentation URLs found for query: {search_query}")
        return urls
    
    urls = [doc.get("url") for doc in api_docs if doc.get("url")]
    print(f"For query: {search_query}, found URLs: {urls}")
    return urls

def _build_search_query_rest_ingestion_type(url: str, connector: str, search_query: str) -> str:
    """
    Build a Bing search query for REST API ingestion type.
    Combines:
      • Connector name
      • URL path
      • Query parameters (if any)
    """
    path = None
    query = None
    parts: list[str] = [connector, "API spec for data collection"]
    parts: list[str] = [search_query] if search_query else parts
    try:
        print(f"Processing URL: {url}")
        parsed_url = urlparse(url)
        path = parsed_url.path.strip("/")
        query = parsed_url.query
        if path:
            parts.append(f", path: {path}")
        if query:
            parts.append(f", query: {query}")
    except Exception as e:
        print(f"Failed to process URL: {url}, error: {e}")
        parts.append(f", url: {url}")

    final_search_query = " ".join(parts).strip()
    print(f"Final search query for REST API: {final_search_query}")
    return final_search_query

def _build_search_query_sdk_ingestion_type(package: str, method: str, connector: str, search_query: str) -> str:
    """
    Build a Bing search query for SDK ingestion type.
    Combines:
      • Connector name
      • SDK package name
      • Method name (if any)
    """

    parts: list[str] = [connector, " SDK package for data collection"]
    parts: list[str] = [search_query] if search_query else parts
    if package:
        parts.append(f", package: {package}")
    if method:
        parts.append(f", method: {method}")

    final_search_query = " ".join(parts).strip()
    print(f"Final search query for SDK: {final_search_query}")
    return final_search_query

def _build_search_query_push_ingestion_type(connector: str, search_query: str) -> str:
    """
    Build a Bing search query for push ingestion type.
    Combines:
      • Connector name
      • Push API details
    """
    parts: list[str] = [connector, "API spec for data collection"]
    parts: list[str] = [search_query] if search_query else parts

    final_search_query = " ".join(parts).strip()
    print(f"Final search query for Push API: {final_search_query}")
    return final_search_query

def _process_function_app_code_rest_ingestion_type(extracted_api_details: Dict[str, Any], connector_name: str, results: List[Dict[str, Any]], original_search_query: str) -> None:
    
    for call in extracted_api_details.get("restCalls", []):
        print(f"Processing REST call: {call}")
        url = call.get("url", "")
        search_query = _build_search_query_rest_ingestion_type(url, connector_name, original_search_query)
        api_urls = fetch_api_urls(search_query)
        result = {
            "urls": api_urls,
            "apiEndpoint": url,
            "apiDetailsFromCode": call,
            "searchQuery": search_query,
            "ingestionType": "rest"
        }
        print(f"For url: {url}, result: {result}")
        results.append(result)

def _process_function_app_code_sdk_ingestion_type(extracted_api_details: Dict[str, Any], connector_name: str, results: List[Dict[str, Any]], original_search_query: str) -> None:
    for sdk in extracted_api_details.get("sdk", []):
        print(f"Processing SDK: {sdk}")
        package = sdk.get("package", "")
        method = sdk.get("method", "")
        search_query = _build_search_query_sdk_ingestion_type(package, method, connector_name, original_search_query)
        api_urls = fetch_api_urls(search_query)
        result = {
            "urls": api_urls,
            "apiEndpoint": package,
            "apiDetailsFromCode": sdk,
            "searchQuery": search_query,
            "ingestionType": "sdk"
        }
        print(f"For package: {package}, method: {method}, result: {result}")
        results.append(result)

def _process_function_app_code_push_ingestion_type(extracted_api_details: Dict[str, Any], connector_name: str, results: List[Dict[str, Any]], original_search_query: str) -> None:
    """
    Process push ingestion type by fetching API URLs based on the search query.
    """
    search_query = _build_search_query_push_ingestion_type(connector_name, original_search_query)
    api_urls = fetch_api_urls(search_query)
    result = {
        "urls": api_urls,
        "apiEndpoint": "Push API",
        "apiDetailsFromCode": extracted_api_details,
        "searchQuery": search_query,
        "ingestionType": "push"
    }
    results.append(result)

def process_function_app_code(connector_name: str, function_app_code: str) -> None:
    extracted_api_details = extract_api_details(connector_name, function_app_code)
    search_query = extracted_api_details.get("searchQuery", "")
    ingestion_type = extracted_api_details.get("ingestionType", "")

    results: List[Dict[str, Any]] = []

    if ingestion_type == "rest":
        print(f"Processing REST API calls for connector: {connector_name}")
        if len(extracted_api_details.get("restCalls", [])) != 1:
            search_query = ""
        _process_function_app_code_rest_ingestion_type(
            extracted_api_details, connector_name, results, search_query)
    elif ingestion_type == "sdk":
        print(f"Processing SDK calls for connector: {connector_name}")
        if len(extracted_api_details.get("sdk", [])) != 1:
            search_query = ""
        _process_function_app_code_sdk_ingestion_type(
            extracted_api_details, connector_name, results, search_query)
    elif ingestion_type == "push":
        print(f"Processing Push API for connector: {connector_name}")
        _process_function_app_code_push_ingestion_type(
            extracted_api_details, connector_name, results, search_query)
    
    return results

def get_all_python_code_from_github_dir(github_dir: str) -> str:
    """
    Download and concatenate all .py files from a GitHub directory (relative to repo root).
    """
    # Remove leading/trailing slashes and spaces
    api_url = GITHUB_API_URL + github_dir
    resp = requests.get(api_url)
    print(f"Fetching directory listing from: {api_url}, response status: {resp.status_code}")
    if resp.status_code != 200:
        raise CodeParseError(f"Failed to list directory: {api_url} (status {resp.status_code})")
    files = resp.json()
    code_parts = []
    for f in files:
        if f['type'] == 'file' and f['name'].endswith('.py'):
            raw_url = GITHUB_RAW_URL + github_dir + '/' + f['name']
            file_resp = requests.get(raw_url)
            if file_resp.status_code == 200:
                code_parts.append(f"# File: {f['name']}\n" + file_resp.text)
            else:
                print(f"Failed to fetch {raw_url}: {file_resp.status_code}")
    return '\n\n'.join(code_parts)

def parse_code(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accepts:
        { "github_dir": "Solutions/GoogleCloudPlatformCDN/Data Connectors" }
    Downloads and concatenates all .py files in the GitHub directory as code input.
    """
    try:
        github_dir = request_data.get("github_dir", "")
        github_dir = github_dir.strip("/ ")
        if not github_dir:
            raise CodeParseError("github_dir must be a non-empty string")

        connector_name = github_dir.split("/")[1]
        print(f"Processing connector: {connector_name}, GitHub directory: {github_dir}")
        code = get_all_python_code_from_github_dir(github_dir)
        if not code:
            raise CodeParseError(f"No Python files found in GitHub directory: {github_dir}")
    
        return {
            "success": True,
            "connectorName": connector_name,
            "githubDir": github_dir,
            "apiDetails": process_function_app_code(connector_name, code)
        }
    except CodeParseError as cpe:
        print(f"CodeParseError in parse_code: {cpe}")
        return {
            "success": False,
            "connectorName": connector_name if 'connector_name' in locals() else "Unknown",
            "githubDir": github_dir if 'github_dir' in locals() else "Unknown",
            "error": str(cpe)
        }
    except Exception as e:
        print(f"Unexpected error in parse_code: {e}")
        return {
            "success": False,
            "connectorName": connector_name if 'connector_name' in locals() else "Unknown",
            "githubDir": github_dir if 'github_dir' in locals() else "Unknown",
            "error": "Failed to parse code"
        }
