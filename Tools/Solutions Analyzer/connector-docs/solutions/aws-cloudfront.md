# AWS CloudFront

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-03-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20CloudFront](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20CloudFront) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Amazon Web Services CloudFront (via Codeless Connector Framework) (Preview)](../connectors/awscloudfrontccpdefinition.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AWSCloudFront_AccessLog_CL`](../tables/awscloudfront-accesslog-cl.md) | [Amazon Web Services CloudFront (via Codeless Connector Framework) (Preview)](../connectors/awscloudfrontccpdefinition.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                                                                           |
|------------|-------------------------------|----------------------------------------------------------------------------------------------|
| 3.0.0      | 24-06-2025                    | Initial Solution Release. <br/>Added new CCF **Data Connector** 'AWSCloudFrontLog_CCF'       |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
