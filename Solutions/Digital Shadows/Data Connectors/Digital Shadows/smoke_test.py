"""
Walking-skeleton smoke test for Phase 1 (GPB-658420).

What it does:
  1. Builds a single hardcoded record matching the skeleton DCR schema
     (TimeGenerated, App, Title) — see digitalshadowsARM.json.
  2. Uses DefaultAzureCredential to acquire a Logs Ingestion API token.
  3. POSTs the record to the configured DCE → DCR → DigitalShadows_V2_CL.
  4. Prints the HTTP status + a tip on where to verify it landed.

How to use (locally or inside the Function App's Kudu console):
  export DCE_URL='https://<dce-name>-xxxx.<region>.ingest.monitor.azure.com'
  export DCR_IMMUTABLE_ID='dcr-xxxxxxxxxxxxxxxx'
  export STREAM_NAME='Custom-DigitalShadows_V2_CL'
  python3 smoke_test.py

Then verify in Log Analytics:
  DigitalShadows_V2_CL
  | where Title startswith "[smoke]"
  | sort by TimeGenerated desc

NOTE: locally this uses your developer creds (az login). On the Function App
it uses the system-assigned Managed Identity. Either must have
'Monitoring Metrics Publisher' on the DCR.
"""
import datetime
import json
import os
import sys

import requests
from azure.identity import DefaultAzureCredential


def main():
    dce_url = os.environ['DCE_URL'].rstrip('/')
    dcr_id  = os.environ['DCR_IMMUTABLE_ID']
    stream  = os.environ['STREAM_NAME']

    record = {
        "TimeGenerated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "App":   "include",
        "Title": "[smoke] walking skeleton — Phase 1 GPB-658420",
    }
    body = json.dumps([record])

    token = DefaultAzureCredential().get_token("https://monitor.azure.com/.default").token

    uri = f"{dce_url}/dataCollectionRules/{dcr_id}/streams/{stream}?api-version=2023-01-01"
    resp = requests.post(
        uri,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json",
        },
        timeout=60,
    )

    print(f"POST {uri}")
    print(f"  status: {resp.status_code}")
    print(f"  body  : {resp.text or '(empty)'}")

    if resp.ok:
        print("\n✅  sent. Now check Log Analytics — note that ingestion can lag a few minutes:")
        print("    DigitalShadows_V2_CL | where Title startswith \"[smoke]\" | sort by TimeGenerated desc")
    else:
        print("\n❌  rejected. Common causes:")
        print("    403 → identity lacks 'Monitoring Metrics Publisher' on the DCR, or role hasn't propagated yet")
        print("    400 → record shape doesn't match the DCR's streamDeclaration columns")
        print("    404 → DCR_IMMUTABLE_ID or STREAM_NAME mismatch")
        sys.exit(1)


if __name__ == "__main__":
    main()
