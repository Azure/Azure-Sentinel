@description('Sentinel workspace name')
param workspaceName string 

param location string = resourceGroup().location
param functionAppName string = 'veeamapp'
param storageAccountName string = '${functionAppName}st'
param relayNamespaceName string = '${functionAppName}relay'

module customTables '../CustomTables/MainTables.bicep' = {
  name: 'deployMainTables'
  params: {
    workspaceName: workspaceName
  }
}
module Roles '../CustomTables/CustomTablesRoles.bicep' = {
  name: 'CustomTablesRoles'
  params: {
    functionAppName: functionAppName
    logAnalyticsWorkspaceName: workspaceName
    version: '1.0'
  }
  dependsOn: [functionApp]
}

param packageUri string = 'https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Data%20Connectors/VeeamConn.zip?raw=true'

@description('App Service Plan SKU for the Function App')
@allowed(['B1', 'S3', 'P2v3'])
param appServicePlanSku string = 'B1'

param keyVaultName string = '${functionAppName}kv'
param vbrWatchlistAlias string = 'vbr_settings'
param voneWatchlistAlias string = 'vone_settings'
param covewareFindingsWatchlistAlias string = 'coveware_settings'

param  covewareBaseUrl string = 'https://api.coveware.com/recon/v1'
param  covewareAuthUrl string = 'https://cognito-idp.us-east-1.amazonaws.com/'
param covewareEarliestEventTime string = substring(dateTimeAdd(utcNow(), '-P90D'), 0, 10) 
param covewareMaxRiskLevel string = 'high'

var dceMalwareEventsIngestionEndpoint string = customTables.outputs.malwareDCEIngestionEndpoint
var dcrMalwareEventsImmutableId string = customTables.outputs.malwareDCRImmutableId
var dcrMalwareEventsStreamName string = 'Custom-${customTables.outputs.malwareTableName}'

var dceBestPracticeAnalysisIngestionEndpoint string = customTables.outputs.bestPracticesDCEIngestionEndpoint
var dcrBestPracticeAnalysisImmutableId string = customTables.outputs.bestPracticesDCRImmutableId
var dcrBestPracticeAnalysisStreamName string = 'Custom-${customTables.outputs.bestPracticesTableName}'

var dceAuthorizationEventsIngestionEndpoint string = customTables.outputs.authorizationDCEIngestionEndpoint
var dcrAuthorizationEventsImmutableId string = customTables.outputs.authorizationDCRImmutableId
var dcrAuthorizationEventsStreamName string = 'Custom-${customTables.outputs.authorizationTableName}'

var dceTriggeredAlarmIngestionEndpoint string = customTables.outputs.triggeredAlarmsDCEIngestionEndpoint
var dcrTriggeredAlarmImmutableId string = customTables.outputs.triggeredAlarmsDCRImmutableId
var dcrTriggeredAlarmStreamName string = 'Custom-${customTables.outputs.triggeredAlarmsTableName}'

var dceCovewareFindingsIngestionEndpoint string = customTables.outputs.CovewareFindingsDCEIngestionEndpoint
var dcrCovewareFindingsImmutableId string = customTables.outputs.CovewareFindingsDCRImmutableId
var dcrCovewareFindingsStreamName string = 'Custom-${customTables.outputs.CovewareFindingsTableName}'

var dceSessionIngestionEndpoint string = customTables.outputs.sessionDCEIngestionEndpoint
var dcrSessionImmutableId string = customTables.outputs.sessionDCRImmutableId
var dcrSessionStreamName string = 'Custom-${customTables.outputs.sessionTableName}'
 
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-06-01' existing = {
  name: workspaceName
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2021-06-01' = {
  name: storageAccountName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${functionAppName}-ai'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// Define SKU mappings for different App Service Plan tiers
var skuMappings = {
  B1: {
    name: 'B1'
    tier: 'Basic'
    capacity: 1
  }
  S3: {
    name: 'S3'
    tier: 'Standard'
    capacity: 1
  }
  P1v2: {
    name: 'P1v2'
    tier: 'PremiumV2'
    capacity: 1
  }
  P2v3: {
    name: 'P2v3'
    tier: 'PremiumV3'
    capacity: 1
  }
}

resource appServicePlan 'Microsoft.Web/serverfarms@2021-03-01' = {
  name: functionAppName
  location: location
  sku: skuMappings[appServicePlanSku]
}

resource keyVault 'Microsoft.KeyVault/vaults@2024-11-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    // enablePurgeProtection: Omitted - defaults to false for new vaults, cannot be explicitly set to false
  }
}

// assign keyvault admin role to the function app managed identity

var keyVaultAdminRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '00482a5a-887f-4fb3-b363-3b7fe8e74483')

resource keyVaultAdminRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, functionApp.id, keyVaultAdminRoleId)
  scope: keyVault
  properties: {
    description: 'Assigns Key Vault Administrator role to Function App managed identity for secret management'
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: keyVaultAdminRoleId
  }
}

// create secrets with keys: CovewareServerClientId, CovewareServerPasswordId, CovewareServerUsernameId with value "UNDEFINED"
resource covewareServerClientIdSecret 'Microsoft.KeyVault/vaults/secrets@2024-11-01' = {
  name: 'CovewareServerClientId'
  parent: keyVault
  properties: {
    value: 'UNDEFINED'
  }
}

resource covewareServerPasswordIdSecret 'Microsoft.KeyVault/vaults/secrets@2024-11-01' = {
  name: 'CovewareServerPasswordId'
  parent: keyVault
  properties: {
    value: 'UNDEFINED'
  }
}

resource covewareServerUsernameIdSecret 'Microsoft.KeyVault/vaults/secrets@2024-11-01' = {
  name: 'CovewareServerUsernameId'
  parent: keyVault
  properties: {
    value: 'UNDEFINED'
  }
}


