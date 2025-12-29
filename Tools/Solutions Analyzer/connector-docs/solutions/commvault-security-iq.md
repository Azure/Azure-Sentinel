# Commvault Security IQ

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Commvault |
| **Support Tier** | Partner |
| **Support Link** | [https://www.commvault.com/support](https://www.commvault.com/support) |
| **Categories** | domains |
| **First Published** | 2023-08-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [CommvaultSecurityIQ](../connectors/commvaultsecurityiq-cl.md)

**Publisher:** Commvault

This Azure Function enables Commvault users to ingest alerts/events into their Microsoft Sentinel instance. With Analytic Rules,Microsoft Sentinel can automatically create Microsoft Sentinel incidents from incoming events and logs.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommvaultSecurityIQ_CL` |
| **Connector Definition Files** | [CommvaultSecurityIQ_API_AzureFunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ/Data%20Connectors/CommvaultSecurityIQ_API_AzureFunctionApp.json) |

[→ View full connector details](../connectors/commvaultsecurityiq-cl.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommvaultSecurityIQ_CL` | [CommvaultSecurityIQ](../connectors/commvaultsecurityiq-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.3       | 12-09-2025                     | Enhanced **Data connector** with configurable event collection and streamlined deployment  |
| 3.0.2       | 28-03-2024                     | Update **Playbook** - Bug fix in disabling data aging  |
| 3.0.1       | 28-03-2024                     | Adding **Data Connector** for Commvault Sentinel Integration|
| 3.0.0       | 21-08-2023                     | Initial Solution Release|

[← Back to Solutions Index](../solutions-index.md)
