param functionAppName string
param logAnalyticsWorkspaceName string
param version string

resource functionApp 'Microsoft.Web/sites@2021-03-01' existing = {
  name: functionAppName
}

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-06-01' existing = {
  name: logAnalyticsWorkspaceName
}


// Metrics Publisher role assignment for the Function App identity to DCRs, so App can fill Custom Tables
var metricsPublisherRoleImmutableId = '3913510d-42f4-4e42-8a64-420c390055eb'


resource dcrMalwareEvents 'Microsoft.Insights/dataCollectionRules@2022-06-01' existing = {
  name: 'VeeamMalwareEventsDCR'
}

resource dcrMalwareEventsMetricsPublisher 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(subscription().id, functionAppName, dcrMalwareEvents.id, metricsPublisherRoleImmutableId)
  scope: dcrMalwareEvents
  properties: {
    principalId: functionApp.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', metricsPublisherRoleImmutableId)
  }
}

resource dceMalwareEvents 'Microsoft.Insights/dataCollectionEndpoints@2022-06-01' existing = {
  name: 'VeeamMalwareEventsDCE'
}

resource dceMalwareEventsMetricsPublisher 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(subscription().id, functionAppName, dceMalwareEvents.id, metricsPublisherRoleImmutableId)
  scope: dceMalwareEvents
  properties: {
    principalId: functionApp.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', metricsPublisherRoleImmutableId)
  }
}


resource dcrBestPracticeAnalysis 'Microsoft.Insights/dataCollectionRules@2022-06-01' existing = {
  name: 'VeeamSecurityComplianceAnalyzerDCR'
}

resource dcrBestPracticeAnalysisMetricsPublisher 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(subscription().id, functionAppName, dcrBestPracticeAnalysis.id, metricsPublisherRoleImmutableId)
  scope: dcrBestPracticeAnalysis
  properties: {
    principalId: functionApp.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', metricsPublisherRoleImmutableId)
  }
}

resource dceBestPracticeAnalysis 'Microsoft.Insights/dataCollectionEndpoints@2022-06-01' existing = {
  name: 'VeeamSecurityComplianceAnalyzerDCE'
}

resource dceBestPracticeAnalysisMetricsPublisher 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(subscription().id, functionAppName, dceBestPracticeAnalysis.id, metricsPublisherRoleImmutableId)
  scope: dceBestPracticeAnalysis
  properties: {
    principalId: functionApp.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', metricsPublisherRoleImmutableId)
  }
}

resource dcrAuthorizationEvents 'Microsoft.Insights/dataCollectionRules@2022-06-01' existing = {
  name: 'VeeamAuthorizationEventsDCR'
}

resource dcrAuthorizationEventsMetricsPublisher 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(subscription().id, functionAppName, dcrAuthorizationEvents.id, metricsPublisherRoleImmutableId)
  scope: dcrAuthorizationEvents
  properties: {
    principalId: functionApp.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', metricsPublisherRoleImmutableId)
  }
}

resource dceAuthorizationEvents 'Microsoft.Insights/dataCollectionEndpoints@2022-06-01' existing = {
  name: 'VeeamAuthorizationEventsDCE'
}

resource dceAuthorizationEventsMetricsPublisher 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(subscription().id, functionAppName, dceAuthorizationEvents.id, metricsPublisherRoleImmutableId)
  scope: dceAuthorizationEvents
  properties: {
    principalId: functionApp.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', metricsPublisherRoleImmutableId)
  }
}

resource dcrTriggeredAlarms 'Microsoft.Insights/dataCollectionRules@2022-06-01' existing = {
  name: 'VeeamOneTriggeredAlarmsDCR'
}

resource dcrTriggeredAlarmsMetricsPublisher 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(subscription().id, functionAppName, dcrTriggeredAlarms.id, metricsPublisherRoleImmutableId)
  scope: dcrTriggeredAlarms
  properties: {
    principalId: functionApp.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', metricsPublisherRoleImmutableId)
  }
}

resource dceTriggeredAlarms 'Microsoft.Insights/dataCollectionEndpoints@2022-06-01' existing = {
  name: 'VeeamOneTriggeredAlarmsDCE'
}

resource dceTriggeredAlarmsMetricsPublisher 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(subscription().id, functionAppName, dceTriggeredAlarms.id, metricsPublisherRoleImmutableId)
  scope: dceTriggeredAlarms
  properties: {
    principalId: functionApp.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', metricsPublisherRoleImmutableId)
  }
}

resource dcrCovewareFindings 'Microsoft.Insights/dataCollectionRules@2022-06-01' existing = {
  name: 'VeeamCovewareFindingsDCR'
}

resource dcrCovewareFindingsMetricsPublisher 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(subscription().id, functionAppName, dcrCovewareFindings.id, metricsPublisherRoleImmutableId)
  scope: dcrCovewareFindings
  properties: {
    principalId: functionApp.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', metricsPublisherRoleImmutableId)
  }
}

resource dceCovewareFindings 'Microsoft.Insights/dataCollectionEndpoints@2022-06-01' existing = {
  name: 'VeeamCovewareFindingsDCE'
}

resource dceCovewareFindingsMetricsPublisher 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(subscription().id, functionAppName, dceCovewareFindings.id, metricsPublisherRoleImmutableId)
  scope: dceCovewareFindings
  properties: {
    principalId: functionApp.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', metricsPublisherRoleImmutableId)
  }
}

resource dcrSession 'Microsoft.Insights/dataCollectionRules@2022-06-01' existing = {
  name: 'VeeamSessionsDCR'
}

resource dcrSessionMetricsPublisher 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(subscription().id, functionAppName, dcrSession.id, metricsPublisherRoleImmutableId)
  scope: dcrSession
  properties: {
    principalId: functionApp.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', metricsPublisherRoleImmutableId)
  }
}

resource dceSession 'Microsoft.Insights/dataCollectionEndpoints@2022-06-01' existing = {
  name: 'VeeamSessionsDCE'
}

resource dceSessionMetricsPublisher 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(subscription().id, functionAppName, dceSession.id, metricsPublisherRoleImmutableId)
  scope: dceSession
  properties: {
    principalId: functionApp.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', metricsPublisherRoleImmutableId)
  }
}

var logAnalyticsContributorImmutableId = '92aaf0da-9dab-42b6-94a3-d43ce8d16293'

resource logAnalyticsReaderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(
    resourceGroup().id,
    functionApp.id,
    logAnalyticsWorkspace.id,
    logAnalyticsContributorImmutableId,
    version
  )
  scope: logAnalyticsWorkspace
  properties: {
    principalId: functionApp.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', logAnalyticsContributorImmutableId)
  }
}
