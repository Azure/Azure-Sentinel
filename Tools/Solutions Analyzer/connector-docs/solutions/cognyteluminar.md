# CognyteLuminar

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Cognyte Luminar |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cognyte.com/contact/](https://www.cognyte.com/contact/) |
| **Categories** | domains |
| **First Published** | 2023-09-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CognyteLuminar](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CognyteLuminar) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### Luminar IOCs and Leaked Credentials

**Publisher:** Cognyte Technologies Israel Ltd

Luminar IOCs and Leaked Credentials connector allows integration of intelligence-based IOC data and customer-related leaked records identified by Luminar.

**Tables Ingested:**

- `ThreatIntelligenceIndicator`

**Connector Definition Files:**

- [CognyteLuminar_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CognyteLuminar/Data%20Connectors/CognyteLuminar_FunctionApp.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ThreatIntelligenceIndicator` | Luminar IOCs and Leaked Credentials |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n