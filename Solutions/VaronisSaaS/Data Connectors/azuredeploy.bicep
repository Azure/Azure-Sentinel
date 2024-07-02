@description('Storage Account type.')
@allowed([
  'Standard_LRS'
  'Standard_GRS'
  'Standard_RAGRS'
])
param storageAccountType string = 'Standard_LRS'

@description('Location for all resources.')
param location string = resourceGroup().location

@description('Name of the Log Analytics workspace used by Microsoft Sentinel.')
param logAnalyticsWorkspaceName string

@description('FQDN/IP for the Integration Connection - Enter the Varonis Web Interface address (e.g. https://example.varonis.com).')
param varonisFQDN string

@description('Copy the API Key from the Varonis web interface.')
@secure()
param varonisApiKey string

@description('Enter the past number of days from which to start retrieving alerts. Up to 30 days and 1,000 alerts are supported.')
@minValue(0)
@maxValue(30)
param alertRetrievalStartPoint int = 7

@description('To retrieve alerts related to specific threat detection policies, enter the relevant policy names. RECOMMENDED: LEAVE THIS BLANK TO RETRIEVE ALL ALERTS (DEFAULT).')
param threatDetectionPolicies string = ''

@description('Specify the Varonis alert status.')
param alertStatus string = 'New, Under Investigation'

@description('Specify the alert severity.')
param alertSeverity string = 'Low, Medium, High'

var functionAppName = 'VaronisSaaS-${uniqueString(resourceGroup().id)}'
var functionWorkerRuntime = 'dotnet'
var functionPlanOS = 'Linux'
var functionAppPlanSku = 'Y1'
var packageUri = 'https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/VaronisSaaS/Data%20Connectors/Varonis.Sentinel.Functions.zip'
var linuxFxVersion = 'DOTNET|6.0'
var hostingPlanName = functionAppName
var applicationInsightsName = functionAppName
var storageAccountName = '${uniqueString(resourceGroup().id)}sa'
var isReserved = ((functionPlanOS == 'Linux') ? true : false)

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-05-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'Storage'
}

resource Microsoft_Web_serverfarms_hostingPlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: hostingPlanName
  location: location
  sku: {
    tier: 'Dynamic'
    name: functionAppPlanSku
  }
  properties: {
    reserved: isReserved
  }
  kind: (isReserved ? 'linux' : 'windows')
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: applicationInsightsName
  location: location
  tags: {
    'hidden-link:${resourceId('Microsoft.Web/sites',applicationInsightsName)}': 'Resource'
  }
  properties: {
    Application_Type: 'web'
  }
  kind: 'web'
}

resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: functionAppName
  location: location
  kind: (isReserved ? 'functionapp,linux' : 'functionapp')
  properties: {
    reserved: isReserved
    serverFarmId: (contains(functionAppPlanSku, 'EP')
      ? Microsoft_Web_serverfarms_hostingPlan.id
      : Microsoft_Web_serverfarms_hostingPlan.id)
    siteConfig: {
      linuxFxVersion: (isReserved ? linuxFxVersion : null)
      appSettings: [
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: applicationInsights.properties.InstrumentationKey
        }
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower(functionAppName)
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: functionWorkerRuntime
        }
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: packageUri
        }
        {
          name: 'VaronisFQDN_IP'
          value: varonisFQDN
        }
        {
          name: 'VaronisApiKey'
          value: varonisApiKey
        }
        {
          name: 'LogAnalyticsKey'
          value: listKeys(
            resourceId('Microsoft.OperationalInsights/workspaces', logAnalyticsWorkspaceName),
            '2021-06-01'
          ).primarySharedKey
        }
        {
          name: 'LogAnalyticsWorkspace'
          value: reference(
            resourceId('Microsoft.OperationalInsights/workspaces', logAnalyticsWorkspaceName),
            '2021-06-01'
          ).customerId
        }
        {
          name: 'AlertRetrievalStart'
            value: '${alertRetrievalStartPoint}'
        }
        {
          name: 'AlertSeverity'
          value: alertSeverity
        }
        {
          name: 'ThreatDetectionPolicies'
          value: threatDetectionPolicies
        }
        {
          name: 'AlertStatus'
          value: alertStatus
        }
      ]
    }
  }
}
