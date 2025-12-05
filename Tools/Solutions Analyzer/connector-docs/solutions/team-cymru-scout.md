# Team Cymru Scout

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Team Cymru |
| **Support Tier** | Partner |
| **Support Link** | [http://team-cymru.com](http://team-cymru.com) |
| **Categories** | domains |
| **First Published** | 2024-07-16 |
| **Last Updated** | 2025-05-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md)

**Publisher:** Team Cymru Scout

The [TeamCymruScout](https://scout.cymru.com/) Data Connector allows users to bring Team Cymru Scout IP, domain and account usage data in Microsoft Sentinel for enrichment.

| | |
|--------------------------|---|
| **Tables Ingested** | `Cymru_Scout_Account_Usage_Data_CL` |
| | `Cymru_Scout_Domain_Data_CL` |
| | `Cymru_Scout_IP_Data_Communications_CL` |
| | `Cymru_Scout_IP_Data_Details_CL` |
| | `Cymru_Scout_IP_Data_Fingerprints_CL` |
| | `Cymru_Scout_IP_Data_Foundation_CL` |
| | `Cymru_Scout_IP_Data_OpenPorts_CL` |
| | `Cymru_Scout_IP_Data_PDNS_CL` |
| | `Cymru_Scout_IP_Data_Summary_Certs_CL` |
| | `Cymru_Scout_IP_Data_Summary_Details_CL` |
| | `Cymru_Scout_IP_Data_Summary_Fingerprints_CL` |
| | `Cymru_Scout_IP_Data_Summary_OpenPorts_CL` |
| | `Cymru_Scout_IP_Data_Summary_PDNS_CL` |
| | `Cymru_Scout_IP_Data_x509_CL` |
| **Connector Definition Files** | [TeamCymruScout_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Data%20Connectors/TeamCymruScout/TeamCymruScout_API_FunctionApp.json) |

[→ View full connector details](../connectors/teamcymruscout.md)

## Tables Reference

This solution ingests data into **14 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Cymru_Scout_Account_Usage_Data_CL` | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) |
| `Cymru_Scout_Domain_Data_CL` | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) |
| `Cymru_Scout_IP_Data_Communications_CL` | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) |
| `Cymru_Scout_IP_Data_Details_CL` | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) |
| `Cymru_Scout_IP_Data_Fingerprints_CL` | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) |
| `Cymru_Scout_IP_Data_Foundation_CL` | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) |
| `Cymru_Scout_IP_Data_OpenPorts_CL` | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) |
| `Cymru_Scout_IP_Data_PDNS_CL` | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) |
| `Cymru_Scout_IP_Data_Summary_Certs_CL` | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) |
| `Cymru_Scout_IP_Data_Summary_Details_CL` | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) |
| `Cymru_Scout_IP_Data_Summary_Fingerprints_CL` | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) |
| `Cymru_Scout_IP_Data_Summary_OpenPorts_CL` | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) |
| `Cymru_Scout_IP_Data_Summary_PDNS_CL` | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) |
| `Cymru_Scout_IP_Data_x509_CL` | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) |

[← Back to Solutions Index](../solutions-index.md)
