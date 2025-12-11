# Microsoft Defender XDR

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md)

**Publisher:** Microsoft

Microsoft Defender XDR is a unified, natively integrated, pre- and post-breach enterprise defense suite that protects endpoint, identity, email, and applications and helps you detect, prevent, investigate, and automatically respond to sophisticated threats.



Microsoft Defender XDR suite includes: 

- Microsoft Defender for Endpoint

- Microsoft Defender for Identity

- Microsoft Defender for Office 365

- Threat & Vulnerability Management

- Microsoft Defender for Cloud Apps



For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2220004&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **License**: M365 E5, M365 A5 or any other Microsoft Defender XDR eligible license.

**Tenant Permissions:**
Requires GlobalAdmin, SecurityAdmin on the workspace's tenant

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect incidents & alerts**

Connect Microsoft Defender XDR incidents to your Microsoft Sentinel. Incidents will appear in the incidents queue.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `MicrosoftThreatProtection`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

**2. Connect events**
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `MicrosoftDefenderATPEvents`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

| | |
|--------------------------|---|
| **Tables Ingested** | `AlertEvidence` |
| | `CloudAppEvents` |
| | `DeviceEvents` |
| | `DeviceFileCertificateInfo` |
| | `DeviceFileEvents` |
| | `DeviceImageLoadEvents` |
| | `DeviceInfo` |
| | `DeviceLogonEvents` |
| | `DeviceNetworkEvents` |
| | `DeviceNetworkInfo` |
| | `DeviceProcessEvents` |
| | `DeviceRegistryEvents` |
| | `EmailAttachmentInfo` |
| | `EmailEvents` |
| | `EmailPostDeliveryEvents` |
| | `EmailUrlInfo` |
| | `IdentityDirectoryEvents` |
| | `IdentityLogonEvents` |
| | `IdentityQueryEvents` |
| | `SecurityAlert` |
| | `SecurityIncident` |
| | `UrlClickEvents` |
| **Connector Definition Files** | [MicrosoftThreatProtection.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Data%20Connectors/MicrosoftThreatProtection.JSON) |

[→ View full connector details](../connectors/microsoftthreatprotection.md)

## Tables Reference

This solution ingests data into **22 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AlertEvidence` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `CloudAppEvents` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `DeviceEvents` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `DeviceFileCertificateInfo` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `DeviceFileEvents` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `DeviceImageLoadEvents` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `DeviceInfo` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `DeviceLogonEvents` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `DeviceNetworkEvents` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `DeviceNetworkInfo` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `DeviceProcessEvents` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `DeviceRegistryEvents` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `EmailAttachmentInfo` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `EmailEvents` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `EmailPostDeliveryEvents` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `EmailUrlInfo` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `IdentityDirectoryEvents` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `IdentityLogonEvents` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `IdentityQueryEvents` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `SecurityAlert` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `SecurityIncident` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |
| `UrlClickEvents` | [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md) |

[← Back to Solutions Index](../solutions-index.md)
