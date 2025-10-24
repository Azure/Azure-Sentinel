param dceName string
param location string

resource dce 'Microsoft.Insights/dataCollectionEndpoints@2024-03-11' = {
  name: dceName
  location: location
  properties: {
    networkAcls: {
      publicNetworkAccess: 'Enabled'
    }
  }
}

output dceId string = dce.id
output dceIngestBase string = 'https://${dce.name}.${location}-1.ingest.monitor.azure.com'
