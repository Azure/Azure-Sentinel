# TenableIO

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Tenable |
| **Support Tier** | Partner |
| **Support Link** | [https://www.tenable.com/support/technical-support](https://www.tenable.com/support/technical-support) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableIO](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableIO) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Tenable.io Vulnerability Management](../connectors/tenableioapi.md)

**Publisher:** Tenable

The [Tenable.io](https://www.tenable.com/products/tenable-io) data connector provides the capability to ingest Asset and Vulnerability data into Microsoft Sentinel through the REST API from the Tenable.io platform (Managed in the cloud). Refer to [API documentation](https://developer.tenable.com/reference) for more information. The connector provides the ability to get data which helps to examine potential security risks, get insight into your computing assets, diagnose configuration problems and more

| | |
|--------------------------|---|
| **Tables Ingested** | `Tenable_IO_Assets_CL` |
| | `Tenable_IO_Vuln_CL` |
| **Connector Definition Files** | [TenableIO.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TenableIO/Data%20Connectors/TenableIO.json) |

[→ View full connector details](../connectors/tenableioapi.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Tenable_IO_Assets_CL` | [Tenable.io Vulnerability Management](../connectors/tenableioapi.md) |
| `Tenable_IO_Vuln_CL` | [Tenable.io Vulnerability Management](../connectors/tenableioapi.md) |

[← Back to Solutions Index](../solutions-index.md)
