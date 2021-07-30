# HaveIBeenPwned ResponseonTeams playbook
 ## Summary
 When a new Azure Sentinel incident is created, this playbook gets triggered and performs below actions:
 1. Fetches the breach information from HaveIBeenPwned.
 1. Send an email to breached user account and change incident configuration based on SOC action.
 1. Add a comment to the incident with the information collected from the HaveIBeenPwned, action taken by SOC and close the incident.

**Adaptive card that will be sent in the Teams SOC Channel:**

![HaveIBeenPwned-ResponseonTeams](./Images/Adaptivecard.png)

**Playbook overview:**
![HaveIBeenPwned-ResponseonTeams](./Images/PlaybookdesignerLight.png)<br>
![HaveIBeenPwned-ResponseonTeams](./Images/PlaybookdesignerDark.png)<br>

**Email sent to pwned user:**

![HaveIBeenPwned-Email](./Images/Email.png)
### Prerequisites 

1. HaveIBeenPwned Custom Connector needs to be deployed prior to the deployment of this playbook under the same subscription and under the same resource group. Capture the name for the connector.
2. Generate an API key. [Refer this link on how to generate the API Key](https://haveibeenpwned.com/API/Key).
3. Users must have access to Microsoft Teams and they should be a part of a Teams channel and also "Power Automate" app should be installed in the Microsoft Teams channel.

### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will lead you to the wizard for deploying an ARM Template.
2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here (Ex: HaveIBeenPwned_ResponseOnTeams)
    * Custom connector Name: Enter the name of your HaveIBeenPwned Custom Connector (e.g. HaveIBeenPwned_CustomConnector)

* Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FHaveIBeenPwned%2FPlaybooks%2FHaveIBeenPwned_ResponseOnTeams%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FHaveIBeenPwned%2FPlaybooks%2FHaveIBeenPwned_ResponseOnTeams%2Fazuredeploy.json)
    
### Post-Deployment instructions 
After deploying the playbook ,open the designer view of the playbook, in the "Post an Adaptive Card to a Teams channel and wait for a response" action, select the team and channel name from the dropdown to post the adaptive card.
####a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Teams connection  resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for other connections such as Office 365 connection and HaveIBeenPwned API Connection (For authorizing the HaveIBeenPwned API connection, API Key needs to be provided)
####b. Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with risky account.
2. Configure the automation rules to trigger this playbook.

## Playbook steps explained

###When Azure Sentinel incident creation rule is triggered
Azure Sentinel incident is created. The playbook receives the incident as the input.

###Entities - Get Accounts
Get the list of risky Accounts as entities from the Incident.

###Initialize the below variables

  a. BreachInfo - Append the account breach information.

  b. ActionTaken - Append the action taken by SOC.

  c. Breaches - Assign account breach Information for a particular account.

 ###Compose image to add in the incident
This action will compose the HaveIBeenPwned image to add to the incident comments.

###For each Account
* Get all the breaches for the account from HaveIBeenPwned API action.
* Based on the response from API,the following actions will be taken:
 * If breach information found, post an adaptive card and wait for the SOC action, if SOC has selected "Send email and Update Incident" then send email to user and update incident else Ignore
 * If no breach information found: Update incident with no breach information found

![comment to the incident](./Images/IncidentcommentLight.PNG)
![comment to the incident](./Images/IncidentcommentDark.PNG)