## Illusive Active Defense Product Suite

# Sentinel Incident Response

## Playbook and setup for incident response

# Readme – Incident Response

The Incident Response playbook leverages Sentinel analytic rules and CrowdStrike or Microsoft Defender for Endpoint integration to automate incident response when specified Illusive incidents are discovered. 
<br/>
Use the playbook to quickly stop or slow down ransomware attacks and critical incidents detected by Illusive in your organization. Upon detection, Sentinel is instructed to use the triggering process information reported by Illusive remove or kill the process. If the triggering process cannot be killed, Sentinel is instructed to isolate the host. These capabilities are available for organizations with CrowdStrike Falcon or Microsoft Defender for Endpoint.

# Playbook Workflow
 
 1. Perform the general solution setup
 2. Add API permissions to the Azure app
 3. Enable Microsoft Defender for Endpoint 
 4. Create the Illusive playbook

# Add API permissions to the Azure app 

 1. From the Azure console, find the Azure app you created to run the Illusive Sentinel Solution. 
 2. Go to API Permissions.
 3. Click Add a permission.
 4. Under Microsoft APIs: 
   - Select Azure Service Management>Delegated, and check user_impersonation. This permission is used to read Azure Sentinel incidents.
   - Under API’s my organization uses, select WindowsDefenderATP, and check the following permissions for both Delegated and Application.
      - Machine.Isolate – to isolate device
      - Machine.Read – to find agent ID - to collect data from a single machine. 
      - Machine.Read.All – to find agent ID – to query all machines and collect device information even if we don’t have a device ID. 
      - File.Read.All – for process handling find and erase/stop suspicious executable
      - Machine.StopAndQuarantine - for process handling find and erase/stop suspicious executable
 5. Once all the API permissions are added, click Grant admin consent for Default Directory and click OK. 

# Configure Microsoft Defender for Endpoint

Enable Microsoft Defender for Endpoint to allow the playbook to stop an attack by triggering an incident response from MDE. 
 1. From the Azure Search bar, search for the Subscription in which MDE is installed.
 2. Click on the existing Subscription.
 3. Click Security in the Subscription menu.
 4. Ensure Microsoft Defender for Endpoint is On.
 5. If MDE is off, click Security Center.
 6. Find the Azure Defender card and click Enable Azure Defender.
 7. Select the desired subscription and click Upgrade.

# Deploy the Incident Response playbook

Deploying the Illusive Incident Enrichment playbook requires a custom deployment template. 
 - The playbook should be deployed under the same resource group, subscription, and workspace as the Azure app.
 - The Illusive API key should contain only the API key and no keywords such as “Bearer” or “Basic”.
 - You will not be prompted for missing information when saving the custom deployment configuration. If the playbook is incorrect or incomplete, the incident response playbook will not be able to isolate hosts, and you will get a playbook execution level error message. 
 - Though it is possible to enter integration information for both CrowdStrike and Microsoft Defender for Endpoint, the Illusive solution requires you to select just one tool for incident response.
 - Use the generic CrowdStrike API URL: https://api.crowdstrike.com. 
The playbook will fail to execute if the URL contains a hyphen  which is not supported by Sentinel (i.e., certain region-specific URLs). 

 1. On Azure home page, filter for Deploy a custom template.
 2. Under Custom Deployment>Select a template, click Build your own template in the editor.
 3. From Edit template, click Load file, the file named IllusiveSentinelIncidentResponse.json provided by Illusive and click Save.
 4. Under Custom Deployment>Basics, enter the configuration details.
    - Select the Subscription and Resource group that contains the Workspace with the dedicated Azure app that will run the Illusive Sentinel solution.
    - Under Instance details, specify the following information:
     - The Region
     - The Workspace Name of the Azure sentinel workspace
     - The authentication parameters required to access the Illusive API:
       - Illusive API URL
       - Illusive API Key
     - The authentication parameters required to access Sentinel API:
       - Azure-Sentinel Client ID: 
       - Azure-Sentinel Client Secret: 
       - Azure-Sentinel Tenant ID:
     - EDR deployed: The EDR which is deployed in the organization and can be used for incident mitigation
       - If CrowdStrike is selected, specify CrowdStrike authentication parameters: 
          - CrowdStrike API URL
          - CrowdStrike Client ID
          - CrowdStrike Client Secret
       - If MDE is selected, specify MDE authentication parameters: 
          - Azure MDE Client ID
          - Azure MDE Client Secret
          - Azure MDE Tenant ID
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
