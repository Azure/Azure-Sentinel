# Microsoft Entra ID Protection

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Protection) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Microsoft Entra ID Protection](../connectors/azureactivedirectoryidentityprotection.md)

**Publisher:** Microsoft

Microsoft Entra ID Protection provides a consolidated view at risk users, risk events and vulnerabilities, with the ability to remediate risk immediately, and set policies to auto-remediate future events. The service is built on Microsoft’s experience protecting consumer identities and gains tremendous accuracy from the signal from over 13 billion logins a day. Integrate Microsoft Microsoft Entra ID Protection alerts with Microsoft Sentinel to view dashboards, create custom alerts, and improve investigation. For more information, see the [Microsoft Sentinel documentation ](https://go.microsoft.com/fwlink/p/?linkid=2220065&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).



[Get Microsoft Entra ID Premium P1/P2 ](https://aka.ms/asi-ipcconnectorgetlink)

| | |
|--------------------------|---|
| **Tables Ingested** | `SecurityAlert` |
| **Connector Definition Files** | [template_AzureActiveDirectoryIdentityProtection.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Protection/Data%20Connectors/template_AzureActiveDirectoryIdentityProtection.JSON) |

[→ View full connector details](../connectors/azureactivedirectoryidentityprotection.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SecurityAlert` | [Microsoft Entra ID Protection](../connectors/azureactivedirectoryidentityprotection.md) |

[← Back to Solutions Index](../solutions-index.md)
