# TheHive

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TheHive](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TheHive) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### TheHive Project - TheHive

**Publisher:** TheHive Project

The [TheHive](http://thehive-project.org/) data connector provides the capability to ingest common TheHive events into Microsoft Sentinel through Webhooks. TheHive can notify external system of modification events (case creation, alert update, task assignment) in real time. When a change occurs in the TheHive, an HTTPS POST request with event information is sent to a callback data connector URL.  Refer to [Webhooks documentation](https://docs.thehive-project.org/thehive/legacy/thehive3/admin/webhooks/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

**Tables Ingested:**

- `TheHive_CL`

**Connector Definition Files:**

- [TheHive_Webhooks_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TheHive/Data%20Connectors/TheHive_Webhooks_FunctionApp.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `TheHive_CL` | TheHive Project - TheHive |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n