param principalId string
param principalType string = 'ServicePrincipal'
param dcrScope string
param dceScope string
param storageScope string = ''
param grantStorageBlobDataContributor bool = false

@description('Monitoring Contributor (built-in)')
param monitoringContributorRoleId string = '749f88d5-cbae-40b8-bcfc-ebaf66f30cf2'
@description('Storage Blob Data Contributor (built-in)')
param storageBlobDataContributorRoleId string = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'

resource raDcr 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(dcrScope, principalId, 'monitoring-contrib')
  scope: dcrScope
  properties: {
    principalId: principalId
    principalType: principalType
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', monitoringContributorRoleId)
  }
}

resource raDce 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(dceScope, principalId, 'monitoring-contrib')
  scope: dceScope
  properties: {
    principalId: principalId
    principalType: principalType
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', monitoringContributorRoleId)
  }
}

resource raStorage 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (grantStorageBlobDataContributor && storageScope != '') {
  name: guid(storageScope, principalId, 'blob-data-contrib')
  scope: storageScope
  properties: {
    principalId: principalId
    principalType: principalType
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRoleId)
  }
}
