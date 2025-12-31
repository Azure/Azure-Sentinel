# Palo Alto Prisma Cloud CWPP

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-06-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Prisma%20Cloud%20CWPP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Prisma%20Cloud%20CWPP) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Palo Alto Prisma Cloud CWPP (using REST API)](../connectors/paloaltoprismacloudcwpp.md)
- [Palo Alto Prisma Cloud CWPP (using REST API)](../connectors/prismacloudcomputenativepoller.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`PrismaCloudCompute_CL`](../tables/prismacloudcompute-cl.md) | [Palo Alto Prisma Cloud CWPP (using REST API)](../connectors/paloaltoprismacloudcwpp.md), [Palo Alto Prisma Cloud CWPP (using REST API)](../connectors/prismacloudcomputenativepoller.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 03-01-2024                     |	Repackaged for _solutionVersion issue in resource            |
| 3.0.2       | 03-01-2024                     |	Updated package version and password as a securestring            |
| 3.0.1       | 30-11-2023                     |	Updated the data connector and its associated package             |
| 3.0.0       | 10-10-2023                     |	Added new files to support CCP CLV2 and its package               |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
