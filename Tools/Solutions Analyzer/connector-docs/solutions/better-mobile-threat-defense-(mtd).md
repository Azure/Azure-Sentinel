# BETTER Mobile Threat Defense (MTD)

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Better Mobile Security Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://www.better.mobi/about#contact-us](https://www.better.mobi/about#contact-us) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BETTER%20Mobile%20Threat%20Defense%20%28MTD%29](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BETTER%20Mobile%20Threat%20Defense%20%28MTD%29) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [BETTER Mobile Threat Defense (MTD)](../connectors/bettermtd.md)

**Publisher:** BETTER Mobile

The BETTER MTD Connector allows Enterprises to connect their Better MTD instances with Microsoft Sentinel, to view their data in Dashboards, create custom alerts, use it to trigger playbooks and expands threat hunting capabilities. This gives users more insight into their organization's mobile devices and ability to quickly analyze current mobile security posture which improves their overall SecOps capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `BetterMTDAppLog_CL` |
| | `BetterMTDDeviceLog_CL` |
| | `BetterMTDIncidentLog_CL` |
| | `BetterMTDNetflowLog_CL` |
| **Connector Definition Files** | [BETTERMTD.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BETTER%20Mobile%20Threat%20Defense%20%28MTD%29/Data%20Connectors/BETTERMTD.json) |

[→ View full connector details](../connectors/bettermtd.md)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `BetterMTDAppLog_CL` | [BETTER Mobile Threat Defense (MTD)](../connectors/bettermtd.md) |
| `BetterMTDDeviceLog_CL` | [BETTER Mobile Threat Defense (MTD)](../connectors/bettermtd.md) |
| `BetterMTDIncidentLog_CL` | [BETTER Mobile Threat Defense (MTD)](../connectors/bettermtd.md) |
| `BetterMTDNetflowLog_CL` | [BETTER Mobile Threat Defense (MTD)](../connectors/bettermtd.md) |

[← Back to Solutions Index](../solutions-index.md)
