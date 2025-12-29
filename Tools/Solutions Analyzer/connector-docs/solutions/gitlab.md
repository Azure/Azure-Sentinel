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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configuration**

>This data connector depends on three parsers based on a Kusto Function to work as expected [**GitLab Access Logs**](https://aka.ms/sentinel-GitLabAccess-parser), [**GitLab Audit Logs**](https://aka.ms/sentinel-GitLabAudit-parser) and [**GitLab Application Logs**](https://aka.ms/sentinel-GitLabApp-parser) which are deployed with the Microsoft Sentinel Solution.

**1. Install and onboard the agent for Linux**

Typically, you should install the agent on a different computer from the one on which the logs are generated.

>  Syslog logs are collected only from **Linux** agents.
**Choose where to install the agent:**

**Install agent on Azure Linux Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install agent on Linux Virtual Machine**

  **Install agent on a non-Azure Linux Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install agent on Linux (Non-Azure)**

**2. Configure the logs to be collected**

Configure the facilities you want to collect and their severities.

1.  Under workspace advanced settings **Configuration**, select **Data** and then **Syslog**.
2.  Select **Apply below configuration to my machines** and select the facilities and severities.
3.  Click **Save**.
- **Open Syslog settings**

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
