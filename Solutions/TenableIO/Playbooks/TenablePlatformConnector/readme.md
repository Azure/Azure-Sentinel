# Tenable Platform API Logic Apps Custom connector

This Custom Connector is used for connection to [Tenable Platform API](https://developer.tenable.com/reference/navigate#tenable-platform).

### Authentication methods supported by this connector

* API Key authentication

### Prerequisites in Tenable

To get Tenable API key, follow the instructions in the [documentation](https://developer.tenable.com/docs/authorization).

### Actions supported by Tenable Platform API Custom Connector

| **Component** | **Description** |
| --------- | -------------- |
| **List permissions** | Returns a list of all permissions in your container. |
| **List user group permissions** | Returns a list of all permissions defined in your container. |
| **List user permissions** | Returns a list of all permissions defined in your container. |
| **Get permission details** | Returns the details for the specified permission. |
| **Search assets** | Returns a list of assets based on the specified search criteria. |
| **Create export** | Exports assets and findings data that matches the request criteria. |
| **Search export jobs** | Returns a list of export jobs. |
| **Get export details** | Returns the details and status of the specified export job. |
| **Delete export job** | Delete an export job regardless of its status. |
| **Download export** | Downloads export data. |
| **Search vulnerability findings** | Returns a list of vulnerability findings. |
| **List groups** | Returns the group list. |
| **List users in group** | Return the group user list. |
| **Delete user from group** | Deletes a user from the group. |
| **Get user details** | Returns details for a specific user. |
| **Delete user** | Deletes a user. |
| **Update user** | Updates an existing user account. |
| **Enable user account** | Enables or disables an existing user account. |



### Deployment instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTenableIO%2FPlaybooks%2FTenablePlatformConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTenableIO%2FPlaybooks%2FTenablePlatformConnector%2Fazuredeploy.json)