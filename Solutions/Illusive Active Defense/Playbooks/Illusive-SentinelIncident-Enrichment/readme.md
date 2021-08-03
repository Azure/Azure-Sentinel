# Readme – Incident Enrichment

The Incident Enrichment playbook leverages Sentinel analytic rules to discover Illusive-based alerts and report the associated data and forensics as Sentinel incident sets. 
Use this playbook to enrich Sentinel security incidents originating from Illusive with Illusive incident and forensics information. Illusive continues to enrich relevant Sentinel incidents as new events are detected. This is done using the Illusive API resource.

# Playbook Workflow

 1. Perform the general solution setup
 2. Add API permissions to the Azure app
 3. Create the Illusive playbook

# Create the Illusive playbook

Deploying the Illusive Incident Enrichment playbook requires a custom deployment template. 
 - The playbook should be deployed under the same resource group, subscription, and workspace as the Azure app.
 - The Illusive API key should contain only the API key and no keywords such as “Bearer” or “Basic”.

# Deploy a custom template
 1. On the Azure home page, filter for Deploy a custom template.
 2. Under Custom Deployment>Select a template, click Build your own template in the editor.
 3. From Edit template, click Load file, the file named IllusiveSentinelIncidentEnrichment.json provided by Illusive and click Save.
 4. Under Custom Deployment>Basics:
  - Specify the Subscription that contains the dedicated Azure app that will run the Illusive Sentinel solution 
  - Specify the Resource group that contains the Workspace where you want to install the playbook.
  - Under Instance details:
    - Region is filled automatically based on the subscription and cannot be changed.
    - Specify the Azure Sentinel Workspace Name where you want to create the playbook.
    - Supply the authentication parameters required to access the Illusive API:
      - Illusive API URL
      - Illusive API Key (just the key, without the prefix) 
    - Supply the authentication parameters required to access the Sentinel API:
      - Azure-Sentinel Client ID: 
      - Azure-Sentinel Client Secret: 
      - Azure-Sentinel Tenant ID:
5. When finished entering details, click Review + Create.
6. On successful validation, click Create.
This completes the playbook deployment. 
7. To view the playbook, click Go to resource group.
  - If there is only one installed playbook in the workspace, clicking on Go to resource group will take you to the playbook page. 
  - If there are multiple installed playbooks in the workspace, clicking on Go to resource group will take you to the All resources page. The deployed playbook will be available in the list.

# Access and view the playbook 

You can view and manage the playbook as well as review the playbook run history. 
1. Find the playbook on the Azure Sentinel or All resources page. 
2. Click on the playbook to view the playbook run History.
3. Select any executed playbook to view the results.
Sample playbook history:

# Playbook retry mechanism

Azure Sentinel handles the retry mechanism. If any condition is not met, Sentinel retries the playbook four times.
