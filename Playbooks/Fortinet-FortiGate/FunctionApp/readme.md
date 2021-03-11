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
    * Function App Name :- Enter the function name which globaly Unique and it should not contain any special Symbol  [Function app naming convention](https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-function-app-portal)
    * Key Vault Secret identifier:- Capture from key vault secret identifier of the your secret (ex: https://{keyvaultname}.vault.azure.net/secrets/{secretidentifiername})
    * Service Endpoint:-            Enter the Fortinet service end point (ex: https://{YourVMIPorTrafficmanagement})
    * Managed Identities Name: Enter the managed identity name (ex: managed identities name)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https://dev.azure.com/SentinelAccenture/Sentinel-Accenture%20Logic%20Apps%20connectors/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?path=%2FOktaCustomConnector%2Fazuredeploy&version=GBOkta) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://login.microsoftonline.us/organizations/oauth2/v2.0/authorize?client_id=c836cbdb-7a5b-44cc-a54f-564b4b486fc6&response_type=code%20id_token&scope=https%3A%2F%2Fmanagement.core.usgovcloudapi.net%2F%2Fuser_impersonation%20openid%20email%20profile&state=OpenIdConnect.AuthenticationProperties%3DaURMJdv8OOjkos8hJrPp2UR3SiCuzPqKSCojZXlvmudMu2wCQivYUBL-PUpm2VklFejdDnBr9Us32MzfuH8tith-XldC_OIlCqCjwB950H9ELHA76IfBBh19cTzh9-nsHhkQkk8wQDSE6bot7rUuEQB8IDVJgDMCfv1HYuUg9brFyPen2T4DF7f3SxN7Wwxfj87B5iDMqyoU1AHKentIKfwHsDQCVmhbtWdvSgPbWWABKGY-a7b1vkmjWNmo8x5v&response_mode=form_post&nonce=637443070124899368.YjM5MDcwYzMtODJkZC00MzRmLTgxNDctMjhhZjY0MWRmNjcxZGRiOWNmMmItMDAyNS00MTIxLWE4MDUtMjdiOTE4MWJhMjg0&redirect_uri=https%3A%2F%2Fportal.azure.us%2Fsignin%2Findex%2F&site_id=501430&msafed=0&client-request-id=5cc07576-a6f1-4a94-b26f-830ed1c4ad77&x-client-SKU=ID_NET45&x-client-ver=5.3.0.0)
## Usage Examples
* Get an address object details
* Get all address groups 


## Post Deployment steps

* Create User Managed Identity in your subscription by following document. Refer this link [Create Managed Identity ](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/how-to-manage-ua-identity-portal#create-a-user-assigned-managed-identity)
* Assign role to user assigned identity. Refer this link [Assign role to user ](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/how-to-manage-ua-identity-portal#assign-a-role-to-a-user-assigned-managed-identity)
* Open created function app, follow below steps or refer steps documented [Function app setting](https://docs.microsoft.com/en-us/azure/logic-apps/logic-apps-azure-functions#enable-authentication-for-functions)
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
* Open function app and go to Identify and capture the object ID [Capture Object ID](https://docs.microsoft.com/en-us/azure/app-service/overview-managed-identity?tabs=dotnet)
* Add azure function app to key Vault access policy [Add access policy](https://docs.microsoft.com/en-us/azure/key-vault/general/assign-access-policy-portal)



