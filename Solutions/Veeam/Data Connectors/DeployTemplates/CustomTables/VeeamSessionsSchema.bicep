// filepath: d:\Forks\Azure-Sentinel-NK\Solutions\Veeam\Data Connectors\CustomTables\VeeamSessionssSchema.bicep
param workspaceName string
param location string
param retentionInDays int = 30

var baseName = 'VeeamSessions'

// Derived names
var tableName = '${baseName}_CL'
var dcrName = '${baseName}DCR'
var dceName = '${baseName}DCE'
var streamKey = 'Custom-${tableName}'

// Common schema definition based on Veeam session JSON structure
var schemaColumns = [
  { name: 'VbrHostName', type: 'string' }
  { name: 'SessionType', type: 'string' }
  { name: 'State', type: 'string' }
  { name: 'PlatformName', type: 'string' }
  { name: 'Id', type: 'string' }
  { name: 'Name', type: 'string' }
  { name: 'JobId', type: 'string' }
  { name: 'CreationTime', type: 'datetime' }
  { name: 'EndTime', type: 'datetime' }
  { name: 'ProgressPercent', type: 'int' }
  { name: 'Result', type: 'string' }
  { name: 'ResultStatus', type: 'string' }
  { name: 'ResultMessage', type: 'string' }
  { name: 'ResultIsCanceled', type: 'boolean' }
  { name: 'Message', type: 'string' }
  { name: 'IsCanceled', type: 'boolean' }
  { name: 'ResourceId', type: 'string' }
  { name: 'ResourceReference', type: 'string' }
  { name: 'ParentSessionId', type: 'string' }
  { name: 'Usn', type: 'long' }
  { name: 'PlatformId', type: 'string' }
]

// Reference existing Log Analytics workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-06-01' existing = {
  name: workspaceName
}

resource VeeamSessionsTable_CL 'Microsoft.OperationalInsights/workspaces/tables@2025-02-01' = {
  parent: logAnalyticsWorkspace
  name: tableName
  properties: {
    totalRetentionInDays: retentionInDays
    plan: 'Analytics'
    schema: {
      name: tableName
      columns: [
        { name: 'TimeGenerated', type: 'datetime' }
        ...schemaColumns
      ]
    }
    retentionInDays: retentionInDays
  }
}

module sessionDCE './dceTemplate.bicep' = {
  name: dceName
  params: {
    location: location
    dceName: dceName
  }
}

// Create Data Collection Rule for session data
resource dataCollectionRule 'Microsoft.Insights/dataCollectionRules@2023-03-11' = {
  name: dcrName
  location: location
  dependsOn: [VeeamSessionsTable_CL]
  properties: {
    dataCollectionEndpointId: sessionDCE.outputs.dceResourceId
    streamDeclarations: {
      '${streamKey}': {
        columns: schemaColumns
      }
    }
    dataSources: {}
    destinations: {
      logAnalytics: [
        {
          workspaceResourceId: logAnalyticsWorkspace.id
          name: 'logAnalyticsDestination'
        }
      ]
    }
    dataFlows: [
      {
        streams: [streamKey]
        destinations: ['logAnalyticsDestination']
        transformKql: 'source | extend TimeGenerated = now()'
        outputStream: streamKey
      }
    ]
  }
}

// Expose immutable ID of the DCR
output dcrImmutableId string = dataCollectionRule.properties.immutableId
output dceIngestionEndpoint string = sessionDCE.outputs.dceIngestionEndpoint
output tableName string = tableName
