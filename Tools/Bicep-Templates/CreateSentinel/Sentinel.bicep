targetScope = 'resourceGroup'

@description('Specifies the name of the client who needs Sentinel.')
param workspaceName string

@description('Specifies the number of days to retain data.')
param retentionInDays int

@description('Which solutions to deploy automatically')
param contentSolutions string[]

var subscriptionId = subscription().id
var location  = resourceGroup().location
//Sentinel Contributor role GUID
var roleDefinitionId = 'ab8e14d6-4a74-4a29-9ba8-549422addade'

// Create the Log Analytics Workspace
resource workspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: workspaceName
  location: location
  properties: {
    retentionInDays: retentionInDays
  }
}

output test string = 'Creating Log Analytics Workspace'

// Create Microsoft Sentinel on the Log Analytics Workspace
resource sentinel 'Microsoft.OperationsManagement/solutions@2015-11-01-preview' = {
  name: 'SecurityInsights(${workspaceName})'
  location: location
  properties: {
    workspaceResourceId: workspace.id
  }
  plan: {
    name: 'SecurityInsights(${workspaceName})'
    product: 'OMSGallery/SecurityInsights'
    promotionCode: ''
    publisher: 'Microsoft'
  }
}


// Onboard Sentinel after it has been created
resource onboardingStates 'Microsoft.SecurityInsights/onboardingStates@2022-12-01-preview' = {
  scope: workspace
  name: 'default'
}

// Enable the Entity Behavior directory service
resource EntityAnalytics 'Microsoft.SecurityInsights/settings@2023-02-01-preview' = {
  name: 'EntityAnalytics'
  kind: 'EntityAnalytics'
  scope: workspace
  properties: {
    entityProviders: ['AzureActiveDirectory']
  }
  dependsOn: [
    onboardingStates
  ]
}

// Enable the additional UEBA data sources
resource uebaAnalytics 'Microsoft.SecurityInsights/settings@2023-02-01-preview' = {
  name: 'Ueba'
  kind: 'Ueba'
  scope: workspace
  properties: {
    dataSources: ['AuditLogs', 'AzureActivity', 'SigninLogs', 'SecurityEvent']
  }
  dependsOn: [
    EntityAnalytics
  ]
}


//Create the user identity to interact with Azure
@description('The user identity for the deployment script.')
resource scriptIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'script-identity'
  location: location
}

//Pausing for 5 minutes to allow the new user identity to propagate
resource pauseScript 'Microsoft.Resources/deploymentScripts@2023-08-01' = {
  name: 'pauseScript'
  location: resourceGroup().location
  kind: 'AzurePowerShell'
  properties: {
    azPowerShellVersion: '12.2.0'
    scriptContent: 'Start-Sleep -Seconds 300'
    timeout: 'PT30M'
    cleanupPreference: 'OnSuccess'
    retentionInterval: 'PT1H'
  }
  dependsOn: [
    scriptIdentity
  ]
}

//Assign the Sentinel Contributor rights on the Resource Group to the User Identity that was just created
resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().name, roleDefinitionId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitionId)
    principalId: scriptIdentity.properties.principalId
  }
  dependsOn: [
    pauseScript
  ]
}

//  Call the external PowerShell script to deploy the solutions and rules
resource deploymentScript 'Microsoft.Resources/deploymentScripts@2023-08-01' = {
  name: 'deploySolutionsScript'
  location: resourceGroup().location
  kind: 'AzurePowerShell'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${scriptIdentity.id}': {}
    }
  }
  properties: {
    azPowerShellVersion: '12.2.0'
    arguments: '-ResourceGroup ${resourceGroup().name} -Workspace ${workspaceName} -Region ${resourceGroup().location} -Solutions ${contentSolutions} -SubscriptionId ${subscriptionId} -TenantId ${subscription().tenantId} -Identity ${scriptIdentity.properties.clientId} '
    scriptContent: loadTextContent('./Create-NewSolutionAndRulesFromList.ps1')
    timeout: 'PT30M'
    cleanupPreference: 'OnSuccess'
    retentionInterval: 'P1D'
  }
  dependsOn: [
    roleAssignment
  ]
}
