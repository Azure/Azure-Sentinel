# Jamf Protect

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Jamf Software, LLC |
| **Support Tier** | Partner |
| **Support Link** | [https://www.jamf.com/support/](https://www.jamf.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-10-10 |
| **Last Updated** | 2025-09-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Jamf Protect Push Connector](../connectors/jamfprotectpush.md)

**Publisher:** Jamf

The [Jamf Protect](https://www.jamf.com/products/jamf-protect/) connector provides the capability to read raw event data from Jamf Protect in Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `jamfprotectalerts_CL` |
| | `jamfprotecttelemetryv2_CL` |
| | `jamfprotectunifiedlogs_CL` |
| **Connector Definition Files** | [connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect/Data%20Connectors/JamfProtect_ccp/connectorDefinition.json) |

[→ View full connector details](../connectors/jamfprotectpush.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `jamfprotectalerts_CL` | [Jamf Protect Push Connector](../connectors/jamfprotectpush.md) |
| `jamfprotecttelemetryv2_CL` | [Jamf Protect Push Connector](../connectors/jamfprotectpush.md) |
| `jamfprotectunifiedlogs_CL` | [Jamf Protect Push Connector](../connectors/jamfprotectpush.md) |

[← Back to Solutions Index](../solutions-index.md)
