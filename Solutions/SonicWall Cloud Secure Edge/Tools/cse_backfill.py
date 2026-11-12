#!/usr/bin/env python3
"""Backfill SonicWall Cloud Secure Edge (CSE) events missing from Microsoft Sentinel.

The CSE events connector does not fetch events missed while it was failing, being
reconnected, or having its API key rotated. This tool fills such a gap:

1. Pull every CSE event in [--after, --before] from the CSE events API, in 1-hour windows.
2. Look up which of those events are already in the CSEEvents_CL table.
3. Send only the missing events, unchanged, to the connector's data collection rule (DCR),
   so backfilled rows are identical to rows from the connector.

Dry run is the default: nothing is sent unless --send is given. Designed for Azure Cloud
Shell (Bash), which provides Python 3, the Azure CLI, and the signed-in identity. Uses only
the Python standard library and the Azure CLI.

The DCR is found from the workspace (--workspace): the tool reads the CSE connector's poller and
uses the DCR it sends to. If the workspace has CSE pollers that send to different DCRs, the tool
lists them and stops; choose one with --dcr-id. Before sending, it checks that the CSE
organization of the pulled events is already in the workspace, so events are not sent to
another customer's workspace by mistake (--allow-new-org overrides this).

Requirements for the signed-in identity:
- Microsoft Sentinel Reader on the workspace (to read the connector), and Reader on the
  workspace resource group (to find the DCR). Not needed with --dcr-id.
- Monitoring Metrics Publisher on the DCR (to send events).
- Log Analytics Reader on the workspace (to check which events are already present).

The CSE API key is read from the CSE_API_TOKEN environment variable, or asked for without
being shown. It is never written to disk or printed.

Example (Azure Cloud Shell):
    python3 cse_backfill.py --workspace <workspace resource ID> \\
        --after 2026-10-28T16:40:00Z --before 2026-10-28T17:10:00Z
    python3 cse_backfill.py --workspace <workspace resource ID> \\
        --after 2026-10-28T16:40:00Z --before 2026-10-28T17:10:00Z --send
"""

import argparse
import datetime
import getpass
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

VERSION = "1.2.0"
CSE_HOSTS = {"us": "https://net.banyanops.com", "eu": "https://eucc.console.banyanops.com"}
EVENTS_PATH = "/api/v1/events"
TABLE = "CSEEvents_CL"
STREAM = "Custom-CSEEventsInput"
PAGE_SIZE = 1000
# Requests over long ranges can time out (HTTP 504) on busy tenants; 1-hour windows did not.
WINDOW_MS = 3_600_000
MIN_WINDOW_MS = 60_000
MAX_RETRIES = 5
SPLIT_RETRIES = 2
REQUEST_TIMEOUT = 90
# Events sent more than about 48 hours after they occurred are stored with TimeGenerated set
# to the ingestion time, so they are refused unless --allow-old is given.
MAX_AGE_MS = 47 * 3600 * 1000
# The Logs Ingestion API accepts up to 1 MB per call.
MAX_BATCH_BYTES = 900_000
LOOKUP_CHUNK = 200
DCR_API_VERSION = "2023-03-11"
INGESTION_API_VERSION = "2023-01-01"
QUERY_API_VERSION = "2017-10-01"
CONNECTOR_API_VERSION = "2024-09-01"
# connectorUiConfig id of the SonicWall CSE connector; its pollers name it in connectorDefinitionName.
CONNECTOR_DEFINITION = "SonicWallCSEEvents"
# Event IDs are inserted into a KQL query, so only canonical UUIDs are accepted.
EVENT_ID_PATTERN = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
# Resource IDs are inserted into ARM URLs, so only these exact shapes are accepted: a subscription
# GUID, and resource group and resource names without "/", "?", "#", "&", "%", spaces, or quotes.
_GUID = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
_NAME = r"[A-Za-z0-9._()-]{1,90}"
_SCOPE = rf"/subscriptions/{_GUID}/resourceGroups/{_NAME}/providers/"
WORKSPACE_ID_PATTERN = re.compile(rf"{_SCOPE}Microsoft\.OperationalInsights/workspaces/{_NAME}", re.IGNORECASE)
DCR_ID_PATTERN = re.compile(rf"{_SCOPE}Microsoft\.Insights/dataCollectionRules/{_NAME}", re.IGNORECASE)
DCE_ID_PATTERN = re.compile(rf"{_SCOPE}Microsoft\.Insights/dataCollectionEndpoints/{_NAME}", re.IGNORECASE)
# The DCR's ingestion endpoint (read from Azure) must be an Azure Monitor ingestion host.
INGESTION_ENDPOINT_PATTERN = re.compile(r"https://[A-Za-z0-9.-]+\.ingest\.monitor\.azure\.com/?", re.IGNORECASE)


