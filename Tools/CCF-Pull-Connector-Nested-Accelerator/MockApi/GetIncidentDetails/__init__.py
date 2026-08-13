import json
import logging
import azure.functions as func


# ---------------------------------------------------------------------------
# Mock incident data store.
# In a real API this data would come from a database.  Here it is hardcoded
# so the demo works without any external dependencies.
# The shape of each record must match the DCR transformKql projection:
#   IncidentId, Title, Severity, Status, createdAt, affectedUser, sourceIp
# ---------------------------------------------------------------------------
INCIDENTS: dict = {
    "INC-001": {
        "incidentId":    "INC-001",
        "title":         "Suspicious login attempt",
        "severity":      "High",
        "status":        "Active",
        "createdAt":     "2026-05-30T14:22:00Z",
        "affectedUser":  "alice@contoso.com",
        "sourceIp":      "198.51.100.42",
    },
    "INC-002": {
        "incidentId":    "INC-002",
        "title":         "Malware detection on endpoint",
        "severity":      "Critical",
        "status":        "Investigating",
        "createdAt":     "2026-05-30T15:07:00Z",
        "affectedUser":  "bob@contoso.com",
        "sourceIp":      "10.0.0.55",
    },
    "INC-003": {
        "incidentId":    "INC-003",
        "title":         "Data exfiltration attempt",
        "severity":      "High",
        "status":        "Active",
        "createdAt":     "2026-05-30T16:44:00Z",
        "affectedUser":  "carol@contoso.com",
        "sourceIp":      "203.0.113.17",
    },
    "INC-004": {
        "incidentId":    "INC-004",
        "title":         "Privilege escalation detected",
        "severity":      "Medium",
        "status":        "Resolved",
        "createdAt":     "2026-05-30T17:31:00Z",
        "affectedUser":  "dave@contoso.com",
        "sourceIp":      "192.168.1.88",
    },
    "INC-005": {
        "incidentId":    "INC-005",
        "title":         "Port scan detected",
        "severity":      "Low",
        "status":        "Closed",
        "createdAt":     "2026-05-30T18:15:00Z",
        "affectedUser":  "eve@contoso.com",
        "sourceIp":      "172.16.0.22",
    },
}


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Mock Contoso Incident API — Get Incident Details endpoint.

    Mimics the second call in a nested API pattern.  The CCF nested poller
    extracts each incidentId from the ListIncidents response and calls this
    endpoint once per ID to retrieve the full record.

    Route parameter:
        incidentId  The incident identifier returned by ListIncidents
                    (e.g. INC-001)

    Response shape (matched by eventsJsonPaths "$" in the CCF PollerConfig):
        {
            "incidentId":   "INC-001",
            "title":        "...",
            "severity":     "...",
            "status":       "...",
            "createdAt":    "...",
            "affectedUser": "...",
            "sourceIp":     "..."
        }
    """
    incident_id = req.route_params.get("incidentId", "")

    auth_header = req.headers.get("x-functions-key", "(missing)")
    logging.info(
        "ContosoMockApi GetIncidentDetails: incidentId=%s x-functions-key=%s",
        incident_id, "(present)" if auth_header != "(missing)" else "(missing)",
    )
    logging.info("ContosoMockApi GetIncidentDetails headers: %s", dict(req.headers))

    if incident_id not in INCIDENTS:
        logging.warning(
            "ContosoMockApi GetIncidentDetails: unknown incidentId=%s", incident_id
        )
        return func.HttpResponse(
            body=json.dumps({"error": f"Incident '{incident_id}' not found."}),
            mimetype="application/json",
            status_code=404,
        )

    return func.HttpResponse(
        body=json.dumps(INCIDENTS[incident_id]),
        mimetype="application/json",
        status_code=200,
    )
