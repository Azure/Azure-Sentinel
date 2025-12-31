# Group-IB

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** |  |
| **Support Tier** |  |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **21 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`GIBTIAAPTThreatActor_CL`](../tables/gibtiaaptthreatactor-cl.md) | Playbooks (writes) |
| [`GIBTIAAPTThreatReports_CL`](../tables/gibtiaaptthreatreports-cl.md) | Playbooks (writes) |
| [`GIBTIAAttacksDDoS_CL`](../tables/gibtiaattacksddos-cl.md) | Playbooks (writes) |
| [`GIBTIAAttacksDeface_CL`](../tables/gibtiaattacksdeface-cl.md) | Playbooks (writes) |
| [`GIBTIAAttacksPhishingKit_CL`](../tables/gibtiaattacksphishingkit-cl.md) | Playbooks (writes) |
| [`GIBTIABPPhishingKit_CL`](../tables/gibtiabpphishingkit-cl.md) | Playbooks (writes) |
| [`GIBTIABPPhishing_CL`](../tables/gibtiabpphishing-cl.md) | Playbooks (writes) |
| [`GIBTIACompromisedCard_CL`](../tables/gibtiacompromisedcard-cl.md) | Playbooks (writes) |
| [`GIBTIACompromisedIMEI_CL`](../tables/gibtiacompromisedimei-cl.md) | Playbooks (writes) |
| [`GIBTIACompromisedMule_CL`](../tables/gibtiacompromisedmule-cl.md) | Playbooks (writes) |
| [`GIBTIAHIThreatActor_CL`](../tables/gibtiahithreatactor-cl.md) | Playbooks (writes) |
| [`GIBTIAHIThreatReports_CL`](../tables/gibtiahithreatreports-cl.md) | Playbooks (writes) |
| [`GIBTIAMalwareCNC_CL`](../tables/gibtiamalwarecnc-cl.md) | Playbooks (writes) |
| [`GIBTIAOSIGitLeak_CL`](../tables/gibtiaosigitleak-cl.md) | Playbooks (writes) |
| [`GIBTIAOSIPublicLeak_CL`](../tables/gibtiaosipublicleak-cl.md) | Playbooks (writes) |
| [`GIBTIAOSIVulnerability_CL`](../tables/gibtiaosivulnerability-cl.md) | Playbooks (writes) |
| [`GIBTIASuspiciousIPOpenProxy_CL`](../tables/gibtiasuspiciousipopenproxy-cl.md) | Playbooks (writes) |
| [`GIBTIASuspiciousIPSocksProxy_CL`](../tables/gibtiasuspiciousipsocksproxy-cl.md) | Playbooks (writes) |
| [`GIBTIASuspiciousIPTorNode_CL`](../tables/gibtiasuspiciousiptornode-cl.md) | Playbooks (writes) |
| [`GIBTIATargetedMalware_CL`](../tables/gibtiatargetedmalware-cl.md) | Playbooks (writes) |
| [`GIBTechTable_CL`](../tables/gibtechtable-cl.md) | Playbooks (writes) |

## Content Items

This solution includes **23 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 23 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [GIBIndicatorProcessor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBIndicatorProcessor.json) | - | - |
| [GIBTIA_APT_ThreatActor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_APT_ThreatActor.json) | - | [`GIBTIAAPTThreatActor_CL`](../tables/gibtiaaptthreatactor-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_APT_Threats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_APT_Threats.json) | - | [`GIBTIAAPTThreatReports_CL`](../tables/gibtiaaptthreatreports-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_Attacks_ddos](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_Attacks_ddos.json) | - | [`GIBTIAAttacksDDoS_CL`](../tables/gibtiaattacksddos-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_Attacks_deface](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_Attacks_deface.json) | - | [`GIBTIAAttacksDeface_CL`](../tables/gibtiaattacksdeface-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_Attacks_phishing](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_Attacks_phishing.json) | - | [`GIBTIAAttacksPhishingKit_CL`](../tables/gibtiaattacksphishingkit-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_Attacks_phishing_kit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_Attacks_phishing_kit.json) | - | [`GIBTIAAttacksPhishingKit_CL`](../tables/gibtiaattacksphishingkit-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_BP_phishing](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_BP_phishing.json) | - | [`GIBTIABPPhishing_CL`](../tables/gibtiabpphishing-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_BP_phishing_kit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_BP_phishing_kit.json) | - | [`GIBTIABPPhishingKit_CL`](../tables/gibtiabpphishingkit-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_Compromised_account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_Compromised_account.json) | - | [`GIBTIABPPhishingKit_CL`](../tables/gibtiabpphishingkit-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_Compromised_card](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_Compromised_card.json) | - | [`GIBTIACompromisedCard_CL`](../tables/gibtiacompromisedcard-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_Compromised_imei](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_Compromised_imei.json) | - | [`GIBTIACompromisedIMEI_CL`](../tables/gibtiacompromisedimei-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_Compromised_mule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_Compromised_mule.json) | - | [`GIBTIACompromisedMule_CL`](../tables/gibtiacompromisedmule-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_HI_Threat](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_HI_Threat.json) | - | [`GIBTIAHIThreatReports_CL`](../tables/gibtiahithreatreports-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_HI_Threat_Actor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_HI_Threat_Actor.json) | - | [`GIBTIAHIThreatActor_CL`](../tables/gibtiahithreatactor-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_Malware_Targeted_Malware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_Malware_Targeted_Malware.json) | - | [`GIBTIATargetedMalware_CL`](../tables/gibtiatargetedmalware-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_Malware_cnc](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_Malware_cnc.json) | - | [`GIBTIAMalwareCNC_CL`](../tables/gibtiamalwarecnc-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_OSI_GitLeak](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_OSI_GitLeak.json) | - | [`GIBTIAOSIGitLeak_CL`](../tables/gibtiaosigitleak-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_OSI_PublicLeak](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_OSI_PublicLeak.json) | - | [`GIBTIAOSIPublicLeak_CL`](../tables/gibtiaosipublicleak-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_OSI_Vulnerability](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_OSI_Vulnerability.json) | - | [`GIBTIAOSIVulnerability_CL`](../tables/gibtiaosivulnerability-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_Suspicious_ip_open_proxy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_Suspicious_ip_open_proxy.json) | - | [`GIBTIASuspiciousIPOpenProxy_CL`](../tables/gibtiasuspiciousipopenproxy-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_Suspicious_ip_socks_proxy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_Suspicious_ip_socks_proxy.json) | - | [`GIBTIASuspiciousIPSocksProxy_CL`](../tables/gibtiasuspiciousipsocksproxy-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |
| [GIBTIA_Suspicious_ip_tor_node](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Group-IB/Playbooks/azuredeploy-GIBTIA_Suspicious_ip_tor_node.json) | - | [`GIBTIASuspiciousIPTorNode_CL`](../tables/gibtiasuspiciousiptornode-cl.md) *(write)*<br>[`GIBTechTable_CL`](../tables/gibtechtable-cl.md) *(read/write)* |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
