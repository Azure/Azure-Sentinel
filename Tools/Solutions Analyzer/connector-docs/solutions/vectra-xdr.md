# Vectra XDR

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Vectra Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.vectra.ai/support](https://www.vectra.ai/support) |
| **Categories** | domains |
| **First Published** | 2023-07-04 |
| **Last Updated** | 2024-08-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Vectra XDR](../connectors/vectraxdr.md)

## Tables Reference

This solution uses **6 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Audits_Data_CL`](../tables/audits-data-cl.md) | [Vectra XDR](../connectors/vectraxdr.md) | Workbooks |
| [`Detections_Data_CL`](../tables/detections-data-cl.md) | [Vectra XDR](../connectors/vectraxdr.md) | Analytics, Workbooks |
| [`Entities_Data_CL`](../tables/entities-data-cl.md) | [Vectra XDR](../connectors/vectraxdr.md) | Analytics |
| [`Entity_Scoring_Data_CL`](../tables/entity-scoring-data-cl.md) | [Vectra XDR](../connectors/vectraxdr.md) | Workbooks |
| [`Health_Data_CL`](../tables/health-data-cl.md) | [Vectra XDR](../connectors/vectraxdr.md) | Workbooks |
| [`Lockdown_Data_CL`](../tables/lockdown-data-cl.md) | [Vectra XDR](../connectors/vectraxdr.md) | Workbooks |

### Internal Tables

The following **3 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AlertEvidence`](../tables/alertevidence.md) | - | Analytics |
| [`SecurityAlert`](../tables/securityalert.md) | - | Playbooks |
| [`SecurityIncident`](../tables/securityincident.md) | - | Playbooks |

## Content Items