resource functionApp 'Microsoft.Web/sites@2021-03-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      cors: {
        allowedOrigins: ['*']
        supportCredentials: false
      }
      appSettings: [        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${listKeys(storageAccount.id, '2021-04-01').keys[0].value};EndpointSuffix=${environment().suffixes.storage}'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'dotnet-isolated'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: applicationInsights.properties.InstrumentationKey
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: applicationInsights.properties.ConnectionString
        }
        {
          name: 'ApplicationInsightsAgent_EXTENSION_VERSION'
          value: '~3'
        }
        {
          name: 'DCE_MALWARE_EVENTS_INGESTION_ENDPOINT'
          value: dceMalwareEventsIngestionEndpoint
        }
        {
          name: 'DCR_MALWARE_EVENTS_IMMUTABLE_ID'
          value: dcrMalwareEventsImmutableId
        }
        {
          name: 'DCR_MALWARE_EVENTS_STREAM_NAME'
          value: dcrMalwareEventsStreamName
        }
        {
          name: 'DCE_BEST_PRACTICE_ANALYSIS_INGESTION_ENDPOINT'
          value: dceBestPracticeAnalysisIngestionEndpoint
        }
        {
          name: 'DCR_BEST_PRACTICE_ANALYSIS_IMMUTABLE_ID'
          value: dcrBestPracticeAnalysisImmutableId
        }
        {
          name: 'DCR_BEST_PRACTICE_ANALYSIS_STREAM_NAME'
          value: dcrBestPracticeAnalysisStreamName
        }     
           {
          name: 'DCE_AUTHORIZATION_EVENTS_INGESTION_ENDPOINT'
          value: dceAuthorizationEventsIngestionEndpoint
        }
        {
          name: 'DCR_AUTHORIZATION_EVENTS_IMMUTABLE_ID'
          value: dcrAuthorizationEventsImmutableId
        }
        {
          name: 'DCR_AUTHORIZATION_EVENTS_STREAM_NAME'
          value: dcrAuthorizationEventsStreamName
        }
        {
          name: 'DCE_TRIGGERED_ALARM_INGESTION_ENDPOINT'
          value: dceTriggeredAlarmIngestionEndpoint
        }
        {
          name: 'DCR_TRIGGERED_ALARM_IMMUTABLE_ID'
          value: dcrTriggeredAlarmImmutableId
        }
        {
          name: 'DCR_TRIGGERED_ALARM_STREAM_NAME'
          value: dcrTriggeredAlarmStreamName
        }
        {
          name: 'DCE_COVEWARE_FINDINGS_INGESTION_ENDPOINT'
          value: dceCovewareFindingsIngestionEndpoint
        }
        {
          name: 'DCR_COVEWARE_FINDINGS_IMMUTABLE_ID'
          value: dcrCovewareFindingsImmutableId
        }
        {
          name: 'DCR_COVEWARE_FINDINGS_STREAM_NAME'
          value: dcrCovewareFindingsStreamName
        }
        {
          name: 'DCE_SESSION_DATA_INGESTION_ENDPOINT'
          value: dceSessionIngestionEndpoint
        }
        {
          name: 'DCR_SESSION_DATA_IMMUTABLE_ID'
          value: dcrSessionImmutableId
        }
        {
          name: 'DCR_SESSION_DATA_STREAM_NAME'
          value: dcrSessionStreamName
        }
        {
          name: 'KEY_VAULT_NAME'
          value: keyVaultName
        }
        {
          name: 'WORKSPACE_ID'
          value: logAnalyticsWorkspace.properties.customerId
        }
        {
          name: 'VBR_WATCHLIST_ALIAS'
          value: vbrWatchlistAlias
        }
        {
          name: 'VONE_WATCHLIST_ALIAS'
          value: voneWatchlistAlias
        }
        {
          name: 'COVEWARE_WATCHLIST_ALIAS'
          value: covewareFindingsWatchlistAlias
        }     
           {
          name: 'COVEWARE_AUTH_URL'
          value: covewareAuthUrl
        }
        {
          name: 'COVEWARE_BASE_URL'
          value: covewareBaseUrl
        }
        {
          name: 'COVEWARE_EARLIEST_EVENT_TIME'
          value: covewareEarliestEventTime
        }
        {
          name: 'COVEWARE_MAX_RISK_LEVEL'
          value: covewareMaxRiskLevel
        }
        {
          name: 'SUBSCRIPTION_ID'
          value: subscription().subscriptionId
        }
        {
          name: 'RESOURCE_GROUP_NAME'
          value: resourceGroup().name
        }
        {
          name: 'WORKSPACE_NAME'
          value: workspaceName
        }
        {
          name:'WEBSITE_RUN_FROM_PACKAGE'
          value: packageUri
        }
      ]
    }
  }
}

resource authSettings 'Microsoft.Web/sites/config@2021-02-01' = {
  name: 'authsettingsV2'
  parent: functionApp
  properties: {
    globalValidation: {
      unauthenticatedClientAction: 'AllowAnonymous'
    }
  }
}
resource relayNamespace 'Microsoft.Relay/namespaces@2024-01-01' = {
  name: relayNamespaceName
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
}


@description('Name for the diagnostic setting on the Function App')
param diagnosticSettingName string = '${functionAppName}-diag'

resource functionDiag 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: diagnosticSettingName
  scope: functionApp
  properties: {
    workspaceId: logAnalyticsWorkspace.id

    logs: [
      {
        category: 'FunctionAppLogs'
        enabled: true
        retentionPolicy: { enabled: false
           days: 0 }
      }
    ]

    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
        retentionPolicy: { enabled: false
           days: 0 }
      }
    ]
  }
}
