import os
import asyncio
from typing import Any

import azure.functions as func
import json
import logging
from datetime import datetime, UTC
from ..generic_utilities.connection_slot_marker import ConnectionSlotMarker
from ..generic_utilities.sentinel import AzureSentinel

def get_error_response(response_data: dict[str, Any], status_code: int = 500) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({
            "success": False,
            "error": response_data,
            "timestamp": datetime.now(UTC).isoformat()
        }),
        status_code=status_code,
        headers={"Content-Type": "application/json"}
    )

def get_incident_id(req_body: dict[str, Any]) -> str:
    incident_id = None

    if 'incidentId' in req_body:
        incident_id = req_body['incidentId']

    elif 'incidentArmId' in req_body:
        incident_id = req_body['incidentArmId'].split('/')[-1]

    elif 'object' in req_body and 'properties' in req_body['object']:
        incident_id = req_body['object']['properties'].get('incidentId')

    if incident_id is None:
        raise Exception(
            "Failed getting incident id!"
        )
    return incident_id

def get_incident_title(req_body: dict[str, Any]) -> str | None:
    if 'title' in req_body:
        return req_body['title']
    elif 'incidentTitle' in req_body:
        return req_body['incidentTitle']
    elif 'object' in req_body and 'properties' in req_body['object']:
        return req_body['object']['properties'].get('title')
    else:
        return None

def get_incident_time(req_body: dict[str, Any]) -> datetime:
    if "incidentProperties" in req_body and "createdTimeUtc" in req_body["incidentProperties"]:
        return datetime.fromisoformat(req_body["incidentProperties"]["createdTimeUtc"].replace("Z", "+00:00"))
    else:
        logging.warning("No createdTimeUtc found in incident properties, using current time")
        return datetime.now(UTC)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Guardicore incident processing function triggered')

    req_body = req.get_json()

    if not req_body:
        return get_error_response(
            {"error": "No incident data provided"}, status_code=400
        )
    if "incidentProperties" in req_body and type(req_body["incidentProperties"]) is str:
        req_body["incidentProperties"] = json.loads(req_body["incidentProperties"])
    if "Entities" in req_body and type(req_body["Entities"]) is str:
        req_body["Entities"] = json.loads(req_body["Entities"])
        
    logging.info(f'Received incident data: {json.dumps(req_body, indent=2)}')
    relevant_ips = set()
    for entity in req_body.get('Entities', []):
        if entity.get('kind') == 'Ip':
            relevant_ips.add(entity.get('properties', {}).get('address'))
    relevant_ips = {ip for ip in relevant_ips if ip is not None}

    incident_id = get_incident_id(req_body)
    incident_time = get_incident_time(req_body)
    incident_title = get_incident_title(req_body)
    incident_title = f'{incident_title}, id: {incident_id} ({incident_time})'
    logging.info(f"Relevant IPs extracted: {relevant_ips}")

    slot_identifiers = ConnectionSlotMarker().mark_slot_for_fetching(
        incident_time, relevant_ips
    )

    if not slot_identifiers:
        return get_error_response(
            {"error": "No relevant IPs found in the incident data"}, status_code=400
        )

    azure_connection = AzureSentinel(
        workspace_id=os.environ.get('SentinelWorkspaceId', ''),
        workspace_key=os.environ.get('SentinelWorkspaceKey', ''),
        log_analytics_url=os.getenv('logAnalyticsUri', '')
    )
    for slot in slot_identifiers:
        identifier = slot['slot_id']
        data = {
            "incidentId": incident_id,
            "incidentTitle": incident_title,
            "incidentTime": incident_time.isoformat(),
            "slot_identifier": identifier,
            "relevantIPs": list(relevant_ips)
        }
        asyncio.run(
            azure_connection.post_data(body=json.dumps(data), log_type="GuardicoreProcessedIncidents")
        )
    logging.info(f"Created/updated slots for incident {incident_id}: {slot_identifiers}")

    return func.HttpResponse(
        json.dumps({
            "success": True,
            "message": "Incident processing started",
            "incidentId": incident_id,
            "incidentTitle": incident_title,
            "slotIdentifiers": slot_identifiers,
            "timestamp": datetime.now(UTC).isoformat()
        }),
        status_code=200,
        headers={"Content-Type": "application/json"}
    )
