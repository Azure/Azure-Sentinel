param dcrName string
param location string
param workspaceResourceId string
param dceId string

@description('Canonical source streams')
param streams object = {
  assets: 'Custom-CyeraAssets_SRC'
  identities: 'Custom-CyeraIdentities_SRC'
  classifications: 'Custom-CyeraClassifications_SRC'
  issues: 'Custom-CyeraIssues_SRC'
}

@description('Output streams → tables')
param outputs object = {
  assetsMs: 'Custom-CyeraAssets_MS_CL'
  assetsExt: 'Custom-CyeraAssets_CL'
  identities: 'Custom-CyeraIdentities_CL'
  classifications: 'Custom-CyeraClassifications_CL'
  issues: 'Custom-CyeraIssues_CL'
}

var transformAssetsMs = loadTextContent('../../artifacts/transforms/transform.assets_ms.kql')
var transformAssetsExt = loadTextContent('../../artifacts/transforms/transform.assets_ext.kql')

resource dcr 'Microsoft.Insights/dataCollectionRules@2024-03-11' = {
  name: dcrName
  location: location
  properties: {
    dataCollectionEndpointId: dceId
    destinations: {
      logAnalytics: [
        { workspaceResourceId: workspaceResourceId, name: 'la' }
      ]
    }
    streamDeclarations: {
      '${streams.assets}': { columns: [] }
      '${streams.identities}': { columns: [] }
      '${streams.classifications}': { columns: [] }
      '${streams.issues}': { columns: [] }
    }
    dataFlows: [
      { streams: [ streams.assets ], destinations: [ 'la' ], outputStream: outputs.assetsMs, transformKql: transformAssetsMs },
      { streams: [ streams.assets ], destinations: [ 'la' ], outputStream: outputs.assetsExt, transformKql: transformAssetsExt },
      { streams: [ streams.identities ], destinations: [ 'la' ], outputStream: outputs.identities },
      { streams: [ streams.classifications ], destinations: [ 'la' ], outputStream: outputs.classifications },
      { streams: [ streams.issues ], destinations: [ 'la' ], outputStream: outputs.issues }
    ]
  }
}

output dcrId string = dcr.id
output dcrImmutableId string = dcr.properties.immutableId
