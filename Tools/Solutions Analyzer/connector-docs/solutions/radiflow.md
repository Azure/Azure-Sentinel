# Radiflow

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Radiflow |
| **Support Tier** | Partner |
| **Support Link** | [https://www.radiflow.com](https://www.radiflow.com) |
| **Categories** | domains |
| **First Published** | 2024-06-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Radiflow iSID via AMA](../connectors/radiflowisid.md)

**Publisher:** Radiflow

iSID enables non-disruptive monitoring of distributed ICS networks for changes in topology and behavior, using multiple security packages, each offering a unique capability pertaining to a specific type of network activity

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [RadiflowIsid.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Data%20Connectors/RadiflowIsid.json) |

[→ View full connector details](../connectors/radiflowisid.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [Radiflow iSID via AMA](../connectors/radiflowisid.md) |

[← Back to Solutions Index](../solutions-index.md)
