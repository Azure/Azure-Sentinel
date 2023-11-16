/*
Deploys a Data Collection Rule for 1Password logs to a Log Analytics workspace.
This Bicep file creates a custom log table, a data collection endpoint, and a data collection rule.
The data collection rule is configured to ingest data from the data collection endpoint into the custom log table.
*/

// Parameters
@description('Specifies the name of the Data Collection Rule to create.')
param dataCollectionRuleName string = '1Password'

@description('Name of the Log Analytics workspace.')
param workspaceName string

@description('Location of the Log Analytics workspace')
param location string = resourceGroup().location

@description('Specifies the name of the Data Collection Endpoint to create')
param dataCollectionEndpointName string = '1Password'

@description('Specifies the name of the Custom Log Table for data ingestion')
param customLogTable string = 'OnePasswordEventLogs_CL'

// This resource block references an existing Log Analytics workspace.
resource workspace 'Microsoft.OperationalInsights/workspaces@2021-12-01-preview' existing = {
  name: workspaceName
}

//  Variables
var customTable = 'Custom-${customLogTable}'

// Resources
// This resource creates a data collection endpoint for 1Password table in Azure Sentinel.
resource dce 'Microsoft.Insights/dataCollectionEndpoints@2021-04-01' = {
  name: dataCollectionEndpointName
  location: location
  properties:{
    networkAcls:{
      publicNetworkAccess: 'Enabled'
    }
  }
}

// Creates a data collection rule that sends data to a Log Analytics workspace.
// The data collection rule collects data from a custom table and transforms it using a KQL query.
resource dcr 'Microsoft.Insights/dataCollectionRules@2021-09-01-preview' = {
  name: dataCollectionRuleName
  location: location
  properties: {
    dataCollectionEndpointId: dce.id
    destinations: {
      logAnalytics: [
        {
          workspaceResourceId: workspace.id
          name: workspace.name
        }
      ]
    }
    dataFlows: [
      {
        streams: [
          customTable
        ]
        destinations: [
          workspace.name
        ]
      outputStream: customTable
      transformKql: 'source | extend TimeGenerated = now()'
      }
    ]
  }
  dependsOn: [
    table
  ]
}

// This resource creates a custom log table in an Azure Monitor Log Analytics workspace to store 1Password data.
resource table 'Microsoft.OperationalInsights/workspaces/tables@2021-12-01-preview' = {
  name: customLogTable
  parent: workspace
  properties: {
  schema: {
    name: customLogTable
    columns: [
    {
      name: 'SourceSystem'
      type: 'string'
    }
    {
      name: 'TimeGenerated'
      type: 'datetime'
    }
    {
      name: 'uuid_s'
      type: 'string'
    }
    {
      name: 'session_uuid'
      type: 'string'
    }
    {
      name: 'timestamp'
      type: 'datetime'
    }
    {
      name: 'country'
      type: 'string'
    }
    {
      name: 'category'
      type: 'string'
    }
    {
      name: 'action_type'
      type: 'string'
    }
    {
      name: 'details'
      type: 'dynamic'
    }
    {
      name: 'target_user'
      type: 'dynamic'
    }
    {
      name: 'client'
      type: 'dynamic'
    }
    {
      name: 'location'
      type: 'dynamic'
    }
    {
      name: 'actor_uuid'
      type: 'string'
    }
    {
      name: 'actor_details'
      type: 'dynamic'
    }
    {
      name: 'action'
      type: 'string'
    }
    {
      name: 'object_type'
      type: 'string'
    }
    {
      name: 'object_uuid'
      type: 'string'
    }
    {
      name: 'aux_info'
      type: 'string'
    }
    {
      name: 'session'
      type: 'dynamic'
    }
    {
      name: 'used_version'
      type: 'int'
    }
    {
      name: 'vault_uuid'
      type: 'string'
    }
    {
      name: 'item_uuid'
      type: 'string'
    }
    {
      name: 'user'
      type: 'dynamic'
    }
  ]
  }
  }
}

// Outputs
// This output variable contains the data collection endpoint for the 1Password data connector.
output dataCollectionEndpoint string = dce.properties.logsIngestion.endpoint

// This output variable contains the immutable ID for the 1Password data connector.
output immutableId string = dce.properties.immutableId

// This output variable contains the endpoint URI for the 1Password data connector.
output endpointUri string = '${dce.properties.logsIngestion.endpoint}/dataCollectionRules/${dcr.properties.immutableId}/streams/${customTable}?api-version=2021-11-01-preview'
