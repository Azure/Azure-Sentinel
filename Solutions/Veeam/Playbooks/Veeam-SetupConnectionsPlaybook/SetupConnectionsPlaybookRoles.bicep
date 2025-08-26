// Bicep template to assign required roles for Veeam Setup Connections Playbook
// This template assigns the following roles to the Logic App's managed identity:
// 1. Sentinel Contributor role on the Microsoft Sentinel workspace
// 2. Key Vault Administrator role on the Key Vault resource
// 3. Website Contributor role on the Function App resource
// 4. Azure Relay Owner role on the Relay Namespace resource

@description('Name of the Logic App that needs role assignments')
param logicAppName string = 'Veeam-SetupConnectionsPlaybook'

@description('Name of the Microsoft Sentinel workspace')
param sentinelWorkspaceName string = 'vz-publish-without-sylog'

@description('Name of the Azure Function App')
param functionAppName string = 'nosyslogapp'


var keyVaultName = '${functionAppName}kv'

var relayNamespaceName string = '${functionAppName}relay'

@description('Resource group name where all resources are located')
param resourceGroupName string = resourceGroup().name

// Built-in role definition IDs for Azure RBAC
var roleDefinitions = {
  sentinelContributor: 'ab8e14d6-4a74-4a29-9ba8-549422addade'  // Microsoft Sentinel Contributor
  keyVaultAdministrator: '00482a5a-887f-4fb3-b363-3b7fe8e74483'  // Key Vault Administrator
  websiteContributor: 'de139f84-1756-47ae-9be6-808fbbe84772'    // Website Contributor
  azureRelayOwner: '2787bf04-f1f5-4bfe-8383-c8a24483ee38'       // Azure Relay Owner
}

// Get references to existing resources
resource logicApp 'Microsoft.Logic/workflows@2019-05-01' existing = {
  name: logicAppName
}

resource sentinelWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' existing = {
  name: sentinelWorkspaceName
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource functionApp 'Microsoft.Web/sites@2023-01-01' existing = {
  name: functionAppName
}

resource relayNamespace 'Microsoft.Relay/namespaces@2021-11-01' existing = {
  name: relayNamespaceName
}

// Role assignment: Sentinel Contributor on Sentinel workspace
resource sentinelContributorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(sentinelWorkspace.id, logicApp.id, roleDefinitions.sentinelContributor)
  scope: sentinelWorkspace
  properties: {
    description: 'Assigns Sentinel Contributor role to Logic App managed identity for Veeam integration'
    principalId: logicApp.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitions.sentinelContributor)
  }
}

// Role assignment: Key Vault Administrator on Key Vault
resource keyVaultAdministratorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, logicApp.id, roleDefinitions.keyVaultAdministrator)
  scope: keyVault
  properties: {
    description: 'Assigns Key Vault Administrator role to Logic App managed identity for secret management'
    principalId: logicApp.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitions.keyVaultAdministrator)
  }
}

// Role assignment: Website Contributor on Function App
resource websiteContributorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(functionApp.id, logicApp.id, roleDefinitions.websiteContributor)
  scope: functionApp
  properties: {
    description: 'Assigns Website Contributor role to Logic App managed identity for Function App management'
    principalId: logicApp.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitions.websiteContributor)
  }
}

// Role assignment: Azure Relay Owner on Relay Namespace
resource azureRelayOwnerRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(relayNamespace.id, logicApp.id, roleDefinitions.azureRelayOwner)
  scope: relayNamespace 
  properties: {
    description: 'Assigns Azure Relay Owner role to Logic App managed identity for hybrid connection management'
    principalId: logicApp.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitions.azureRelayOwner)
  }
}

// Outputs
@description('The principal ID of the Logic App managed identity')
output logicAppPrincipalId string = logicApp.identity.principalId

@description('Role assignment IDs for tracking')
output roleAssignmentIds object = {
  sentinelContributor: sentinelContributorRoleAssignment.name
  keyVaultAdministrator: keyVaultAdministratorRoleAssignment.name
  websiteContributor: websiteContributorRoleAssignment.name
  azureRelayOwner: azureRelayOwnerRoleAssignment.name
}

@description('Resource IDs for reference')
output resourceIds object = {
  logicApp: logicApp.id
  sentinelWorkspace: sentinelWorkspace.id
  keyVault: keyVault.id
  functionApp: functionApp.id
  relayNamespace: relayNamespace.id
}
