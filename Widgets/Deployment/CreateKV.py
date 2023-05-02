from argparse import ArgumentParser
from azure.identity import InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
import json
import hashlib

def create_kv_name_from_workspace_id(workspace_id):
    hash = hashlib.sha256(workspace_id.encode())
    uniqueHash = hash.digest().hex()
    return f'widgets-{uniqueHash[:16]}'

def main(subscription_id, resource_group_name, workspace_id, template_file_path):
    credential = InteractiveBrowserCredential()

    print('Manage to get credentials')
    with open(template_file_path, 'r') as template_file:
        template = json.load(template_file)
    
    print(f"Manage to read template from '{template_file}'")
    client = ResourceManagementClient(credential, subscription_id)
    kv_name = create_kv_name_from_workspace_id(workspace_id)

    print(f"Manage to create kv name: '{kv_name}'")
    deployment_properties = {
        'properties': {
            'mode': DeploymentMode.incremental,
            'template': template,
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

    deployment.wait()

    print(f"Deployment for kv - '{kv_name}' started.")
    print(f"Deployment status: {deployment.properties.provisioning_state}")


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--subscription-id', required=True)
    parser.add_argument('--resource-group-name', required=True)
    parser.add_argument('--workspace-id', required=True)
    parser.add_argument('--template-file-path', required=True)
    args = parser.parse_args()

    main(args.subscription_id, args.resource_group_name, args.workspace_id, args.template_file_path)
