import _ from "lodash";
import { RequiredConnectorPermissions, ConnectorCategory } from "../dataConnector.js";
import { DataConnectorValidationError } from "../validationError.js";

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

// Direct Logs Ingestion API senders use a DCR role assignment, not workspace shared keys.
// Keep this profile limited to REST API connectors; CEF and Event retain their existing checks.
const LogsIngestionAPIPermissions = {
    resourceProvider: [{
        provider: "Microsoft.OperationalInsights/workspaces",
        permissionsDisplayText: "Read and write permissions are required to configure the workspace tables.",
        providerDisplayName: "Workspace",
        scope: "Workspace",
        requiredPermissions: { read: true, write: true }
    }],
    custom: {
        name: "Azure Monitor Logs Ingestion API",
        description: "The sending application requires the Monitoring Metrics Publisher role on the data collection rule (DCR). Workspace shared keys are not used."
    }
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

const SysLogDataSourcesPermissions = {
    "resourceProvider": [
            {
                "provider": "Microsoft.OperationalInsights/workspaces/datasources",
                "permissionsDisplayText": "read and write permissions.",
                "providerDisplayName": "Workspace data sources",
                "scope": "Workspace",
                "requiredPermissions": {
                    "read": true,
                    "write": true
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
        case ConnectorCategory.Event:
        case ConnectorCategory.RestAPI:
            const hasLogsIngestionPermissions = connectorCategory === ConnectorCategory.RestAPI
                && _.isEqual(permissions.resourceProvider, LogsIngestionAPIPermissions.resourceProvider)
                && permissions.customs?.some(custom => _.isEqual(custom, LogsIngestionAPIPermissions.custom));
            if(!_.isEqual(permissions.resourceProvider, CEFRestAPIPermissions.resourceProvider) && !hasLogsIngestionPermissions)
            {
                throw new DataConnectorValidationError("Provided permissions does not match with "+ connectorCategory +" Template. Please refer template https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Templates/Connector_"+ connectorCategory +"_template.json ");
            }
            break;
        case ConnectorCategory.SysLog:
            var hasSysLogPermissions = _.isEqual(permissions.resourceProvider, SysLogPermissions.resourceProvider)
            var hasSysLogDataSourcesPermissions = _.isEqual(permissions.resourceProvider, SysLogDataSourcesPermissions.resourceProvider)
 
if (!hasSysLogPermissions && !hasSysLogDataSourcesPermissions) {
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
