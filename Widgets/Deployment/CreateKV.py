from argparse import ArgumentParser
from azure.identity import InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
import json
import hashlib

template = '''{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "keyVaultName": {
      "type": "string",
      "metadata": {
        "description": "The name of the key vault to create."
      }
    }
  },
  "variables": {
    "SentinelFirstAppId": "df410494-9bdd-4bbe-997f-51bab37e3d91",
    "SentinelTenantId": "72f988bf-86f1-41af-91ab-2d7cd011db47"
  },
  "resources": [
    {
      "type": "Microsoft.KeyVault/vaults",
      "name": "[parameters('keyVaultName')]",
      "apiVersion": "2022-11-01",
      "location": "[resourceGroup().location]",
      "properties": {
        "sku": {
          "family": "A",
          "name": "Standard"
        },
        "tenantId": "[subscription().tenantId]",
        "accessPolicies": [
          {
            "tenantId": "[variables('SentinelTenantId')]",
            "objectId": "[variables('SentinelFirstAppId')]",
            "permissions": {
              "keys": [],
              "secrets": [
                "get",
                "list"
              ],
              "certificates": []
            }
          }
        ],
        "enabledForDeployment": true,
        "enableSoftDelete": false
      }
    }
  ],
  "outputs": {},
  "functions": []
}'''

def create_kv_name_from_workspace_id(workspace_id):
    hash = hashlib.sha256(workspace_id.encode())
    uniqueHash = hash.digest().hex()
    return f'widgets-{uniqueHash[:16]}'

def main(subscription_id, resource_group_name, workspace_id, print_kv_name = False):
    credential = InteractiveBrowserCredential()

    client = ResourceManagementClient(credential, subscription_id)
    kv_name = create_kv_name_from_workspace_id(workspace_id)

    print(f"Key vault name: '{kv_name}'")
    if(print_kv_name):
        return
    
    deployment_properties = {
        'properties': {
            'mode': DeploymentMode.incremental,
            'template': json.loads(template),
            'parameters': {
                'keyVaultName': {
                    'value': kv_name
                }
            }
        }    
    }

    deployment_name = f'keyvault-deployment-{kv_name}'


    deployment = client.deployments.begin_create_or_update(
        resource_group_name,
        deployment_name,
        deployment_properties
    )

    print(f"Deployment for kv - '{kv_name}' started.")
    print("Please wait until deployment is finished...")
    deployment.wait()
    print("Deployment finished.")

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--subscription-id', required=True)
    parser.add_argument('--resource-group-name', required=True)
    parser.add_argument('--workspace-id', required=True)
    parser.add_argument('--print_kv_name', required=False)
    args = parser.parse_args()

    main(args.subscription_id, args.resource_group_name, args.workspace_id, args.print_kv_name)
