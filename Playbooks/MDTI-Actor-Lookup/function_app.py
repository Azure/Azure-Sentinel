import requests
import logging
import json
import asyncio
import aiohttp
import nest_asyncio
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.function_name(name="MDTIActor")
@app.route(route="MDTIActor")
async def main_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    item = req.params.get('item')
    if not item:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            item = req_body.get('item')

    if not item:
        return func.HttpResponse(
            "Please pass an item on the query string or in the request body",
            status_code=400
        )

    combined_results = await main(item)
    return func.HttpResponse(json.dumps(combined_results), status_code=200)

client_id = "<MDTI_CLIENT_ID>"
client_secret = "<MDTI_CLIENT_SECRET>"
tenant_id = "<MDTI_TENANT_ID>"

def get_access_token(client_id, client_secret, tenant_id):
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default"
    }
    response = requests.post(url, headers=headers, data=data)
    
    # Log the response for debugging
    logging.info(f"Token response: {response.json()}")
    
    response.raise_for_status()
    return response.json()["access_token"]

# Generate a new access token
access_token = get_access_token(client_id, client_secret, tenant_id)
headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

def list_grab(item):
    services = f"https://graph.microsoft.com/beta/security/threatIntelligence/hosts/{item}/passivedns?$top=1000"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    artifact_list = []
    
    while services:
        response = requests.get(services, headers=headers)
        data = response.json()
        
        # Check if 'value' key exists in the response
        if 'value' in data:
            artifacts = data['value']
            artifact_ids = [item['artifact']['id'] for item in artifacts]
            artifact_list.extend(artifact_ids)
            logging.info(f"Fetched {len(artifact_ids)} artifacts, total so far: {len(artifact_list)}")
        else:
            logging.warning(f"'value' key not found in response: {data}")
            continue
        
        # Check for the presence of @odata.nextLink
        services = data.get('@odata.nextLink', None)
        if services:
            logging.info(f"Next link found: {services}")
        else:
            logging.info("No next link found, ending pagination.")
    
    return artifact_list

URL = "https://graph.microsoft.com/beta/security/threatIntelligence/hosts/{}/reputation"

def get_tasks(session, artifact_list):
    tasks = [session.get(URL.format(artifact_id), headers=headers, ssl=False) for artifact_id in artifact_list]
    return tasks

async def run_tasks(session, artifact_list):
    tasks = get_tasks(session, artifact_list)
    responses = await asyncio.gather(*tasks)
    results = [await response.json() for response in responses]
    return results

def combine_artifacts_with_marge(artifact_list, results):
    combined_results = []
    for artifact, homer in zip(artifact_list, results):
        if "rules" in homer:
            for bart in homer['rules']:
                if "name" in bart and bart["name"] == "Cyber Threat Intelligence":
                    description = bart['description']
                    if isinstance(description, str):
                        combined_entry = f"{description}, {artifact}"
                        combined_results.append(combined_entry)
                    elif isinstance(description, list):
                        for desc in description:
                            combined_entry = f"{desc}, {artifact}"
                            combined_results.append(combined_entry)
    return combined_results

async def main(item):
    artifact_list = list_grab(item)
    
    async with aiohttp.ClientSession() as session:
        results = await run_tasks(session, artifact_list)
    
    combined_results = combine_artifacts_with_marge(artifact_list, results)
    
    # Log the combined results
    logging.info(f"Combined results: {combined_results}")
    
    return combined_results

nest_asyncio.apply()

def condition(data):
    return "rules" in data and any(rule.get("name") == "Cyber Threat Intelligence" for rule in data["rules"])

async def fetch_all(session, url, condition):
    # Implementation of fetch_all function
    pass
