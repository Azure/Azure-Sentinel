# Cisco Umbrella Management API Logic Apps Custom connector

This Custom Connector is used for connection to Cisco Umbrella Management API.

### Authentication methods supported by this connector

* Basic authentication

### Prerequisites in Cisco Umbrella

To get Cisco Umbrella Management API credentials, follow the instructions:

1. Log in to your Cisco Umbrella dashboard.
2. Navigate to Admin > API Keys, and click Create; or in a management console (Multi-org, MSP, or MSSP), navigate to Settings > API Keys, and click Add.
3. Select Umbrella Management and click Create.
4. Expand Umbrella Management, copy Your Key and Your Secret.
5. Click *To keep it secure, ...* checkbox, and then click Close.

## Actions supported by Cisco Umbrella Management API custom connector

| **Component** | **Description** |
| --------- | -------------- |
| **Retrieve all destination lists** | Retrieve all destination lists of organization |
| **Create a destination list** | Create a destination list |
| **Get a destination list** | Return destination list |
| **Get list of destinations related to destination list** | Get list of destinations related to destination list |
| **Add list of destinations to destination list** | Add list of destinations to destination list |
| **Delete list of destinations from destination list** | Delete list of destinations from destination list |

### Deployment instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoUmbrella%2FPlaybooks%2FCiscoUmbrellaManagementAPIConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoUmbrella%2FPlaybooks%2FCiscoUmbrellaManagementAPIConnector%2Fazuredeploy.json)