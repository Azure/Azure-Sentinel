import re

with open('Solutions/ZoomReports/Package/mainTemplate.json', 'r', encoding='utf-8') as f:
    content = f.read()

old_auth = '''"auth": {
                  "type": "JwtToken",
                  "TokenEndpoint": "[[concat(parameters('TokenBaseUrl'),'?grant_type=account_credentials&account_id=',parameters('AccountId'))]",
                  "IsJsonRequest": false,
                  "Headers": {
                    "Content-Type": "application/x-www-form-urlencoded"
                  },
                  "JwtTokenJsonPath": "$.access_token",
                  "NoAccessTokenPrepend": false,
                  "TokenEndpointHttpMethod": "POST",
                  "UserTokenPrepend": "Basic",
                  "UserToken": "[[base64(concat(parameters('ClientId'),':',parameters('ClientSecret')))]"
                },'''

new_auth = '''"auth": {
                  "type": "OAuth2",
                  "ClientId": "[[parameters('ClientId')]",
                  "ClientSecret": "[[parameters('ClientSecret')]",
                  "GrantType": "client_credentials",
                  "TokenEndpoint": "[[concat(parameters('TokenBaseUrl'),'?grant_type=account_credentials&account_id=',parameters('AccountId'))]",
                  "TokenEndpointHeaders": {
                    "Content-Type": "application/x-www-form-urlencoded"
                  }
                },'''

count = content.count(old_auth)
updated = content.replace(old_auth, new_auth)

with open('Solutions/ZoomReports/Package/mainTemplate.json', 'w', encoding='utf-8') as f:
    f.write(updated)

print(f'Replaced {count} JwtToken auth blocks with OAuth2 in mainTemplate.json')
