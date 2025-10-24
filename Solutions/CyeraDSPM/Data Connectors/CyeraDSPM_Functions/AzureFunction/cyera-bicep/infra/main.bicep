targetScope = 'resourceGroup'

@description('Deployment location (must match LA workspace region)')
param location string

@description('Log Analytics workspace ARM resourceId')
param workspaceResourceId string

@description('Names for resources')
param dceName string = 'cyera-dce'
param dcrName string = 'cyera-dcr'
param storageAccountName string = 'stcyerafunc${uniqueString(resourceGroup().id)}'
param planName string = 'plan-cyera'
param functionAppName string = 'func-cyera-connector-${uniqueString(resourceGroup().id)}'

@description('Cyera credentials (use KeyVault in production)')
param cyeraClientId string
@secure()
param cyeraSecret string
param cyeraBaseUrl string = 'https://api.cyera.io'

@description('Whether to grant blob RBAC to the Function MI for state storage')
param enableBlobState bool = false

@description('Provide a public or SAS URL for the function package (zip). If empty, you must deploy code separately.')
param functionPackageUrl string = ''

// 1) DCE
module dce 'modules/dce.bicep' = {
  name: 'dce'
  params: {
    dceName: dceName
    location: location
  }
}

// 2) DCR (streams + transforms)
module dcr 'modules/dcr.bicep' = {
  name: 'dcr'
  params: {
    dcrName: dcrName
    location: location
    workspaceResourceId: workspaceResourceId
    dceId: dce.outputs.dceId
  }
}

// 3) LA tables (via deployment script + az rest)
module tables 'modules/tables.deploymentscript.bicep' = {
  name: 'tables'
  params: {
    workspaceResourceId: workspaceResourceId
    location: location
  }
}

// 4) Storage for Function
module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: {
    storageAccountName: storageAccountName
    location: location
  }
}

// 5) Function App + MSI + app settings
module func 'modules/function.bicep' = {
  name: 'function'
  params: {
    functionAppName: functionAppName
    planName: planName
    location: location
    storageAccountName: storage.outputs.storageName
    dceIngestBase: dce.outputs.dceIngestBase
    dcrImmutableId: dcr.outputs.dcrImmutableId
    cyeraBaseUrl: cyeraBaseUrl
    cyeraClientId: cyeraClientId
    cyeraSecret: cyeraSecret
    enableBlobState: enableBlobState
    functionPackageUrl: functionPackageUrl
  }
}

// 6) RBAC assignments for Function MI
module roles 'modules/roleAssignments.bicep' = {
  name: 'roles'
  params: {
    principalId: func.outputs.functionPrincipalId
    dcrScope: dcr.outputs.dcrId
    dceScope: dce.outputs.dceId
    storageScope: storage.outputs.storageId
    grantStorageBlobDataContributor: enableBlobState
  }
}

output dceId string = dce.outputs.dceId
output dcrId string = dcr.outputs.dcrId
output dcrImmutableId string = dcr.outputs.dcrImmutableId
output functionAppName string = functionAppName
