<p align="left">  
<img width="300" height="100" src="./Images/logo.jpg"> </a>
</p>

# Illusive Incident Enrichment Playbook

The Incident Enrichment playbook leverages Sentinel analytic rules to discover Illusive-based alerts and report the associated data and forensics as Sentinel incident sets. 

Use this playbook to enrich Sentinel security incidents originating from Illusive with Illusive incident and forensics information. Illusive continues to enrich relevant Sentinel incidents as new events are detected. This is done using the Illusive API resource.

 1. [Playbook workflow](#playbook-workflow)
 2. [Playbook execution](#playbook-execution)
 3. [Playbook output](#playbook-output)
 4. [Access Playbook](#Access_playbook)
 5. [Playbook retry mechanism](#playbook-retry-mechanism) 

<a name="playbook-workflow">

## Playbook Workflow

 1. Perform the general solution setup. [(see instructions here)](https://github.com/IllusiveNetworks-Labs/Azure-Sentinel/tree/Illusive/Solutions/Illusive%20Active%20Defense)
 2. [Create the Illusive playbook.](#create-illusive-playbook)
 3. [Connect the playbook to Azure Sentinel](#API_connection)

<a name="create-illusive-playbook">
 
## Create the Illusive playbook

Deploying the Illusive Incident Enrichment playbook requires a custom deployment template. 
 - The playbook should be deployed under the same resource group, subscription, and workspace as the Azure app.
 - The Illusive API key should contain only the API key and no keywords such as “Bearer” or “Basic”.

### Deploy a custom template
 1. On the Azure home page, filter for Deploy a custom template.
       <p align="center">  
          <img src="./Images/deploy-custom-template-search.png"> </a>
       </p>
 1. Under <b>Custom Deployment>Select a template</b>, click <b>Build your own template in the editor</b>.
       <p align="center">  
          <img src="./Images/deploy-custom-template-page.png"> </a>
       </p>
 1. From <b>Edit template</b>, click <b>Load file</b>, and load the file named <u>IllusiveSentinelIncidentEnrichment.json</u> provided by Illusive and click <b>Save</b>.
       <p align="center">  
          <img src="./Images/deploy-custom-template-load-file.png"> </a>
       </p>
       <p align="center" width="5cm">  
          <img src="./Images/deploy-custom-template-edit-template-incident-enrichment.png"> </a>
       </p>
 1. Under <b>Custom Deployment>Basics:</b>
    - Specify the <b>Subscription</b> that contains the dedicated Azure app that will run the Illusive Sentinel solution 
    - Specify the <b>Resource group</b> that contains the Workspace where you want to install the playbook.
    - Under <b>Instance details:</b>
      <table>
       <tr>
        <td><b>Field</b></td>
        <td><b>Instructions</b></td>
       </tr>
       <tr>
        <td>Region</td>
        <td>Filled automatically based on the subscription and cannot be changed.</td>
       </tr>
       <tr>
        <td>Workspace Name</td>
        <td>Specify the Azure Sentinel <b>Workspace Name</b> where you want to create the playbook.</td>
       </tr>
       <tr>
        <td>Illusive API URL <br/> Illusive API Key</td>
        <td>Supply the authentication parameters required to access the Illusive API
         <b>Important:</b> Enter the API key without the keyword</td>
       </tr>
       <tr>
        <td>Azure-Sentinel Client ID:  <br/> Azure-Sentinel Client Secret:  <br/> Azure-Sentinel Tenant ID:</td>
        <td>Supply the authentication parameters required to access the Azure-Sentinel API</td>
       </tr>
      </table>
      <p align="center">  
         <img src="./Images/custom-deployment-basics-incident-enrichment.png"> </a>
      </p>
1. When finished entering details, click <b>Review + Create</b>.
      <p align="center">  
         <img src="./Images/custom-deployment-review-create.png"> </a>
      </p>
1. On successful validation, click <b>Create</b>.  
This completes the playbook deployment. 
      <p align="center">
         <img src="./Images/custom-deployment-is-complete.png"> </a>
      </p>
      
<a name="API_connection">

## Connect the playbook to Azure Sentinel
Connect the playbook to Azure Sentinel by configuring the playbook's API connection. 
     <p align="center">  
       <img src="./Images/api-connection-setup.png"> </a>
     </p>
  1. From <b>Your custom deployment is complete</b>, click <b>Go to all resources</b>. 
     - If there is only one installed playbook in the workspace, clicking on <b>Go to resource group</b> will take you to the playbook page. 
     - If there are multiple installed playbooks in the workspace, clicking on <b>Go to resource group</b> will take you to the All resources page. The playbook will be available in the list.
  2. Click the deployed playbook and then click <b>API connections.</b>
  3. Under API connections, click <b>azuresentinel</b>.
  4. On the <b>azuresentinel</b> card, click <b>Edit API connection</b>.
  5. Edit the <b>Display Name</b>. (optional)
  6. Under Authorize, click <b>Authorize</b> and provide authorization by signing in.
  7. To save the authorization, click <b>Save</b>. To cancel, click <b>Discard</b>.

<a name="playbook-execution">

## Playbook Execution 
- This playbook is triggered by a new Sentinel Alert that originates from a new Illusive event Syslog.
- Sentinel uses Illusive API to fetch the incident details and update the corresponding Sentinel incident.
- Illusive API is used again to fetch the event details and update the Sentinel incident with the event’s Illusive event id and triggering process information.

 
<a name="playbook-output">

## Output
- The Azure Sentinel incident is updated with the following Illusive incident information:
- Severity - incident severity
- Account - the last seen user on the compromised host
- Host - the compromised host hostname
- Host>OS - the compromised host operating system
- IP - the compromised host IP address
- Status - the incident status will be updated to closed once the Illusive incident is closed
- Added as custom fields:
   - Illusive Incident Id
   - Illusive Event Id’s - string of events already processed, separated by comma
   - Forensics - whether forensics has been collected or not
- Added as comments:
   - Incident creation time - incidentTimeUTC
   - Associated deception family - deceptionFamilies
   - The proximity of the compromised host to high value assets (Risk insights) - stepsToCrownJewel, stepsToDomainAdmin
   - Triggering process information for each event - “Event Id: {event_id} Process Information: {Response of triggering process info}”

<a name="Access_playbook">

## Access and view the playbook 

You can view and manage the playbook as well as review the playbook run history. This can be helpful for troubleshooting or for understanding playbook behavior and results. 

1. Find the playbook on the Azure Sentinel or All resources page. 
2. Click on the playbook to view the playbook run History.
3. Select any executed playbook to view the results.

Sample playbook history:
<p align="center">  
   <img src="./Images/playbook-history-incident-enrichment.png"> </a>
</p>

<a name="playbook-retry-mechanism">
 
## Playbook retry mechanism

<p align="center">  
   <img src="./Images/playbook-retry-mechanism.png"> </a>
</p>

Azure Sentinel handles the retry mechanism. If any condition is not met, Sentinel retries the playbook four times.
