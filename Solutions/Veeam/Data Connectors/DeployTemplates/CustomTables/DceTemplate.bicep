@description('The Azure region where resources will be deployed')
param location string

@description('Name of the Data Collection Endpoint to be created')
param dceName string

resource dceResource 'Microsoft.Insights/dataCollectionEndpoints@2023-03-11' = {
  name: dceName
  location: location
  tags: {
    displayName: dceName
    purpose: 'Sentinel Custom Data Collection'
  }
  properties: {
    configurationAccess: {}
    logsIngestion: {}
    metricsIngestion: {}
    networkAcls: {
      publicNetworkAccess: 'Enabled'
    }
  }
}

output dceIngestionEndpoint string = dceResource.properties.logsIngestion.endpoint
output dceResourceId string = dceResource.id
