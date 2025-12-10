# Microsoft Defender XDR

| | |
|----------|-------|
| **Connector ID** | `MicrosoftThreatProtection` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AlertEvidence`](../tables-index.md#alertevidence), [`CloudAppEvents`](../tables-index.md#cloudappevents), [`DeviceEvents`](../tables-index.md#deviceevents), [`DeviceFileCertificateInfo`](../tables-index.md#devicefilecertificateinfo), [`DeviceFileEvents`](../tables-index.md#devicefileevents), [`DeviceImageLoadEvents`](../tables-index.md#deviceimageloadevents), [`DeviceInfo`](../tables-index.md#deviceinfo), [`DeviceLogonEvents`](../tables-index.md#devicelogonevents), [`DeviceNetworkEvents`](../tables-index.md#devicenetworkevents), [`DeviceNetworkInfo`](../tables-index.md#devicenetworkinfo), [`DeviceProcessEvents`](../tables-index.md#deviceprocessevents), [`DeviceRegistryEvents`](../tables-index.md#deviceregistryevents), [`EmailAttachmentInfo`](../tables-index.md#emailattachmentinfo), [`EmailEvents`](../tables-index.md#emailevents), [`EmailPostDeliveryEvents`](../tables-index.md#emailpostdeliveryevents), [`EmailUrlInfo`](../tables-index.md#emailurlinfo), [`IdentityDirectoryEvents`](../tables-index.md#identitydirectoryevents), [`IdentityLogonEvents`](../tables-index.md#identitylogonevents), [`IdentityQueryEvents`](../tables-index.md#identityqueryevents), [`SecurityAlert`](../tables-index.md#securityalert), [`SecurityIncident`](../tables-index.md#securityincident), [`UrlClickEvents`](../tables-index.md#urlclickevents) |
| **Used in Solutions** | [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md) |
| **Connector Definition Files** | [MicrosoftThreatProtection.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Data%20Connectors/MicrosoftThreatProtection.JSON) |

Microsoft Defender XDR is a unified, natively integrated, pre- and post-breach enterprise defense suite that protects endpoint, identity, email, and applications and helps you detect, prevent, investigate, and automatically respond to sophisticated threats.



Microsoft Defender XDR suite includes: 

- Microsoft Defender for Endpoint

- Microsoft Defender for Identity

- Microsoft Defender for Office 365

- Threat & Vulnerability Management

- Microsoft Defender for Cloud Apps



For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2220004&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **License**: M365 E5, M365 A5 or any other Microsoft Defender XDR eligible license.

**Tenant Permissions:**
Requires GlobalAdmin, SecurityAdmin on the workspace's tenant

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect incidents & alerts**

Connect Microsoft Defender XDR incidents to your Microsoft Sentinel. Incidents will appear in the incidents queue.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `MicrosoftThreatProtection`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

**2. Connect events**
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `MicrosoftDefenderATPEvents`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
