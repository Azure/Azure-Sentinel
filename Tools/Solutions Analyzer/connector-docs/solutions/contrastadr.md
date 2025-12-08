# ContrastADR

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Contrast Security |
| **Support Tier** | Partner |
| **Support Link** | [https://support.contrastsecurity.com/hc/en-us](https://support.contrastsecurity.com/hc/en-us) |
| **Categories** | domains |
| **First Published** | 2025-01-18 |
| **Last Updated** | 2025-01-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [ContrastADR](../connectors/contrastadr.md)

**Publisher:** Contrast Security

The ContrastADR data connector provides the capability to ingest Contrast ADR attack events into Microsoft Sentinel using the ContrastADR Webhook. ContrastADR data connector can enrich the incoming webhook data with ContrastADR API enrichment calls.

| | |
|--------------------------|---|
| **Tables Ingested** | `ContrastADRIncident_CL` |
| | `ContrastADR_CL` |
| **Connector Definition Files** | [ContrastADR_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Data%20Connectors/ContrastADR_API_FunctionApp.json) |

[→ View full connector details](../connectors/contrastadr.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ContrastADRIncident_CL` | [ContrastADR](../connectors/contrastadr.md) |
| `ContrastADR_CL` | [ContrastADR](../connectors/contrastadr.md) |

[← Back to Solutions Index](../solutions-index.md)
