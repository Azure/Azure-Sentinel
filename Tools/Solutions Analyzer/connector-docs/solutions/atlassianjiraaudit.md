# AtlassianJiraAudit

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-01-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Atlassian Jira Audit](../connectors/jiraauditapi.md)
- [Atlassian Jira Audit (using REST API)](../connectors/jiraauditccpdefinition.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Jira_Audit_CL`](../tables/jira-audit-cl.md) | [Atlassian Jira Audit](../connectors/jiraauditapi.md) | Analytics, Hunting, Workbooks |
| [`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) | [Atlassian Jira Audit](../connectors/jiraauditapi.md), [Atlassian Jira Audit (using REST API)](../connectors/jiraauditccpdefinition.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **30 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 10 |
| Hunting Queries | 10 |
| Playbooks | 8 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Jira - Global permission added](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Analytic%20Rules/JiraGlobalPermissionAdded.yaml) | Medium | PrivilegeEscalation | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - New site admin user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Analytic%20Rules/JiraNewPrivilegedUser.yaml) | High | Persistence, PrivilegeEscalation | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - New site admin user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Analytic%20Rules/JiraPrivilegedUserPasswordChanged.yaml) | High | InitialAccess | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - New user created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Analytic%20Rules/JiraNewUser.yaml) | Medium | Persistence | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - Permission scheme updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Analytic%20Rules/JiraPermissionSchemeUpdated.yaml) | Medium | Impact | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - Project roles changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Analytic%20Rules/JiraProjectRolesChanged.yaml) | Medium | Impact | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - User removed from group](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Analytic%20Rules/JiraUserRemovedFromGroup.yaml) | Medium | Impact | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - User removed from project](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Analytic%20Rules/JiraUserRemovedFromProject.yaml) | Medium | Impact | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - User's password changed multiple times](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Analytic%20Rules/JiraUserPasswordChange.yaml) | High | Persistence | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - Workflow scheme copied](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Analytic%20Rules/JiraWorkflowSchemeCopied.yaml) | Medium | Collection | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Jira - Blocked tasks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Hunting%20Queries/JiraBlockedTasks.yaml) | Impact | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - New users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Hunting%20Queries/JiraNewUsers.yaml) | Persistence | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - Project versions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Hunting%20Queries/JiraUpdatedProjectVersions.yaml) | Impact | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - Project versions released](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Hunting%20Queries/JiraProjectVersionsReleased.yaml) | Impact | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - Updated projects](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Hunting%20Queries/JiraUpdatedProjects.yaml) | Impact | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - Updated users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Hunting%20Queries/JiraUpdatedUsers.yaml) | PrivilegeEscalation, Impact | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - Updated workflow schemes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Hunting%20Queries/JiraUpdatedWorkflowSchemes.yaml) | Impact | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - Updated workflows](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Hunting%20Queries/JiraUpdatedWorkflows.yaml) | Impact | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - Users' IP addresses](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Hunting%20Queries/JiraUserIPs.yaml) | Persistence | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |
| [Jira - Workflow schemes added to projects](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Hunting%20Queries/JiraWorkflowAddedToProject.yaml) | Impact | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AtlassianJiraAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Workbooks/AtlassianJiraAudit.json) | [`Jira_Audit_CL`](../tables/jira-audit-cl.md)<br>[`Jira_Audit_v2_CL`](../tables/jira-audit-v2-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Create And Update Jira Issue](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Playbooks/Jira-CreateAndUpdateIssue/azuredeploy.json) | This playbook will create or update incident in Jira. When incident is created, playbook will run an... | - |
| [Create Jira Issue alert-trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Playbooks/Create-Jira-Issue/alert-trigger/azuredeploy.json) | This playbook will open a Jira Issue when a new incident is opened in Microsoft Sentinel. | - |
| [Create Jira Issue incident-trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Playbooks/Create-Jira-Issue/incident-trigger/azuredeploy.json) | This playbook will open a Jira Issue when a new incident is opened in Microsoft Sentinel. | - |
| [Sync Jira from Sentinel - Create incident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Playbooks/Sync-Incidents/azuredeploy.json) | This Playbook will create JIRA incidents for every Microsoft Sentinel which is created. It includes ... | - |
| [Sync Jira to Sentinel - Assigned User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Playbooks/Sync-AssignedUser/azuredeploy.json) | This Playbook will sync the assigned user from JIRA to Microsoft Sentinel. | - |
| [Sync Jira to Sentinel - Status](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Playbooks/Sync-Status/azuredeploy.json) | This Playbook will sync the status from JIRA to Microsoft Sentinel. | - |
| [Sync Jira to Sentinel - public comments](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Playbooks/Add-JiraLinkComment/azuredeploy.json) | This Playbook will sync the public comments from JIRA to Microsoft Sentinel. | - |
| [Sync-CommentsFunctionApp](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Playbooks/Sync-CommentsFunctionApp/azuredeploy.json) | - | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [JiraAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianJiraAudit/Parsers/JiraAudit.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                        |
|-------------|--------------------------------|---------------------------------------------------------------------------|
| 3.0.4       | 30-08-2024                     | Updated parameters for CCP **Data Connector**							   |
| 3.0.3       | 14-08-2024                     | **Data Connector**[Atlassian Jira Audit (using REST API)] Globally Available  |
| 3.0.2       | 22-05-2024                     | Added new CCP **Data Connector** to the Solution 
| 3.0.1       | 16-04-2024                     | Added Deploy to Azure Goverment button for Government portal in **Dataconnector** |
| 3.0.0       | 06-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID.  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
