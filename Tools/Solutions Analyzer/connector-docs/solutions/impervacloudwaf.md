# ImpervaCloudWAF

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-09-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Imperva Cloud WAF](../connectors/impervacloudwaflogsccfdefinition.md)

**Publisher:** Microsoft

### [Imperva Cloud WAF](../connectors/impervawafcloudapi.md)

**Publisher:** Imperva

The [Imperva Cloud WAF](https://www.imperva.com/resources/resource-library/datasheets/imperva-cloud-waf/) data connector provides the capability to integrate and ingest Web Application Firewall events into Microsoft Sentinel through the REST API. Refer to Log integration [documentation](https://docs.imperva.com/bundle/cloud-application-security/page/settings/log-integration.htm#Download) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| | |
|--------------------------|---|
| **Tables Ingested** | `ImpervaWAFCloud_CL` |
| **Connector Definition Files** | [ImpervaWAFCloud_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Data%20Connectors/ImpervaWAFCloud_FunctionApp.json) |

[→ View full connector details](../connectors/impervawafcloudapi.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ImpervaWAFCloudV2_CL` | [Imperva Cloud WAF](../connectors/impervacloudwaflogsccfdefinition.md) |
| `ImpervaWAFCloud_CL` | [Imperva Cloud WAF](../connectors/impervawafcloudapi.md) |

[← Back to Solutions Index](../solutions-index.md)