# Time helpers

def parse_time(value):
    """Accept epoch milliseconds or ISO 8601 (UTC if no offset); return epoch milliseconds."""
    if value.isdigit():
        return int(value)
    parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return int(parsed.timestamp() * 1000)


def iso(epoch_ms):
    moment = datetime.datetime.fromtimestamp(epoch_ms / 1000, tz=datetime.timezone.utc)
    return moment.isoformat(timespec="seconds").replace("+00:00", "Z")


# Azure CLI helpers

def checked_id(value, pattern, label):
    """Return value if it is a resource ID of the expected shape; otherwise stop."""
    if not value or not pattern.fullmatch(value):
        sys.exit(f"Not a valid {label} resource ID: {value!r}")
    return value


def az_command():
    """Return the command that starts the Azure CLI, without a shell.

    On Windows, az is a batch file (az.cmd) that runs the CLI's bundled Python with -IBm azure.cli;
    a batch file can only be run through cmd.exe, which would interpret characters such as "&" in
    the arguments. So the bundled Python is called directly, as az.cmd does.
    """
    path = shutil.which("az")
    if not path:
        sys.exit("The Azure CLI (az) was not found. Install it, or run the tool in Azure Cloud Shell.")
    if path.lower().endswith((".cmd", ".bat")):
        python = os.path.normpath(os.path.join(os.path.dirname(path), "..", "python.exe"))
        if not os.path.isfile(python):
            sys.exit(f"The Azure CLI's Python was not found next to {path}.")
        return [python, "-IBm", "azure.cli"]
    return [path]


AZ = None


def az(*args):
    """Run an Azure CLI command and return its JSON output."""
    global AZ
    AZ = AZ or az_command()
    environment = dict(os.environ, AZ_INSTALLER=os.environ.get("AZ_INSTALLER", "MSI")) if len(AZ) > 1 else None
    result = subprocess.run([*AZ, *args, "-o", "json"], capture_output=True, text=True, env=environment)
    if result.returncode != 0:
        sys.exit(f"Azure CLI failed ({' '.join(args[:2])}): {result.stderr.strip()}")
    return json.loads(result.stdout) if result.stdout.strip() else None


def arm_get(resource_id, api_version):
    return az("rest", "--method", "get", "--url", f"https://management.azure.com{resource_id}?api-version={api_version}")


