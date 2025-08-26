@description('Name of the ChangeCollectionTime Logic App that needs permissions')
param changeCollectionTimeLogicAppName string = 'Veeam-ChangeCollectionTime'

@description('Resource group name where Logic Apps are located')
param resourceGroupName string = resourceGroup().name

@description('Subscription ID')
param subscriptionId string = subscription().subscriptionId

@description('Name of the Log Analytics workspace (Sentinel workspace)')
param workspaceName string

@description('Names of the specific Veeam collection playbooks to assign permissions to')
param veeamCollectionPlaybooks array = [
  'Veeam-CollectMalwareEvents'
  'Veeam-CollectVeeamAuthorizationEvents'
  'Veeam-CollectVeeamBestPracticeAnalysis'
  'Veeam-CollectVeeamONEAlarms'
  'Veeam-CollectCovewareFindings'
]

// Get reference to the existing ChangeCollectionTime Logic App
resource changeCollectionTimeLogicApp 'Microsoft.Logic/workflows@2019-05-01' existing = {
  name: changeCollectionTimeLogicAppName
}

// Get reference to the existing Log Analytics workspace (Sentinel workspace)
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: workspaceName
}

// Logic App Contributor role definition ID
var logicAppContributorRoleId = '87a39d53-fc1b-424a-814c-f7e04687dc9e'

// Contributor role definition ID (needed for Management API access)
var contributorRoleId = 'b24988ac-6180-42a0-ab88-20f7382dd24c'

// Microsoft Sentinel Contributor role definition ID
var sentinelContributorRoleId = 'ab8e14d6-4a74-4a29-9ba8-549422addade'

// Get references to the existing Veeam collection Logic Apps
resource veeamCollectionLogicApps 'Microsoft.Logic/workflows@2019-05-01' existing = [for playbook in veeamCollectionPlaybooks: {
  name: playbook
}]

// Logic App Contributor role assignment for each specific Veeam collection playbook
// This allows the ChangeCollectionTime Logic App to manage specific collection playbooks
resource logicAppContributorRoleAssignments 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for (playbook, index) in veeamCollectionPlaybooks: {
  name: guid(veeamCollectionLogicApps[index].id, changeCollectionTimeLogicApp.id, logicAppContributorRoleId)
  scope: veeamCollectionLogicApps[index]
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', logicAppContributorRoleId)
    principalId: changeCollectionTimeLogicApp.identity.principalId
    principalType: 'ServicePrincipal'
    description: 'Allows the ChangeCollectionTime Logic App to manage the ${playbook} collection playbook scheduling'
  }
}]

// Contributor role assignment at resource group level for Management API access
// This is required for the Logic App to make Azure Management API calls to update other Logic Apps
resource contributorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, changeCollectionTimeLogicApp.id, contributorRoleId)
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', contributorRoleId)
    principalId: changeCollectionTimeLogicApp.identity.principalId
    principalType: 'ServicePrincipal'
    description: 'Allows the ChangeCollectionTime Logic App to make Azure Management API calls for Logic App management'
  }
}

// Microsoft Sentinel Contributor role assignment at workspace level
// This allows the ChangeCollectionTime Logic App to access Sentinel resources
resource sentinelContributorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(logAnalyticsWorkspace.id, changeCollectionTimeLogicApp.id, sentinelContributorRoleId)
  scope: logAnalyticsWorkspace
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', sentinelContributorRoleId)
    principalId: changeCollectionTimeLogicApp.identity.principalId
    principalType: 'ServicePrincipal'
    description: 'Allows the ChangeCollectionTime Logic App to access Microsoft Sentinel resources and operations'
  }
}

// Output the principal ID for reference
output changeCollectionTimeLogicAppPrincipalId string = changeCollectionTimeLogicApp.identity.principalId

// Output the role assignment IDs for each playbook
output roleAssignmentIds array = [for (playbook, index) in veeamCollectionPlaybooks: {
  playbookName: playbook
  roleAssignmentId: logicAppContributorRoleAssignments[index].id
  resourceId: veeamCollectionLogicApps[index].id
}]

// Output summary for verification
output assignmentSummary object = {
  sourceLogicApp: changeCollectionTimeLogicAppName
  targetPlaybooks: veeamCollectionPlaybooks
  roleAssigned: 'Logic App Contributor'
  assignmentScope: 'Individual Logic App level'
  totalAssignments: length(veeamCollectionPlaybooks)
  contributorRoleAssigned: true
  contributorScope: 'Resource Group level'
  sentinelContributorAssigned: true
  sentinelContributorScope: 'Log Analytics Workspace level'
  workspaceName: workspaceName
}

// Output the Contributor role assignment details
output contributorRoleAssignment object = {
  roleAssignmentId: contributorRoleAssignment.id
  roleName: 'Contributor'
  principalId: changeCollectionTimeLogicApp.identity.principalId
  scope: resourceGroup().id
}

// Output the Sentinel Contributor role assignment details
output sentinelRoleAssignment object = {
  roleAssignmentId: sentinelContributorRoleAssignment.id
  roleName: 'Microsoft Sentinel Contributor'
  principalId: changeCollectionTimeLogicApp.identity.principalId
  scope: logAnalyticsWorkspace.id
  workspaceName: workspaceName
}

