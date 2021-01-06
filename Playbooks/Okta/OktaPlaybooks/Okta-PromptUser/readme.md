# Okta-Prompt User Playbook
 ## Summary

When a new sentinal incident is created, this playbook gets triggered and performs below actions
1. An adaptive card is sent to the risky user asking if he has done any malicious activity on his Okta account
2. If user confirms yes, the incident will be closed with the user details
3. Else,the user sessions will be cleared and reset password link will be sent to user 
4. An adaptvie card is sent to the SOC Teams channel, providing information about the incident and risky user details.The SOC can investigate further on the user.


![Okta-Prompt User](https://dev.azure.com/SentinelAccenture/a94836bc-ff1d-480a-af0f-79be76a3c9e4/_apis/git/repositories/d1bebabf-1feb-4577-8c0b-7d41b70f49df/items?path=%2FOktaPlaybooks%2FOkta-PromptUser%2FOkta-PromptUser.PNG&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=Okta&resolveLfs=true&%24format=octetStream&api-version=5.0)
### Prerequisites 
1. Okta custom connector needs to be deployed prior to the deployment of this playbook under the same subscription.
2. Generate an API key.Refer this link [ how to generate the API Key](https://developer.okta.com/docs/guides/create-an-api-token/overview/)

### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Playbook Name : Enter the playbook name here (ex:OktaPlaybook)
    * Teams GroupId : Enter the Teams channel id to send the adaptive card
    * Teams ChannelId : Enter the Teams Group id to send the adaptive card
     [Refer the below link to get the channel id and group id](https://docs.microsoft.com/en-us/powershell/module/teams/get-teamchannel?view=teams-ps)

### Post-Deployment instructions 
####a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for other connections such as Teams connection and Okta Api  Connection (For authorizing the Okta API connection, the API Key needs to be provided)
####b. Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with risky user account 
2. Configure the automation rules to trigger this playbook



[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fdev.azure.com/SentinelAccenture/Sentinel-Accenture%20Logic%20Apps%20connectors/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?version=GBOkta&path=%2FOktaPlaybooks%2FOkta-PromptUser%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://login.microsoftonline.us/organizations/oauth2/v2.0/authorize?client_id=c836cbdb-7a5b-44cc-a54f-564b4b486fc6&response_type=code%20id_token&scope=https%3A%2F%2Fmanagement.core.usgovcloudapi.net%2F%2Fuser_impersonation%20openid%20email%20profile&state=OpenIdConnect.AuthenticationProperties%3DaURMJdv8OOjkos8hJrPp2UR3SiCuzPqKSCojZXlvmudMu2wCQivYUBL-PUpm2VklFejdDnBr9Us32MzfuH8tith-XldC_OIlCqCjwB950H9ELHA76IfBBh19cTzh9-nsHhkQkk8wQDSE6bot7rUuEQB8IDVJgDMCfv1HYuUg9brFyPen2T4DF7f3SxN7Wwxfj87B5iDMqyoU1AHKentIKfwHsDQCVmhbtWdvSgPbWWABKGY-a7b1vkmjWNmo8x5v&response_mode=form_post&nonce=637443070124899368.YjM5MDcwYzMtODJkZC00MzRmLTgxNDctMjhhZjY0MWRmNjcxZGRiOWNmMmItMDAyNS00MTIxLWE4MDUtMjdiOTE4MWJhMjg0&redirect_uri=https%3A%2F%2Fportal.azure.us%2Fsignin%2Findex%2F&site_id=501430&msafed=0&client-request-id=5cc07576-a6f1-4a94-b26f-830ed1c4ad77&x-client-SKU=ID_NET45&x-client-ver=5.3.0.0)

## Playbook steps explained
###When Azure Sentinel incident creation rule is triggered

Azure Sentinel incident is created. The playbook receives the incident as the input.
###Entities - Get Accounts

Get the list of risky/malicious accounts as entities from the Incident
###For each-risky account received from the incident
Iterates on the accounts found in this incident (probably one) and performs the following:
For the risky user account, playbook uses "Get User" action to get user details from Okta
#### Posts an Adaptive card to  user 
In this step we post a message in Microsoft Teams to the risky user with Incident details and ask for his confirmation on the malicious activity described in the incident.
#### If Condition based on the user confirmation
#### If the user confirms it was him:
  a. Incident is commented with all the  details below
   * User information collected by "Get User" action from Okta
     User id, User name, User login, User email, User status, User created, User activated, User statusChanged, User lastLogin, User lastUpdated, User passwordChanged
   * Actions taken on Sentinel 

  b. Close Incident
#### If the user confirms it was not him:
  a. Playbook uses "Clear User Sessions" action to clear the user sessions in Okta

  b. Playbook uses "Reset Password" action to resest the password of the user in Okta


  c. SOC user will be sent an adaptive card with the user details, Incident information to investigate further

  d. Add a comment to the incident with the following details:
  
  * User information collected by "Get User" action from Okta such as
     * User id, User name,User login,User email,User status,User created,User activated,User statusChanged, User lastLogin, User lastUpdated, User passwordChanged  

  * Actions taken on Okta: Cleared the user sessions and reset the password of the user.

  * Actions taken on Sentinel: Informed the SOC admin about the risky user and asked him to investigate further

