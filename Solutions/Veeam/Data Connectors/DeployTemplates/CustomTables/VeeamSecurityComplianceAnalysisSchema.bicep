param workspaceName string
param location string
param retentionInDays int = 30

var baseName = 'VeeamSecurityComplianceAnalyzer'

// Derived names
var tableName = '${baseName}_CL'
var dcrName   = '${baseName}DCR'
var dceName   = '${baseName}DCE'
var streamKey = 'Custom-${tableName}'

// Common schema definition
var schemaColumns = [
  { name: 'VbrHostName',   type: 'string'   }
  { name: 'Status',        type: 'string'   }
  { name: 'Id',            type: 'string'   }
  { name: 'BestPractice',  type: 'string'   }
  { name: 'Note',          type: 'string'   }
]

// Reference existing Log Analytics workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-06-01' existing = {
  name: workspaceName
}

resource VeeamBestPracticesAnalysisTable_CL 'Microsoft.OperationalInsights/workspaces/tables@2025-02-01' = {
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


module bestPracticesDCE './dceTemplate.bicep' = {
  name: dceName
  params: {
    location: location
    dceName: dceName
  }
}

// Create Data Collection Rule for best practices analysis
resource dataCollectionRule 'Microsoft.Insights/dataCollectionRules@2023-03-11' = {
  name: dcrName
  location: location
  dependsOn: [VeeamBestPracticesAnalysisTable_CL]
  properties: {
    dataCollectionEndpointId: bestPracticesDCE.outputs.dceResourceId
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
output dceIngestionEndpoint string = bestPracticesDCE.outputs.dceIngestionEndpoint
output tableName string = tableName
