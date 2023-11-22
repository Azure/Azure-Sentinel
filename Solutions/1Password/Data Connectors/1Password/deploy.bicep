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

param location string = resourceGroup().location

@description('Specifies the URI to the package to deploy')
param packageUri string = 'https://github.com/azurekid/Azure-Sentinel/raw/feature/1password/Solutions/1Password/Data%20Connectors/1Password/function.zip'

var storageAccountName = '${substring(toLower(replace(functionName, '-', '')), 0, 9)}${uniqueString(resourceGroup().id)}'
var keyVaultName = '${substring(functionName, 0, 9)}${uniqueString(resourceGroup().id)}'
var storageSuffix = environment().suffixes.storage
var keyVaultSecretReader = '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/4633458b-17de-408a-b874-0445c86b69e6'
var metricsPublisher = '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/3913510d-42f4-4e42-8a64-420c390055eb'
var uniqueRoleGuidMetricsPublisher = guid(storageAccount.id)
var uniqueRoleGuidKeyVaultSecretReader = guid(keyVault.id)

resource datacollectionRule 'Microsoft.Insights/dataCollectionRules@2021-09-01-preview' existing = {
  name: '1Password'
}

resource AppInsights 'Microsoft.Insights/components@2015-05-01' = {
  name: functionName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    ApplicationId: functionName
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2016-10-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enabledForDeployment: true
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    enableRbacAuthorization: true
  }
  dependsOn: [
    functionApp
  ]
}

resource AzureWebJobsStorage 'Microsoft.KeyVault/vaults/secrets@2016-10-01' = {
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

resource APIKey 'Microsoft.KeyVault/vaults/secrets@2016-10-01' = {
  parent: keyVault
  name: 'APIKey'
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
    principalId: functionApp.identity.principalId
  }
}

resource MetricsPublisher 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  scope: datacollectionRule
  name: uniqueRoleGuidMetricsPublisher
  properties: {
    roleDefinitionId: metricsPublisher
    principalId: functionApp.identity.principalId
  }
}

resource serverfarms 'Microsoft.Web/serverfarms@2018-02-01' = {
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

resource functionApp 'Microsoft.Web/sites@2021-03-01' = {
  name: functionName
  location: location
  kind: 'functionapp'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    name: functionName
    serverFarmId: serverfarms.id
    httpsOnly: true
    clientAffinityEnabled: true
    alwaysOn: true
    siteConfig: {
      powerShellVersion: '7.2'
    }
  }
  dependsOn: [
    storageAccount
  ]
}

resource functionName_appsettings 'Microsoft.Web/sites/config@2021-03-01' = {
  parent: functionApp
  name: 'appsettings'
  kind: 'string'
  properties: {
    APPINSIGHTS_INSTRUMENTATIONKEY: AppInsights.properties.InstrumentationKey
    APPLICATIONINSIGHTS_CONNECTION_STRING: AppInsights.properties.ConnectionString
    AzureWebJobsStorage: '@Microsoft.KeyVault(VaultName={keyVaultName};SecretName=AzureWebJobsStorage)'
    WEBSITE_CONTENTAZUREFILECONNECTIONSTRING: '@Microsoft.KeyVault(VaultName={keyVaultName};SecretName=AzureWebJobsStorage)'
    WEBSITE_CONTENTSHARE: toLower(functionName)
    FUNCTIONS_EXTENSION_VERSION: '~4'
    FUNCTIONS_WORKER_RUNTIME: 'powershell'
    FUNCTIONS_WORKER_RUNTIME_VERSION: '7.2'
    schedule: functionSchedule
    apiEndpoint: apiEndpoint
    APIKey: '@Microsoft.KeyVault(VaultName={keyVaultName};SecretName=APIKey)'
    dataCollectionEndpoint: dataCollectionEndpoint
  }
  dependsOn: [
    KeyVaultSecretReader
    AzureWebJobsStorage
  ]
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
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

// resource BlobService 'Microsoft.Storage/storageAccounts/blobServices@2019-06-01' = {
//   parent: storageAccount
//   name: 'default'
//   properties: {
//     cors: {
//       corsRules: []
//     }
//     deleteRetentionPolicy: {
//       enabled: false
//     }
//   }
// }

resource fileServices 'Microsoft.Storage/storageAccounts/fileServices@2019-06-01' = {
  name: '${storageAccount.name}/default'
  properties: {
    cors: {
      corsRules: []
    }
  }
}

resource azure_webjobs_hosts 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${storageAccount.name}/azure-webjobs-hosts'
  properties: {
    publicAccess: 'None'
  }
}

resource azure_webjobs_secrets 'Microsoft.Storage/storageAccounts/blobServices/containers@2019-06-01' = {
  name: '${storageAccount.name}/azure-webjobs-secrets'
  properties: {
    publicAccess: 'None'
  }
}

resource storageContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2019-06-01' = {
  name: '${storageAccount.name}/cursors'
  properties: {
    publicAccess: 'None'
  }
}

resource shares 'Microsoft.Storage/storageAccounts/fileServices/shares@2019-06-01' = {
  name: '${storageAccount.name}/${storageAccount.name}'
  properties: {
    shareQuota: 5120
  }
}

output functionAppName string = functionName
output storageAccountName string = storageAccountName
output keyVaultName string = keyVaultName
