param scopedResourceName string
param roleDefId string
param principalId string

resource scopedResource 'Microsoft.OperationalInsights/workspaces@2022-10-01' existing = {
 name: scopedResourceName  
}

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2020-10-01-preview' = {
  name: guid(scopedResource.id, roleDefId, principalId)
  scope: scopedResource
  properties: {
    roleDefinitionId: roleDefId
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}