def workspace_query(workspace_id, kql):
    """Run a KQL query on the workspace and return rows as dictionaries."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
        json.dump({"query": kql, "timespan": "P30D"}, handle)
        body_path = handle.name
    try:
        url = f"https://management.azure.com{workspace_id}/query?api-version={QUERY_API_VERSION}"
        table = az("rest", "--method", "post", "--url", url, "--body", f"@{body_path}")["tables"][0]
    finally:
        os.remove(body_path)
    names = [column["name"] for column in table["columns"]]
    return [dict(zip(names, row)) for row in table["rows"]]


def arm_list(path, api_version):
    """Return every item of an ARM list call, following nextLink."""
    items, url = [], f"https://management.azure.com{path}?api-version={api_version}"
    while url:
        page = az("rest", "--method", "get", "--url", url)
        items.extend(page.get("value", []))
        url = page.get("nextLink")
    return items


def find_dcr(workspace_id):
    """Return the resource ID of the DCR that the workspace's CSE connector sends to."""
    connectors = arm_list(f"{workspace_id}/providers/Microsoft.SecurityInsights/dataConnectors", CONNECTOR_API_VERSION)
    pollers = [c for c in connectors if c.get("kind") == "RestApiPoller"
               and c.get("properties", {}).get("connectorDefinitionName") == CONNECTOR_DEFINITION]
    if not pollers:
        sys.exit("No SonicWall CSE connector found in this workspace. Check the workspace, or give the DCR with --dcr-id.")
    immutable_ids = {}
    for poller in pollers:
        immutable_id = (poller["properties"].get("dcrConfig") or {}).get("dataCollectionRuleImmutableId")
        immutable_ids.setdefault(immutable_id, []).append(poller["name"])
    # The connector creates its DCR in the workspace resource group; search the subscription if not found there.
    parts = workspace_id.split("/")
    found = {}
    for scope in ("/".join(parts[:5]), "/".join(parts[:3])):
        rules = arm_list(f"{scope}/providers/Microsoft.Insights/dataCollectionRules", DCR_API_VERSION)
        found = {rule["properties"].get("immutableId"): rule["id"] for rule in rules}
        if all(immutable_id in found for immutable_id in immutable_ids):
            break
    found = {key: value for key, value in found.items() if value and DCR_ID_PATTERN.fullmatch(value)}
    if len(immutable_ids) > 1:
        print("This workspace has SonicWall CSE connectors that send to different DCRs:")
        for immutable_id, names in sorted(immutable_ids.items(), key=lambda item: str(item[0])):
            print(f"  {found.get(immutable_id, f'DCR not found ({immutable_id})')}  (connector {', '.join(names)})")
        sys.exit("Choose the DCR of the connector that uses this CSE API key and run again with --dcr-id.")
    immutable_id = next(iter(immutable_ids))
    if immutable_id not in found:
        sys.exit(f"The CSE connector's DCR ({immutable_id}) was not found. The signed-in identity needs Reader on the "
                 "workspace resource group, or give the DCR with --dcr-id.")
    return found[immutable_id]


def new_organizations(workspace_id, events):
    """Return the CSE organization IDs of the events that have no events in the workspace in 30 days.

    Returns nothing when the workspace has no CSE events yet (a first backfill after connecting).
    """
    pulled = {event.get("org_id") for event in events if event.get("org_id")}
    rows = workspace_query(workspace_id, f"{TABLE} | where TimeGenerated > ago(30d) | distinct OrgId")
    known = {row["OrgId"] for row in rows if row.get("OrgId")}
    return sorted(pulled - known) if known else []


def resolve_dcr(dcr_id):
    """Return the ingestion URL and the workspace resource ID for the connector's DCR."""
    dcr = arm_get(dcr_id, DCR_API_VERSION)
    properties = dcr["properties"]
    endpoint = (properties.get("endpoints") or {}).get("logsIngestion")
    if not endpoint:
        dce_id = properties.get("dataCollectionEndpointId")
        if not dce_id:
            sys.exit("The DCR has no logs ingestion endpoint and no data collection endpoint.")
        dce_id = checked_id(dce_id, DCE_ID_PATTERN, "data collection endpoint")
        endpoint = arm_get(dce_id, DCR_API_VERSION)["properties"]["logsIngestion"]["endpoint"]
    if not INGESTION_ENDPOINT_PATTERN.fullmatch(endpoint or ""):
        sys.exit(f"The DCR's ingestion endpoint is not an Azure Monitor ingestion URL: {endpoint!r}; nothing was sent.")
    endpoint = endpoint.rstrip("/")
    if not re.fullmatch(r"dcr-[0-9a-fA-F]{32}", properties.get("immutableId") or ""):
        sys.exit("The DCR has no valid immutable ID; nothing was sent.")
    if STREAM not in properties.get("streamDeclarations", {}):
        sys.exit(f"The DCR does not declare the stream {STREAM}; check that it is the CSE connector's DCR.")
    workspaces = (properties.get("destinations") or {}).get("logAnalytics") or []
    if not workspaces:
        sys.exit("The DCR has no Log Analytics destination.")
    url = (f"{endpoint}/dataCollectionRules/{properties['immutableId']}/streams/{STREAM}"
           f"?api-version={INGESTION_API_VERSION}")
    return url, checked_id(workspaces[0].get("workspaceResourceId"), WORKSPACE_ID_PATTERN, "DCR destination workspace")


