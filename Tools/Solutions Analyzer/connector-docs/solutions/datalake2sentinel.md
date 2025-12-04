# Datalake2Sentinel

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Orange Cyberdefense |
| **Support Tier** | Partner |
| **Support Link** | [https://www.orangecyberdefense.com/global/contact](https://www.orangecyberdefense.com/global/contact) |
| **Categories** | domains,verticals |
| **First Published** | 2024-01-15 |
| **Last Updated** | 2024-01-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Datalake2Sentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Datalake2Sentinel) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### Datalake2Sentinel

**Publisher:** Orange Cyberdefense

This solution installs the Datalake2Sentinel connector which is built using the Codeless Connector Platform and allows you to automatically ingest threat intelligence indicators from **Datalake Orange Cyberdefense's CTI platform** into Microsoft Sentinel via the Upload Indicators REST API. After installing the solution, configure and enable this data connector by following guidance in Manage solution view.

**Tables Ingested:**

- `ThreatIntelligenceIndicator`

**Connector Definition Files:**

- [Datalake2SentinelConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Datalake2Sentinel/Data%20Connectors/Datalake2SentinelConnector.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ThreatIntelligenceIndicator` | Datalake2Sentinel |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n