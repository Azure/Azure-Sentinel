# F5 BIG-IP

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | F5 Networks |
| **Support Tier** | Partner |
| **Support Link** | [https://support.f5.com/csp/home](https://support.f5.com/csp/home) |
| **Categories** | domains |
| **First Published** | 2022-05-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20BIG-IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20BIG-IP) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [F5 BIG-IP](../connectors/f5bigip.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`F5Telemetry_ASM_CL`](../tables/f5telemetry-asm-cl.md) | [F5 BIG-IP](../connectors/f5bigip.md) | Workbooks |
| [`F5Telemetry_AVR_CL`](../tables/f5telemetry-avr-cl.md) | - | Workbooks |
| [`F5Telemetry_LTM_CL`](../tables/f5telemetry-ltm-cl.md) | [F5 BIG-IP](../connectors/f5bigip.md) | Workbooks |
| [`F5Telemetry_system_CL`](../tables/f5telemetry-system-cl.md) | [F5 BIG-IP](../connectors/f5bigip.md) | Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 2 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [F5BIGIPSystemMetrics](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20BIG-IP/Workbooks/F5BIGIPSystemMetrics.json) | [`F5Telemetry_AVR_CL`](../tables/f5telemetry-avr-cl.md)<br>[`F5Telemetry_system_CL`](../tables/f5telemetry-system-cl.md) |
| [F5Networks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20BIG-IP/Workbooks/F5Networks.json) | [`F5Telemetry_ASM_CL`](../tables/f5telemetry-asm-cl.md)<br>[`F5Telemetry_LTM_CL`](../tables/f5telemetry-ltm-cl.md)<br>[`F5Telemetry_system_CL`](../tables/f5telemetry-system-cl.md) |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
