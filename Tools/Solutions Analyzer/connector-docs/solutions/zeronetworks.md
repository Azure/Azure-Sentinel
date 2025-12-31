# ZeroNetworks

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Zero Networks |
| **Support Tier** | Partner |
| **Support Link** | [https://zeronetworks.com](https://zeronetworks.com) |
| **Categories** | domains |
| **First Published** | 2022-06-06 |
| **Last Updated** | 2025-09-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Zero Networks Segment Audit](../connectors/zeronetworkssegmentauditnativepoller.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ZNSegmentAuditNativePoller_CL`](../tables/znsegmentauditnativepoller-cl.md) | [Zero Networks Segment Audit](../connectors/zeronetworkssegmentauditnativepoller.md) | Analytics, Hunting, Workbooks |
| [`ZNSegmentAudit_CL`](../tables/znsegmentaudit-cl.md) | - | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **13 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 4 |
| Playbooks | 4 |
| Analytic Rules | 3 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Zero Networks Segement - Machine Removed from protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks/Analytic%20Rules/ZNSegmentMachineRemovedfromProtection.yaml) | High | DefenseEvasion | [`ZNSegmentAuditNativePoller_CL`](../tables/znsegmentauditnativepoller-cl.md)<br>[`ZNSegmentAudit_CL`](../tables/znsegmentaudit-cl.md) |
| [Zero Networks Segment - New API Token created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks/Analytic%20Rules/ZNSegmentNewAPIToken.yaml) | Low | CredentialAccess | [`ZNSegmentAuditNativePoller_CL`](../tables/znsegmentauditnativepoller-cl.md)<br>[`ZNSegmentAudit_CL`](../tables/znsegmentaudit-cl.md) |
| [Zero Networks Segment - Rare JIT Rule Creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks/Analytic%20Rules/ZNSegmentRareJITRuleCreation.yaml) | Medium | LateralMovement | [`ZNSegmentAuditNativePoller_CL`](../tables/znsegmentauditnativepoller-cl.md)<br>[`ZNSegmentAudit_CL`](../tables/znsegmentaudit-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Zero Networks Segment - Excessive access by user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks/Hunting%20Queries/ZNSegmentExcessiveAccessbyUser.yaml) | LateralMovement | [`ZNSegmentAuditNativePoller_CL`](../tables/znsegmentauditnativepoller-cl.md)<br>[`ZNSegmentAudit_CL`](../tables/znsegmentaudit-cl.md) |
| [Zero Networks Segment - Excessive access to a built-in group by user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks/Hunting%20Queries/ZNSegmentExcessiveAccesstoBuiltinGroupbyUser.yaml) | LateralMovement | [`ZNSegmentAuditNativePoller_CL`](../tables/znsegmentauditnativepoller-cl.md)<br>[`ZNSegmentAudit_CL`](../tables/znsegmentaudit-cl.md) |
| [Zero Networks Segment - Inbound Block Rules Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks/Hunting%20Queries/ZNSegmentInboundBlockRulesDeleted.yaml) | DefenseEvasion | [`ZNSegmentAuditNativePoller_CL`](../tables/znsegmentauditnativepoller-cl.md)<br>[`ZNSegmentAudit_CL`](../tables/znsegmentaudit-cl.md) |
| [Zero Networks Segment - Outbound Block Rules Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks/Hunting%20Queries/ZNSegmentOutboundBlockRulesDeleted.yaml) | DefenseEvasion | [`ZNSegmentAuditNativePoller_CL`](../tables/znsegmentauditnativepoller-cl.md)<br>[`ZNSegmentAudit_CL`](../tables/znsegmentaudit-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ZNSegmentAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks/Workbooks/ZNSegmentAudit.json) | [`ZNSegmentAuditNativePoller_CL`](../tables/znsegmentauditnativepoller-cl.md)<br>[`ZNSegmentAudit_CL`](../tables/znsegmentaudit-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Add Asset to Protection - Zero Networks Segment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks/Playbooks/ZeroNetworksSegment-AddAssettoProtection/azuredeploy.json) | This playbook takes a host from a Microsoft Sentinel incident and adds it to protection. The playboo... | - |
| [Add Block Outbound Rule - Zero Networks Acccess Orchestrator](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks/Playbooks/ZeroNetworksSegment-AddBlockOutboundRule/azuredeploy.json) | This playbook allows blocking an IP outbound from protected assets in Zero Networks Segment. | - |
| [Enrich Incident - Zero Networks Acccess Orchestrator](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks/Playbooks/ZeroNetworksSegment-EnrichIncident/azuredeploy.json) | This playbook will take each Host entity and get its Asset status from Zero Network Segment. The pla... | - |
| [ZeroNetworks-swagger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks/Playbooks/ZeroNetworksConnector/ZeroNetworks-swagger.json) | - | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ZNSegmentAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroNetworks/Parsers/ZNSegmentAudit.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                     |
|-------------|--------------------------------|--------------------------------------------------------|
|  3.0.2      |  17-09-2025                    | Removed Deprecated **Data Connector**.  |
|  3.0.1      |  06-02-2025                    | Added missing parameter **URI** to Solution.  |
|  3.0.0      |  11-12-2024                    | Updated solution to 3.0.0  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
