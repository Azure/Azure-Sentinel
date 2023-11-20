/*
Deploys a Function App that queries the 1Password API and sends the data to a Log Analytics workspace.
The Function App is deployed with an Application Insights instance, a Key Vault instance, and a Storage Account.
The Key Vault instance is used to store the API Key for the 1Password API and the Storage Account is used to store cursors.
*/
/* TODO: User defined functions are not supported and have not been decompiled */

@description('Specifies the name of the Function App.')
param functionName string

@description('uri to the API endpoint to query data.')
param apiEndpoint string = 'https://events.1password.com'

@description('Provide schedule in the form of a [cron expression](https://en.wikipedia.org/wiki/Cron#CRON_expression)')
param functionSchedule string = '0 */5 * * * *'

@description('Specifies the name of the Data Collection Endpoint to create')
param dataCollectionEndpoint string

@description('Specifies the API Key to connect to the API of 1Password')
@secure()
param apiToken string

@description('Specifies the name location of the resources.')
param location string = resourceGroup().location

var storageAccountName = substring(concat(substring(toLower(replace(functionName, '-', '')), 0, 9), uniqueString(resourceGroup().id)), 0, 20)
var keyVaultName = substring(concat(substring(functionName, 0, 9), uniqueString(resourceGroup().id)), 0, 20)
var storageSuffix = environment().suffixes.storage
var keyVaultSecretReader = '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/4633458b-17de-408a-b874-0445c86b69e6'
var metricsPublisher = '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/3913510d-42f4-4e42-8a64-420c390055eb'
var uniqueRoleGuidMetricsPublisher = guid(reference(storageAccountName).id)
var uniqueRoleGuidKeyVaultSecretReader = guid(reference(keyVaultName).id)

// This resource block references an existing Log Analytics workspace.
resource dataCollectionRule 'Microsoft.Insights/dataCollectionRules@2022-06-01' existing = {
  name: '1Password'
}

resource applictionInsights 'Microsoft.Insights/components@2015-05-01' = {
  name: functionName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    ApplicationId: functionName
  }
}

// Creates a Key Vault resource with the specified name and properties.
// The resource is dependent on the Microsoft_Web_sites_function resource.
resource keyVault 'Microsoft.KeyVault/vaults@2016-10-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    enableRbacAuthorization: true
  }
  dependsOn: [
    Microsoft_Web_sites_function
  ]
}

resource keyVaultName_AzureWebJobsStorage 'Microsoft.KeyVault/vaults/secrets@2016-10-01' = {
  parent: keyVault
  name: 'AzureWebJobsStorage'
  properties: {
    value: 'DefaultEndpointsProtocol=https;AccountName=${toLower(storageAccountName)};AccountKey=${listKeys(storageAccount.id, '2019-06-01').keys[0].value};EndpointSuffix=${toLower(storageSuffix)}'
    contentType: 'string'
    attributes: {
      enabled: true
    }
  }
}

resource keyVaultName_API_Key 'Microsoft.KeyVault/vaults/secrets@2016-10-01' = {
  parent: keyVault
  name: 'API-Key'
  properties: {
    value: apiToken
    contentType: 'string'
    attributes: {
      enabled: true
    }
  }
}

resource KeyVaultSecretReader 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  scope: keyVault
  name: uniqueRoleGuidKeyVaultSecretReader
  properties: {
    roleDefinitionId: keyVaultSecretReader
    principalId: reference(Microsoft_Web_sites_function.id, '2019-08-01', 'full').identity.principalId
  }
}

resource MetricsPublisher 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  scope: dataCollectionRule
  name: uniqueRoleGuidMetricsPublisher
  properties: {
    roleDefinitionId: metricsPublisher
    principalId: reference(Microsoft_Web_sites_function.id, '2019-08-01', 'full').identity.principalId
  }
}

resource Microsoft_Web_serverfarms_function 'Microsoft.Web/serverfarms@2018-02-01' = {
  name: functionName
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  kind: 'functionapp'
  properties: {
    name: functionName
    workerSize: '0'
    workerSizeId: '0'
    numberOfWorkers: '1'
  }
}

