# Agari

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Agari |
| **Support Tier** | Partner |
| **Support Link** | [https://support.agari.com/hc/en-us/articles/360000645632-How-to-access-Agari-Support](https://support.agari.com/hc/en-us/articles/360000645632-How-to-access-Agari-Support) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Agari](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Agari) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Agari Phishing Defense and Brand Protection](../connectors/agari.md)

**Publisher:** Agari

This connector uses a Agari REST API connection to push data into Azure Sentinel Log Analytics.

| | |
|--------------------------|---|
| **Tables Ingested** | `agari_apdpolicy_log_CL` |
| | `agari_apdtc_log_CL` |
| | `agari_bpalerts_log_CL` |
| **Connector Definition Files** | [Agari_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Agari/Data%20Connectors/Agari_API_FunctionApp.json) |

[→ View full connector details](../connectors/agari.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `agari_apdpolicy_log_CL` | [Agari Phishing Defense and Brand Protection](../connectors/agari.md) |
| `agari_apdtc_log_CL` | [Agari Phishing Defense and Brand Protection](../connectors/agari.md) |
| `agari_bpalerts_log_CL` | [Agari Phishing Defense and Brand Protection](../connectors/agari.md) |

[← Back to Solutions Index](../solutions-index.md)
