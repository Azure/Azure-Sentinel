
<p align="left">  
<img width="300" height="100" src="./Images/logo.jpg"> </a>
</p>

## Illusive Active Defense Product Suite

# Microsoft Azure Sentinel

  Playbook and setup for incident enrichment and response

# Table of Contents

1. [Executive Summary](#executive_summary)
   - [Azure Application Setup](#azureappsetup)

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
   
To use the Illusive Active Defense solution, you must have the following: 
 - An Azure AD subscription with a configured Sentinel workspace
 - An Illusive ADS (deceptions) license

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
   <p align="center">  
      <img src="./Images/Workspace.png"> </a>
   </p>
3. Use the above highlighted name as the “Workspace Name” while deployment.

<a name="azureappsetup">
   
# Azure Application Setup
   
## Prerequisites
   An Azure account that has an active subscription.
## Register an Azure App
   
1. Login to [http://portal.azure.com/](http://portal.azure.com/) 
2. If you have access to multiple tenants, in the top menu, use the Directory + subscription filter to select the tenant in which you want to register the application
   <p align="center">  
      <img src="./Images/app_registration.png"> </a>
   </p>
3. Search for and select Azure Active Directory.
4. Under Manage, select App registrations>New registration.The Register an application page appears.
   <p align="center">  
      <img src="./Images/app_name.png"> </a>
   </p>
5. Specify a Name for your application.
Conform to company naming conventions. Do not use “illusive” or any other word that might reveal the existence of Illusive in the environment. 
6. Under Supported account types, select Accounts in this organizational directory only.
7. To complete the initial app registration, click Register.

## Collect App Information
You need the Application (client) ID and the Directory (tenant) ID to configure Illusive solution playbooks. 
 1. Go to the created application’s Overview page.
 2. Copy and save the Application (client) ID and the Directory (tenant) ID. You need this information to configure the playbooks.

## Generate and save a Client Secret
You need a secret Value to configure Illusive solution playbooks.
  1. Click Certificates & Secrets.
  2. Click New Client Secret.
  3. Add a Description for the Client Secret.
  4. Select an Expiry date for the Client Secret (recommended 6 months).
  5. Click Add 
  6. Copy and save the secret Value. You need this information to configure the Playbooks.

# Generate an Illusive API Key
You need the Illusive REST API URL and an Illusive API key to configure Illusive solution playbooks.
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
    3. Click Add.The API Key is created and added to the list of keys shown.<br/>
    4. Copy the header containing the key to a text file and save it securely.The key is valid for one year to access the REST API on this Management Server only.

# Configure and Deploy Playbooks
To configure and deploy the Incident Response playbook, go to Incident Response Playbook.
<br>
To configure and deploy the Incident Enrichment playbook, go to Incident Enrichment Playbook. 
# API connection setup
To connect the Illusive solution playbooks to Azure Sentinel, configure the API connection for each deployed playbook. 
<br>
<b>NOTE:</b> The API connection is the same for both the incident enrichment playbook and the incident response playbook. 

  1. Click the deployed playbook and then click <b>API connections.</b>
  2. Under API connections, click <b>azuresentinel.</b>
  3. On the <b>azuresentinel</b> card, click <b>Edit API connection.</b>
  4. Under Authorize, click <b>Authorize</b> and provide authorization by signing in.
  5. To save the authorization, click <b>Save.</b> To cancel, click <b>Discard.</b>

## Configure the Illusive analytic rule
The analytic rule instructs Azure Sentinel to search for information of interest and to supply this information to the Illusive solution playbooks. 
  1. Log onto http://portal.azure.com/ 
  2. Click <b>Azure Sentinel.</b>
  3. Select the required workspace (resource group)
  4. Select <b>Analytics.</b>
  5. Click <b>Create>Scheduled query rule</b> and click <b>Next.</b>
  6. Enter the analytics rule details:
      - <b>Name</b>– Specify a display name for the rule. (e.g., “Illusive analytic rule”)
      - <b>Description</b>– Add a description for what the rule does. 
<br/><b>E.g.:</b>  Triggers a Sentinel alert upon detecting an Illusive event and creates a Sentinel incident. The Sentinel incident will correspond to the Illusive incident and will include all subsequent associated Illusive events. 
      - <b>Tactics</b> – do not select any tactics. 
      - <b>Severity</b> – select the severity of incidents created by the Illusive solution. Recommended severity level: <b>High</b> 
      - <b>Status</b> – ensure the rule is <b>Enabled.</b>
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
   9. Under <b>Alert Enrichment,</b> expand <b>Entity Mapping</b> and add entities as below:
      - Host > FullName : SourceHostName
      - IP > Address : SourceIP
      - Host > OMSAgentID : Computer
  10. Under <b>Alert Enrichment,</b> expand <b>Custom details</b> and add key-value pairs as below:
      - isHostIsolated : isHostIsolated
      - isProcessIsolated : isProcessIsolated 
      - IllusiveIncidentId : DeviceCustomNumber2
      - HasForensics : HasForensics
      - Account : SourceUserName
  11. Under <b>Alert Enrichment,</b> expand <b>Alert details,</b> and configure the following fields:
       - <b>Alert Name Format:</b> Illusive Incident: {{DeviceCustomNumber2}}
       - <b>Alert Description Format:</b> {{DeviceCustomNumber2}} generated at {{TimeGenerated}}
  12. Under <b>Query scheduling,</b> configure the following details:
       - <b>Run query every</b> = “5 minutes”. This is because the minimum time for an analytic rule to trigger is 5 minutes.
       - <b>Lookup data from the last</b> = “5 minutes”. This is because the lookup data (Illusive incidents inserted in Azure Sentinel) will run only for 5 minutes. 
  13. Under <b>Alert Threshold,</b> set <b>Generate alert when number of query results</b> “is greater than 0”.
  14. Under <b>Event grouping,</b> select <b>Trigger an alert for each event (preview).</b>
  15. Keep <b>Suppression</b> “Off”.
  16. Click <b>Next.</b>
  17. On the <b>Incident setting (Preview)</b> tab, enable <b>Create incidents from alerts triggered by this analytics rule.</b>
  18. Enable <b>Alert Grouping.</b><br/>
<b>Note:</b> Up to 150 alerts can be grouped into a single incident. If more than 150 alerts are generated, a new incident will be created with the same incident details as the original. Additional alerts will be grouped into the new incident.
  19. Under <b>Alert Grouping,</b> select the time range during which an alert’s associated events will be grouped into a single incident in the Sentinel system. (This can be configured based on customer requirements)
  20. Under <b>Group alerts triggered by this analytics rule into a single incident by,</b> select <b>Grouping alerts into a single incident if the selected entity types and details match:</b> and select the <b>IllusiveIncidentId</b> entity as in the image below: 
  21. Enable <b>Re-open closed matching incidents</b> to allow incidents to be reopened. 
  22. On <b>Automated response</b> tab, from the dropdown list under the <b>Alert automation</b> section, select the configured Illusive solution playbooks: 
       - <b>IllusiveSentinelIncidentEnrichment </b>
       - <b>IllusiveSentinelIncidentResponse </b>
  23. Then, click <b>Next:Review.</b>
  24. On the <b>Review and create</b> tab, review all the entered data, and click <b>Save.</b>
  25. The new analytic rule can be seen in the <b>Analytics>Active rules</b> table.
    
# Add a SIEM Server
Configure Illusive to automatically send Illusive activity logs and event messages to a Linux based Syslog server. Sentinel will consume this information and trigger the Illusive solution playbooks.
<br>
Every Syslog message also contains the incident ID, which allows the SOC team to merge or aggregate events in the SIEM.
  1. Install a syslog on a Linux machine 
  2. Configure the Linux machine as a syslog server in the Illusive Console.
  3. Navigate to <b>Settings>Reporting</b> and scroll down to <b>Syslog Servers.</b>
  4. In the <b>Host Name</b> server field, supply the server IP address or host name.
  5. In the <b>Port</b> field, supply the Syslog server’s communication port. (Default <b>514</b>)
  6. From the <b>Protocol</b> dropdown menu, select <b>TCP.</b><br>
<b>Recommendation:</b> For high reliability, select the TCP protocol.
  7. From the <b>Audit messages</b> drop-down menu, select one of the following (either option is okay; this integration only requires the event messages):
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
  8. Click <b>+Add.
