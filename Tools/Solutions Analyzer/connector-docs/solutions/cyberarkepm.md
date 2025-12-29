# CyberArkEPM

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | CyberArk Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyberark.com/services-support/technical-support-contact/](https://www.cyberark.com/services-support/technical-support-contact/) |
| **Categories** | domains |
| **First Published** | 2022-04-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [CyberArkEPM](../connectors/cyberarkepm.md)

**Publisher:** CyberArk

The [CyberArk Endpoint Privilege Manager](https://www.cyberark.com/products/endpoint-privilege-manager/) data connector provides the capability to retrieve security event logs of the CyberArk EPM services and more events into Microsoft Sentinel through the REST API. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CyberArkEPM_CL` |
| **Connector Definition Files** | [CyberArkEPM_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Data%20Connectors/CyberArkEPM_API_FunctionApp.json) |

[→ View full connector details](../connectors/cyberarkepm.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CyberArkEPM_CL` | [CyberArkEPM](../connectors/cyberarkepm.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                         |
|-------------|--------------------------------|------------------------------------------------------------|
| 3.0.0       | 27-07-2023                     | Updated solution to fix deployment validations             | 
| 3.0.1       | 28-04-2025                     | Updated deployment instructions to use Python 3.10 version |

[← Back to Solutions Index](../solutions-index.md)
