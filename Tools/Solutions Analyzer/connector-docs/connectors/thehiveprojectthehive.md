# TheHive Project - TheHive

| | |
|----------|-------|
| **Connector ID** | `TheHiveProjectTheHive` |
| **Publisher** | TheHive Project |
| **Tables Ingested** | [`TheHive_CL`](../tables-index.md#thehive_cl) |
| **Used in Solutions** | [TheHive](../solutions/thehive.md) |
| **Connector Definition Files** | [TheHive_Webhooks_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TheHive/Data%20Connectors/TheHive_Webhooks_FunctionApp.json) |

The [TheHive](http://thehive-project.org/) data connector provides the capability to ingest common TheHive events into Microsoft Sentinel through Webhooks. TheHive can notify external system of modification events (case creation, alert update, task assignment) in real time. When a change occurs in the TheHive, an HTTPS POST request with event information is sent to a callback data connector URL.  Refer to [Webhooks documentation](https://docs.thehive-project.org/thehive/legacy/thehive3/admin/webhooks/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[← Back to Connectors Index](../connectors-index.md)
