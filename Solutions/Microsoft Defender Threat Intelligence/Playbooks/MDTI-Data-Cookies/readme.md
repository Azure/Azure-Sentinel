# MDTI-Data-Cookies

## Overview
This playbook uses the [Microsoft Defender Threat Intelligence](https://learn.microsoft.com/en-us/defender/threat-intelligence/what-is-microsoft-defender-threat-intelligence-defender-ti) **Cookies** data set to automatically enrich Microsoft Sentinel incidents. It extracts Host and IP entities from new incidents and queries the MDTI Cookies data ([dataset reference](https://learn.microsoft.com/en-us/defender/threat-intelligence/data-sets#cookies)) to identify cookie names observed for the related infrastructure. The playbook then adds formatted comments to the incident summarizing any cookies discovered so analysts can quickly pivot for deeper investigation. Cookies can contain application state, tracking identifiers, or values abused by adversaries for persistence or victim correlation.

## Key Capabilities
- Automatically triggers on new Sentinel incidents (incident creation trigger).
- Collects Host and IP entities (up to the limits of the incident payload).
- Queries MDTI Cookies data via Microsoft Graph (Managed Identity auth).
- Generates per-host and per-IP HTML tables summarizing cookie observations.
- Adds structured comments back to the originating incident.

## Prerequisites
1. Microsoft Defender Threat Intelligence (MDTI) Premium license enabled for the tenant.
2. One of the following Azure AD roles (to grant Graph application permissions to the playbook's Managed Identity): Security Administrator, Global Administrator, or Privileged Role Administrator.

## Deployment Parameters
| Name | Description | Default |
|------|-------------|---------|
| PlaybookName | Name of the Logic App (playbook) | MDTI-Data-Cookies |
| MDTI-BaseUrl | MDTI Graph API base URL (must start with https://) | https://graph.microsoft.com |
| Api-Version | MDTI Graph API version | v1.0 |

## Deploy to Azure
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMicrosoft%2520Defender%2520Threat%2520Intelligence%2FPlaybooks%2FMDTI-Data-Cookies%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton" alt="Deploy to Azure"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMicrosoft%2520Defender%2520Threat%2520Intelligence%2FPlaybooks%2FMDTI-Data-Cookies%2Fazuredeploy.json" target="_blank">
    <img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png" alt="Deploy to Azure Gov"/>
</a>

## Post-Deployment Steps

### 1. Assign Microsoft Graph Permission (ThreatIntelligence.Read.All) to Managed Identity
To allow the playbook to query Microsoft Defender Threat Intelligence data, you must grant the managed identity of the playbook the `ThreatIntelligence.Read.All` application permission in Microsoft Graph. Follow these steps:

1. Ensure you have the necessary Azure AD permissions (Security Administrator, Global Administrator, or Privileged Role Administrator).
2. Open the [Azure Cloud Shell](https://shell.azure.com/) or use a local PowerShell session with the Microsoft Graph module installed.
3. Run the following commands, replacing `'MDTI-Data-Cookies'` with your playbook's name if different:

```powershell
# Install the Microsoft Graph module for interacting with Microsoft Graph APIs
Install-Module Microsoft.Graph -Scope CurrentUser -AllowClobber -Force
Import-Module Microsoft.Graph

# Authenticate to Microsoft Graph using Managed Identity
Connect-MgGraph -Identity

# Retrieve the Microsoft Graph Service Principal
$graphSp = Get-MgServicePrincipal -Filter "displayName eq 'Microsoft Graph'"

# Find the ThreatIntelligence.Read.All role
$role = $graphSp.AppRoles | Where-Object { $_.Value -eq 'ThreatIntelligence.Read.All' -and $_.AllowedMemberTypes -contains 'Application' }

# Define the Logic App name (update if different)
$logicAppName = 'MDTI-Data-Cookies'
$logicAppSp = Get-MgServicePrincipal -Filter "displayName eq '$logicAppName'"

# Assign the ThreatIntelligence.Read.All role to the Logic App's Managed Identity
New-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $logicAppSp.Id `
    -PrincipalId $logicAppSp.Id `
    -ResourceId $graphSp.Id `
    -AppRoleId $role.Id

# Confirm the role assignment
Write-Host "Permission assigned successfully to Logic App ${logicAppName}."
```

**2. Authorize Connections**

After deployment, authorize all connections:

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
Repeat steps for all connections.

**3. Assign Microsoft Sentinel Responder Role to Playbook**

This playbook uses a managed identity, which must have the Microsoft Sentinel Responder role assigned in the Sentinel instances to enable adding comments.

1. Select the Playbook resource.
2. In the left menu, click Identity.
3. Under Permissions, click Azure role assignments.
4. Click Add role assignment (Preview).
5. Use the drop-down lists to select the resource group that your *Sentinel Workspace* is in. If multiple workspaces are used in different resource groups consider selecting subscription as a scope instead.
6. In the Role drop-down list, select the role 'Microsoft Sentinel Responder'.
7. Click Save to assign the role.

**4. Attach the Incident Triggered Playbook to an Automation Rule**

To run the playbook automatically:

1. In Microsoft Sentinel, go to **Automation** > **Automation rules**.
2. Click **+ Add new** to create a new automation rule.
3. Set the rule conditions (e.g., when an alert/incident is created, or based on alert/incident details).
4. In the Actions section, select **Run playbook** and choose your Alert Triggered Playbook.
5. Save the automation rule.

For more details, see the [official documentation on automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules).

**5. Configure Analytics Rules to run Playbook**

To ensure this playbook is triggered by alerts/incidents containing URL entities, configure your analytics rules as follows:

1. In Microsoft Sentinel, go to **Analytics** and create a new scheduled query rule or edit an existing one.
2. In the rule creation workflow, go to the **Set rule logic** tab.
3. In the **Alert enhancement** section, expand **Entity mapping**.
4. Click **Add new entity**:
   - For IPs, select **IP** as the entity type, then map the **Address** identifier to the field in your query that contains the IP address value.
   - For Hostnames, select **Host** as the entity type, then map the **FullName** identifier to the field in your query that contains the IP address value.
5. You can map up to 10 entities per rule and up to 3 identifiers per entity.
6. Complete the rest of the rule configuration and save.

For more details, see the official documentation on [mapping data fields to entities in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/map-data-fields-to-entities#how-to-map-entities).

## How It Works
1. Incident creation trigger fires
2. Retrieves related Host and IP entities
3. For each Host/IP, calls MDTI Cookies endpoint (Graph) using Managed Identity
4. Builds HTML tables summarizing observed cookies
5. Posts consolidated comments back to the incident

## Troubleshooting
- No comments added: Verify automation rule executed and incident includes Host/IP entities.
- HTTP 403 on Graph calls: Confirm Managed Identity permission (ThreatIntelligence.Read.All) and admin consent granted.
- Empty cookie tables: Dataset may have no observations for the indicator; validate indicator in MDTI portal.

## References
- MDTI Overview: https://learn.microsoft.com/en-us/defender/threat-intelligence/what-is-microsoft-defender-threat-intelligence-defender-ti
- Cookies Dataset: https://learn.microsoft.com/en-us/defender/threat-intelligence/data-sets#cookies
- Reputation & TI Permissions: https://learn.microsoft.com/en-us/graph/permissions-reference
- Sentinel Entity Mapping: https://learn.microsoft.com/azure/sentinel/map-data-fields-to-entities
