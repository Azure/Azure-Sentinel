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

This solution provides **1 data connector(s)**:

- [Samsung Knox Asset Intelligence](../connectors/samsungdcdefinition.md)

## Tables Reference

This solution uses **6 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Samsung_Knox_Application_CL`](../tables/samsung-knox-application-cl.md) | [Samsung Knox Asset Intelligence](../connectors/samsungdcdefinition.md) | Workbooks |
| [`Samsung_Knox_Audit_CL`](../tables/samsung-knox-audit-cl.md) | [Samsung Knox Asset Intelligence](../connectors/samsungdcdefinition.md) | Analytics, Workbooks |
| [`Samsung_Knox_Network_CL`](../tables/samsung-knox-network-cl.md) | [Samsung Knox Asset Intelligence](../connectors/samsungdcdefinition.md) | Workbooks |
| [`Samsung_Knox_Process_CL`](../tables/samsung-knox-process-cl.md) | [Samsung Knox Asset Intelligence](../connectors/samsungdcdefinition.md) | Analytics, Workbooks |
| [`Samsung_Knox_System_CL`](../tables/samsung-knox-system-cl.md) | [Samsung Knox Asset Intelligence](../connectors/samsungdcdefinition.md) | Analytics, Workbooks |
| [`Samsung_Knox_User_CL`](../tables/samsung-knox-user-cl.md) | [Samsung Knox Asset Intelligence](../connectors/samsungdcdefinition.md) | Analytics, Workbooks |

## Content Items

This solution includes **8 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 7 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Samsung Knox - Application Privilege Escalation or Change Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Samsung%20Knox%20Asset%20Intelligence/Analytic%20Rules/SamsungKnoxApplicationPrivilegeEscalationOrChange.yaml) | High | PrivilegeEscalation | [`Samsung_Knox_Process_CL`](../tables/samsung-knox-process-cl.md) |
| [Samsung Knox - Mobile Device Boot Compromise Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Samsung%20Knox%20Asset%20Intelligence/Analytic%20Rules/SamsungKnoxMobileDeviceBootCompromise.yaml) | High | Persistence | [`Samsung_Knox_System_CL`](../tables/samsung-knox-system-cl.md) |
| [Samsung Knox - Password Lockout Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Samsung%20Knox%20Asset%20Intelligence/Analytic%20Rules/SamsungKnoxPasswordLockout.yaml) | High | CredentialAccess | [`Samsung_Knox_User_CL`](../tables/samsung-knox-user-cl.md) |
| [Samsung Knox - Peripheral Access  Detection with Camera Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Samsung%20Knox%20Asset%20Intelligence/Analytic%20Rules/SamsungKnoxPeripheralAccessDetectionWithCamera.yaml) | High | - | [`Samsung_Knox_System_CL`](../tables/samsung-knox-system-cl.md) |
| [Samsung Knox - Peripheral Access  Detection with Mic Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Samsung%20Knox%20Asset%20Intelligence/Analytic%20Rules/SamsungKnoxPeripheralAccessDetectionWithMic.yaml) | High | - | [`Samsung_Knox_System_CL`](../tables/samsung-knox-system-cl.md) |
| [Samsung Knox - Security Log Full Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Samsung%20Knox%20Asset%20Intelligence/Analytic%20Rules/SamsungKnoxSecurityLogFull.yaml) | High | - | [`Samsung_Knox_Audit_CL`](../tables/samsung-knox-audit-cl.md) |
| [Samsung Knox - Suspicious URL Accessed Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Samsung%20Knox%20Asset%20Intelligence/Analytic%20Rules/SamsungKnoxSuspiciousURLs.yaml) | High | InitialAccess | [`Samsung_Knox_User_CL`](../tables/samsung-knox-user-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SamsungKnoxAssetIntelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Samsung%20Knox%20Asset%20Intelligence/Workbooks/SamsungKnoxAssetIntelligence.json) | [`Samsung_Knox_Application_CL`](../tables/samsung-knox-application-cl.md)<br>[`Samsung_Knox_Audit_CL`](../tables/samsung-knox-audit-cl.md)<br>[`Samsung_Knox_Network_CL`](../tables/samsung-knox-network-cl.md)<br>[`Samsung_Knox_Process_CL`](../tables/samsung-knox-process-cl.md)<br>[`Samsung_Knox_System_CL`](../tables/samsung-knox-system-cl.md)<br>[`Samsung_Knox_User_CL`](../tables/samsung-knox-user-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                     |
|-------------|--------------------------------|----------------------------------------------------------------------------------------|
| 3.0.2       | 25-07-2025                     | Updated **Data Connector** to support new Columns. |
| 3.0.1       | 28-01-2025                     | Enhance DCR instruction steps in **Data Connector** & Update **Analytics rules** name. |
| 3.0.1       | 22-04-2025                     | Initial Solution public Release.                                                       |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
