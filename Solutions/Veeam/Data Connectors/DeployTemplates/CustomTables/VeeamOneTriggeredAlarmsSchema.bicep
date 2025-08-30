param workspaceName string
param location string
param retentionInDays int = 30

var baseName = 'VeeamOneTriggeredAlarms'

// Derived names
var tableName = '${baseName}_CL'
var dcrName = '${baseName}DCR'
var dceName = '${baseName}DCE'
var streamKey = 'Custom-${tableName}'

// Schema definition
var schemaColumns = [
  {name: 'VoneHostName', type: 'string'}
  { name: 'TriggeredAlarmId', type: 'int' }
  { name: 'Name', type: 'string' }
  { name: 'AlarmTemplateId', type: 'int' }
  { name: 'PredefinedAlarmId', type: 'int' }
  { name: 'TriggeredTime', type: 'datetime' }
  { name: 'Status', type: 'string' }
  { name: 'Description', type: 'string' }
  { name: 'Comment', type: 'string' }
  { name: 'RepeatCount', type: 'int' }
  { name: 'ObjectId', type: 'int' }
  { name: 'ObjectName', type: 'string' }
  { name: 'ObjectType', type: 'string' }
  { name: 'ChildAlarmsCount', type: 'int' }
  { name: 'RemediationDescription', type: 'string' }
  { name: 'RemediationMode', type: 'string' }
]

// Reference existing Log Analytics workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-06-01' existing = {
  name: workspaceName
}

resource VeeamOneTriggeredAlaramsTable_CL 'Microsoft.OperationalInsights/workspaces/tables@2025-02-01' = {
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

module triggeredAlarmsDCE './dceTemplate.bicep' = {
  name: dceName
  params: {
    location: location
    dceName: dceName
  }
}

// Create Data Collection Rule for triggered alarms
resource dataCollectionRule 'Microsoft.Insights/dataCollectionRules@2023-03-11' = {
  name: dcrName
  location: location
  dependsOn: [VeeamOneTriggeredAlaramsTable_CL]
  properties: {
    dataCollectionEndpointId: triggeredAlarmsDCE.outputs.dceResourceId
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
output dceIngestionEndpoint string = triggeredAlarmsDCE.outputs.dceIngestionEndpoint
output tableName string = tableName
