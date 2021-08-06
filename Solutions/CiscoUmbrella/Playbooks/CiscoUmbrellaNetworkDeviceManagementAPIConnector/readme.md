# Cisco Umbrella Network Device Management API Logic Apps Custom connector

This Custom Connector is used for connection to Cisco Umbrella Network Device Management API.

### Authentication methods supported by this connector

* Basic authentication

### Prerequisites in Cisco Umbrella

To get Cisco Umbrella Network Device Management API credentials, follow the instructions:

1. Log in to your Cisco Umbrella dashboard.
2. Navigate to Admin > API Keys and click Create.
3. Select Umbrella Network Devices and click Create.
4. Expand Umbrella Network Devices, copy Your Key and Your Secret.
5. Click *To keep it secure, ...* checkbox, and then click Close.

## Actions supported by Cisco Umbrella Network Device Management API custom connector

| **Component** | **Description** |
| --------- | -------------- |
| **Get organization id** | Get your organization id and name. |
| **List all policies of a network device** | List DNS and web policies associated with a network device. |
| **Assign a policy to an identity** | Add an Identity to a directly applied DNS or web policy. |
| **Delete an identity from a policy** | Remove an Identity from a directly applied DNS or web policy. |


### Deployment instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoUmbrella%2FPlaybooks%2FCiscoUmbrellaNetworkDeviceManagementAPIConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoUmbrella%2FPlaybooks%2FCiscoUmbrellaNetworkDeviceManagementAPIConnector%2Fazuredeploy.json)