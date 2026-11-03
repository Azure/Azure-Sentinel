extension 'br:mcr.microsoft.com/bicep/extensions/microsoftgraph/v1.0:1.0.0'

@description('Unique name and display name for the Sentinel-to-XDR delegated public client app registration.')
param appUniqueName string = 'Sentinel-XDR-CustomDetection'

@description('Space-separated Microsoft Graph delegated scopes to grant admin consent for.')
@allowed([
  'ThreatHunting.Read.All'
  'CustomDetection.ReadWrite.All'
  'ThreatHunting.Read.All CustomDetection.ReadWrite.All'
  'CustomDetection.ReadWrite.All ThreatHunting.Read.All'
  'User.Read ThreatHunting.Read.All'
  'User.Read CustomDetection.ReadWrite.All'
  'User.Read ThreatHunting.Read.All CustomDetection.ReadWrite.All'
  'User.Read CustomDetection.ReadWrite.All ThreatHunting.Read.All'
])
param delegatedScopes string = 'User.Read ThreatHunting.Read.All CustomDetection.ReadWrite.All'

@description('OAuth2 permission grant consent type: Principal (least-privilege single user) or AllPrincipals (tenant-wide).')
@allowed([
  'Principal'
  'AllPrincipals'
])
param consentType string = 'AllPrincipals'

@description('Entra ID user objectId when consentType is Principal.')
param principalId string = ''

@description('Also instantiate and grant delegated scopes to Microsoft Azure CLI (04b07795-8ddb-461a-bbee-02f9e1bf7b46) so az rest / az account get-access-token can query Graph Hunting API directly.')
param grantToAzureCli bool = false

// 1. Reference the tenant's Microsoft Graph resource service principal (00000003-0000-0000-c000-000000000000)
resource msGraphSp 'Microsoft.Graph/servicePrincipals@v1.0' existing = {
  appId: '00000003-0000-0000-c000-000000000000'
}

// 2. Create/update the dedicated Sentinel-XDR public client application with requiredResourceAccess
resource xdrApp 'Microsoft.Graph/applications@v1.0' = {
  uniqueName: appUniqueName
  displayName: appUniqueName
  signInAudience: 'AzureADMyOrg'
  isFallbackPublicClient: true
  publicClient: {
    redirectUris: [
      'http://localhost'
    ]
  }
  requiredResourceAccess: [
    {
      resourceAppId: '00000003-0000-0000-c000-000000000000'
      resourceAccess: [
        {
          // CustomDetection.ReadWrite.All
          id: 'c34088fb-0649-4714-af0b-bcbfec155897'
          type: 'Scope'
        }
        {
          // ThreatHunting.Read.All
          id: 'b152eca8-ea73-4a48-8c98-1a6742673d99'
          type: 'Scope'
        }
      ]
    }
  ]
}

// 3. Create/update the Enterprise Application (servicePrincipal) for the custom app
resource xdrSp 'Microsoft.Graph/servicePrincipals@v1.0' = {
  appId: xdrApp.appId
}

// 4. Grant delegated permission consent (oauth2PermissionGrants) to the custom app
resource xdrGrant 'Microsoft.Graph/oauth2PermissionGrants@v1.0' = {
  clientId: xdrSp.id
  consentType: consentType
  principalId: consentType == 'Principal' ? principalId : null
  resourceId: msGraphSp.id
  scope: delegatedScopes
}

// 5. Optionally ensure the Microsoft Azure CLI servicePrincipal exists in the tenant and grant it the same scopes
resource azCliSp 'Microsoft.Graph/servicePrincipals@v1.0' = if (grantToAzureCli) {
  appId: '04b07795-8ddb-461a-bbee-02f9e1bf7b46'
}

resource azCliGrant 'Microsoft.Graph/oauth2PermissionGrants@v1.0' = if (grantToAzureCli) {
  clientId: azCliSp!.id
  consentType: consentType
  principalId: consentType == 'Principal' ? principalId : null
  resourceId: msGraphSp.id
  scope: delegatedScopes
}

output customAppId string = xdrApp.appId
output customAppObjectId string = xdrApp.id
output customServicePrincipalId string = xdrSp.id
