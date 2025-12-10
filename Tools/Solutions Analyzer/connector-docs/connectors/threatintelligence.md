# Threat Intelligence Platforms

| | |
|----------|-------|
| **Connector ID** | `ThreatIntelligence` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog), [`ThreatIntelIndicators`](../tables-index.md#threatintelindicators), [`ThreatIntelObjects`](../tables-index.md#threatintelobjects), [`ThreatIntelligenceIndicator`](../tables-index.md#threatintelligenceindicator) |
| **Used in Solutions** | [Threat Intelligence](../solutions/threat-intelligence.md), [Threat Intelligence (NEW)](../solutions/threat-intelligence-(new).md) |
| **Connector Definition Files** | [template_ThreatIntelligence.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Data%20Connectors/template_ThreatIntelligence.json) |

Microsoft Sentinel integrates with Microsoft Graph Security API data sources to enable monitoring, alerting, and hunting using your threat intelligence. Use this connector to send threat indicators to Microsoft Sentinel from your Threat Intelligence Platform (TIP), such as Threat Connect, Palo Alto Networks MindMeld, MISP, or other integrated applications. Threat indicators can include IP addresses, domains, URLs, and file hashes. For more information, see the [Microsoft Sentinel documentation >](https://go.microsoft.com/fwlink/p/?linkid=2223729&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Tenant Permissions:**
Requires GlobalAdmin, SecurityAdmin on the workspace's tenant

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. You can connect your threat intelligence data sources to Microsoft Sentinel by either:**

- Using an integrated Threat Intelligence Platform (TIP), such as Threat Connect, Palo Alto Networks MindMeld, MISP, and others.

- Calling the Microsoft Graph Security API directly from another application.

**2. Follow These Steps to Connect your Threat Intelligence:**

1) [Register an application](https://docs.microsoft.com/graph/auth-v2-service#1-register-your-app) in Azure Active Directory.

2) [Configure permissions](https://docs.microsoft.com/graph/auth-v2-service#2-configure-permissions-for-microsoft-graph) and be sure to add the ThreatIndicators.ReadWrite.OwnedBy permission to the application.

3) Ask your Azure AD tenant administrator to [grant consent](https://docs.microsoft.com/graph/auth-v2-service#3-get-administrator-consent) to the application.

4) Configure your TIP or other integrated application to push indicators to Microsoft Sentinel by specifying the following:

    a. The application ID and secret you received when registering the app (step 1 above). 

    b. Set “Microsoft Sentinel” as the target.

    c. Set an action for each indicator - ‘alert’ is most relevant for Microsoft Sentinel use cases 

For the latest list of integrated Threat Intelligence Platforms and detailed configuration instructions, see the [full documentation](https://docs.microsoft.com/azure/sentinel/import-threat-intelligence#adding-threat-indicators-to-azure-sentinel-with-the-threat-intelligence-platforms-data-connector).

Click on "Connect" below

> Data from all regions will be sent to and stored in the workspace's region.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `ThreatIntelligence`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
