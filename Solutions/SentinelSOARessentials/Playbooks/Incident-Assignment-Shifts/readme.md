# Incident-Assignment-Shifts


author: Jeremy Tan

version: 2.2

This playbook will assign an Incident to an owner based on the Shifts schedule in Microsoft Teams.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSentinelSOARessentials%2FPlaybooks%2FIncident-Assignment-Shifts%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSentinelSOARessentials%2FPlaybooks%2FIncident-Assignment-Shifts%2Fazuredeploy.json)





## Pre-requisites:

Ensure you have the following details:


### 1. User account or Service Principal or Managed Identity with Microsoft Sentinel Responder role
- Create or use an existing user account/ Service Principal/ Managed Identity with Microsoft Sentinel Responder role.

- This will be used in Microsoft Sentinel connectors (Incident Trigger, Update incident & Add comment to incident) and a HTTP connector.

- This example will walk you through using System Managed Identity for the above connectors.


### 2. Setup Shifts schedule
- You must have the [Shifts](https://support.microsoft.com/office/get-started-in-shifts-5f3e30d8-1821-4904-be26-c3cd25a497d6) schedule setup in Microsoft Teams.

- The Shifts schedule must be published (**Share with team**).

  <img src="https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Incident-Assignment-Shifts/images/Pic2.png" width="700" height="350">

### 3. User account with Owner role in Microsoft Teams
- Create or use an existing user account or managed identity with **Owner** role in a Team.

- The user account will be used in Shifts connector (List all shifts).


### 4. User account or Service Principal with Log Analytics Reader role
- Create or use an existing user account or Service Principal with Log Analytics Reader role on the Microsoft Sentinel workspace.

- The user account or Service Principal will be used in Azure Monitor Logs connector (Run query and list results).


### 5. An O365 account to be used to send email notification
- The user account will be used in O365 connector (Send an email).


## Post Deployment Configuration:

### 1. Enable Managed Identity and configure role assignment
- Once deployed, go to the Logic App's blade and click on **Identity** under Settings.
- Select **On** under the **System assigned** tab. Click **Save** and select **Yes** when prompted.

  <img src="https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Incident-Assignment-Shifts/readmeImages/Pic8.png" width="900" height="360">
   <br />    
   
- Click on **Azure role assignments** to assign role to the Managed Identity.

 <img src="https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Incident-Assignment-Shifts/readmeImages/Pic9.png" width="900" height="280">
   <br />  
   
- Click on **+ Add role assignment**. 
- Select **Resource group** under Scope and select the **Subscription** and **Resource group** where the Microsoft Sentinel **Workspace** is located. 
  Select **Microsoft Sentinel Responder** under Role and click **Save**.


### 2. Configure connections
- Edit the Logic App or go to Logic app designer.
- Expand each step to find the following connectors (6 in total) with <img src="https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Incident-Assignment-Shifts/readmeImages/Pic1.png" width="30" height="30">. 
  1. Incident Trigger
  2. Update Incident
  3. Add comment to incident
  4. List all shifts
  5. Run query and list results
  6. Send an email  
- Fix these connectors by adding a new connection to each connector and sign in with the accounts described under pre-requisites.


### 3. Select the Shifts schedule
- Edit the Logic App or go to Logic app designer.
- Find the **List all shifts** connector, click on the **X** sign next to Team field for the drop-down list to appear.
    
   <img src="https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Incident-Assignment-Shifts/images/Pic3.png" width="500" height="140">
   <br />    
   
- Select the Teams channel with your Shifts schedule from the drop-down list. 
   
   <img src="https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Incident-Assignment-Shifts/images/Pic7.png" width="500" height="200">
   
    
- Save the Logic App once you have completed the above steps.





## Incident Assignment Logic:

Incidents are assigned to users based on the following criteria:

- Only users who have started their shifts during the time the Logic App runs will be considered.
- Users who still have at least **1** hours left before going off shift. 
  
  You can change this value by modifying the below variable:

    <img src="https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Incident-Assignment-Shifts/images/Pic4.png" width="500" height="180">

- User with the least incidents assigned on the current Shift will be assigned incident first.

    
    
## Email Notification:

- When an incident is assigned, the incident owner will be notified via email.
- Below is the sample email notification:

   <img src="https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Incident-Assignment-Shifts/images/Pic6.png" width="500" height="240">

- The email body has a banner with colour mapped to incident's severity (High=red, Medium=orange, Low=yellow and Informational=grey).
