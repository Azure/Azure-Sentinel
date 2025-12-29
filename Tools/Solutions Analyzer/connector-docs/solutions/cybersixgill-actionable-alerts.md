# Cybersixgill-Actionable-Alerts

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cybersixgill |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cybersixgill.com/](https://www.cybersixgill.com/) |
| **Categories** | domains |
| **First Published** | 2023-02-27 |
| **Last Updated** | 2024-09-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cybersixgill-Actionable-Alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cybersixgill-Actionable-Alerts) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Cybersixgill Actionable Alerts](../connectors/cybersixgillactionablealerts.md)

**Publisher:** Cybersixgill

Actionable alerts provide customized alerts based on configured assets

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CyberSixgill_Alerts_CL` |
| **Connector Definition Files** | [Cybersixgill_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cybersixgill-Actionable-Alerts/Data%20Connectors/Cybersixgill_FunctionApp.json) |

[→ View full connector details](../connectors/cybersixgillactionablealerts.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CyberSixgill_Alerts_CL` | [Cybersixgill Actionable Alerts](../connectors/cybersixgillactionablealerts.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 02-09-2024                     | Updated the python runtime version to 3.11  |
| 3.0.0       | 20-02-2024                     | Replaced Hyperlinks with Shortlinks (aka.ms) in Data Connector |

[← Back to Solutions Index](../solutions-index.md)
