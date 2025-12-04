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
| `AlertEvidence` | Microsoft Defender XDR |
| `CloudAppEvents` | Microsoft Defender XDR |
| `DeviceEvents` | Microsoft Defender XDR |
| `DeviceFileCertificateInfo` | Microsoft Defender XDR |
| `DeviceFileEvents` | Microsoft Defender XDR |
| `DeviceImageLoadEvents` | Microsoft Defender XDR |
| `DeviceInfo` | Microsoft Defender XDR |
| `DeviceLogonEvents` | Microsoft Defender XDR |
| `DeviceNetworkEvents` | Microsoft Defender XDR |
| `DeviceNetworkInfo` | Microsoft Defender XDR |
| `DeviceProcessEvents` | Microsoft Defender XDR |
| `DeviceRegistryEvents` | Microsoft Defender XDR |
| `EmailAttachmentInfo` | Microsoft Defender XDR |
| `EmailEvents` | Microsoft Defender XDR |
| `EmailPostDeliveryEvents` | Microsoft Defender XDR |
| `EmailUrlInfo` | Microsoft Defender XDR |
| `IdentityDirectoryEvents` | Microsoft Defender XDR |
| `IdentityLogonEvents` | Microsoft Defender XDR |
| `IdentityQueryEvents` | Microsoft Defender XDR |
| `SecurityAlert` | Microsoft Defender XDR |
| `SecurityIncident` | Microsoft Defender XDR |
| `UrlClickEvents` | Microsoft Defender XDR |

[← Back to Solutions Index](../solutions-index.md)
