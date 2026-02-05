@description('The name of the Log Analytics workspace where the custom table will be created')
param workspaceName string

@description('The Azure region where resources will be deployed')
param location string

@description('The number of days to retain the data in the table')
@minValue(4)
@maxValue(730)
param retentionInDays int = 30


// Base name for all resources in this module
var baseName = 'VeeamAuthorizationEvents'

// Resource naming convention variables
var tableName = '${baseName}_CL'  // _CL suffix for custom log table
var dceName = '${baseName}DCE'         // Data Collection Endpoint name
var dcrName = '${baseName}DCR'         // Data Collection Rule name
var streamKey = 'Custom-${tableName}'  // Stream identifier for the DCR

var authorizationSchema array = [
  { name: 'CreatedBy', type: 'string' }
  { name: 'CreationTime', type: 'datetime' }
  { name: 'Description', type: 'string' }
  { name: 'ExpirationTime', type: 'datetime' }
  { name: 'Id', type: 'string' }
  { name: 'Name', type: 'string' }
  { name: 'ProcessedBy', type: 'string' }
  { name: 'ProcessedTime', type: 'datetime' }
  { name: 'State', type: 'string' }
  { name: 'VbrHostName', type: 'string' }
]

// Reference existing Log Analytics workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-06-01' existing = {
  name: workspaceName
}

// Create custom table in Log Analytics
resource authorizationTable 'Microsoft.OperationalInsights/workspaces/tables@2023-09-01' = {
  parent: logAnalyticsWorkspace
  name: tableName
  properties: {
    totalRetentionInDays: retentionInDays
    retentionInDays: retentionInDays
    plan: 'Analytics'
    schema: {
      name: tableName
      columns: [
        { name: 'TimeGenerated', type: 'datetime' }
        ...authorizationSchema
      ] 
    }
  }
}

// Deploy Data Collection Endpoint module
module authorizationDCE './dceTemplate.bicep' = {
  name: dceName
  params: {
    location: location
    dceName: dceName
  }
}

// Create Data Collection Rule with enhanced documentation
resource authorizationDCR 'Microsoft.Insights/dataCollectionRules@2023-03-11' = {
  name: dcrName
  location: location
  tags: {
    displayName: dcrName
    purpose: 'Sentinel Custom Table'
    module: 'VeeamAuthorizationEvents'
  }
  properties: {
    dataCollectionEndpointId: authorizationDCE.outputs.dceResourceId
    streamDeclarations: {
      '${streamKey}': {
        columns: authorizationSchema
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
    // Consider adding description for better documentation
    description: 'Data Collection Rule for Veeam Authorization Events'
  }
}

// Expose immutable ID of the DCR
output dcrImmutableId string = authorizationDCR.properties.immutableId
output dceIngestionEndpoint string = authorizationDCE.outputs.dceIngestionEndpoint
output tableName string = tableName
