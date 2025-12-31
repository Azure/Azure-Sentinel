# AWS_AccessLogs

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-02-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_AccessLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_AccessLogs) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [AWS S3 Server Access Logs (via Codeless Connector Framework)](../connectors/awss3serveraccesslogsdefinition.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AWSS3ServerAccess`](../tables/awss3serveraccess.md) | [AWS S3 Server Access Logs (via Codeless Connector Framework)](../connectors/awss3serveraccesslogsdefinition.md) | - |

## Release Notes

**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                                                                         |
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.1      | 10-06-2025                    | AWS S3 Server Access Log CCF **Data Connector** Moving to GA.  |
| 3.0.0      | 08-08-2025                    | Initial Solution Release. <br/>New CCF **Data Connector** for AWS_AccessLogs.  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
