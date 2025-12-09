# Workplace from Facebook

| | |
|----------|-------|
| **Connector ID** | `WorkplaceFacebook` |
| **Publisher** | Facebook |
| **Tables Ingested** | [`Workplace_Facebook_CL`](../tables-index.md#workplace_facebook_cl) |
| **Used in Solutions** | [Workplace from Facebook](../solutions/workplace-from-facebook.md) |
| **Connector Definition Files** | [WorkplaceFacebook_Webhooks_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workplace%20from%20Facebook/Data%20Connectors/WorkplaceFacebook/WorkplaceFacebook_Webhooks_FunctionApp.json) |

The [Workplace](https://www.workplace.com/) data connector provides the capability to ingest common Workplace events into Microsoft Sentinel through Webhooks. Webhooks enable custom integration apps to subscribe to events in Workplace and receive updates in real time. When a change occurs in Workplace, an HTTPS POST request with event information is sent to a callback data connector URL.  Refer to [Webhooks documentation](https://developers.facebook.com/docs/workplace/reference/webhooks) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[← Back to Connectors Index](../connectors-index.md)
