# Workplace from Facebook

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workplace%20from%20Facebook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workplace%20from%20Facebook) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Workplace from Facebook](../connectors/workplacefacebook.md)

**Publisher:** Facebook

The [Workplace](https://www.workplace.com/) data connector provides the capability to ingest common Workplace events into Microsoft Sentinel through Webhooks. Webhooks enable custom integration apps to subscribe to events in Workplace and receive updates in real time. When a change occurs in Workplace, an HTTPS POST request with event information is sent to a callback data connector URL.  Refer to [Webhooks documentation](https://developers.facebook.com/docs/workplace/reference/webhooks) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| | |
|--------------------------|---|
| **Tables Ingested** | `Workplace_Facebook_CL` |
| **Connector Definition Files** | [WorkplaceFacebook_Webhooks_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workplace%20from%20Facebook/Data%20Connectors/WorkplaceFacebook/WorkplaceFacebook_Webhooks_FunctionApp.json) |

[→ View full connector details](../connectors/workplacefacebook.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Workplace_Facebook_CL` | [Workplace from Facebook](../connectors/workplacefacebook.md) |

[← Back to Solutions Index](../solutions-index.md)
