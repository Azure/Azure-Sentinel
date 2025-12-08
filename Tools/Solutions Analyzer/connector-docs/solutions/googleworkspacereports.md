# GoogleWorkspaceReports

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-01-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleWorkspaceReports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleWorkspaceReports) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Google Workspace Activities (via Codeless Connector Framework)](../connectors/googleworkspaceccpdefinition.md)

**Publisher:** Microsoft

### [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md)

**Publisher:** Google

The [Google Workspace](https://workspace.google.com/) data connector provides the capability to ingest Google Workspace Activity events into Microsoft Sentinel through the REST API. The connector provides ability to get [events](https://developers.google.com/admin-sdk/reports/v1/reference/activities) which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems, track who signs in and when, analyze administrator activity, understand how users create and share content, and more review events in your org.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| | |
|--------------------------|---|
| **Tables Ingested** | `GWorkspace_ReportsAPI_access_transparency_CL` |
| | `GWorkspace_ReportsAPI_admin_CL` |
| | `GWorkspace_ReportsAPI_calendar_CL` |
| | `GWorkspace_ReportsAPI_chat_CL` |
| | `GWorkspace_ReportsAPI_chrome_CL` |
| | `GWorkspace_ReportsAPI_context_aware_access_CL` |
| | `GWorkspace_ReportsAPI_data_studio_CL` |
| | `GWorkspace_ReportsAPI_drive_CL` |
| | `GWorkspace_ReportsAPI_gcp_CL` |
| | `GWorkspace_ReportsAPI_gplus_CL` |
| | `GWorkspace_ReportsAPI_groups_CL` |
| | `GWorkspace_ReportsAPI_groups_enterprise_CL` |
| | `GWorkspace_ReportsAPI_jamboard_CL` |
| | `GWorkspace_ReportsAPI_keep_CL` |
| | `GWorkspace_ReportsAPI_login_CL` |
| | `GWorkspace_ReportsAPI_meet_CL` |
| | `GWorkspace_ReportsAPI_mobile_CL` |
| | `GWorkspace_ReportsAPI_rules_CL` |
| | `GWorkspace_ReportsAPI_saml_CL` |
| | `GWorkspace_ReportsAPI_token_CL` |
| | `GWorkspace_ReportsAPI_user_accounts_CL` |
| | `GoogleWorkspaceReports_CL` |
| **Connector Definition Files** | [GWorkspaceReports_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleWorkspaceReports/Data%20Connectors/GWorkspaceReports_API_FunctionApp.json) |

[→ View full connector details](../connectors/googleworkspacereportsapi.md)

## Tables Reference

This solution ingests data into **23 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GWorkspace_ReportsAPI_access_transparency_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_admin_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_calendar_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_chat_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_chrome_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_context_aware_access_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_data_studio_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_drive_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_gcp_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_gplus_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_groups_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_groups_enterprise_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_jamboard_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_keep_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_login_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_meet_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_mobile_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_rules_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_saml_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_token_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GWorkspace_ReportsAPI_user_accounts_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |
| `GoogleWorkspaceReports` | [Google Workspace Activities (via Codeless Connector Framework)](../connectors/googleworkspaceccpdefinition.md) |
| `GoogleWorkspaceReports_CL` | [[DEPRECATED] Google Workspace (G Suite)](../connectors/googleworkspacereportsapi.md) |

[← Back to Solutions Index](../solutions-index.md)
