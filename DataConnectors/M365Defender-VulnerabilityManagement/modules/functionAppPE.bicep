param FunctionAppName string
param FunctionAppId string
param PrivateEndpointSubnetId string
param Location string
param VnetId string

resource peFunctionApp 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-${FunctionAppName}'
  location: Location
  properties: { 
     subnet: {
      id: PrivateEndpointSubnetId
     }
     privateLinkServiceConnections: [
      {
        name: 'pe-${FunctionAppName}'
        properties: {
         privateLinkServiceId: FunctionAppId
         groupIds: [
          'sites'
         ] 
        }
      }
     ] 
  } 
}

resource privateDnsZoneFunctionApp 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.azurewebsites.net'
  location: 'global'
}

resource privateDnsZoneLinkFunctionApp 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  name: '${privateDnsZoneFunctionApp.name}-link'
  parent: privateDnsZoneFunctionApp
  location: 'global'
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: VnetId
    }  
  }   
}

resource peDnsGroupFunctionApp 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  name: 'dnsGroup'
  parent: peFunctionApp
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'config1'
        properties: {
          privateDnsZoneId: privateDnsZoneFunctionApp.id
        } 
      }
    ]
  }
}

output functionAppName string = FunctionAppName
