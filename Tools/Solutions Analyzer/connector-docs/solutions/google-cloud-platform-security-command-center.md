# Google Cloud Platform Security Command Center

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2023-09-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Google Security Command Center](../connectors/googlesccdefinition.md)

**Publisher:** Microsoft

The Google Cloud Platform (GCP) Security Command Center is a comprehensive security and risk management platform for Google Cloud, ingested from Sentinel's connector. It offers features such as asset inventory and discovery, vulnerability and threat detection, and risk mitigation and remediation to help you gain insight into your organization's security and data attack surface. This integration enables you to perform tasks related to findings and assets more effectively.

| | |
|--------------------------|---|
| **Tables Ingested** | `GoogleCloudSCC` |
| **Connector Definition Files** | [GCPSecurityCommandCenter.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Security%20Command%20Center/Data%20Connectors/GCPSecurityCommandCenter.json) |

[→ View full connector details](../connectors/googlesccdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GoogleCloudSCC` | [Google Security Command Center](../connectors/googlesccdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
