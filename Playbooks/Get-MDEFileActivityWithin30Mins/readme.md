# Get-MDEFileActivityWithin30Mins
author: Dennis Pike

## Overview
This Playbook queries Microsoft Defender for Endpoint telemetry data via the Microsoft 365 Defender Advanced Hunting API for all File Events (Read, Write, Modify, Delete) that occur within 30 minutes of the incident and adds a comment to the incident specifying the number of File Events and KQL query that will list all of the events.

## Required Paramaters
-Region
-Playbook Name
-User Name - this is used to pre-populate the username used in the various Azure connections 

an Azure AD App registration with required API permissions and secret will needed to provide the following parameters
https://docs.microsoft.com/en-us/microsoft-365/security/mtp/api-advanced-hunting?view=o365-worldwide

-Tenant ID
-Client ID
-Secret

### Necessary configuration steps

Once this Playbooks template is deployed, you will need to go into the Logic App, edit it and click on each of the steps that require an authenticated connection to your tenant and complete the connection process.  These steps will have and exclamation point showing that the connection needs to be completed.  Make sure to also open the "For each" step and the "Condition 2" step within it which also contains steps that require authenticated connections.

