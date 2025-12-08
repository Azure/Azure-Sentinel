# Bitwarden

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Bitwarden Inc |
| **Support Tier** | Partner |
| **Support Link** | [https://bitwarden.com](https://bitwarden.com) |
| **Categories** | domains |
| **First Published** | 2024-05-12 |
| **Last Updated** | 2024-10-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitwarden](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitwarden) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Bitwarden Event Logs](../connectors/bitwardeneventlogs.md)

**Publisher:** Bitwarden Inc

This connector provides insight into activity of your Bitwarden organization such as user's activity (logged in, changed password, 2fa, etc.), cipher activity (created, updated, deleted, shared, etc.), collection activity, organization activity, and more.

| | |
|--------------------------|---|
| **Tables Ingested** | `BitwardenEventLogs_CL` |
| | `BitwardenGroups_CL` |
| | `BitwardenMembers_CL` |
| **Connector Definition Files** | [definitions.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitwarden/Data%20Connectors/BitwardenEventLogs/definitions.json) |

[→ View full connector details](../connectors/bitwardeneventlogs.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `BitwardenEventLogs_CL` | [Bitwarden Event Logs](../connectors/bitwardeneventlogs.md) |
| `BitwardenGroups_CL` | [Bitwarden Event Logs](../connectors/bitwardeneventlogs.md) |
| `BitwardenMembers_CL` | [Bitwarden Event Logs](../connectors/bitwardeneventlogs.md) |

[← Back to Solutions Index](../solutions-index.md)
