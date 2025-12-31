# Microsoft Exchange Security - Exchange Online

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-12-21 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Exchange Security Insights Online Collector](../connectors/esi-exchangeonlinecollector.md)

## Tables Reference

This solution uses **8 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ESIExchangeOnlineConfig_CL`](../tables/esiexchangeonlineconfig-cl.md) | [Exchange Security Insights Online Collector](../connectors/esi-exchangeonlinecollector.md) | Workbooks |
| [`ExchangeAdminAuditLogs`](../tables/exchangeadminauditlogs.md) | - | Workbooks |
| [`ExchangeConfiguration`](../tables/exchangeconfiguration.md) | - | Workbooks |
| [`ExchangeEnvironmentList`](../tables/exchangeenvironmentlist.md) | - | Workbooks |
| [`OfficeActivity`](../tables/officeactivity.md) | - | Workbooks |
| [`RolevsCmdlet`](../tables/rolevscmdlet.md) | - | Workbooks |
| [`WhenCreated`](../tables/whencreated.md) | - | Workbooks |
| [`allDataRange`](../tables/alldatarange.md) | - | Workbooks |

## Content Items

This solution includes **10 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 5 |
| Workbooks | 4 |
| Watchlists | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Microsoft Exchange Admin Activity - Online](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Workbooks/Microsoft%20Exchange%20Admin%20Activity%20-%20Online.json) | [`OfficeActivity`](../tables/officeactivity.md) |
| [Microsoft Exchange Least Privilege with RBAC - Online](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Workbooks/Microsoft%20Exchange%20Least%20Privilege%20with%20RBAC%20-%20Online.json) | [`ESIExchangeOnlineConfig_CL`](../tables/esiexchangeonlineconfig-cl.md)<br>[`ExchangeAdminAuditLogs`](../tables/exchangeadminauditlogs.md)<br>[`ExchangeEnvironmentList`](../tables/exchangeenvironmentlist.md)<br>[`RolevsCmdlet`](../tables/rolevscmdlet.md) |
| [Microsoft Exchange Search AdminAuditLog - Online](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Workbooks/Microsoft%20Exchange%20Search%20AdminAuditLog%20-%20Online.json) | [`OfficeActivity`](../tables/officeactivity.md) |
| [Microsoft Exchange Security Review - Online](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Workbooks/Microsoft%20Exchange%20Security%20Review%20-%20Online.json) | [`ESIExchangeOnlineConfig_CL`](../tables/esiexchangeonlineconfig-cl.md)<br>[`ExchangeConfiguration`](../tables/exchangeconfiguration.md)<br>[`ExchangeEnvironmentList`](../tables/exchangeenvironmentlist.md)<br>[`WhenCreated`](../tables/whencreated.md)<br>[`allDataRange`](../tables/alldatarange.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ExchangeConfiguration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Parsers/ExchangeConfiguration.yaml) | - | - |
| [ExchangeEnvironmentList](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Parsers/ExchangeEnvironmentList.yaml) | - | - |
| [MESCheckOnlineVIP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Parsers/MESCheckOnlineVIP.yaml) | - | - |
| [MESCompareDataMRA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Parsers/MESCompareDataMRA.yaml) | - | - |
| [MESOfficeActivityLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Parsers/MESOfficeActivityLogs.yaml) | - | - |

### Watchlists

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ExchOnlineVIP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Watchlists/ExchOnlineVIP.json) | - | - |

## Additional Documentation

> 📄 *Source: [Microsoft Exchange Security - Exchange Online/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft Exchange Security - Exchange Online/README.md)*

## Overview

We have published Public Contents for the Microsoft Exchange Security Sentinel Solution. The contents can be found here:

* [General Documentation & Artifacts](./%23%20-%20General%20Content/README.md)

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.1.7       | 26-03-2025                     | Update documentation link to new repository     |
| 3.1.6       | 30-08-2024                     | Correct bug on LasdtReceivedData of DataConnector. and change parser     |
| 3.1.5       | 15-05-2024                     | Enhancement in existing **Parser**       |
| 3.1.4       | 30-04-2024                     | Repackaged for parser issue       |
| 3.1.3       | 25-04-2024                     | Repackaged for parser issue with old names       |
| 3.1.2       | 18-04-2024                     | Repackaged for parser issue while update       |
| 3.1.1       | 19-03-2024                     | Manually updated package content       |
| 3.0.5       | 20-02-2024                     | Correct DataConnector last Log indicator       |
| 3.0.4       | 18-12-2023                     | Correct Parser parameters and force version update       |
| 3.0.3       | 05-12-2023                     | Added parameters in **Parser** to fix default values issue.        |
| 3.0.2       | 01-11-2023                     | Added a **Parser** to verify if user is Microsoft Exchange Security VIP (Watchlist)          |
| 3.0.1       | 13-09-2023                     | Readme file for parsers added and typo correction                      |
| 3.0.0       | 23-08-2023                     | ExchangeEnvironmentList parser name  corrected in **Workbooks**.  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
