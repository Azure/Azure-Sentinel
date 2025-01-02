param FunctionAppName string
param Location string
param UserAssignedMiId string
param UserAssignedMiPrincipalId string
param HostingPlanId string
param EnablePrivateNetworking bool
param FunctionAppSubnetId string = ''
param AppSettings array
param DeployFunctionCode bool
param RoleIdOwner string

resource functionApp 'Microsoft.Web/sites@2024-04-01' = {
  name: FunctionAppName
  location: Location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${UserAssignedMiId}': {}
    }
  }
  kind: 'functionapp'
  properties: {
    serverFarmId: HostingPlanId
    keyVaultReferenceIdentity: UserAssignedMiId
    httpsOnly: true
    clientCertEnabled: true
    clientCertMode: 'OptionalInteractiveUser'
    virtualNetworkSubnetId: EnablePrivateNetworking == true ? FunctionAppSubnetId : (null)
    vnetContentShareEnabled: EnablePrivateNetworking == true ? true : false
    vnetRouteAllEnabled: EnablePrivateNetworking == true ? true : false 
    siteConfig: {
      appSettings: AppSettings
      powerShellVersion: '7.4'
      minTlsVersion: '1.2' 
      ftpsState: 'Disabled'
      http20Enabled: true
      alwaysOn: true
      publicNetworkAccess: 'Enabled'
      cors: {
        allowedOrigins: [
          'https://portal.azure.com'
        ] 
      }  
    }
  }
}

resource roleAssignmentFa 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (DeployFunctionCode == true) {
  name: guid(subscription().id, resourceGroup().id, UserAssignedMiId)
  scope: functionApp
  properties: {
    principalId: UserAssignedMiPrincipalId
    roleDefinitionId: RoleIdOwner
    principalType: 'ServicePrincipal'
  }
}

output functionAppName string = functionApp.name
output functionAppId string = functionApp.id
