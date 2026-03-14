import azure.functions as func
import json

from utils.client import get_brand_client

SUPPORTED_ACTIONS = ['entityRestore', 'eventRestore']
SUPPORTED_BRANDS = ['checkpoint', 'avanan']
_ACTION = 'restore'

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)

    brand = body.get('brand')
    host = body.get('host')
    client_id = body.get('clientId')
    client_secret = body.get('clientSecret')
    action = body.get('action')
    entity_type = body.get('entityType')
    entity_ids = body.get('entityIds', [])

    if brand not in SUPPORTED_BRANDS:
        return func.HttpResponse(f'Brand {brand} is not one of supported {SUPPORTED_BRANDS}',
                                 status_code=400)
    elif action not in SUPPORTED_ACTIONS:
        return func.HttpResponse(f'Action {action} is not one of support actionS {SUPPORTED_ACTIONS}',
                             status_code=400)

    client = get_brand_client(brand, host, client_id, client_secret)

    if action == 'entityRestore':
        if not entity_type:
            return func.HttpResponse(f'For entityAction action type, entityType must be specified'
                                     , status_code=400)
        args = [entity_ids, entity_type, _ACTION]
        _func = client.entity_action
    elif action == 'eventRestore':
        args = [entity_ids, _ACTION]
        _func = client.event_action

    try:
        res = _func(*args)
        return func.HttpResponse(json.dumps(res), status_code=200)
    except Exception as e:
        return func.HttpResponse(f'Failed to execute action {e}', status_code=500)

