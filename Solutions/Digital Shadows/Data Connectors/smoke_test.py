"""
Walking-skeleton smoke test for Phase 1 (GPB-658420).

What it does:
  1. Builds TWO records that exercise the full DCR schema:
       - record 1: incident-shaped  → IncidentId set, AlertId omitted
       - record 2: alert-shaped     → AlertId set, IncidentId omitted
     This proves both id branches and that all 22 columns are accepted.
  2. Uses DefaultAzureCredential to acquire a Logs Ingestion API token.
  3. POSTs the records to the configured DCE → DCR → DigitalShadows_V2_CL.
  4. Prints the HTTP status + the KQL to verify in Log Analytics.

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


def _now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _common_fields(kind):
    """Fields shared by both shapes — exercises every non-id column."""
    return {
        "TimeGenerated":            _now_iso(),
        "App":                       "include",
        "Title":                     f"[smoke] {kind} — Phase 1 GPB-658420",
        "TimeRaised":                _now_iso(),
        "TimeUpdated":               _now_iso(),
        "Classification":            "exposed-credential",
        "RiskLevel":                 "high",
        "RiskAssessmentRiskLevel":   "high",
        "GreyMatterLink":            "https://greymatter.myreliaquest.com/test/smoke",
        "Assets":                    "example.com,1.2.3.4",
        "Description":               "smoke-test description",
        "ImpactDescription":         "smoke-test impact",
        "Mitigation":                "smoke-test mitigation",
        "RiskFactors":               "credential-exposure",
        "Comments":                  "[]",
        "PortalId":                  "smoke-portal-1",
        "Status":                    "unread",
        "TriageId":                  "triage-smoke-1",
        "TriageRaisedTime":          _now_iso(),
        "TriageUpdatedTime":         _now_iso(),
    }


def main():
    dce_url = os.environ['DCE_URL'].rstrip('/')
    dcr_id  = os.environ['DCR_IMMUTABLE_ID']
    stream  = os.environ['STREAM_NAME']

    incident_row = _common_fields("incident-shaped")
    incident_row["IncidentId"] = 424242

    alert_row = _common_fields("alert-shaped")
    alert_row["AlertId"] = "alert-smoke-7777"

    body = json.dumps([incident_row, alert_row])

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
    print(f"  sent  : {len(body)} bytes, 2 records (1 incident-shaped, 1 alert-shaped)")

    if resp.ok:
        print("\n✅  sent. Verify in Log Analytics (ingestion lag ~2-5 min):")
        print("    DigitalShadows_V2_CL")
        print('    | where Title startswith "[smoke]"')
        print("    | sort by TimeGenerated desc")
        print("    | project TimeGenerated, App, Title, IncidentId, AlertId, GreyMatterLink")
    else:
        print("\n❌  rejected. Common causes:")
        print("    403 → identity lacks 'Monitoring Metrics Publisher' on the DCR, or role hasn't propagated yet")
        print("    400 → record shape doesn't match the DCR's streamDeclaration columns")
        print("    404 → DCR_IMMUTABLE_ID or STREAM_NAME mismatch")
        sys.exit(1)


if __name__ == "__main__":
    main()
