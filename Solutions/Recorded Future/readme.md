[<img alt="Recorded Future" src="Playbooks\RecordedFuture-IOC_Enrichment-IP_Domain_URL_Hash\images\RecordedFuture.png"  />](https://www.recordedfuture.com/)
# Recorded Future Intelligence for Microsoft Sentinel

Instructions how to install and use Recorded Future Solution for Microsoft Sentinel or how to install individual playbooks kan be found in the main [readme.md](Playbooks/readme.md) in the Playbook subdirectory in this repository.

Recorded Future also provide standalone Playbooks in this repository for EntraID (identity) and Defender for endpoints:

**Recorded Future Intelligence Solution**
- [Installation guide](Playbooks/readme.md)

**Recorded Future Defender Integrations**
- [Recorded Future Defender playbooks](../../Playbooks/RecordedFuture-Block-IPs-and-Domains-on-Microsoft-Defender-for-Endpoint/)
- [Recorded Future Defender SCF playbooks](../../Playbooks/RecordedFuture_IP_SCF/)

**Recorded Future for Identity**
- [Recorded Future Identity](../Recorded%20Future%20Identity/Playbooks/readme.md)

This guide provides instructions on how to install, update and configure Recorded Future Intelligence for Microsoft Sentinel.

# About Recorded Future

Recorded Future is the world's largest provider of intelligence for enterprise security. By seamlessly combining automated data collection, pervasive analytics, and expert human analysis, Recorded Future delivers timely, accurate, and actionable intelligence.

**Benefits of Recorded Future integrations** 
- Detect indicators of compromise (IOCs) in your environment.
- Triage alerts faster with elite, real-time intelligence.
- Respond quickly with transparency and context around internal telemetry data.
- Maximize your investment in Microsoft Sentinel.

[Learn more about Recorded Future for Microsoft Sentinel](https://www.recordedfuture.com/microsoft-azure-sentinel-integration)

[Start a 30-day free trial of Recorded Future for Microsoft Sentinel from here!](https://go.recordedfuture.com/microsoft-azure-sentinel-free-trial?utm_campaign=&utm_source=microsoft&utm_medium=gta)


# Key Features
Recorded Future for Microsoft Sentinel offers a range of powerful intelligence capabilities, some of the key features include:
## **IOC Detection (Detect)**

The TI-IndicatorImport playbooks pulls risk lists from Recorded Future and writes the contained indicators to the Microsoft Sentinel ThreatIntelligenceIndicator table via the RecordedFuture-ThreatIntelligenceImport playbook. 
![](Playbooks/Images/2023-04-19-17-08-46.png)\
Microsoft Sentinel analytic rules correlates threat intelligence indicators with logs provided to Microsoft Sentinel and creates alerts/incidents for matches found.\
![](Playbooks/Images/2023-04-19-17-46-32.png)

## **IOC Enrichment (Respond)**

Automation rules triggers on each incident and enriches incidents with Recorded Future intelligence. 
![](Playbooks/Images/2023-04-19-17-46-13.png)

## **Malware Sandbox Analysis (Sandbox)**

Uploads and detonate samples in Recorded Future's Malware Analysis Sandbox. The sandbox provides safe and immediate behavioral analysis, helping contextualize key artifacts in an investigation, leading to faster triage.
![](Playbooks/Images/2023-06-26-10-04-42.png)

## **Import Alerts (SOC Efficiency)**

To increase the visibility and availability of Recorded Future Alerts. Import Recorded Future Alerts and Playbook Alerts from Recorded Future Portal into Microsoft Sentinel. 

## **Recorded Future Automated Threat Hunt (Threat Hunt)**
Threat hunting is the proactive and iterative process of searching for and detecting cyber threats that have evaded traditional security measures, such as firewalls, antivirus software, and intrusion detection systems. It involves using a combination of manual and automated techniques to identify and investigate potential security breaches and intrusions within an organization's network.

[More about Threat Hunt](https://support.recordedfuture.com/hc/en-us/articles/20849290045203-Automated-Threat-Hunting-with-Recorded-Future) (requires login)

## Recorded Future Risk Lists
Risk Lists are curated lists that contain Indicators of Compromise (IOCs), such as IP addresses, domains, file hashes, or URLs associated with malicious activity. These lists are generated based on a wide array of Recorded Future intelligence sources, including open web, dark web, and other technical sources. 

* [Manage Risk Lists](https://www.recordedfuture.com/support/install-configure-manage-risk-lists)
* [About Risk Lists](https://support.recordedfuture.com/hc/en-us/articles/115000897248-Recorded-Future-Risk-Lists) (requires login)
* [Risk List Download Recommendations](https://support.recordedfuture.com/hc/en-us/articles/115010401968-Risk-List-Download-Recommendations) (requires login)
