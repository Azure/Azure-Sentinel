
<p align="left">  
<img width="300" height="100" src="./Images/logo.jpg"> </a>
</p>

## Illusive Active Defense Product Suite

# Microsoft Azure Sentinel

  Playbook and setup for incident enrichment and response

# Table of Contents

Readme – General
 1. [Executive Summary](#executive_summary)
 2. [Basic Requirements](#BasicRequirements)
 3. [Workflow](#workflowlink)
 4. [Locate the Sentinel workspace](#Sentinel_Workspace)
 5. [Azure Application Setup](#azureappsetup)
     - [Register an Azure App](#Register_Azure_App)
     - [Collect App Information](#Collect_App_Information)
     - [Generate and save a Client Secret](#Generate_ClientSecret)
     - [Add User Impersonation API permission](#Add_UserImpersonation)
 6. [Generate an Illusive API Key](#Illusive_API_Key)
 7. [Add a SIEM Server](#SIEM_Server)
 8. [Configure and Deploy Playbooks](#Deploy_Playbooks)
 9. [API connection setup](#API_connection)
10. [Configure the Illusive analytic rule](#Illusive_analytic_rule)
11. [Access and view the playbook](#Access_playbook)

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
  
<a name="BasicRequirements">
  
## Basic Requirements (set up in advance) 
   
To use the Illusive Active Defense solution, you must have the following: 
 - An Azure AD subscription with a configured Sentinel workspace
 - An Illusive ADS (deceptions) license
  
<a name="workflowlink">

## Workflow 
    
  1. [Locate the Sentinel workspace](#Sentinel_Workspace)
  2. [Azure Application Setup](#azureappsetup)
  3. [Generate an Illusive API Key](#Illusive_API_Key)
  4. [Add a Syslog Server](#SIEM_Server)
  5. [Configure and Deploy Playbooks](#Deploy_Playbooks)
  6. [API connection setup](#API_connection)
  7. [Configure the Illusive analytic rule](#Illusive_analytic_rule)
   
<a name="Sentinel_Workspace">
  
## Locate the Sentinel Workspace
   
The workspace <b>name</b>, as well as the <b>Subscription</b> and <b>resource group</b> it belongs to are required later on during this configuration.

  <br>
Steps to locate the Sentinel Workspace name, subscription, and resource group:
   <br>
  
1. In the [Azure portal](https://portal.azure.com/), go to <b>Azure Sentinel</b>. 
2. Type "Azure Sentinel" in the <b>Search bar</b>, or click on the Azure Sentinel icon.
3. On the Azure Sentinel page, in the list, find the workspace where you want to create the playbook and its associated API connection.
   <p align="center">  
      <img src="./Images/Workspace.png"> </a>
   </p>
4. Make a note of the workspace <b>Name</b>, <b>resource group</b>, and <b>Subscription</b>.  You will need these during playbook deployment.

<a name="azureappsetup">
   
# Azure Application Setup
  The Illusive solution playbooks run with an Azure application with the required API permissions.

  This procedure sets out the general registration and configuration requirements that apply to both the Incident Enrichment and Incident Response playbooks. 
  
<a name="Register_Azure_App">
    
## Register an Azure App
   
1. Login to [http://portal.azure.com/](http://portal.azure.com/) 
2. If you have access to multiple tenants, in the top menu, use the Directory + subscription filter to select the tenant in which you want to register the application.
   <p align="center">  
      <img src="./Images/app_registration.png"> </a>
   </p>
3. Search for and select <b>Azure Active Directory</b>.
4. Under Manage, select <b>App registrations>New registration</b>.The <b>Register an application</b> page appears.
   <p align="center">  
      <img src="./Images/app_name.png"> </a>
   </p>
5. Specify a <b>Name</b> for your application.
    <br>
    Conform to company naming conventions. Do not use “illusive” or any other word that might reveal the existence of Illusive in the environment. 
6. Under <b>Supported account types</b>, select <b>Accounts in this organizational directory only</b>.
7. To complete the initial app registration, click <b>Register</b>.
  
<a name="Collect_App_Information">

## Collect App Information
You need the <b>Application (client) ID</b> and the <b>Directory (tenant) ID</b> to configure Illusive solution playbooks. 
 1. Go to the created application’s <b>Overview</b> page.
 2. Copy and save the <b>Application (client) ID</b> and the <b>Directory (tenant) ID</b>. You need this information to configure the Illusive playbooks.
         <p align="center">  
            <img src="./Images/App_registration_app-information.png"> </a>
         </p>
  
<a name="Generate_ClientSecret">

## Generate and save a Client Secret
You need specify a secret <b>Value</b> to configure Illusive solution playbooks.
  1. Click <b>Certificates & Secrets</b>.
  2. Click <b>New Client Secret</b>.
  3. Add a <b>Description</b> for the Client Secret.
  4. Select an <b>Expiry date</b> for the Client Secret (recommended 6 months).
  5. Click <b>Add</b>. 
  6. Copy and save the secret Value. You need this information to configure Illusive playbooks.
        <p align="center">  
            <img src="./Images/App_registration_secret-value.png"> </a>
        </p>
  
<a name="Add_UserImpersonation">

## Add the User Impersonation API Permission
  The user_impersonation permission is used to read Azure Sentinel incidents.  
  Additional API permissions are required for the Incident Response playbook. These are specified in the [Incident Response playbook deployment instructions](./Playbooks/Illusive-SentinelIncident-Response).

  1.	From the Azure console, find the Azure app you created to run the Illusive Sentinel Solution. 
  2.	Go to <b>API Permissions</b>.
  3.	Click <b>Add a permission</b>.
  4.	Under <b>Microsoft APIs</b>, select <b>Azure Service Management</b>.
        <p align="center">  
            <img src="./Images/azure-app-api-user-impersonation1.png"> </a>
        </p>
  5.	Select <b>Delegated permissions</b>, check <b>user_impersonation</b>, and click <b>Add permissions</b>.
        <p align="center">  
            <img src="./Images/azure-app-api-user-impersonation2.png"> </a>
        </p>        
  6. Click <b>Grant admin consent for Default Directory</b> and click <b>Yes</b>.
        <p align="center">  
            <img src="./Images/azure-app-api-user-impersonation3.png"> </a>
        </p>        
  7. Verify admin consent has been granted. This step is important, even if the admin consent status is green. Only a Global Admin can approve admin consent requests.
       1. Go to <b>Enterprise>Admin Consent requests</b>.
       1. Go to <b>My pending</b> and verify that this permission is not pending.

<a name="Illusive_API_Key">
  
# Generate an Illusive API Key
You need the Illusive REST API URL and an Illusive API key to configure Illusive solution playbooks.
        <p align="center">  
            <img src="./Images/illusive-api-key-card.png"> </a>
        </p>        
  1. In the Illusive Console, navigate to Settings>General>API Keys. 
  2. Enter values in the following fields:   
        <table>
          <tr>
              <td><b>Field</b></td>
              <td><b>Description and values</b></td>
          </tr>
          <tr>
              <td>Description</td>
              <td>Specify description of key. <br/>
            - All Permissions<br/>
            - Create Event Read<br/>
            - Monitoring Data
              </td>
          </tr>
          <tr>
              <td>Permissions</td>
              <td>Select the permission:</td>
          </tr>
          <tr>
              <td>Restrict SourceIP</td>
              <td>Limit the API key to be used only from the specified source IP address. (optional)</td>
          </tr>
        </table>
    3. Click <b>Add API key</b>. The API Key is created and added to the list of keys shown.
    4. Copy the header containing the key to a text file and save it securely. The key is valid for one year to access the REST API on this Management Server only.
    5. To get the Illusive API URL, click <b>REST API Documentation</b>. This opens the Swagger API page. Copy the URL from the browser address bar.

<a name="SIEM_Server">
      
# Add a syslog Server
Configure Illusive to automatically send Illusive activity logs and event messages to a Linux based Syslog server. Sentinel will consume this information and trigger the Illusive solution playbooks.
          <p align="center">  
            <img src="./Images/illusive-syslog-server-integration-card.png"> </a>
          </p>
<br>
Every Syslog message also contains the incident ID, which allows the SOC team to merge or aggregate events in the SIEM.
  1. Install a syslog on a Linux machine. 
  2. Configure the Linux machine as a syslog server in the Illusive Console.
      1. In the Illusive Console, navigate to <b>Settings>Reporting</b> and scroll down to <b>Syslog Servers.</b>
      2. In the <b>Host Name</b> server field, supply the server IP address or host name.
      3. In the <b>Port</b> field, supply the Syslog server’s communication port. (Default <b>514</b>)
      4. From the <b>Protocol</b> dropdown menu, select <b>TCP.</b><br>
    <b>Recommendation:</b> For high reliability, select the TCP protocol.
      5. From the <b>Audit messages</b> drop-down menu, select one of the following (either option is okay; this integration only requires the event messages):
          <table>
            <tr>
              <th><b>Option</b></th>
              <th><b>Description</b></th>
            </tr>
            <tr>
              <td><b>Send audit messages to server</b></td>
              <td><b>Sends Illusive event and audit messages</b> to your Syslog server</td>
            </tr>
            <tr>
              <td><b>Don’t send audit messages to server</b></td>
              <td><b>Sends only Illusive event messages and system health data</b> to your Syslog server</td>
            </tr>
          </table>
      6. Click <b>Add</b>.
  
<a name="Deploy_Playbooks">
  
# Configure and Deploy Playbooks
To configure and deploy the Incident Enrichment playbook, go to [Incident Enrichment Playbook](./Playbooks/Illusive-SentinelIncident-Enrichment). 
<br>
To configure and deploy the Incident Response playbook, go to [Incident Response Playbook](./Playbooks/Illusive-SentinelIncident-Response).
  
<a name="API_connection">
  
# API connection setup
To connect the Illusive solution playbooks to Azure Sentinel, configure the API connection for each deployed playbook. 
<br>
<b>NOTE:</b> The API connection is the same for both the incident enrichment playbook and the incident response playbook. 

          <p align="center">  
            <img src="./Images/api-connection-setup.png"> </a>
          </p>

  1. Click the deployed playbook and then click <b>API connections.</b>
  2. Under API connections, click <b>azuresentinel.</b>
  3. On the <b>azuresentinel</b> card, click <b>Edit API connection.</b>
  4. Under Authorize, click <b>Authorize</b> and provide authorization by signing in.
  5. To save the authorization, click <b>Save.</b> To cancel, click <b>Discard.</b>

<a name="Illusive_analytic_rule">
  
## Configure the Illusive analytic rule
The analytic rule instructs Azure Sentinel to search for information of interest and to supply this information to the Illusive solution playbooks. 
  1. Log onto http://portal.azure.com/ 
  2. Click <b>Azure Sentinel.</b>
  3. Select the resource group and workspace in which the Illusive playbooks are deployed. 
  4. Select <b>Analytics.</b>
  5. Click <b>Create>Scheduled query rule</b> and click <b>Next.</b>
          <p align="center">  
            <img src="./Images/sentinel-analytics-create-scheduled-query-rule.png"> </a>
          </p>
  6. Enter the analytics rule details:
      - <b>Name</b>– Specify a display name for the rule. (e.g., “Illusive analytic rule”)
      - <b>Description</b>– Add a description for what the rule does. 
<br/><b>E.g.:</b>  Triggers a Sentinel alert upon detecting an Illusive event and creates a Sentinel incident. The Sentinel incident will correspond to the Illusive incident and will include all subsequent associated Illusive events. 
      - <b>Tactics</b> – do not select any tactics. 
      - <b>Severity</b> – select the severity of incidents created by the Illusive solution. Recommended severity level: <b>High</b> 
      - <b>Status</b> – ensure the rule is <b>Enabled.</b>
           <p align="center">  
            <img src="./Images/sentinel-analysis-config.png"> </a>
           </p>
  7. When finished entering Analytic rule details, click <b>Next: Set rule logic.</b>
  8. In <b>Set rule logic,</b> under <b>Rule query,</b> copy and paste the following KQL query:<br/>
```markdown
     CommonSecurityLog
      | where DeviceProduct == "illusive"
      | summarize arg_max(TimeGenerated, *) by DeviceCustomNumber2, AdditionalExtensions, TimeGenerated
      | extend Category = extract(@'cat=([^;]+)(\;|$)', 1, AdditionalExtensions), HasForensics = extract(@'cs7=([^;]+)(\;|$)', 1, AdditionalExtensions)
      | where Category == "illusive:alerts"
      | extend isHostIsolated = false
      | extend isProcessIsolated = false
```
   <p align="center">  
     <img src="./Images/sentinel-analysis-set-rule-logic-code.png"> </a>
   </p>

  9. Under <b>Alert Enrichment,</b> expand <b>Entity Mapping</b> and add entities as below:
      - Host > FullName : SourceHostName
      - IP > Address : SourceIP
      - Host > OMSAgentID : Computer
       <p align="center">  
         <img src="./Images/sentinel-analysis-alert-enrichment-config.png"> </a>
       </p>

  10. Under <b>Alert Enrichment,</b> expand <b>Custom details</b> and add key-value pairs as below:
      - isHostIsolated : isHostIsolated
      - isProcessIsolated : isProcessIsolated 
      - IllusiveIncidentId : DeviceCustomNumber2
      - HasForensics : HasForensics
      - Account : SourceUserName
        <p align="center">  
         <img src="./Images/sentinel-analysis-alert-enrichment-custom-details.png"> </a>
        </p>

  11. Under <b>Alert Enrichment,</b> expand <b>Alert details,</b> and configure the following fields:
       - <b>Alert Name Format:</b> Illusive Incident: {{DeviceCustomNumber2}}
       - <b>Alert Description Format:</b> {{DeviceCustomNumber2}} generated at {{TimeGenerated}}
        <p align="center">  
         <img src="./Images/sentinel-analysis-alert-enrichment-alert-details.png"> </a>
        </p>
    
  12. Under <b>Query scheduling,</b> configure the following details:
       - <b>Run query every</b> = “5 minutes”. This is because the minimum time for an analytic rule to trigger is 5 minutes.
       - <b>Lookup data from the last</b> = “5 minutes”. This is because the lookup data (Illusive incidents inserted in Azure Sentinel) will run only for 5 minutes.
        <p align="center">  
         <img src="./Images/sentinel-analysis-query-scheduling.png"> </a>
        </p>
 
  13. Under <b>Alert Threshold,</b> set <b>Generate alert when number of query results</b> “is greater than 0”.
        <p align="center">  
         <img src="./Images/sentinel-analysis-alert-threshold.png"> </a>
        </p>
        
  14. Under <b>Event grouping,</b> select <b>Trigger an alert for each event (preview).</b>
        <p align="center">  
         <img src="./Images/sentinel-analysis-alert-event-grouping.png"> </a>
        </p>

  15. Keep <b>Suppression</b> “Off”.
  16. Click <b>Next.</b>
  17. On the <b>Incident setting (Preview)</b> tab, enable <b>Create incidents from alerts triggered by this analytics rule.</b>
  18. Enable <b>Alert Grouping.</b><br/>
        <b>Note:</b> Up to 150 alerts can be grouped into a single incident. If more than 150 alerts are generated, a new incident will be created with the same incident details as the original. Additional alerts will be grouped into the new incident.
  19. Under <b>Alert Grouping,</b> select the time range during which an alert’s associated events will be grouped into a single incident in the Sentinel system. (This can be configured based on customer requirements)
        <p align="center">  
         <img src="./Images/sentinel-analysis-alert-grouping.png"> </a>
        </p>
        
  20. Under <b>Group alerts triggered by this analytics rule into a single incident by,</b> select <b>Grouping alerts into a single incident if the selected entity types and details match:</b> and select the <b>IllusiveIncidentId</b> entity as in the image below: 
  21. Enable <b>Re-open closed matching incidents</b> to allow incidents to be reopened. 
        <p align="center">  
         <img src="./Images/sentinel-analysis-reopen-closed-matching-incidents.png"> </a>
        </p>

  22. On <b>Automated response</b> tab, from the dropdown list under the <b>Alert automation</b> section, select the configured Illusive solution playbooks: 
       - <b>IllusiveSentinelIncidentEnrichment </b>
       - <b>IllusiveSentinelIncidentResponse </b>
  23. Then, click <b>Next:Review.</b>
  24. On the <b>Review and create</b> tab, review all the entered data, and click <b>Save.</b>
  25. The new analytic rule can be seen in the <b>Analytics>Active rules</b> table.

<a name="Access_playbook">

# Access and view a playbook 
You can view and manage Illusive playbooks as well as review playbook run history. This can be helpful for understanding how the playbook responds when triggered, and for troubleshooting. 
1.	Find the playbook on the <b>Azure Sentinel</b> or <b>All resources</b> pages. 
2.	Click on the playbook to view the playbook run History.
3.	Select any executed playbook to view the results.

Sample playbook history (incident response):
        <p align="center">  
         <img src="./Images/playbook-history-incident-response.png"> </a>
        </p>

