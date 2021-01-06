# Okta Logic Apps Custom connector

This custom connector connects to Okta service end point and perform defined automated actions on the Okta user accounts 
### Authentication methods this connector supports

*  API Key authentication

### Prerequisites for deploying Custom Connector
1. Okta service end point should be known(ex : https://{yourOktaDomain}/)
2. Generate an API key.Refer this link [ how to generate the API Key](https://developer.okta.com/docs/guides/create-an-api-token/overview/)
3. API key needs to have admin previligies to perform specific actions like expire password on okta accounts


## Actions supported by okta custom connector

| Component | Description |
| --------- | -------------- |
| **Get user** | Get user information by User Id  |
| **Suspend user** | Suspend a user.|
| **Unsuspend user** | Unsuspend a user.|
| **Clear User Sessions** | Forcing a user to authenticate on the next operation.|
| **Expire Password** | This will cause a user to be forced to change their current password the next time they login to a connected system.|
| **Reset Password** |Resets a user password with a temp password or a password link.|
| **Get users groups** | Get all the groups a user belongs to.|
| **Update User** | Updates a user's profile and/or credentials using strict-update semantics.  Change user attributes to enforce policies in Okta.|
| **Group – Add member** | Adds a user to a group |
| **Group – Remove member** | Removes a user from a group |
| **List group members** | Get a list of all members of a given group.|
| **List enrolled Factors** | Enumerates all of the enrolled Factors for the specified User|
| **Reset Factor** | Unenrolls an existing Factor for the specified user, allowing the user to enroll a new Factor |

### Deployment instructions 
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Custom Connector Name : Enter the Custom connector name (ex:contoso Okta connector)
    * Service Endpoint : Enter the okta service end point (ex:https://{yourOktaDomain})

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https://dev.azure.com/SentinelAccenture/Sentinel-Accenture%20Logic%20Apps%20connectors/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?path=%2FOktaCustomConnector%2Fazuredeploy&version=GBOkta) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://login.microsoftonline.us/organizations/oauth2/v2.0/authorize?client_id=c836cbdb-7a5b-44cc-a54f-564b4b486fc6&response_type=code%20id_token&scope=https%3A%2F%2Fmanagement.core.usgovcloudapi.net%2F%2Fuser_impersonation%20openid%20email%20profile&state=OpenIdConnect.AuthenticationProperties%3DaURMJdv8OOjkos8hJrPp2UR3SiCuzPqKSCojZXlvmudMu2wCQivYUBL-PUpm2VklFejdDnBr9Us32MzfuH8tith-XldC_OIlCqCjwB950H9ELHA76IfBBh19cTzh9-nsHhkQkk8wQDSE6bot7rUuEQB8IDVJgDMCfv1HYuUg9brFyPen2T4DF7f3SxN7Wwxfj87B5iDMqyoU1AHKentIKfwHsDQCVmhbtWdvSgPbWWABKGY-a7b1vkmjWNmo8x5v&response_mode=form_post&nonce=637443070124899368.YjM5MDcwYzMtODJkZC00MzRmLTgxNDctMjhhZjY0MWRmNjcxZGRiOWNmMmItMDAyNS00MTIxLWE4MDUtMjdiOTE4MWJhMjg0&redirect_uri=https%3A%2F%2Fportal.azure.us%2Fsignin%2Findex%2F&site_id=501430&msafed=0&client-request-id=5cc07576-a6f1-4a94-b26f-830ed1c4ad77&x-client-SKU=ID_NET45&x-client-ver=5.3.0.0)
## Usage Examples
* Suspend/unsuspend user accounts on Okta through playbook
* Expire password for user accounts on Okta through playbook
* Add user to okta groups through playbook



