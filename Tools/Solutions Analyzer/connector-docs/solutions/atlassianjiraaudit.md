# AtlassianJiraAudit

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-01-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Atlassian Jira Audit](../connectors/jiraauditapi.md)

**Publisher:** Atlassian

### [Atlassian Jira Audit (using REST API)](../connectors/jiraauditccpdefinition.md)

**Publisher:** Microsoft

The [Atlassian Jira](https://www.atlassian.com/software/jira) Audit data connector provides the capability to ingest [Jira Audit Records](https://support.atlassian.com/jira-cloud-administration/docs/audit-activities-in-jira-applications/) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-audit-records/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| | |
|--------------------------|---|
| **Tables Ingested** | `Jira_Audit_v2_CL` |
| **Connector Definition Files** | [JiraAudit_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Data%20Connectors/JiraAuditAPISentinelConnector_ccpv2/JiraAudit_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/jiraauditccpdefinition.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Jira_Audit_CL` | [Atlassian Jira Audit](../connectors/jiraauditapi.md) |
| `Jira_Audit_v2_CL` | [Atlassian Jira Audit (using REST API)](../connectors/jiraauditccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