This solution includes **33 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 20 |
| Analytic Rules | 7 |
| Parsers | 5 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Defender Alert Evidence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Analytic%20Rules/Defender_Alert_Evidence.yaml) | High | Persistence | *Internal use:*<br>[`AlertEvidence`](../tables/alertevidence.md) |
| [Vectra Create Detection Alert for Accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Analytic%20Rules/Detection_Account.yaml) | Medium | Persistence | [`Detections_Data_CL`](../tables/detections-data-cl.md) |
| [Vectra Create Detection Alert for Hosts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Analytic%20Rules/Detection_Host.yaml) | Medium | Persistence | [`Detections_Data_CL`](../tables/detections-data-cl.md) |
| [Vectra Create Incident Based on Priority for Accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Analytic%20Rules/Priority_Account.yaml) | Medium | Persistence | [`Entities_Data_CL`](../tables/entities-data-cl.md) |
| [Vectra Create Incident Based on Priority for Hosts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Analytic%20Rules/Priority_Host.yaml) | Medium | Persistence | [`Entities_Data_CL`](../tables/entities-data-cl.md) |
| [Vectra Create Incident Based on Tag for Accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Analytic%20Rules/Create_Incident_Based_On_Tag_For_Account_Entity.yaml) | High | Persistence | [`Entities_Data_CL`](../tables/entities-data-cl.md) |
| [Vectra Create Incident Based on Tag for Hosts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Analytic%20Rules/Create_Incident_Based_On_Tag_For_Host_Entity.yaml) | High | Persistence | [`Entities_Data_CL`](../tables/entities-data-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [VectraXDR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Workbooks/VectraXDR.json) | [`Audits_Data_CL`](../tables/audits-data-cl.md)<br>[`Detections_Data_CL`](../tables/detections-data-cl.md)<br>[`Entity_Scoring_Data_CL`](../tables/entity-scoring-data-cl.md)<br>[`Health_Data_CL`](../tables/health-data-cl.md)<br>[`Lockdown_Data_CL`](../tables/lockdown-data-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Vectra Add Note To Entity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraAddNoteToEntity/azuredeploy.json) | This playbook extracts notes from incident comments and adds them to Vectra Entity if comment added ... | - |
| [Vectra Add Tag To Entity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraAddTagToEntity/azuredeploy.json) | This playbook extracts tags from incident comments and adds them to the entity if comment found with... | - |
| [Vectra Add Tag To Entity All Detections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraAddTagToEntityAllDetections/azuredeploy.json) | This playbook enables user to add tags to all detections associated with a Vectra Entity. Tags can b... | - |
| [Vectra Add Tag To Entity Selected Detections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraAddTagToEntitySelectedDetections/azuredeploy.json) | This playbook enables users to add tags to selected detections associated with an entity. Users can ... | - |
| [Vectra Assign Dynamic User To Entity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraAssignDynamicUserToEntity/azuredeploy.json) | This playbook will assign a user selected by user from teams adpative card to an entity in Vectra wh... | - |
| [Vectra Assign Static User To Entity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraAssignStaticUserToEntity/azuredeploy.json) | This playbook will assign a predefined user to an entity in Vectra when the status of an incident ch... | - |
| [Vectra Close Detections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraCloseDetections/azuredeploy.json) | This playbook enables user to close detections associated with a Vectra Entity with reason as Remedi... | - |
| [Vectra Decorate Incident Based On Tag](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraDecorateIncidentBasedOnTag/azuredeploy.json) | This playbook will add pre-defined or user customizable comment to an incident generated based on ta... | - |
| [Vectra Decorate Incident Based On Tags And Notify](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraDecorateIncidentBasedOnTagAndNotify/azuredeploy.json) | This playbook will add pre-defined or user customizable comment to an incident generated based on ta... | - |
| [Vectra Download Pcap File To Storage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectaDownloadPcapFileToStorage/azuredeploy.json) | This playbook enables user to download pcap file of any detections associated with a Vectra Entity t... | - |
| [Vectra Dynamic Assign Member To Group](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraDynamicAssignMembersToGroup/azuredeploy.json) | This playbook allows users to filter the group list by providing a group type and a description. Fro... | - |
| [Vectra Dynamic Resolve Assignment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraDynamicResolveAssignment/azuredeploy.json) | When an incident is closed, This playbook will prompt the operator to select an outcome from a prede... | - |
| [Vectra Generate Access Token](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraGenerateAccessToken/azuredeploy.json) | This playbook will generate access token and refresh token for another playbooks. | - |
| [Vectra Incident Timeline Update](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraIncidentTimelineUpdate/azuredeploy.json) | This playbook will update the incident timeline by keeping most recent alerts and adding most recent... | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) *(read)*<br>[`SecurityIncident`](../tables/securityincident.md) *(read)* |
| [Vectra Mark Detections As Fixed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraMarkDetectionsAsFixed/azuredeploy.json) | This playbook will mark active detection as fixed associated with an entity based on choice of user ... | - |
| [Vectra Open Closed Detections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraOpenClosedDetections/azuredeploy.json) | This playbook enables user to close opened detections associated with a Vectra Entity. User can add ... | - |
| [Vectra Operate On Entity Source IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraOperateOnEntitySourceIP/azuredeploy.json) | This Playbook will extract the ip from entities associated with an incident on which playbook is tri... | - |
| [Vectra Static Assign Member To Group](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraStaticAssignMembersToGroup/azuredeploy.json) | This playbook will take input of group id and members from user via MS teams and assign members to t... | - |
| [Vectra Static Resolve Assignment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraStaticResolveAssignment/azuredeploy.json) | This playbook resolves the assignment for an entity in Vectra and adds a note for the assignment whe... | - |
| [Vectra Update Incident Based on Tag And Notify](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Playbooks/VectraUpdateIncidentBasedOnTagAndNotify/azuredeploy.json) | This playbook runs hourly to identify entities with Medium severity incidents, checks for user-defin... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [VectraAudits](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Parsers/VectraAudits.yaml) | - | - |
| [VectraDetections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Parsers/VectraDetections.yaml) | - | - |
| [VectraEntityScoring](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Parsers/VectraEntityScoring.yaml) | - | - |
| [VectraHealth](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Parsers/VectraHealth.yaml) | - | - |
| [VectraLockdown](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20XDR/Parsers/VectraLockdown.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                             |
|-------------|--------------------------------|----------------------------------------------------------------|
| 3.3.0       | 29-10-2025                     | Added Playbooks, Vectra API version update and Log ingestion API support |
| 3.2.0       | 01-08-2024                     | Added Playbooks, Analytic rules and updated Data Connector and Workbook |
| 3.1.1       | 03-04-2024                     | Repackaged for parser issue fix on reinstall                   |
| 3.1.0       | 04-01-2024                     | Included **Parser** files in yaml format                       |
| 3.0.2       | 04-10-2023                     | Enhanced **Data Connector** logic to post data into Sentinel   |
| 3.0.1       | 21-08-2023                     | **Workbook** metadata issue resolved                           |
| 3.0.0       | 03-08-2023                     | Initial Solution Release                                        |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
