param workspaceName string
param location string
param retentionInDays int = 30

var baseName = 'VeeamCovewareFindings'

// Derived names
var tableName = '${baseName}_CL'
var dcrName = '${baseName}DCR'
var dceName = '${baseName}DCE'
var streamKey = 'Custom-${tableName}'

// Schema definition based on the provided JSON structure
var schemaColumns = [
  { name: 'CovewareHostName', type: 'string' }
  { name: 'Artifact', type: 'string' }
  { name: 'EventType', type: 'string' }
  { name: 'TechniqueId', type: 'string' }
  { name: 'EventTime', type: 'datetime' }
  { name: 'FirstRunOrAccessed', type: 'datetime' }
  { name: 'Hostname', type: 'string' }
  { name: 'EventActivity', type: 'string' }
  { name: 'Country', type: 'string' }
  { name: 'Id', type: 'string' }
  { name: 'Md5Hash', type: 'string' }
  { name: 'Sha1Hash', type: 'string' }
  { name: 'Sha256Hash', type: 'string' }
  { name: 'MachineId', type: 'string' }
  { name: 'RiskLevel', type: 'string' }
  { name: 'ScanTime', type: 'datetime' }
  { name: 'Username', type: 'string' }
]

// Reference existing Log Analytics workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-06-01' existing = {
  name: workspaceName
}

resource CovewareFindingsTable_CL 'Microsoft.OperationalInsights/workspaces/tables@2025-02-01' = {
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

module CovewareDCE './dceTemplate.bicep' = {
  name: dceName
  params: {
    location: location
    dceName: dceName
  }
}

// Create Data Collection Rule for Coveware findings
resource dataCollectionRule 'Microsoft.Insights/dataCollectionRules@2023-03-11' = {
  name: dcrName
  location: location
  dependsOn: [CovewareFindingsTable_CL]
  properties: {
    dataCollectionEndpointId: CovewareDCE.outputs.dceResourceId
    streamDeclarations: {
      '${streamKey}': {
        columns: schemaColumns
      }
    }
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
output dceIngestionEndpoint string = CovewareDCE.outputs.dceIngestionEndpoint
output tableName string = tableName
