# Samsung Knox Asset Intelligence

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Samsung Electronics Co., Ltd. |
| **Support Tier** | Partner |
| **Support Link** | [https://www2.samsungknox.com/en/support](https://www2.samsungknox.com/en/support) |
| **Categories** | domains |
| **First Published** | 2025-01-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Samsung%20Knox%20Asset%20Intelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Samsung%20Knox%20Asset%20Intelligence) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Samsung Knox Asset Intelligence](../connectors/samsungdcdefinition.md)

**Publisher:** Samsung

Samsung Knox Asset Intelligence Data Connector lets you centralize your mobile security events and logs in order to view customized insights using the Workbook template, and identify incidents based on Analytics Rules templates.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Samsung_Knox_Application_CL` |
| | `Samsung_Knox_Audit_CL` |
| | `Samsung_Knox_Network_CL` |
| | `Samsung_Knox_Process_CL` |
| | `Samsung_Knox_System_CL` |
| | `Samsung_Knox_User_CL` |
| **Connector Definition Files** | [Template_Samsung.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Samsung%20Knox%20Asset%20Intelligence/Data%20Connectors/Template_Samsung.json) |

[→ View full connector details](../connectors/samsungdcdefinition.md)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Samsung_Knox_Application_CL` | [Samsung Knox Asset Intelligence](../connectors/samsungdcdefinition.md) |
| `Samsung_Knox_Audit_CL` | [Samsung Knox Asset Intelligence](../connectors/samsungdcdefinition.md) |
| `Samsung_Knox_Network_CL` | [Samsung Knox Asset Intelligence](../connectors/samsungdcdefinition.md) |
| `Samsung_Knox_Process_CL` | [Samsung Knox Asset Intelligence](../connectors/samsungdcdefinition.md) |
| `Samsung_Knox_System_CL` | [Samsung Knox Asset Intelligence](../connectors/samsungdcdefinition.md) |
| `Samsung_Knox_User_CL` | [Samsung Knox Asset Intelligence](../connectors/samsungdcdefinition.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                     |
|-------------|--------------------------------|----------------------------------------------------------------------------------------|
| 3.0.2       | 25-07-2025                     | Updated **Data Connector** to support new Columns. |
| 3.0.1       | 28-01-2025                     | Enhance DCR instruction steps in **Data Connector** & Update **Analytics rules** name. |
| 3.0.1       | 22-04-2025                     | Initial Solution public Release.                                                       |

[← Back to Solutions Index](../solutions-index.md)
