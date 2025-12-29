# VMRay

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | VMRay |
| **Support Tier** | Partner |
| **Support Link** | [https://www.vmray.com/contact/customer-support/](https://www.vmray.com/contact/customer-support/) |
| **Categories** | domains |
| **First Published** | 2025-07-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [VMRayThreatIntelligence](../connectors/vmray.md)

**Publisher:** VMRay

VMRayThreatIntelligence connector automatically generates and feeds threat intelligence for all submissions to VMRay, improving threat detection and incident response in Sentinel. This seamless integration empowers teams to proactively address emerging threats.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ThreatIntelligenceIndicator` |
| **Connector Definition Files** | [VMRayThreatIntelligence_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMRay/Data%20Connectors/VMRayThreatIntelligence_FunctionApp.json) |

[→ View full connector details](../connectors/vmray.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ThreatIntelligenceIndicator` | [VMRayThreatIntelligence](../connectors/vmray.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 07-11-2025                     | Fixed Premium ARM template                  |
| 3.0.0       | 23-07-2025                     | Initial Solution Release                    |

[← Back to Solutions Index](../solutions-index.md)
