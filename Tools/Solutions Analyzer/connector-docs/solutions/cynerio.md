# Cynerio

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cynerio |
| **Support Tier** | Partner |
| **Support Link** | [https://cynerio.com](https://cynerio.com) |
| **Categories** | domains |
| **First Published** | 2023-03-29 |
| **Last Updated** | 2023-03-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cynerio](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cynerio) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Cynerio Security Events](../connectors/cyneriosecurityevents.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CynerioEvent_CL`](../tables/cynerioevent-cl.md) | [Cynerio Security Events](../connectors/cyneriosecurityevents.md) | Analytics, Workbooks |

## Content Items

This solution includes **8 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 5 |
| Parsers | 2 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Cynerio - Exploitation Attempt of IoT device](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cynerio/Analytic%20Rules/IoTExploitationAttempts.yaml) | High | LateralMovement | [`CynerioEvent_CL`](../tables/cynerioevent-cl.md) |
| [Cynerio - IoT - Default password](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cynerio/Analytic%20Rules/IoTDefaultPasswords.yaml) | High | CredentialAccess | [`CynerioEvent_CL`](../tables/cynerioevent-cl.md) |
| [Cynerio - IoT - Weak password](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cynerio/Analytic%20Rules/IoTWeakPasswords.yaml) | High | CredentialAccess | [`CynerioEvent_CL`](../tables/cynerioevent-cl.md) |
| [Cynerio - Medical device scanning](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cynerio/Analytic%20Rules/MedicalDeviceScanning.yaml) | Medium | LateralMovement | [`CynerioEvent_CL`](../tables/cynerioevent-cl.md) |
| [Cynerio - Suspicious Connection to External Address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cynerio/Analytic%20Rules/SuspiciousConnections.yaml) | High | LateralMovement | [`CynerioEvent_CL`](../tables/cynerioevent-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CynerioOverviewWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cynerio/Workbooks/CynerioOverviewWorkbook.json) | [`CynerioEvent_CL`](../tables/cynerioevent-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CynerioEvent_Authentication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cynerio/Parsers/CynerioEvent_Authentication.yaml) | - | - |
| [CynerioEvent_NetworkSession](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cynerio/Parsers/CynerioEvent_NetworkSession.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 11-07-2023                     | New analytic rules and workbook
| 2.0.0       | 29-03-2023                     | Initial Solution Release |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
