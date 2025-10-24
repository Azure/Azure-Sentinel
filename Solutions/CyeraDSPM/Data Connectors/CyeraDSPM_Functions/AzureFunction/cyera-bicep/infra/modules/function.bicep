param functionAppName string
param planName string
param location string
param storageAccountName string

@description('DCE ingest base URL (e.g., https://<dce>.<region>-1.ingest.monitor.azure.com)')
param dceIngestBase string
@description('DCR immutable id (dcr-...)')
param dcrImmutableId string

// Cyera config
param cyeraBaseUrl string = 'https://api.cyera.io'
@secure()
param cyeraClientId string
@secure()
param cyeraSecret string

// Source stream names
param streams object = {
  assets: 'Custom-CyeraAssets_SRC'
  identities: 'Custom-CyeraIdentities_SRC'
  classifications: 'Custom-CyeraClassifications_SRC'
  issues: 'Custom-CyeraIssues_SRC'
}

// Optional state storage settings (blob based)
param enableBlobState bool = false
param stateContainer string = 'cyera-cursors'
param statePrefix string = 'cursors'

// Optional: run-from-package URL (SAS or public)
param functionPackageUrl string = ''

resource sa 'Microsoft.Storage/storageAccounts@2023-01-01' existing = {
  name: storageAccountName
}

var storageKey = listKeys(sa.id, '2023-01-01').keys[0].value
var jobsConn = 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${storageKey};EndpointSuffix=core.windows.net'

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  sku: { name: 'Y1', tier: 'Dynamic' }
  properties: { reserved: true }
}

resource site 'Microsoft.Web/sites@2023-12-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  identity: { type: 'SystemAssigned' }
  properties: {
    serverFarmId: plan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        { name: 'AzureWebJobsStorage'; value: jobsConn },
        { name: 'WEBSITE_RUN_FROM_PACKAGE'; value: functionPackageUrl },
        { name: 'CYERA_BASE_URL'; value: cyeraBaseUrl },
        { name: 'CYERA_CLIENT_ID'; value: cyeraClientId },
        { name: 'CYERA_SECRET'; value: cyeraSecret },
        { name: 'DCE_INGEST'; value: dceIngestBase },
        { name: 'DCR_IMMUTABLE_ID'; value: dcrImmutableId },
        { name: 'STREAM_ASSETS'; value: streams.assets },
        { name: 'STREAM_IDENTITIES'; value: streams.identities },
        { name: 'STREAM_CLASSIFICATIONS'; value: streams.classifications },
        { name: 'STREAM_ISSUES'; value: streams.issues },
        { name: 'FUNCTIONS_EXTENSION_VERSION'; value: '~4' },
        { name: 'FUNCTIONS_WORKER_RUNTIME'; value: 'python' }
      ]
    }
    httpsOnly: true
  }
}

resource siteSettings 'Microsoft.Web/sites/config@2023-12-01' = if (enableBlobState) {
  name: '${functionAppName}/appsettings'
  properties: {
    'STATE_ACCOUNT_URL': 'https://${storageAccountName}.blob.core.windows.net',
    'STATE_CONTAINER': stateContainer,
    'STATE_PREFIX': statePrefix
  }
}

output functionPrincipalId string = site.identity.principalId
output functionId string = site.id
