# Alibaba Cloud

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alibaba%20Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alibaba%20Cloud) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [AliCloud](../connectors/alicloud.md)

**Publisher:** AliCloud

The [AliCloud](https://www.alibabacloud.com/product/log-service) data connector provides the capability to retrieve logs from cloud applications using the Cloud API and store events into Microsoft Sentinel through the [REST API](https://aliyun-log-python-sdk.readthedocs.io/api.html). The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `AliCloud_CL` |
| **Connector Definition Files** | [AliCloud_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alibaba%20Cloud/Data%20Connectors/AliCloud_API_FunctionApp.json) |

[→ View full connector details](../connectors/alicloud.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AliCloud_CL` | [AliCloud](../connectors/alicloud.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------| 
| 3.0.1       | 24-02-2025                     |	Updated **Data Connector** Instructions |
| 3.0.0       | 09-09-2024                     |	Updated the python runtime version to 3.11   |

[← Back to Solutions Index](../solutions-index.md)