resource Microsoft_Web_sites_function 'Microsoft.Web/sites@2021-03-01' = {
  name: functionName
  location: location
  kind: 'functionapp'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    name: functionName
    serverFarmId: Microsoft_Web_serverfarms_function.id
    httpsOnly: true
    clientAffinityEnabled: true
    alwaysOn: true
    siteConfig: {
      powerShellVersion: '7.2'
    }
  }
  dependsOn: [
    storageAccount
    applictionInsights
  ]
}

resource functionName_appsettings 'Microsoft.Web/sites/config@2021-03-01' = {
  parent: Microsoft_Web_sites_function
  name: 'appsettings'
  kind: 'string'
  properties: {
    APPINSIGHTS_INSTRUMENTATIONKEY: applictionInsights.properties.InstrumentationKey
    APPLICATIONINSIGHTS_CONNECTION_STRING: applictionInsights.properties.ConnectionString
    AzureWebJobsStorage: NF.secretName(keyVaultName, 'AzureWebJobsStorage')
    WEBSITE_CONTENTAZUREFILECONNECTIONSTRING: NF.secretName(keyVaultName, 'AzureWebJobsStorage')
    APIKey: NF.secretName(keyVaultName, 'API-Key')
    WEBSITE_CONTENTSHARE: toLower(functionName)
    FUNCTIONS_EXTENSION_VERSION: '~4'
    FUNCTIONS_WORKER_RUNTIME: 'powershell'
    FUNCTIONS_WORKER_RUNTIME_VERSION: '7.2'
    powerShellVersion: '7.2'
    schedule: functionSchedule
    apiEndpoint: apiEndpoint
    dataCollectionEndpoint: dataCollectionEndpoint
  }
  dependsOn: [

    keyVault
    keyVaultName_AzureWebJobsStorage
    extensionResourceId(keyVault.id, 'Microsoft.Authorization/roleAssignments/', uniqueRoleGuidKeyVaultSecretReader)
  ]
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
    tier: 'Standard'
  }
  kind: 'StorageV2'
  properties: {
    networkAcls: {
      bypass: 'AzureServices'
      virtualNetworkRules: []
      ipRules: []
      defaultAction: 'Allow'
    }
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
    encryption: {
      services: {
        file: {
          keyType: 'Account'
          enabled: true
        }
        blob: {
          keyType: 'Account'
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
  }
}

resource storageAccountName_default 'Microsoft.Storage/storageAccounts/blobServices@2019-06-01' = {
  parent: storageAccount
  name: 'default'
  sku: {
    name: 'Standard_LRS'
    tier: 'Standard'
  }
  properties: {
    cors: {
      corsRules: []
    }
    deleteRetentionPolicy: {
      enabled: false
    }
  }
}

resource Microsoft_Storage_storageAccounts_fileServices_storageAccountName_default 'Microsoft.Storage/storageAccounts/fileServices@2019-06-01' = {
  parent: storageAccount
  name: 'default'
  sku: {
    name: 'Standard_LRS'
    tier: 'Standard'
  }
  properties: {
    cors: {
      corsRules: []
    }
  }
}

resource storageAccountName_default_azure_webjobs_hosts 'Microsoft.Storage/storageAccounts/blobServices/containers@2019-06-01' = {
  parent: storageAccountName_default
  name: 'azure-webjobs-hosts'
  properties: {
    publicAccess: 'None'
  }
}

resource storageAccountName_default_azure_webjobs_secrets 'Microsoft.Storage/storageAccounts/blobServices/containers@2019-06-01' = {
  parent: storageAccountName_default
  name: 'azure-webjobs-secrets'
  properties: {
    publicAccess: 'None'
  }
}

resource storageAccountName_default_storageContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2019-06-01' = {
  parent: storageAccountName_default
  name: 'cursors'
  properties: {
    publicAccess: 'None'
  }
}


output functionAppName string = functionName
output storageAccountName string = storageAccountName
output keyVaultName string = keyVaultName