# CSE events API

def get_page(base_url, key, params, retries, give_up):
    """Fetch one page; retry on HTTP 429 and 5xx. Return None if retries run out and give_up is False."""
    url = base_url + EVENTS_PATH + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        request = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                data = json.loads(response.read().decode("utf-8")).get("data")
                if not isinstance(data, list):
                    sys.exit("Unexpected response from the CSE events API (no 'data' list).")
                return data
        except urllib.error.HTTPError as error:
            if error.code == 401:
                sys.exit("The CSE API key was not accepted (HTTP 401).")
            if error.code != 429 and error.code < 500:
                sys.exit(f"CSE events API returned HTTP {error.code}.")
            wait = int(error.headers.get("Retry-After", 2 ** attempt)) if error.code == 429 else 2 ** attempt
        except (urllib.error.URLError, TimeoutError):
            wait = 2 ** attempt
        time.sleep(wait)
    if give_up:
        sys.exit(f"CSE events API still failing after {retries} attempts.")
    return None


def pull_window(base_url, key, after, before):
    """Page one window oldest first; halve it if it keeps failing with server errors."""
    splittable = before - after >= 2 * MIN_WINDOW_MS
    events, skip = [], 0
    while True:
        params = {"after": after, "before": before, "order": "ASC", "limit": PAGE_SIZE, "skip": skip}
        page = get_page(base_url, key, params, SPLIT_RETRIES if splittable else MAX_RETRIES, not splittable)
        if page is None:
            middle = (after + before) // 2
            return pull_window(base_url, key, after, middle) + pull_window(base_url, key, middle + 1, before)
        events.extend(page)
        if len(page) < PAGE_SIZE:
            return events
        skip += PAGE_SIZE


def pull(base_url, key, after, before):
    """Return every event with a storage time in [after, before], both inclusive, without duplicates."""
    events, seen, start = [], set(), after
    while start <= before:
        end = min(start + WINDOW_MS - 1, before)
        for event in pull_window(base_url, key, start, end):
            if event.get("id") and event["id"] not in seen:
                seen.add(event["id"])
                events.append(event)
        start = end + 1
    return events


# Sentinel side

def present_ids(workspace_id, ids):
    """Return the IDs already in the table. Refuses IDs that are not UUIDs."""
    invalid = [event_id for event_id in ids if not EVENT_ID_PATTERN.fullmatch(str(event_id))]
    if invalid:
        sys.exit(f"Stopped: {len(invalid)} events from the CSE API have an ID that is not a UUID; nothing was sent.")
    found = set()
    ids = sorted(ids)
    for start in range(0, len(ids), LOOKUP_CHUNK):
        chunk = ", ".join(f"'{event_id}'" for event_id in ids[start:start + LOOKUP_CHUNK])
        rows = workspace_query(workspace_id, f"{TABLE} | where EventId in ({chunk}) | distinct EventId")
        found.update(row["EventId"] for row in rows)
    return found


def batches(events):
    batch, size = [], 2
    for event in events:
        encoded = len(json.dumps(event, separators=(",", ":")).encode("utf-8")) + 1
        if batch and size + encoded > MAX_BATCH_BYTES:
            yield batch
            batch, size = [], 2
        batch.append(event)
        size += encoded
    if batch:
        yield batch


