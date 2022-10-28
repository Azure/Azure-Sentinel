#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Usage: $0 <name-for-your-app>"
    exit 1
fi
appName=$1

funcName=$appName
funcUrl=https://$funcName.azurewebsites.net

# uncomment the following if you receive a Graph API error
#tenantId=<your-tenant-id>
#az login --tenant $tenantId

# register a new AAD app, and configure it
appId=$(az ad app create --display-name $appName --web-home-page-url $funcUrl --sign-in-audience AzureADMyOrg --query appId --enable-id-token-issuance true | sed 's/.\(.*\)/\1/' | sed 's/\(.*\)./\1/')
secret=$(az ad app credential reset --id $appId --append --query password | sed 's/.\(.*\)/\1/' | sed 's/\(.*\)./\1/')
objId=$(az ad app show --id $appId --query id | sed 's/.\(.*\)/\1/' | sed 's/\(.*\)./\1/')
az rest --method PATCH --uri "https://graph.microsoft.com/v1.0/applications/$objId" --headers 'Content-Type=application/json' --body "{\"web\":{\"redirectUris\":[\"$funcUrl/.auth/login/aad/callback\"]}}"
az rest --method PATCH --uri "https://graph.microsoft.com/v1.0/applications/$objId" --headers 'Content-Type=application/json' --body '{	"requiredResourceAccess": [		{			"resourceAppId":"cfa8b339-82a2-471a-a3c9-0fc0be7a4093",			"resourceAccess": [				{					"id": "f53da476-18e3-4152-8e01-aec403e6edc0",					"type": "Scope"				}			]		},		{			"resourceAppId":"00000003-0000-0000-c000-000000000000",			"resourceAccess": [				{					"id": "e1fe6dd8-ba31-4d61-89e7-88639da4683d",					"type": "Scope"				}			]		}	]}'

echo "function app name: $funcName"
echo "AAD App ID: $appId"
echo "AAD App Secret: $secret"
