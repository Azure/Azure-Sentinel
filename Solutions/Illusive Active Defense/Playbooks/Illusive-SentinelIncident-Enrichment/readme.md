# Incident Enrichment

The Incident Enrichment playbook leverages Sentinel analytic rules to discover Illusive-based alerts and report the associated data and forensics as Sentinel incident sets. 

Use this playbook to enrich Sentinel security incidents originating from Illusive with Illusive incident and forensics information. Illusive continues to enrich relevant Sentinel incidents as new events are detected. This is done using the Illusive API resource.

## Playbook Workflow

 1. Perform the general solution setup. [(see instructions here)](https://github.com/IllusiveNetworks-Labs/Azure-Sentinel/tree/Illusive/Solutions/Illusive%20Active%20Defense)
 1. Create the Illusive playbook.

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
 1. From <b>Edit template</b>, click <b>Load file</b>, the file named <u>IllusiveSentinelIncidentEnrichment.json</u> provided by Illusive and click <b>Save</b>.
       <p align="center">  
          <img src="./Images/deploy-custom-template-load-file.png"> </a>
       </p>
       <p align="center">  
          <img src="./Images/deploy-custom-template-edit-template.png"> </a>
       </p>
 1. Under <b>Custom Deployment>Basics</b>:
  - Specify the <b>Subscription</b> that contains the dedicated Azure app that will run the Illusive Sentinel solution. 
  - Specify the <b>Resource group</b> that contains the Workspace where you want to install the playbook.
  - Under <b>Instance details</b>:
    - <b>Region</b> is filled automatically based on the subscription and cannot be changed.
    - Specify the Azure Sentinel <b>Workspace Name</b> where you want to create the playbook.
    - Supply the authentication parameters required to access the Illusive API:
      - Illusive API URL
      - Illusive API Key (just the key, without the prefix) 
    - Supply the authentication parameters required to access the Sentinel API:
      - Azure-Sentinel Client ID: 
      - Azure-Sentinel Client Secret: 
      - Azure-Sentinel Tenant ID:
1. When finished entering details, click <b>Review + Create</b>.
1. On successful validation, click <b>Create</b>.
   This completes the playbook deployment. 

1. To view the playbook, click <b>Go to resource group</b>.
  - If there is only one installed playbook in the workspace, clicking on <b>Go to resource group</b> will take you to the playbook page. 
  - If there are multiple installed playbooks in the workspace, clicking on <b>Go to resource group</b> will take you to the All resources page. The deployed playbook will be available in the list.

## Playbook Execution 
- This playbook is triggered by a new Sentinel Alert that originates from a new Illusive event Syslog.
- Sentinel uses Illusive API to fetch the incident details and update the corresponding Sentinel incident.
- Illusive API is used again to fetch the event details and update the Sentinel incident with the event’s Illusive event id and triggering process information.

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

## Access and view the playbook 

You can view and manage the playbook as well as review the playbook run history. 
1. Find the playbook on the Azure Sentinel or All resources page. 
2. Click on the playbook to view the playbook run History.
3. Select any executed playbook to view the results.
Sample playbook history:

## Playbook retry mechanism

Azure Sentinel handles the retry mechanism. If any condition is not met, Sentinel retries the playbook four times.
