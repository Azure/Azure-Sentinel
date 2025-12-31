# Phosphorus

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Phosphorus Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://phosphorus.io](https://phosphorus.io) |
| **Categories** | domains |
| **First Published** | 2024-08-13 |
| **Last Updated** | 2024-08-13 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Phosphorus](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Phosphorus) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Phosphorus Devices](../connectors/phosphorus-polling.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Phosphorus_CL`](../tables/phosphorus-cl.md) | [Phosphorus Devices](../connectors/phosphorus-polling.md) | - |

## Additional Documentation

> 📄 *Source: [Phosphorus/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Phosphorus/README.md)*

This repository contains all resources for the Phosphorus Azure Sentinel Solution.
The Phosphorus Solution is built in order to easily integrate Phosphorus with Azure Sentinel.

By deploying this solution, you'll be able to ingest device data from Phosphorus into Microsoft Sentinel

The solution consists out of the following resources:
- A codeless API connector to ingest data into Sentinel.

## Data Connector Deployment
The data connector will retrieve the Phosphorus device data through the Phosphorus REST API.

This is a codeless API connector. After the deployment of the ARM template, the connector will be available in the Data Connectors list to connect.

Input the Phosphorus Instance Domain name, Integration Name, API key , click Connect button and Microsoft Sentinel will start to pull in device data.

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 15-08-2024                     | Initial Solution Release |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
