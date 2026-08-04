import json

with open('Solutions/ZoomReports/Data Connectors/ZoomReports_ccf/PollingConfig.json', 'r') as f:
    connectors = json.load(f)

new_auth = {
    "type": "OAuth2",
    "ClientId": "[[parameters('ClientId')]",
    "ClientSecret": "[[parameters('ClientSecret')]",
    "GrantType": "client_credentials",
    "TokenEndpoint": "[[concat(parameters('TokenBaseUrl'),'?grant_type=account_credentials&account_id=',parameters('AccountId'))]",
    "TokenEndpointHeaders": {
        "Content-Type": "application/x-www-form-urlencoded"
    }
}

for c in connectors:
    c['properties']['auth'] = new_auth

with open('Solutions/ZoomReports/Data Connectors/ZoomReports_ccf/PollingConfig.json', 'w') as f:
    json.dump(connectors, f, indent=2)

print(f'Updated {len(connectors)} connectors to OAuth2 auth type')
