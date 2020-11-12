# Incident-Assignment-Shifts


author: Jeremy Tan

This playbook will assign an Incident to an owner based on the Shifts schedule in Microsoft Teams.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIncident-Assignment-Shifts%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIncident-Assignment-Shifts%2Fazuredeploy.json)





## Pre-requisites:

Ensure you have the following details to hand:


### 1. Sentinel Workspace details

- Workspace Name.

- Workspace Resource Group Name.

### 2. Service Principal
Create or use an existing Service Principal with the Azure Sentinel Responder role.

**Steps to create a new Service Principal:**

Follow the steps in this [link](https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal):

- Register an application to Azure AD and create a Service Principal.

- Create a new application secret.

- Assign a role to the application (assign the **Azure Sentinel Responder** role).


### 3. Shifts for Teams
- You must have the [Shifts](https://support.microsoft.com/office/get-started-in-shifts-5f3e30d8-1821-4904-be26-c3cd25a497d6) schedule setup in Microsoft Teams.

- The Shifts schedule must be published (**Share with team**).

  <img src="https://github.com/tatecksi/SentinelPlaybooks/blob/master/Sentinel_Incident_Assignment_Shifts/media/pic2.png" width="700" height="350">


### 4. Permission on Azure AD
- There is an Azure AD connector in this Logic App to get details for a user.
- To use the Azure AD connector, you need to **Sign-in** with an account with the following administrator permissions:
    - Group.ReadWrite.All
    - User.ReadWrite.All
    - Directory.ReadWrite.All
    
### 5. An O365 account to be used to send email notification
- Login details of the O365 account.



## Post Deployment Configuration:

- Once deployed, edit the Logic App and find the connectors (5 in total) that has been marked with <img src="https://github.com/tatecksi/SentinelPlaybooks/blob/master/Sentinel_Incident_Assignment_Shifts/media/pic1.png" width="30" height="30">. 
- Fix these connectors by adding a new connection to each connector within your Logic App and sign in to authenticate.
- For the Shifts connector, make sure you have selected the Teams channel with a Shifts schedule.
    
   <img src="https://github.com/tatecksi/SentinelPlaybooks/blob/master/Sentinel_Incident_Assignment_Shifts/media/Pic3.png" width="500" height="120">
    
- Save the Logic App once you have completed the above steps.





## Incident Assignment Logic:

Incidents are assigned to users based on the following criteria:

- Users who are on shift during the time that the incident is triggeres and the Logic App runs.
- Users who still have at least **1** hours left before going off shift. 
  
  You can change this value by modifying the below variable:

    <img src="https://github.com/tatecksi/SentinelPlaybooks/blob/master/Sentinel_Incident_Assignment_Shifts/media/pic4.png" width="500" height="180">

- Users who have had the fewer incidents assigned to them over the past 24 hours will be assigned incident first.

- If an incident is already assigned to someone, triggering this Playbook will not perform reassignment.

  Although not recommended, but you can modify the following variable to allow reassignment:

    <img src="https://github.com/tatecksi/SentinelPlaybooks/blob/master/Sentinel_Incident_Assignment_Shifts/media/pic5.png" width="500" height="180">


## Email Notification:

- When an incident is assigned, the incident owner will be notified via email.
- Below is the sample email notification:

   <img src="https://github.com/tatecksi/SentinelPlaybooks/blob/master/Sentinel_Incident_Assignment_Shifts/media/pic6.png" width="500" height="240">

- The email body has a banner with colour mapped to incident's severity (High=red, Medium=orange, Low=yellow and Informational=grey).
