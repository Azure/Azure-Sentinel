import _ from "lodash";
import { RequiredConnectorPermissions, ConnectorCategory } from "../dataConnector";
import { DataConnectorValidationError } from "../validationError";

const CEFRestAPIPermissions = {
    "resourceProvider": [
        {
            "provider": "Microsoft.OperationalInsights/workspaces",
            "permissionsDisplayText": "read and write permissions are required.",
            "providerDisplayName": "Workspace",
            "scope": "Workspace",
            "requiredPermissions": {
                "write": true,
                "read": true,
                "delete": true
            }
        },
        {
            "provider": "Microsoft.OperationalInsights/workspaces/sharedKeys",
            "permissionsDisplayText": "read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).",
            "providerDisplayName": "Keys",
            "scope": "Workspace",
            "requiredPermissions": {
                "action": true
            }
        }
    ]
};

const SysLogPermissions = {
    "resourceProvider": [
        {
            "provider": "Microsoft.OperationalInsights/workspaces",
            "permissionsDisplayText": "write permission is required.",
            "providerDisplayName": "Workspace",
            "scope": "Workspace",
            "requiredPermissions": {
                "write": true,
                "delete": true
            }
        }
    ]
};

const AzureFunctionPermissions = {
    "resourceProvider": [
        {
            "provider": "Microsoft.OperationalInsights/workspaces",
            "permissionsDisplayText": "read and write permissions on the workspace are required.",
            "providerDisplayName": "Workspace",
            "scope": "Workspace",
            "requiredPermissions": {
                "write": true,
                "read": true,
                "delete": true
            }
        },
        {
            "provider": "Microsoft.OperationalInsights/workspaces/sharedKeys",
            "permissionsDisplayText": "read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).",
            "providerDisplayName": "Keys",
            "scope": "Workspace",
            "requiredPermissions": {
                "action": true
            }
        }
    ],
    "customs": [
        {
            "name": "Microsoft.Web/sites permissions",
            "description": "Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/)."
        }
    ]
};

export function isValidPermissions(permissions: RequiredConnectorPermissions, connectorCategory: any) {   
    
    switch(connectorCategory)
    {
        case ConnectorCategory.CEF:
        case ConnectorCategory.RestAPI:
            if(!_.isEqual(permissions.resourceProvider, CEFRestAPIPermissions.resourceProvider))
            {
                throw new DataConnectorValidationError("Provided permissions does not match with "+ connectorCategory +" Template. Please refer template https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Templates/Connector_"+ connectorCategory +"_template.json ");
            }
            break;
        case ConnectorCategory.SysLog:
            if(!_.isEqual(permissions.resourceProvider, SysLogPermissions.resourceProvider))
            {
                throw new DataConnectorValidationError("Provided permissions does not match with Syslog Connector Template. Please refer template https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Templates/Connector_Syslog_template.json ");
            }
            break;
            case ConnectorCategory.AzureFunction:
            if(!(_.isEqual(permissions.resourceProvider, AzureFunctionPermissions.resourceProvider) && isValidCustomPermission(permissions)))
            {
                throw new DataConnectorValidationError("Provided permissions does not match with Azure Function Connector Template. Please refer template https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Templates/Connector_REST_API_AzureFunctionApp_template/DataConnector_API_AzureFunctionApp_template.json");
            }
            break;
        default:
            return true;
    }

    return true;
}

function isValidCustomPermission(permissions:RequiredConnectorPermissions)
{
    if(permissions.customs?.some(customPermission=>customPermission.name===(AzureFunctionPermissions.customs[0].name)
    && customPermission.description===(AzureFunctionPermissions.customs[0].description)))
    {
        return true;
    }
    
    return false;
}