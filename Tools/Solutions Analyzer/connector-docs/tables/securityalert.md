# SecurityAlert

Reference for SecurityAlert table in Azure Monitor Logs.

| | |
|----------|-------|
| **Table Name** | `SecurityAlert` |
| **Category** | Security |
| **Solutions Using Table** | 9 |
| **Connectors Ingesting** | 10 |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/securityalert) |

⚠️ **Note:** This table name is unique to specific connectors.

---

## Solutions (9)

This table is used by the following solutions:

- [IoTOTThreatMonitoringwithDefenderforIoT](../solutions/iototthreatmonitoringwithdefenderforiot.md)
- [Microsoft Defender For Identity](../solutions/microsoft-defender-for-identity.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [Microsoft Defender for Cloud](../solutions/microsoft-defender-for-cloud.md)
- [Microsoft Defender for Cloud Apps](../solutions/microsoft-defender-for-cloud-apps.md)
- [Microsoft Defender for Office 365](../solutions/microsoft-defender-for-office-365.md)
- [Microsoft Entra ID Protection](../solutions/microsoft-entra-id-protection.md)
- [MicrosoftDefenderForEndpoint](../solutions/microsoftdefenderforendpoint.md)
- [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md)

## Connectors (10)

This table is ingested by the following connectors:

- [Microsoft Entra ID Protection](../connectors/azureactivedirectoryidentityprotection.md)
- [Microsoft Defender for Identity](../connectors/azureadvancedthreatprotection.md)
- [Subscription-based Microsoft Defender for Cloud (Legacy)](../connectors/azuresecuritycenter.md)
- [Microsoft Defender for IoT](../connectors/iot.md)
- [Microsoft Defender for Cloud Apps](../connectors/microsoftcloudappsecurity.md)
- [Microsoft Defender for Endpoint](../connectors/microsoftdefenderadvancedthreatprotection.md)
- [Tenant-based Microsoft Defender for Cloud](../connectors/microsoftdefenderforcloudtenantbased.md)
- [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md)
- [Microsoft Defender for Office 365 (Preview)](../connectors/officeatp.md)
- [Microsoft 365 Insider Risk Management](../connectors/officeirm.md)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.securityinsights/securityinsights`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
