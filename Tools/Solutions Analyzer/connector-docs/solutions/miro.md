# Miro

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Miro |
| **Support Tier** | Partner |
| **Support Link** | [https://help.miro.com](https://help.miro.com) |
| **Categories** | domains |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Miro](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Miro) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Miro Audit Logs (Enterprise Plan)](../connectors/miroauditlogsdataconnector.md)
- [Miro Content Logs (Enterprise Plan + Enterprise Guard)](../connectors/mirocontentlogsdataconnector.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`MiroAuditLogs_CL`](../tables/miroauditlogs-cl.md) | [Miro Audit Logs (Enterprise Plan)](../connectors/miroauditlogsdataconnector.md) | - |
| [`MiroContentLogs_CL`](../tables/mirocontentlogs-cl.md) | [Miro Content Logs (Enterprise Plan + Enterprise Guard)](../connectors/mirocontentlogsdataconnector.md) | - |

## Additional Documentation

> 📄 *Source: [Miro/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Miro/README.md)*

<img src="./Logo/Miro.svg" alt="Miro" width="20%"/><br>

## Overview

The [Miro](https://miro.com/) connector ingests audit logs and content activity logs from [Miro REST APIs](https://developers.miro.com/reference) into Microsoft Sentinel using the Codeless Connector Framework (CCF). This centralizes Miro workspace activity monitoring in Microsoft Sentinel for security threat detection, incident investigation, and compliance reporting.

## Data connectors

This solution includes two data connectors:

1. **Miro Audit Logs (Enterprise Plan)**: Organization-wide audit events including user authentication, content access, team changes, and administrative actions. [API documentation](https://developers.miro.com/reference/enterprise-get-audit-logs) | [Audit logs overview](https://developers.miro.com/reference/audit-logs).
2. **Miro Content Logs (Enterprise Plan + Enterprise Guard)**: Content activity tracking including item creation, updates, and deletions for compliance and eDiscovery. [API documentation](https://developers.miro.com/reference/enterprise-board-content-item-logs-fetch) | [Content logs overview](https://developers.miro.com/reference/board-content-logs).

## Prerequisites

### General requirements

- Active Microsoft Sentinel workspace.
- Company Admin role in your Miro organization.
- Miro OAuth access token (non-expiring).

### Connector-specific requirements

**For audit logs connector:**

- Miro Enterprise Plan.
- OAuth scope: `auditlogs:read`.
- Access token.

**For content logs connector:**

- Miro Enterprise Plan + Enterprise Guard add-on.
- OAuth scope: `contentlogs:export`.
- Access token.
- Miro organization ID.

## Installation

There are two ways to set up the Miro connectors.

- **Option 1 (recommended):** Use enterprise integrations. Simplest setup with automatic token generation.
- **Option 2 (alternative):** Create custom OAuth application. More control over OAuth app configuration.

**Note:** When using Option 1, the integration is automatically tied to the team with the largest number of users in your organization. When using Option 2, you can choose which team to install the app to. However, **the team selection does not affect which logs are collected**—both options provide organization-wide log access. All integration-relevant events from all teams are included in your logs.

---

### Option 1: Use enterprise integrations (recommended)

This is the simplest option for most users. It automatically creates an OAuth application and generates an access token for you through Miro's enterprise integrations settings.

#### For audit logs connector

1. Open [Miro company settings](https://miro.com/app/settings/).
2. Expand the **Apps and integrations** section.
3. Click **Enterprise integrations**.
4. Enable the **SIEM** toggle.
5. Copy the **Access Token** value that appears.
6. Store the token securely.

#### For content logs connector

1. Open [Miro company settings](https://miro.com/app/settings/).

*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                              |
|-------------|--------------------------------|-------------------------------------------------------------------------------------------------|
| 3.0.0       | 05-12-2025                     | Initial release of the Miro solution with two **CCF connectors** (Audit Logs and Content Logs). |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
