# PurviewDataSensitivityLogs

Reference for PurviewDataSensitivityLogs table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Azure Resources, Security |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/purviewdatasensitivitylogs) |

## Solutions (2)

This table is used by the following solutions:

- [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md)
- [Microsoft Purview](../solutions/microsoft-purview.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Purview](../connectors/microsoftazurepurview.md)

---

## Content Items Using This Table (4)

### Analytic Rules (2)

**In solution [Microsoft Purview](../solutions/microsoft-purview.md):**
- [Sensitive Data Discovered in the Last 24 Hours](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Purview/Analytic%20Rules/MicrosoftPurviewSensitiveDataDiscovered.yaml)
- [Sensitive Data Discovered in the Last 24 Hours - Customized](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Purview/Analytic%20Rules/MicrosoftPurviewSensitiveDataDiscoveredCustom.yaml)

### Workbooks (2)

**In solution [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md):**
- [GDPRComplianceAndDataSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GDPR%20Compliance%20%26%20Data%20Security/Workbooks/GDPRComplianceAndDataSecurity.json)

**In solution [Microsoft Purview](../solutions/microsoft-purview.md):**
- [MicrosoftPurview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Purview/Workbooks/MicrosoftPurview.json)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.securityinsights/purview`
- `microsoft.purview/accounts`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
