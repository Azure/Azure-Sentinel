# MDTI Playbook Guide

![Microsoft Defender Threat Intelligence](./MDTI.jpg)<br>

## Table of Contents

1. [Overview](#overview)
2. [Deployment](#deployment)
3. [Authentication](#authentication)
4. [Post Deployment Steps](#postdeployment)

<a name="overview">

## Overview
Microsoft centralizes numerous data sets into a single platform, Microsoft Defender Threat Intelligence [(MDTI)](https://learn.microsoft.com/en-us/defender/threat-intelligence/what-is-microsoft-defender-threat-intelligence-defender-ti), making it easier for Microsoft’s community and customers to conduct infrastructure analysis. Microsoft’s primary focus is to provide as much data as possible about Internet infrastructure to support a variety of security use cases. If you have trouble accessing your account or your credentials, contact your account representative or reach out to discussMDTI[@]microsoft.com.

<a name="deployment">

## Deployment Instructions

#### Deployment Parameters
| Name           | Description                                           | Default                     |
|----------------|-------------------------------------------------------|-----------------------------|
| PlaybookName   | Name of the Logic App (playbook)                      | MDTI-*                      |
| MDTI-BaseUrl   | MDTI Graph API base URL (must start with https://)    | https://graph.microsoft.com |
| Api-Version    | MDTI Graph API version                                | v1.0                        |

1. Deploy the playbooks by clicking on the "Deploy to Azure" button within each sub-folder. This will take you to the ARM Template deployment wizard.
2. Fill in the required parameters for deploying the playbooks.

<a name="authentication">

## Authentication

**Note: The Microsoft Graph API for Microsoft Defender Threat Intelligence requires an active [Defender Threat Intelligence Premium license](https://www.microsoft.com/en-us/security/business/siem-and-xdr/microsoft-defender-threat-intelligence) for the tenant.**

Playbook uses managed identity to query Microsoft Defender Threat Intelligence data, you must grant the managed identity of the playbook the `ThreatIntelligence.Read.All` application permission in Microsoft Graph. Once all the playbooks are deployed, follow these steps to assign permissions at once for very playbook:

1. Ensure you have the necessary Azure AD permissions (Security Administrator, Global Administrator, or Privileged Role Administrator).
2. Open the [Azure Cloud Shell](https://shell.azure.com/) or use a local PowerShell session with the Microsoft Graph module installed.
3. Run the following commands,

```powershell
# Install and import Microsoft Graph module
Install-Module Microsoft.Graph -Scope CurrentUser -AllowClobber
Import-Module Microsoft.Graph

# Authenticate to Microsoft Graph using Managed Identity
Connect-MgGraph -Identity

# Get Microsoft Graph service principal
$graphSp = Get-MgServicePrincipal -Filter "displayName eq 'Microsoft Graph'"

# Get the App Role ID for ThreatIntelligence.Read.All
$role = $graphSp.AppRoles | Where-Object {
    $_.Value -eq "ThreatIntelligence.Read.All" -and $_.AllowedMemberTypes -contains "Application"
}

# List of Logic App names
$logicAppNames = @(,
    "MDTI-Automated-Triage",
    "MDTI-Data-Cookies",
    "MDTI-Data-WebComponents",
    "MDTI-Intel-Reputation",
    "MDTI-Data-PassiveDns",
    "MDTI-Data-ReverseDnS",
    "MDTI-Data-Trackers"
)  # Add more names as needed

foreach ($appName in $logicAppNames) {
    Write-Host "Processing Logic App: $appName"

    # Get the Logic App's managed identity service principal
    $logicAppSp = Get-MgServicePrincipal -Filter "displayName eq '$appName'"

    if ($logicAppSp) {
        # Assign the permission to the Logic App
        New-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $logicAppSp.Id `
            -PrincipalId $logicAppSp.Id `
            -ResourceId $graphSp.Id `
            -AppRoleId $role.Id

        Write-Host "Permission assigned successfully to Logic App: $appName"
    } else {
        Write-Host "Service Principal not found for Logic App: $appName"
    }
}
```



For more details, refer to the [MDTI API documentation](https://learn.microsoft.com/en-us/graph/api/resources/security-threatintelligence-overview?view=graph-rest-beta&branch=pr-en-us-20472).

<a name="postdeployment">

## Post-Deployment Instructions


**1. Authorize Connections**

After deployment, authorize all connections:

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
Repeat steps for all connections.

**2. Assign Microsoft Sentinel Responder/Contributor Role to Playbook**

This playbook uses a managed identity, which must have the Microsoft Sentinel Responder/Contributor role assigned in the Sentinel instances to enable adding comments.

1. Select the Playbook resource.
2. In the left menu, click Identity.
3. Under Permissions, click Azure role assignments.
4. Click Add role assignment (Preview).
5. Use the drop-down lists to select the resource group that your *Sentinel Workspace* is in. If multiple workspaces are used in different resource groups consider selecting subscription as a scope instead.
6. In the Role drop-down list, select the role 'Microsoft Sentinel Responder' or 'Microsoft Sentinel Contributor'.
7. Click Save to assign the role.

**3. Attach the Incident Triggered Playbook to an Automation Rule**

To run the playbook automatically:

1. In Microsoft Sentinel, go to **Automation** > **Automation rules**.
2. Click **+ Add new** to create a new automation rule.
3. Set the rule conditions (e.g., when an alert/incident is created, or based on alert/incident details).
4. In the Actions section, select **Run playbook** and choose your Alert Triggered Playbook.
5. Save the automation rule.

For more details, see the [official documentation on automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules).

**4. Configure Analytics Rules to run Playbook**

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

## Troubleshooting
- No comments added: Verify automation rule executed and incident includes Host/IP entities.
- HTTP 403 on Graph calls: Confirm Managed Identity permission (ThreatIntelligence.Read.All) and admin consent granted.
- Empty cookie tables: Dataset may have no observations for the indicator; validate indicator in MDTI portal.

## References

- MDTI Overview: https://learn.microsoft.com/en-us/defender/threat-intelligence/what-is-microsoft-defender-threat-intelligence-defender-ti
- Trackers Dataset: https://learn.microsoft.com/en-us/defender/threat-intelligence/data-sets#trackers
- Web Components Dataset: https://learn.microsoft.com/en-us/defender/threat-intelligence/data-sets#components
- Reputation Dataset: https://learn.microsoft.com/en-us/defender/threat-intelligence/reputation-scoring
- Cookies Dataset: https://learn.microsoft.com/en-us/defender/threat-intelligence/data-sets#cookies
- Passive DNS Dataset: https://learn.microsoft.com/en-us/defender/threat-intelligence/data-sets#resolutions
- Passive DNS Reverse Dataset: https://learn.microsoft.com/en-us/defender/threat-intelligence/data-sets#reverse-dns
- Reputation & TI Permissions: https://learn.microsoft.com/en-us/graph/permissions-reference
- Sentinel Entity Mapping: https://learn.microsoft.com/azure/sentinel/map-data-fields-to-entities


