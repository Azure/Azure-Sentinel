# Okta Logic Apps Custom connector

This custom connector connects to Okta service end point and perform defined automated actions on the Okta user accounts.
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

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FOkta%2FOktaCustomConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FOkta%2FOktaCustomConnector%2Fazuredeploy.json)

## Usage Examples
* Suspend/unsuspend user accounts on Okta through playbook
* Expire password for user accounts on Okta through playbook
* Add user to okta groups through playbook



