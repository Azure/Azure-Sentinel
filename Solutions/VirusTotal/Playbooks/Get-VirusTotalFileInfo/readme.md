# Get-VirusTotalFileInfo
Author: Nicholas DiCola

This playbook processes each File Hash entity to query VirusTotal for detailed file information. For more details, visit the [VirusTotal File Info API documentation](https://developers.virustotal.com/v3.0/reference#file-info).

## Prerequisites
- Obtain a VirusTotal API key by registering with the VirusTotal community. [Register here](https://www.virustotal.com/gui/join-us)

## Quick Deployment
**Deploy with Incident Trigger** (Recommended)

Deploy this playbook and attach it to an **automation rule** to ensure it runs automatically whenever an incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVirusTotal%2FPlaybooks%2FGet-VirusTotalFileInfo%2Fincident-trigger%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVirusTotal%2FPlaybooks%2FGet-VirusTotalFileInfo%2Fincident-trigger%2Fazuredeploy.json)

**Deploy with Alert Trigger**

Deploy this playbook to run manually on alerts or attach it to an **analytics rule** to execute automatically when an alert is generated.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVirusTotal%2FPlaybooks%2FGet-VirusTotalFileInfo%2Falert-trigger%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVirusTotal%2FPlaybooks%2FGet-VirusTotalFileInfo%2Falert-trigger%2Fazuredeploy.json)

## Post Deployment Instructions

**1. Authorize Connections**

After deployment, authorize all connections:

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
Repeat steps for all connections.

**2. Assign Microsoft Sentinel Responder Role to Playbook**

This playbook uses a managed identity, which must have the Microsoft Sentinel Responder role assigned in the Sentinel instances to enable adding comments.

1. Select the Playbook resource.
2. In the left menu, click Identity.
3. Under Permissions, click Azure role assignments.
4. Click Add role assignment (Preview).
5. Use the drop-down lists to select the resource group that your *Sentinel Workspace* is in. If multiple workspaces are used in different resource groups consider selecting subscription as a scope instead.
6. In the Role drop-down list, select the role 'Microsoft Sentinel Responder'.
7. Click Save to assign the role.

**3. Only for Alert Triggered Playbooks - Assign the Log Analytics Reader Role to Playbook**

Alert triggered playbooks need to read data from Log Analytics workspace, assign the Log Analytics Reader role to its managed identity:

1. Go to the Azure portal and navigate to your Log Analytics Workspace.
2. In the left menu, select **Access control (IAM)**.
3. Click **Add > Add role assignment**.
4. In the Role drop-down, select **Log Analytics Reader**.
5. In the Members tab, select **Managed identity** and choose the playbook's managed identity.
6. Click **Review + assign** to complete.

**4. Attach the Alert Triggered Playbook to an Automation Rule**

To run the playbook automatically:

1. In Microsoft Sentinel, go to **Automation** > **Automation rules**.
2. Click **+ Add new** to create a new automation rule.
3. Set the rule conditions (e.g., when an alert/incident is created, or based on alert/incident details).
4. In the Actions section, select **Run playbook** and choose your Alert Triggered Playbook.
5. Save the automation rule.

For more details, see the [official documentation on automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules).

**5. Configure Analytics Rules to run Playbook**

To ensure this playbook is triggered by alerts/incidents containing File Hash entities, configure your analytics rules as follows:

1. In Microsoft Sentinel, go to **Analytics** and create a new scheduled query rule or edit an existing one.
2. In the rule creation workflow, go to the **Set rule logic** tab.
3. In the **Alert enhancement** section, expand **Entity mapping**.
4. Click **Add new entity**:
   - For file hashes, select **File** as the entity type, then map the appropriate identifier (such as **SHA256**, **SHA1**, or **MD5**) to the field in your query that contains the file hash value.
5. You can map up to 10 entities per rule and up to 3 identifiers per entity.
6. Complete the rest of the rule configuration and save.

For more details, see the official documentation on [mapping data fields to entities in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/map-data-fields-to-entities#how-to-map-entities).

## Screenshots
**Incident Trigger**
![Incident Trigger](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/VirusTotal/Playbooks/Get-VirusTotalFileInfo/incident-trigger/images/designerLight.png)

**Alert Trigger**
![Alert Trigger](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/VirusTotal/Playbooks/Get-VirusTotalFileInfo/alert-trigger/images/Get-VirusTotalFileInfo_alert.png)