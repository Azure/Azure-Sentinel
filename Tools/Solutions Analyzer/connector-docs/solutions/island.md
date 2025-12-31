# Island

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Island |
| **Support Tier** | Partner |
| **Support Link** | [https://www.island.io](https://www.island.io) |
| **Categories** | domains |
| **First Published** | 2023-05-02 |
| **Last Updated** | 2023-07-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Island](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Island) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Island Enterprise Browser Admin Audit (Polling CCP)](../connectors/island-admin-polling.md)
- [Island Enterprise Browser User Activity (Polling CCP)](../connectors/island-user-polling.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Island_Admin_CL`](../tables/island-admin-cl.md) | [Island Enterprise Browser Admin Audit (Polling CCP)](../connectors/island-admin-polling.md) | Workbooks |
| [`Island_User_CL`](../tables/island-user-cl.md) | [Island Enterprise Browser User Activity (Polling CCP)](../connectors/island-user-polling.md) | Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 2 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [IslandAdminAuditOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Island/Workbooks/IslandAdminAuditOverview.json) | [`Island_Admin_CL`](../tables/island-admin-cl.md) |
| [IslandUserActivityOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Island/Workbooks/IslandUserActivityOverview.json) | [`Island_User_CL`](../tables/island-user-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 28-07-2023                     | Added API Url field to Data Connectors so all regions can be supported |
|       |                     | Added new query rate limit in Data Connectors to prevent API flooding |
|       |                     | Bug fix for wrong table referenced in query in workbook |
| 2.0.1       | 08-05-2023                     | Bug fix for APIVersion in Data Connector |
| 2.0.0       | 14-02-2023                     | Initial Solution Release |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
