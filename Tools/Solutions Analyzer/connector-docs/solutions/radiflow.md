# Radiflow

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Radiflow |
| **Support Tier** | Partner |
| **Support Link** | [https://www.radiflow.com](https://www.radiflow.com) |
| **Categories** | domains |
| **First Published** | 2024-06-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Radiflow iSID via AMA](../connectors/radiflowisid.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [Radiflow iSID via AMA](../connectors/radiflowisid.md) | Analytics |

## Content Items

This solution includes **9 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 8 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Radiflow - Exploit Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowExploitDetected.yaml) | High | InitialAccess, PrivilegeEscalation, LateralMovement | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Radiflow - Network Scanning Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowNetworkScanningDetected.yaml) | High | Discovery | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Radiflow - New Activity Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowNewActivityDetected.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Radiflow - Platform Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowPlatformAlert.yaml) | Medium | PrivilegeEscalation, Execution, CommandAndControl, Exfiltration, LateralMovement, ImpairProcessControl, InhibitResponseFunction, InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Radiflow - Policy Violation Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowPolicyViolationDetected.yaml) | Medium | LateralMovement, ImpairProcessControl, Execution, Collection, Persistence | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Radiflow - Suspicious Malicious Activity Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowSuspiciousMaliciousActivityDetected.yaml) | High | DefenseEvasion, InhibitResponseFunction | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Radiflow - Unauthorized Command in Operational Device](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowUnauthorizedCommandinOperationalDevice.yaml) | Medium | Execution, LateralMovement, InhibitResponseFunction, ImpairProcessControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Radiflow - Unauthorized Internet Access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowUnauthorizedInternetAccess.yaml) | Medium | InitialAccess, Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [RadiflowEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Parsers/RadiflowEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                             |
|-------------|--------------------------------|------------------------------------------------|
| 3.0.0       | 18-05-2024                     | Initial Solution Release                      |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
