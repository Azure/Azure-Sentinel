
# Illusive Active Defense Product Suite

# Table of Contents

1. [Executive Summary](#executive_summary)
   - [Azure Application Setup](#azureappsetup)
3. [Deploy Playbook templates](#deployall)
4. [Deployment instructions](#deployinstr)
5. [Test the playbook](#testplaybook)
<br>

<a name="executive_summary">

# Executive Summary

Configure Sentinel and load custom playbooks to have Illusive open Sentinel incidents, populate them with Illusive-based information, and automate incident response.
This document provides detailed instructions for setting, running, and using the Illusive Active Defense solution.
   <br>
   <b>Incident Enrichment – </b>leverages Sentinel analytic rules to discover Illusive-based alerts and report the associated data and forensics as Sentinel incident sets. 
Use this playbook to enrich Sentinel security incidents originating from Illusive with Illusive incident and forensics information. Illusive continues to enrich relevant Sentinel incidents as new events are detected. This is done using the Illusive API resource.   
   <br>
<b>Incident Response – </b>leverages CrowdStrike or Microsoft Defender for Endpoint integration to automate incident response when specified Illusive incidents are discovered. 
Use the playbook to quickly stop or slow down ransomware attacks and critical incidents detected by Illusive in your organization. Upon detection, Sentinel is instructed to use the triggering process information reported by Illusive remove or kill the process. If the triggering process cannot be killed, Sentinel is instructed to isolate the host. These capabilities are available for organizations with CrowdStrike Falcon or Microsoft Defender for Endpoint.   
   <br>
<b>Analytic Rule –</b> Trigger a Sentinel alert upon detecting an Illusive event and create a Sentinel incident. The Sentinel incident will correspond to the Illusive incident and will include all subsequent associated Illusive events.
   <br>

 ## Basic Requirements (set up in advance) 
   
Trigger a Sentinel alert upon detecting an Illusive event and create a Sentinel incident. The Sentinel incident will correspond to the Illusive incident and will include all subsequent associated Illusive events.

## Workflow 
   
1. Sentinel Workspace
2. Azure Application Setup 
3. Illusive API Key 
4. SIEM server integration 
   
## Locate the Sentinel Workspace
   
The Workspace name and its location in the Azure hierarchy (Resource group and Subscription) is required later on during this configuration.
   <br>
Steps to locate the Sentinel Workspace name:
   <br>
1. In the [Azure portal](https://portal.azure.com/), go to <b>Azure Sentinel</b>
   Type Azure Sentinel in the <b>Search bar</b>, or click on the Azure Sentinel icon
2. On the Azure Sentinel page, find the workspace within which the playbook and its API connection are deployed
3. Use the above highlighted name as the “Workspace Name” while deployment.

<a name="azureappsetup">
   
# Azure Application Setup
   
## Prerequisites
   An Azure account that has an active subscription.
## Register an Azure App
   
1. Login to [http://portal.azure.com/](http://portal.azure.com/) 
2. If you have access to multiple tenants, in the top menu, use the Directory + subscription filter to select the tenant in which you want to register the application
3. Search for and select Azure Active Directory.
4. Under Manage, select App registrations>New registration.The Register an application page appears.
5. Specify a Name for your application.
Conform to company naming conventions. Do not use “illusive” or any other word that might reveal the existence of Illusive in the environment. 
6. Under Supported account types, select Accounts in this organizational directory only.
7. To complete the initial app registration, click Register.
8. Go to the created application’s Overview page.
9. Copy and save the Application (client) ID and the Directory (tenant) ID. You need these to configure the Playbooks.
10. Generate and save a Client Secret. 
    - Click Certificates & Secrets.
    - Click New Client Secret.
    - Add a Description for the Client Secret.
    - Select an Expiry date for the Client Secret.
    - Click Add 
    - Copy and save the secret Value. You need these to configure the Playbooks.
11. Give API permissions to the application.
    - Go to API Permissions.
    - Click Add a permission.
    - Under Microsoft APIs.
    - Select Azure Service Management>Delegated, and check user_impersonation. Used to read Azure Sentinel incidents. 
12. FOR INCIDENT RESPONSE PLAYBOOK ONLY: Under API’s my organization uses”
    - Select WindowsDefenderATP, and check the following permissions for both Delegated and Application.
      - Machine.Isolate – to isolate device
      - Machine.Read – to find agent ID- to collect data from a single machine. 
      - Machine.Read.All – to find agent ID – to query all machines 
      - File.Read.All – for process handling find and erase/stop suspicious executable
      - Machine.StopAndQuarantine - for process handling find and erase/stop suspicious executable
13. Once all the API permissions are added, click Grant admin consent for Default Directory and click OK. 
