# PaloAltoCDL

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via Legacy Agent](../connectors/paloaltocdl.md)
- [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via AMA](../connectors/paloaltocdlama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via AMA](../connectors/paloaltocdlama.md), [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via Legacy Agent](../connectors/paloaltocdl.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **22 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 10 |
| Hunting Queries | 10 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [PaloAlto - Dropping or denying session with traffic](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Analytic%20Rules/PaloAltoCDLDroppingSessionWithSentTraffic.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - File type changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Analytic%20Rules/PaloAltoCDLFileTypeWasChanged.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - Forbidden countries](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Analytic%20Rules/PaloAltoCDLUnexpectedCountries.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - Inbound connection to high risk ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Analytic%20Rules/PaloAltoCDLInboundRiskPorts.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - MAC address conflict](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Analytic%20Rules/PaloAltoCDLConflictingMacAddress.yaml) | Low | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - Possible attack without response](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Analytic%20Rules/PaloAltoCDLPossibleAttackWithoutResponse.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - Possible flooding](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Analytic%20Rules/PaloAltoCDLPossibleFlooding.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - Possible port scan](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Analytic%20Rules/PaloAltoCDLPossiblePortScan.yaml) | High | Reconnaissance | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - Put and post method request in high risk file type](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Analytic%20Rules/PaloAltoCDLPutMethodInHighRiskFileType.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - User privileges was changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Analytic%20Rules/PaloAltoCDLPrivilegesWasChanged.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [PaloAlto - Agent versions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Hunting%20Queries/PaloAltoCDLOutdatedAgentVersions.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - Critical event result](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Hunting%20Queries/PaloAltoCDLCriticalEventResult.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - Destination ports by IPs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Hunting%20Queries/PaloAltoCDLIPsByPorts.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - File permission with PUT or POST request](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Hunting%20Queries/PaloAltoCDLFilePermissionWithPutRequest.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - Incomplete application protocol](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Hunting%20Queries/PaloAltoCDLIncompleteApplicationProtocol.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - Multiple Deny result by user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Hunting%20Queries/PaloAltoCDLMultiDenyResultbyUser.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - Outdated config vesions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Hunting%20Queries/PaloAltoCDLOutdatedConfigVersions.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - Rare application layer protocols](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Hunting%20Queries/PaloAltoCDLRareApplicationLayerProtocol.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - Rare files observed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Hunting%20Queries/PaloAltoCDLRareFileRequests.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [PaloAlto - Rare ports by user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Hunting%20Queries/PaloAltoCDLRarePortsbyUser.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [PaloAltoCDL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Workbooks/PaloAltoCDL.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [PaloAltoCDLEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Parsers/PaloAltoCDLEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 12-11-2024                     | Removed Deprecated **Data Connector**                              |
| 3.0.2       | 12-07-2024                     | Deprecated **Data Connector**                                      |
| 3.0.1       | 12-06-2024                     | Optimized parser                                                   |
| 3.0.0       | 25-09-2023                     | Addition of new PaloAltoCDL AMA **Data Connector**                 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
