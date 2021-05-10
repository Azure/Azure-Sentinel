#  Fortinet Function APP connector

This function app connects to Fortinet service end point and fetch the details of the entities of the fortinet firewall.

![Fortinet](./Fortinetlogo.png)<br>

### Authentication criteria for Function app
* User Assigned identity
### Prerequisites for deploying Custom Connector
* Add new secret to the existing Key Vault (Create new if not exist) for Fortinet API key and capture the secret identifier of new key
* Fortinet service end point should be known (ex: https://{yourVMIPorTrafficmanagername}/)

## Actions supported by function app

| **Component**  | **Description** |
| ------------- | ------------- |
| **List address objects**  | Fetch the list of address objects  |
| **List address groups**  | Fetch the list of address groups  |
| **Get an address object**  | Retrieve the details of an address object  |
| **Get a policy object details** | Retrieve the details of policy object |

### Deployment instructions 
- Deploy the Function app by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
- Fill the required parameters:
    * Function App Name :- Enter the function name which globaly Unique and it should not contain any special Symbol  [Function app naming convention](https://docs.microsoft.com/azure/azure-functions/functions-create-function-app-portal)
    * Key Vault Secret identifier:- Capture from key vault secret identifier of the your secret (ex: https://{keyvaultname}.vault.azure.net/secrets/{secretidentifiername})
    * Service Endpoint:-            Enter the Fortinet service end point (ex: https://{YourVMIPorTrafficmanagement})
    * Managed Identities Name: Enter the managed identity name (ex: managed identities name)[Create user assigned manage identity](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/how-to-manage-ua-identity-portal)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FFortinet-FortiGate%2FFunctionApp%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FFortinet-FortiGate%2FFunctionApp%2Fazuredeploy.json)

## Usage Examples
* Get an address object details
* Get all address groups 


## Post Deployment steps

* Create User Managed Identity in your subscription by following document. Refer this link [Create Managed Identity ](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/how-to-manage-ua-identity-portal#create-a-user-assigned-managed-identity)
* Assign role to user assigned identity. Refer this link [Assign role to user ](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/how-to-manage-ua-identity-portal#assign-a-role-to-a-user-assigned-managed-identity)
* Open created function app, follow below steps or refer steps documented [Function app setting](https://docs.microsoft.com/azure/logic-apps/logic-apps-azure-functions#enable-authentication-for-functions)
     - Go to Authentication / Authorization option   
     - Enable App Service Authentication
     - Select "Login with Azure Active Directory" for Action to take when request is not authenticated
     - Select Azure Active Directory as Authentication Providers
     - Select advanced option from the management mode and fill details 
     - UserIdentity object id as client ID (ex: b1fd400b-e34b-40c0-996f506d8a98)
     - Issuer url (format should be https://sts.windows.net/<tenentID>), refer for to get tenentID [Get tenentID](https://ms.portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/Overview)
     - Allow token Audiences (ex: https://management.azure.com )
     - Click ok
     - Click on save
* Open function app and go to Identify and capture the object ID [Capture Object ID](https://docs.microsoft.com/azure/app-service/overview-managed-identity?tabs=dotnet)
* Add azure function app to key Vault access policy [Add access policy](https://docs.microsoft.com/azure/key-vault/general/assign-access-policy-portal)



