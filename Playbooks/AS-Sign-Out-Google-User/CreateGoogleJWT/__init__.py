import logging
import azure.functions as func
import time
from jwt import encode


def create_google_jwt(iss: str, scope: str, aud: str, private_key_id: str, private_key: str) -> str:
    iat = time.time()
    exp = iat + 3600
    payload = {'iss': iss,
               'scope': scope,
               'aud': aud,
               'iat': iat,
               'exp': exp}
    additional_headers = {'kid': private_key_id}
    signed_jwt = encode(payload, private_key, headers=additional_headers, algorithm='RS256')
    return signed_jwt


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Please pass 'iss', 'scope', 'aud', 'private_key_id', and 'private_key' in the request body.",
            status_code=400
        )
    
    iss = req_body.get('iss')
    scope = req_body.get('scope')
    aud = req_body.get('aud')
    private_key_id = req_body.get('private_key_id')
    private_key = req_body.get('private_key')

    if all([iss, scope, aud, private_key_id, private_key]):
        jwt = create_google_jwt(iss, scope, aud, private_key_id, private_key)
        return func.HttpResponse(jwt)
    else:
        return func.HttpResponse(
             "Please ensure all parameters ('iss', 'scope', 'aud', 'private_key_id', and 'private_key') are in the request body.",
             status_code=400
        )
