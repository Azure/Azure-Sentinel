@description('The name of the Log Analytics workspace where the custom tables will be created')
param workspaceName string

@description('The number of days to retain the data in the tables')
@minValue(4)
@maxValue(730)
param retentionInDays int = 30


// Reference existing Log Analytics workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-06-01' existing = {
  name: workspaceName
}

module malwareEventsTable './VeeamMalwareEventsSchema.bicep' = {
  name: 'VeeamMalwareEventsTable'
  params: {
    workspaceName: workspaceName
    location: logAnalyticsWorkspace.location
    retentionInDays: retentionInDays
  }
}

module bestPracticesTable './VeeamSecurityComplianceAnalysisSchema.bicep' = {
  name: 'VeeamSecurityComplianceAnalysisTable'
  params: {
    workspaceName: workspaceName
    location: logAnalyticsWorkspace.location
    retentionInDays: retentionInDays
  }
}

module authorizationEventsTable './VeeamAuthorizationEventsSchema.bicep' = {
  name: 'VeeamAuthorizationEventsTable'
  params: {
    workspaceName: workspaceName
    location: logAnalyticsWorkspace.location
    retentionInDays: retentionInDays
  }
}

module triggeredAlarmsTable './VeeamOneTriggeredAlarmsSchema.bicep' = {
  name: 'VeeamOneTriggeredAlarmsTable'
  params: {
    workspaceName: workspaceName
    location: logAnalyticsWorkspace.location
    retentionInDays: retentionInDays
  }
}

module CovewareFindingsTable './CovewareFindingsSchema.bicep' = {
  name: 'CovewareFindingsTable'
  params: {
    workspaceName: workspaceName
    location: logAnalyticsWorkspace.location
    retentionInDays: retentionInDays
  }
}

module sessionTable './VeeamSessionsSchema.bicep' = {
  name: 'VeeamSessionsTable'
  params: {
    workspaceName: workspaceName
    location: logAnalyticsWorkspace.location
    retentionInDays: retentionInDays
  }
}


output malwareDCRImmutableId string = malwareEventsTable.outputs.dcrImmutableId
output malwareDCEIngestionEndpoint string = malwareEventsTable.outputs.dceIngestionEndpoint
output malwareTableName string = malwareEventsTable.outputs.tableName

output bestPracticesDCRImmutableId string = bestPracticesTable.outputs.dcrImmutableId
output bestPracticesDCEIngestionEndpoint string = bestPracticesTable.outputs.dceIngestionEndpoint
output bestPracticesTableName string = bestPracticesTable.outputs.tableName

output authorizationDCRImmutableId string = authorizationEventsTable.outputs.dcrImmutableId
output authorizationDCEIngestionEndpoint string = authorizationEventsTable.outputs.dceIngestionEndpoint
output authorizationTableName string = authorizationEventsTable.outputs.tableName

output triggeredAlarmsDCRImmutableId string = triggeredAlarmsTable.outputs.dcrImmutableId
output triggeredAlarmsDCEIngestionEndpoint string = triggeredAlarmsTable.outputs.dceIngestionEndpoint
output triggeredAlarmsTableName string = triggeredAlarmsTable.outputs.tableName

output CovewareFindingsDCRImmutableId string = CovewareFindingsTable.outputs.dcrImmutableId
output CovewareFindingsDCEIngestionEndpoint string = CovewareFindingsTable.outputs.dceIngestionEndpoint
output CovewareFindingsTableName string = CovewareFindingsTable.outputs.tableName

output sessionDCRImmutableId string = sessionTable.outputs.dcrImmutableId
output sessionDCEIngestionEndpoint string = sessionTable.outputs.dceIngestionEndpoint
output sessionTableName string = sessionTable.outputs.tableName
