# Playbooks under deprecation 

More information about Recorded Future Intelligence Solution for Microsoft Sentinel can be found in the main [readme](../readme.md).

The following playbooks are being deprecated due to Microsoft are deprecating underlying APIs.

We are deprecating the RecordedFuture-ImportToSentinel and all \*-TIProcessor playbooks. Going forward, install the new IndicatorImport playbooks and configure them to download you selection of risk lists. Investigate the risk lists being downloaded and the cadence and use the same configuration using the TIProcessor playbooks. Use the same description for threat indicators if you have analytic rules set up for alerting. 

Our support will end when Microsoft decommission their underlying API. More information can be found on [Microsoft Learn](https://learn.microsoft.com/en-us/azure/sentinel/understand-threat-intelligence#add-threat-indicators-to-microsoft-sentinel-with-the-threat-intelligence-platforms-data-connector)

- [RecordedFuture-DOMAIN-C2_DNS_Name-IndicatorProcessor](RecordedFuture-DOMAIN-C2_DNS_Name-IndicatorProcessor/readme.md)
- [RecordedFuture-HASH-Observed_in_Underground_Virus_Test_Sites-IndicatorProcessor](RecordedFuture-HASH-Observed_in_Underground_Virus_Test_Sites-IndicatorProcessor/readme.md)
- [RecordedFuture-ImportToSentinel](RecordedFuture-ImportToSentinel/readme.md)
- [RecordedFuture-IP-Actively_Comm_C2_Server-IndicatorProcessor](RecordedFuture-IP-Actively_Comm_C2_Server-IndicatorProcessor/readme.md)
- [RecordedFuture-Ukraine-IndicatorProcessor](RecordedFuture-Ukraine-IndicatorProcessor/readme.md)
- [RecordedFuture-URL-Recent_Rep_by_Insikt_Group-IndicatorProcessor](RecordedFuture-URL-Recent_Rep_by_Insikt_Group-IndicatorProcessor/readme.md)