import json
import logging
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Mock Contoso Incident API — List Incidents endpoint.

    Mimics a real security product API that returns only a list of incident
    identifiers for a given time window.  The CCF nested poller calls this
    endpoint first (call 1) and then calls GetIncidentDetails (call 2) once
    per returned incidentId to retrieve the full record.

    Query parameters (accepted but not filtered on — all incidents are
    returned on every call so the demo always produces visible data):
        startTime  ISO 8601 datetime
        endTime    ISO 8601 datetime

    Response shape (must match the eventsJsonPaths "$.incidents" in the
    CCF PollerConfig):
        {
            "incidents": [
                { "incidentId": "INC-001" },
                ...
            ]
        }
    """
    start_time = req.params.get("startTime", "(not provided)")
    end_time   = req.params.get("endTime",   "(not provided)")

    auth_header = req.headers.get("x-functions-key", "(missing)")
    logging.info(
        "ContosoMockApi ListIncidents: startTime=%s endTime=%s x-functions-key=%s",
        start_time, end_time, "(present)" if auth_header != "(missing)" else "(missing)",
    )
    logging.info("ContosoMockApi ListIncidents headers: %s", dict(req.headers))

    # Fixed set of five incidents — every poll returns all five so the
    # demo produces data regardless of the query window.
    incidents = [
        {"incidentId": "INC-001"},
        {"incidentId": "INC-002"},
        {"incidentId": "INC-003"},
        {"incidentId": "INC-004"},
        {"incidentId": "INC-005"},
    ]

    return func.HttpResponse(
        body=json.dumps({"incidents": incidents}),
        mimetype="application/json",
        status_code=200,
    )
