# GitLab

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-04-27 |
| **Last Updated** | 2022-06-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] GitLab](../connectors/gitlab.md)

**Publisher:** Microsoft

The [GitLab](https://about.gitlab.com/solutions/devops-platform/) connector allows you to easily connect your GitLab (GitLab Enterprise Edition - Standalone) logs with Microsoft Sentinel. This gives you more security insight into your organization's DevOps pipelines.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Syslog_GitLab.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab/Data%20Connectors/Connector_Syslog_GitLab.json) |

[→ View full connector details](../connectors/gitlab.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] GitLab](../connectors/gitlab.md) |

[← Back to Solutions Index](../solutions-index.md)