def send(url, batch):
    """Send one batch to the Logs Ingestion API; retry on HTTP 429 and 5xx."""
    token = az("account", "get-access-token", "--resource", "https://monitor.azure.com")["accessToken"]
    body = json.dumps(batch, separators=(",", ":")).encode("utf-8")
    for attempt in range(MAX_RETRIES):
        request = urllib.request.Request(url, data=body, method="POST",
                                         headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                return response.status
        except urllib.error.HTTPError as error:
            if error.code == 403:
                sys.exit("Sending was refused (HTTP 403). The signed-in identity needs the Monitoring "
                         "Metrics Publisher role on the DCR; a new role assignment can take a few minutes to apply.")
            if error.code != 429 and error.code < 500:
                sys.exit(f"Logs Ingestion API returned HTTP {error.code}: {error.read().decode('utf-8', 'replace')[:300]}")
            time.sleep(int(error.headers.get("Retry-After", 2 ** attempt)))
    sys.exit(f"Logs Ingestion API still failing after {MAX_RETRIES} attempts.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--workspace", help="Resource ID of the Sentinel workspace; the CSE connector's DCR is found from it")
    target.add_argument("--dcr-id", help="Resource ID of the CSE connector's data collection rule")
    parser.add_argument("--after", required=True, help="Start of the gap, ISO 8601 UTC or epoch ms (inclusive)")
    parser.add_argument("--before", required=True, help="End of the gap, ISO 8601 UTC or epoch ms (inclusive)")
    parser.add_argument("--region", choices=sorted(CSE_HOSTS), default="us", help="CSE Command Center region (default: us)")
    parser.add_argument("--send", action="store_true", help="Send the missing events (default: dry run)")
    parser.add_argument("--allow-old", action="store_true",
                        help="Also send events older than 47 hours; Sentinel sets their TimeGenerated to the send time")
    parser.add_argument("--allow-new-org", action="store_true",
                        help="Send even if the events' CSE organization has no events in the workspace yet")
    parser.add_argument("--version", action="version", version=f"cse_backfill {VERSION}")
    args = parser.parse_args()

    after, before = parse_time(args.after), parse_time(args.before)
    now = int(time.time() * 1000)
    if after > before:
        sys.exit("--after must not be later than --before.")
    if after < now - 14 * 86400000:
        print("Note: CSE keeps events for 14 days; older events can no longer be backfilled.")

    key = os.environ.get("CSE_API_TOKEN", "").strip() or getpass.getpass("CSE API key: ").strip()
    if not key:
        sys.exit("No CSE API key given.")

    # Check the resource IDs before any Azure call.
    if args.workspace:
        checked_id(args.workspace, WORKSPACE_ID_PATTERN, "workspace")
    else:
        checked_id(args.dcr_id, DCR_ID_PATTERN, "data collection rule")
    dcr_id = args.dcr_id or find_dcr(args.workspace)
    url, workspace_id = resolve_dcr(dcr_id)
    if args.workspace and workspace_id.lower() != args.workspace.lower():
        sys.exit("The connector's DCR sends to a different workspace than --workspace; nothing was sent.")
    print(f"DCR: {dcr_id}")
    events = pull(CSE_HOSTS[args.region], key, after, before)
    present = present_ids(workspace_id, {event["id"] for event in events}) if events else set()
    missing = [event for event in events if event["id"] not in present]

    print(f"Window: {iso(after)} to {iso(before)}")
    print(f"CSE events: {len(events)}  Already in Sentinel: {len(present)}  Missing: {len(missing)}")
    if not missing:
        print("Nothing to backfill.")
        return
    created = sorted(event["created_at"] for event in missing)
    print(f"Missing events occurred from {iso(created[0])} to {iso(created[-1])}")

    old = [event for event in missing if event["created_at"] < now - MAX_AGE_MS]
    if old:
        print(f"Warning: {len(old)} missing events are older than 47 hours. If sent, Sentinel stores them with "
              f"TimeGenerated set to the send time; the EventTime column of the CSEEvents parser keeps the real time.")
        if args.send and not args.allow_old:
            sys.exit("Not sent. Add --allow-old to send them anyway.")

    new_orgs = new_organizations(workspace_id, missing)
    if new_orgs:
        print(f"Warning: the CSE organization of these events ({', '.join(new_orgs)}) has no events in this "
              "workspace in the last 30 days. Check that the API key and the workspace belong to the same customer.")
        if args.send and not args.allow_new_org:
            sys.exit("Not sent. Add --allow-new-org to send them anyway.")

    planned = list(batches(missing))
    if not args.send:
        print(f"Dry run: nothing sent. Add --send to send {len(missing)} events in {len(planned)} batches.")
        return
    for number, batch in enumerate(planned, 1):
        status = send(url, batch)
        print(f"Batch {number} of {len(planned)}: {len(batch)} events, HTTP {status}")
    print(f"Sent {len(missing)} events. Wait 10 minutes, then run the same command without --send: "
          f"it should report Missing: 0.")


if __name__ == "__main__":
    main()
