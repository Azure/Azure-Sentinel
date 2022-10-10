# Minemeld- Add Indicators in Minemeld Playbook
 ## Summary
 When a new Azure Sentinel incident is created, this playbook gets triggered and performs below actions
 1. Searches for the matching indicator info of Entities (IP Address, FileHash, URL) in Minemeld 
 2. If indicators are not found, this playbook adds the new indicators to Minemeld Local database (Separate indicators for each IP Address, FileHash, URL that are 
 present in Sentinel incident)
 

### 
requisites 
1. Minemeld Custom Connector needs to be deployed prior to the deployment of this playbook under the same subscription.
2. Basic authentication of user and password is required for accessing Minemeld API.

### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMinemeld%2FPlaybooks%2FMinemeldPlaybooks%2FMinemeld-CreateIndicator%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMinemeld%2FPlaybooks%2F%2FMinemeldPlaybooks%2FMinemeld-CreateIndicator%2Fazuredeploy.json)

2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here (Ex: Minemeld-CreateIndicator)
    * Custom Connector Name: Enter the Minemeld custom connector name here (Ex: MinemeldCustomConnector)
    
### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for Minemeld Api  Connection (For authorizing the Minemeld GraphQL API connection, user and password to be provided)
#### b. Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with entity mapping of URL ,FileHash or IP Address. 
2. Configure the automation rules to trigger this playbook
