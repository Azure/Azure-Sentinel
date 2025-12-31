# Zscaler Private Access (ZPA)

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-01-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Zscaler Private Access](../connectors/zscalerprivateaccess.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ZPA_CL`](../tables/zpa-cl.md) | [[Deprecated] Zscaler Private Access](../connectors/zscalerprivateaccess.md) | Analytics, Hunting, Workbooks |

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
| [Zscaler - Connections by dormant user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Analytic%20Rules/ZscalerZPAConnectionsByDormantUser.yaml) | High | Persistence | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - Forbidden countries](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Analytic%20Rules/ZscalerUnexpectedCountries.yaml) | High | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - Shared ZPA session](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Analytic%20Rules/ZscalerSharedZPASession.yaml) | High | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - Unexpected ZPA session duration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Analytic%20Rules/ZscalerZPAUnexpectedSessionDuration.yaml) | Medium | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - Unexpected event count of rejects by policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Analytic%20Rules/ZscalerUnexpectedCountEventResult.yaml) | High | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - Unexpected update operation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Analytic%20Rules/ZscalerUnexpectedUpdateOperation.yaml) | Medium | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - ZPA connections by new user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Analytic%20Rules/ZscalerZPAConnectionsByNewUser.yaml) | Medium | Persistence | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - ZPA connections from new IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Analytic%20Rules/ZscalerZPAConnectionsFromNewIP.yaml) | Medium | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - ZPA connections from new country](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Analytic%20Rules/ZscalerZPAConnectionsFromNewCountry.yaml) | Medium | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - ZPA connections outside operational hours](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Analytic%20Rules/ZscalerZPAConnectionsOutsideOperationalHours.yaml) | Medium | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Zscaler - Abnormal total bytes size](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Hunting%20Queries/ZscalerAbnormalTotalBytesSize.yaml) | Exfiltration, Collection | - |
| [Zscaler - Applications using by accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Hunting%20Queries/ZscalerApplicationByUsers.yaml) | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - Connection close reasons](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Hunting%20Queries/ZscalerConnectionCloseReason.yaml) | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - Destination ports by IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Hunting%20Queries/ZscalerIPsByPorts.yaml) | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - Rare urlhostname requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Hunting%20Queries/ZscalerUrlhostname.yaml) | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - Server error by user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Hunting%20Queries/ZscalerUserServerErrors.yaml) | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - Top connectors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Hunting%20Queries/ZscalerTopConnectors.yaml) | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - Top source IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Hunting%20Queries/ZscalerTopSourceIP.yaml) | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - Users access groups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Hunting%20Queries/ZscalerUserAccessGroups.yaml) | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |
| [Zscaler - Users by source location countries](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Hunting%20Queries/ZscalerSourceLocation.yaml) | InitialAccess | [`ZPA_CL`](../tables/zpa-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ZscalerZPA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Workbooks/ZscalerZPA.json) | [`ZPA_CL`](../tables/zpa-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ZPAEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Parsers/ZPAEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 28-08-2025                     | The parser query now includes additional fields such as SessionID, IPProtocol, ClientCountryCode, and others, improving event parsing and enrichment.                                              |
| 3.0.2       | 08-07-2025                     | Enhanced **Parser** logic to improve result filtering. |
| 3.0.1       | 05-12-2024                     | Removed Deperacted **Data connectors**                             |
| 3.0.0       | 22-08-2024                     | Deprecating data connectors    								    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
