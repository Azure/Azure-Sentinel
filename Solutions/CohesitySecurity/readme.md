# Cohesity SIEM/SOAR Integration with Sentinel
This is a Cohesity authored integration for use with Sentinel, Microsoft’s cloud-native security information and event manager (SIEM) platform, to enable Security Operators and ITOps the automation and operational simplicity to respond to threats and recover from ransomware incidents, from inside Sentinel. Here are the key workflows 
* Send ransomware alerts into Sentinel via RESTful APIs integration.
* View incidents with the alert details.
* Escalate to ITSM tool via included playbooks.
* Initiate recovery of clean snapshot via included playbook.
* Closed loop integration resolves alerts in Helios via included playbook.

## Package Building and Validation Instructions
__Disclaimer:__ You can skip these steps and use one of the pre-built packages from [this directory](https://github.com/cohesity/Azure-Sentinel/tree/CohesitySecurity.internal/Solutions/CohesitySecurity/Package). These steps are required _only_ if you'd like to rebuild the package yourself.
1. Follow this [readme.md](https://github.com/cohesity/Azure-Sentinel/blob/CohesitySecurity.internal/Solutions/README.md) for setup build prerequisites.
2. Edit [cohesity.json](https://github.com/cohesity/Azure-Sentinel/blob/CohesitySecurity.internal/Solutions/CohesitySecurity/cohesity.json) to replace the obfuscated values with your own. __Note:__ The obfuscation is done to protect PII information from leaking outside of the company.
3. Run [build.ps1](https://github.com/cohesity/Azure-Sentinel/blob/CohesitySecurity.internal/Solutions/CohesitySecurity/build.ps1) to build the package.
4. Follow [readme.md](https://github.com/cohesity/Azure-Sentinel/blob/CohesitySecurity.internal/Solutions/README.md) for post-build manual validation.

## Deployment
The package consists of the following Azure functions ([install pre-requisites](https://github.com/cohesity/Azure-Sentinel/tree/CohesitySecurity.internal/DataConnectors/CohesitySecurity/Helios2Sentinel#readme))
* _IncidentProducer_ to retrieve Helios alerts via a special REST API ([deployment steps](https://github.com/cohesity/Azure-Sentinel/blob/CohesitySecurity.internal/DataConnectors/CohesitySecurity/Helios2Sentinel/IncidentProducer/readme.md))
* _IncidentConsumer_ to create incidents in MS Sentinel ([deployment steps](https://github.com/cohesity/Azure-Sentinel/blob/CohesitySecurity.internal/DataConnectors/CohesitySecurity/Helios2Sentinel/IncidentConsumer/readme.md))

It also has a few playbooks for automation.
* *Cohesity_Send_Incident_Email* to send an email to the recipient with the incident details ([deployment steps](https://github.com/cohesity/Azure-Sentinel/tree/CohesitySecurity.internal/Solutions/CohesitySecurity/Playbooks/Cohesity_Send_Incident_Email#readme.md)).
* *Cohesity_CreateOrUpdate_ServiceNow_Incident* to create and update the incident in the ServiceNow platform ([deployment steps](https://github.com/cohesity/Azure-Sentinel/tree/CohesitySecurity.internal/Solutions/CohesitySecurity/Playbooks/SNOW-CreateAndUpdateIncident#readme.md)).
* *Cohesity_Restore_From_Last_Snapshot* to restore data from the latest clean snapshot in Helios ([deployment steps](https://github.com/cohesity/Azure-Sentinel/tree/CohesitySecurity.internal/Solutions/CohesitySecurity/Playbooks/Cohesity_Restore_From_Last_Snapshot#readme.md))

## Misc
This directory also has [build_one_solution.ps1](https://github.com/cohesity/Azure-Sentinel/blob/CohesitySecurity.internal/Solutions/CohesitySecurity/build_one_solution.ps1) that is needed when you'd like to build one specific solution.
The default build-script, provided by Microsoft, loops through all solutions, which often takes significant time.
