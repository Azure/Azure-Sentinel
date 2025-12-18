# Threat Intelligence (NEW)

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2025-04-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29) |

## Data Connectors

This solution provides **6 data connector(s)**.

### [Microsoft Defender Threat Intelligence](../connectors/microsoftdefenderthreatintelligence.md)

**Publisher:** Microsoft

### [Premium Microsoft Defender Threat Intelligence](../connectors/premiummicrosoftdefenderforthreatintelligence.md)

**Publisher:** Microsoft

### [Threat Intelligence Platforms](../connectors/threatintelligence.md)

**Publisher:** Microsoft

### [Threat intelligence - TAXII](../connectors/threatintelligencetaxii.md)

**Publisher:** Microsoft

### [Threat intelligence - TAXII Export (Preview)](../connectors/threatintelligencetaxiiexport.md)

**Publisher:** Microsoft

### [Threat Intelligence Upload API (Preview)](../connectors/threatintelligenceuploadindicatorsapi.md)

**Publisher:** Microsoft

Microsoft Sentinel offers a data plane API to bring in threat intelligence from your Threat Intelligence Platform (TIP), such as Threat Connect, Palo Alto Networks MineMeld, MISP, or other integrated applications. Threat indicators can include IP addresses, domains, URLs, file hashes and email addresses. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2269830&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permissions are required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. You can connect your threat intelligence data sources to Microsoft Sentinel by either:**

>Using an integrated Threat Intelligence Platform (TIP), such as Threat Connect, Palo Alto Networks MineMeld, MISP, and others. 

>Calling the Microsoft Sentinel data plane API directly from another application. 
 - Note: The 'Status' of the connector will not appear as 'Connected' here, because the data is ingested by making an API call.

**2. Follow These Steps to Connect to your Threat Intelligence:**

**1. Get Microsoft Entra ID Access Token**

To send request to the APIs, you need to acquire Microsoft Entra ID access token. You can follow instruction in this page: https://docs.microsoft.com/azure/databricks/dev-tools/api/latest/aad/app-aad-token#get-an-azure-ad-access-token 
  - Notice: Please request Microsoft Entra ID access token with scope value:  
Fairfax: https://management.usgovcloudapi.net/.default  
Mooncake: https://management.chinacloudapi.cn/.default

**2. Send STIX objects to Sentinel**

You can send the supported STIX object types by calling our Upload API. For more information about the API, click [here](https://learn.microsoft.com/azure/sentinel/stix-objects-api). 

>HTTP method: POST 

>Endpoint: 
Fairfax: https://api.ti.sentinel.azure.us/workspaces/[WorkspaceID]/threatintelligence-stix-objects:upload?api-version=2024-02-01-preview 
Mooncake: https://api.ti.sentinel.azure.cn/workspaces/[WorkspaceID]/threatintelligence-stix-objects:upload?api-version=2024-02-01-preview 

>WorkspaceID: the workspace that the STIX objects are uploaded to.  


>Header Value 1: "Authorization" = "Bearer [Microsoft Entra ID Access Token from step 1]" 


> Header Value 2: "Content-Type" = "application/json"  
 
>Body: The body is a JSON object containing an array of STIX objects.

| | |
|--------------------------|---|
| **Tables Ingested** | `ThreatIntelIndicators` |
| | `ThreatIntelObjects` |
| **Connector Definition Files** | [template_ThreatIntelligenceUploadIndicators_ForGov.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Data%20Connectors/template_ThreatIntelligenceUploadIndicators_ForGov.json) |

[→ View full connector details](../connectors/threatintelligenceuploadindicatorsapi.md)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [Threat Intelligence Platforms](../connectors/threatintelligence.md) |
| `ThreatIntelExportOperation` | [Threat intelligence - TAXII Export (Preview)](../connectors/threatintelligencetaxiiexport.md) |
| `ThreatIntelIndicators` | [Microsoft Defender Threat Intelligence](../connectors/microsoftdefenderthreatintelligence.md), [Premium Microsoft Defender Threat Intelligence](../connectors/premiummicrosoftdefenderforthreatintelligence.md), [Threat Intelligence Platforms](../connectors/threatintelligence.md), [Threat Intelligence Upload API (Preview)](../connectors/threatintelligenceuploadindicatorsapi.md), [Threat intelligence - TAXII](../connectors/threatintelligencetaxii.md) |
| `ThreatIntelObjects` | [Microsoft Defender Threat Intelligence](../connectors/microsoftdefenderthreatintelligence.md), [Premium Microsoft Defender Threat Intelligence](../connectors/premiummicrosoftdefenderforthreatintelligence.md), [Threat Intelligence Platforms](../connectors/threatintelligence.md), [Threat Intelligence Upload API (Preview)](../connectors/threatintelligenceuploadindicatorsapi.md), [Threat intelligence - TAXII](../connectors/threatintelligencetaxii.md) |

[← Back to Solutions Index](../solutions-index.md)
