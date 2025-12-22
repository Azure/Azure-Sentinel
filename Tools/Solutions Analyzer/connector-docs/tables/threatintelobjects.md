# ThreatIntelObjects

Reference for ThreatIntelObjects table in Azure Monitor Logs.

| | |
|----------|-------|
| **Table Name** | `ThreatIntelObjects` |
| **Category** | Security |
| **Solutions Using Table** | 1 |
| **Connectors Ingesting** | 5 |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/threatintelobjects) |

⚠️ **Note:** This table name is unique to specific connectors.

---

## Solutions (1)

This table is used by the following solutions:

- [Threat Intelligence (NEW)](../solutions/threat-intelligence-(new).md)

## Connectors (5)

This table is ingested by the following connectors:

- [Microsoft Defender Threat Intelligence](../connectors/microsoftdefenderthreatintelligence.md)
- [Premium Microsoft Defender Threat Intelligence](../connectors/premiummicrosoftdefenderforthreatintelligence.md)
- [Threat Intelligence Platforms](../connectors/threatintelligence.md)
- [Threat intelligence - TAXII](../connectors/threatintelligencetaxii.md)
- [Threat Intelligence Upload API (Preview)](../connectors/threatintelligenceuploadindicatorsapi.md)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.securityinsights/threatintelligence`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
