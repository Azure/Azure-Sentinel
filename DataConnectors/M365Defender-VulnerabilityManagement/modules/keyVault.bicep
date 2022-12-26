param kvName string
param location string
param skuFamily string
param skuName string
param principalId string
param secretPermissions array
param aclIpRules string = ''
param aclBypass string = 'None'
param aclDefaultAction string = 'AzureServices'

resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: kvName
  location: location
  properties: {
    sku: {
      family: skuFamily
      name: skuName
    }
    tenantId: subscription().tenantId
    accessPolicies: [
      {
        objectId: principalId
        permissions: {
          secrets: secretPermissions
        }
        tenantId: subscription().tenantId
      }
    ]
    networkAcls: {
      bypass: aclBypass
      defaultAction: aclDefaultAction
      ipRules: aclIpRules == '' ? [] : json('${'[{"value": "'}${replace(aclIpRules, ',', '"},{"value": "')}${'"}]'}')
    }
  }
}
