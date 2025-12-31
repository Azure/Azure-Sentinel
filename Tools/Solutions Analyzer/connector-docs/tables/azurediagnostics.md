# AzureDiagnostics

Reference for AzureDiagnostics table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Various |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/azurediagnostics) |

## Solutions (37)

This table is used by the following solutions:

- [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md)
- [Azure Batch Account](../solutions/azure-batch-account.md)
- [Azure Cognitive Search](../solutions/azure-cognitive-search.md)
- [Azure DDoS Protection](../solutions/azure-ddos-protection.md)
- [Azure Data Lake Storage Gen1](../solutions/azure-data-lake-storage-gen1.md)
- [Azure Event Hubs](../solutions/azure-event-hubs.md)
- [Azure Firewall](../solutions/azure-firewall.md)
- [Azure Key Vault](../solutions/azure-key-vault.md)
- [Azure Logic Apps](../solutions/azure-logic-apps.md)
- [Azure Network Security Groups](../solutions/azure-network-security-groups.md)
- [Azure SQL Database solution for sentinel](../solutions/azure-sql-database-solution-for-sentinel.md)
- [Azure Service Bus](../solutions/azure-service-bus.md)
- [Azure Stream Analytics](../solutions/azure-stream-analytics.md)
- [Azure Web Application Firewall (WAF)](../solutions/azure-web-application-firewall-%28waf%29.md)
- [Azure kubernetes Service](../solutions/azure-kubernetes-service.md)
- [AzureSecurityBenchmark](../solutions/azuresecuritybenchmark.md)
- [Cloud Service Threat Protection Essentials](../solutions/cloud-service-threat-protection-essentials.md)
- [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md)
- [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md)
- [DNS Essentials](../solutions/dns-essentials.md)
- [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md)
- [Google Threat Intelligence](../solutions/google-threat-intelligence.md)
- [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md)
- [HIPAA Compliance](../solutions/hipaa-compliance.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [NISTSP80053](../solutions/nistsp80053.md)
- [Network Session Essentials](../solutions/network-session-essentials.md)
- [Recorded Future](../solutions/recorded-future.md)
- [SentinelSOARessentials](../solutions/sentinelsoaressentials.md)
- [SlashNext](../solutions/slashnext.md)
- [Threat Intelligence](../solutions/threat-intelligence.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)
- [ThreatAnalysis&Response](../solutions/threatanalysis&response.md)
- [ThreatConnect](../solutions/threatconnect.md)
- [Web Shells Threat Protection](../solutions/web-shells-threat-protection.md)
- [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md)

## Connectors (15)

This table is ingested by the following connectors:

- [Azure Batch Account](../connectors/azurebatchaccount-ccp.md)
- [Azure Cognitive Search](../connectors/azurecognitivesearch-ccp.md)
- [Azure Data Lake Storage Gen1](../connectors/azuredatalakestoragegen1-ccp.md)
- [Azure Event Hub](../connectors/azureeventhub-ccp.md)
- [Azure Firewall](../connectors/azurefirewall.md)
- [Azure Key Vault](../connectors/azurekeyvault.md)
- [Azure Kubernetes Service (AKS)](../connectors/azurekubernetes.md)
- [Azure Logic Apps](../connectors/azurelogicapps-ccp.md)
- [Network Security Groups](../connectors/azurensg.md)
- [Azure Service Bus](../connectors/azureservicebus-ccp.md)
- [Azure SQL Databases](../connectors/azuresql.md)
- [Azure Stream Analytics](../connectors/azurestreamanalytics-ccp.md)
- [Azure DDoS Protection](../connectors/ddos.md)
- [SlashNext Function App](../connectors/slashnextfunctionapp.md)
- [Azure Web Application Firewall (WAF)](../connectors/waf.md)

---

## Content Items Using This Table (114)

### Analytic Rules (58)

**In solution [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md):**
- [Azure WAF matching for Log4j vuln(CVE-2021-44228)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Analytic%20Rules/AzureWAFmatching_log4j_vuln.yaml)
- [Log4j vulnerability exploit aka Log4Shell IP IOC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Analytic%20Rules/Log4J_IPIOC_Dec112021.yaml)

**In solution [Azure DDoS Protection](../solutions/azure-ddos-protection.md):**
- [DDoS Attack IP Addresses - PPS Threshold](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20DDoS%20Protection/Analytic%20Rules/AttackSourcesPPSThreshold.yaml)
- [DDoS Attack IP Addresses - Percent Threshold](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20DDoS%20Protection/Analytic%20Rules/AttackSourcesPercentThreshold.yaml)

**In solution [Azure Key Vault](../solutions/azure-key-vault.md):**
- [Azure Key Vault access TimeSeries anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Analytic%20Rules/TimeSeriesKeyvaultAccessAnomaly.yaml)
- [Mass secret retrieval from Azure Key Vault](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Analytic%20Rules/KeyvaultMassSecretRetrieval.yaml)
- [NRT Sensitive Azure Key Vault operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Analytic%20Rules/NRT_KeyVaultSensitiveOperations.yaml)
- [Sensitive Azure Key Vault operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Analytic%20Rules/KeyVaultSensitiveOperations.yaml)

**In solution [Azure SQL Database solution for sentinel](../solutions/azure-sql-database-solution-for-sentinel.md):**
- [Affected rows stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-VolumeAffectedRowsStatefulAnomalyOnDatabase.yaml)
- [Credential errors stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-ErrorsCredentialStatefulAnomalyOnDatabase.yaml)
- [Drop attempts stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-HotwordsDropStatefulAnomalyOnDatabase.yaml)
- [Execution attempts stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-HotwordsExecutionStatefulAnomalyOnDatabase.yaml)
- [Firewall errors stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-ErrorsFirewallStatefulAnomalyOnDatabase.yaml)
- [Firewall rule manipulation attempts stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-HotwordsFirewallRuleStatefulAnomalyOnDatabase.yaml)
- [OLE object manipulation attempts stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-HotwordsOLEObjectStatefulAnomalyOnDatabase.yaml)
- [Outgoing connection attempts stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-HotwordsOutgoingStatefulAnomalyOnDatabase.yaml)
- [Response rows stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-VolumeResponseRowsStatefulAnomalyOnDatabase.yaml)
- [Syntax errors stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-ErrorsSyntaxStatefulAnomalyOnDatabase.yaml)

**In solution [Azure Web Application Firewall (WAF)](../solutions/azure-web-application-firewall-%28waf%29.md):**
- [AFD WAF - Code Injection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/AFD-WAF-Code-Injection.yaml)
- [AFD WAF - Path Traversal Attack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/AFD-WAF-Path-Traversal-Attack.yaml)
- [Front Door Premium WAF - SQLi Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/AFD-Premium-WAF-SQLiDetection.yaml)
- [Front Door Premium WAF - XSS Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/AFD-Premium-WAF-XSSDetection.yaml)

**In solution [DNS Essentials](../solutions/dns-essentials.md):**
- [Detect DNS queries reporting multiple errors from different clients - Anomaly Based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/MultipleErrorsReportedForSameDNSQueryAnomalyBased.yaml)
- [Detect DNS queries reporting multiple errors from different clients - Static threshold based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/MultipleErrorsReportedForSameDNSQueryStaticThresholdBased.yaml)
- [Detect excessive NXDOMAIN DNS queries - Anomaly based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/ExcessiveNXDOMAINDNSQueriesAnomalyBased.yaml)
- [Detect excessive NXDOMAIN DNS queries - Static threshold based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/ExcessiveNXDOMAINDNSQueriesStaticThresholdBased.yaml)
- [Ngrok Reverse Proxy on Network (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/NgrokReverseProxyOnNetwork.yaml)
- [Potential DGA(Domain Generation Algorithm) detected via Repetitive Failures - Anomaly based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/PotentialDGADetectedviaRepetitiveFailuresAnomalyBased.yaml)
- [Potential DGA(Domain Generation Algorithm) detected via Repetitive Failures - Static threshold based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/PotentialDGADetectedviaRepetitiveFailuresStaticThresholdBased.yaml)
- [Rare client observed with high reverse DNS lookup count - Anomaly based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/RareClientObservedWithHighReverseDNSLookupCountAnomalyBased.yaml)
- [Rare client observed with high reverse DNS lookup count - Static threshold based (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Analytic%20Rules/RareClientObservedWithHighReverseDNSLookupCountStaticThresholdBased.yaml)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntDomain.yaml)
- [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntIp.yaml)

**In solution [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md):**
- [GreyNoise TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_imNetworkSession.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Possible Phishing with CSL and Network Sessions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/PossiblePhishingwithCSL%26NetworkSession.yaml)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [Anomaly found in Network Session Traffic (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/AnomalyFoundInNetworkSessionTraffic.yaml)
- [Anomaly in SMB Traffic(ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/Anomaly%20in%20SMB%20Traffic%28ASIM%20Network%20Session%20schema%29.yaml)
- [Detect port misuse by anomaly based detection (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/DetectPortMisuseByAnomalyBasedDetection.yaml)
- [Detect port misuse by static threshold (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/DetectPortMisuseByStaticThreshold.yaml)
- [Excessive number of failed connections from a single source (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/ExcessiveHTTPFailuresFromSource.yaml)
- [Network Port Sweep from External Network (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/NetworkPortSweepFromExternalNetwork.yaml)
- [Port scan detected  (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/PortScan.yaml)
- [Potential beaconing activity (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/PossibleBeaconingActivity.yaml)
- [Remote Desktop Network Brute force (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/Remote%20Desktop%20Network%20Brute%20force%20%28ASIM%20Network%20Session%20schema%29.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Domain All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingDomainAllActors.yaml)
- [RecordedFuture Threat Hunting IP All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingIPAllActors.yaml)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI Map IP Entity to Azure SQL Security Audit Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureSQL.yaml)
- [TI map Domain entity to Dns Events (ASIM DNS Schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/imDns_DomainEntity_DnsEvents.yaml)
- [TI map IP entity to Azure Key Vault logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureKeyVault.yaml)
- [TI map IP entity to AzureFirewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureFirewall.yaml)
- [TI map IP entity to DNS Events (ASIM DNS schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/imDns_IPEntity_DnsEvents.yaml)
- [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_imNetworkSession.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI Map IP Entity to Azure SQL Security Audit Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AzureSQL.yaml)
- [TI map Domain entity to Dns Events (ASIM DNS Schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/imDns_DomainEntity_DnsEvents.yaml)
- [TI map IP entity to Azure Key Vault logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AzureKeyVault.yaml)
- [TI map IP entity to DNS Events (ASIM DNS schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/imDns_IPEntity_DnsEvents.yaml)
- [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_imNetworkSession.yaml)

**In solution [ThreatConnect](../solutions/threatconnect.md):**
- [ThreatConnect TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_IPEntity_NetworkSessions.yaml)

### Hunting Queries (34)

**In solution [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md):**
- [Azure WAF Log4j CVE-2021-44228 hunting](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Hunting%20Queries/WAF_log4j_vulnerability.yaml)

**In solution [Azure SQL Database solution for sentinel](../solutions/azure-sql-database-solution-for-sentinel.md):**
- [Affected rows stateful anomaly on database - hunting query](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-VolumeAffectedRowsStatefulAnomalyOnDatabase.yaml)
- [Anomalous Query Execution Time](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-AffectedRowAnomaly.yaml)
- [Anomalous Query Execution Time](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-ExecutionTimeAnomaly.yaml)
- [Boolean Blind SQL Injection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-BooleanBlindSQLi.yaml)
- [Prevalence Based SQL Query Size Anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-PrevalenceBasedQuerySizeAnomaly.yaml)
- [Response rows stateful anomaly on database - hunting query](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-VolumeResponseRowsStatefulAnomalyOnDatabase.yaml)
- [Suspicious SQL Stored Procedures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-SuspiciousStoredProcedures.yaml)
- [Time Based SQL Query Size Anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-TimeBasedQuerySizeAnomaly.yaml)

**In solution [Azure kubernetes Service](../solutions/azure-kubernetes-service.md):**
- [Azure RBAC AKS created role details](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service/Hunting%20Queries/AKS-Rbac.yaml)
- [Determine users with cluster admin role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service/Hunting%20Queries/AKS-clusterrolebinding.yaml)

**In solution [Cloud Service Threat Protection Essentials](../solutions/cloud-service-threat-protection-essentials.md):**
- [Azure Key Vault Access Policy Manipulation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Service%20Threat%20Protection%20Essentials/Hunting%20Queries/AzureKeyVaultAccessManipulation.yaml)

**In solution [DNS Essentials](../solutions/dns-essentials.md):**
- [CVE-2020-1350 (SIGRED) exploitation pattern (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/CVE-2020-1350%20%28SIGRED%29ExploitationPattern.yaml)
- [Connection to Unpopular Website Detected (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/ConnectionToUnpopularWebsiteDetected.yaml)
- [Increase in DNS Requests by client than the daily average count (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/IncreaseInDNSRequestsByClientThanTheDailyAverageCount.yaml)
- [Possible DNS Tunneling or Data Exfiltration Activity (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/PossibleDNSTunnelingOrDataExfiltrationActivity.yaml)
- [Potential beaconing activity (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/PotentialBeaconingActivity.yaml)
- [Top 25 DNS queries with most failures in last 24 hours (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/DNSQueryWithFailuresInLast24Hours.yaml)
- [Top 25 Domains with large number of Subdomains (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/DomainsWithLargeNumberOfSubDomains.yaml)
- [Top 25 Sources(Clients) with high number of errors in last 24hours (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/Sources%28Clients%29WithHighNumberOfErrors.yaml)
- [Unexpected top level domains (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/UnexpectedTopLevelDomains.yaml)
- [[Anomaly] Anomalous Increase in DNS activity by clients (ASIM DNS Solution)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Hunting%20Queries/AnomalousIncreaseInDNSActivityByClients.yaml)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntDomain.yaml)
- [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntIp.yaml)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [Detect Outbound LDAP Traffic(ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/Detect%20Outbound%20LDAP%20Traffic%28ASIM%20Network%20Session%20schema%29.yaml)
- [Detect port misuse by anomaly (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/DetectPortMisuseByAnomalyHunting.yaml)
- [Detect port misuse by static threshold (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/DetectPortMisuseByStaticThresholdHunting.yaml)
- [Detects several users with the same MAC address (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/DetectsSeveralUsersWithTheSameMACAddress.yaml)
- [Mismatch between Destination App name and Destination Port (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/MismatchBetweenDestinationAppNameAndDestinationPort.yaml)
- [Protocols passing authentication in cleartext (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/Protocols%20passing%20authentication%20in%20cleartext%20%28ASIM%20Network%20Session%20schema%29.yaml)
- [Remote Desktop Network Traffic(ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/Remote%20Desktop%20Network%20Traffic%28ASIM%20Network%20Session%20schema%29.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Domain All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureDomainThreatActorHunt.yaml)
- [RecordedFuture Threat Hunting IP All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureIPThreatActorHunt.yaml)

**In solution [Web Shells Threat Protection](../solutions/web-shells-threat-protection.md):**
- [Possible Webshell usage attempt related to SpringShell(CVE-2022-22965)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Hunting%20Queries/SpringshellWebshellUsage.yaml)

### Workbooks (20)

**In solution [Azure DDoS Protection](../solutions/azure-ddos-protection.md):**
- [AzDDoSStandardWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20DDoS%20Protection/Workbooks/AzDDoSStandardWorkbook.json)

**In solution [Azure Firewall](../solutions/azure-firewall.md):**
- [AzureFirewallWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Workbooks/AzureFirewallWorkbook.json)

**In solution [Azure Key Vault](../solutions/azure-key-vault.md):**
- [AzureKeyVaultWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Workbooks/AzureKeyVaultWorkbook.json)

**In solution [Azure SQL Database solution for sentinel](../solutions/azure-sql-database-solution-for-sentinel.md):**
- [Workbook-AzureSQLSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Workbooks/Workbook-AzureSQLSecurity.json)

**In solution [Azure Web Application Firewall (WAF)](../solutions/azure-web-application-firewall-%28waf%29.md):**
- [WebApplicationFirewallFirewallEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Workbooks/WebApplicationFirewallFirewallEvents.json)
- [WebApplicationFirewallGatewayAccessEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Workbooks/WebApplicationFirewallGatewayAccessEvents.json)
- [WebApplicationFirewallOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Workbooks/WebApplicationFirewallOverview.json)

**In solution [AzureSecurityBenchmark](../solutions/azuresecuritybenchmark.md):**
- [AzureSecurityBenchmark](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/Workbooks/AzureSecurityBenchmark.json)

**In solution [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md):**
- [ContinuousDiagnostics&Mitigation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics%26Mitigation/Workbooks/ContinuousDiagnostics%26Mitigation.json)

**In solution [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md):**
- [CybersecurityMaturityModelCertification_CMMCV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CybersecurityMaturityModelCertification%28CMMC%292.0/Workbooks/CybersecurityMaturityModelCertification_CMMCV2.json)

**In solution [DNS Essentials](../solutions/dns-essentials.md):**
- [DNSSolutionWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DNS%20Essentials/Workbooks/DNSSolutionWorkbook.json)

**In solution [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md):**
- [GDPRComplianceAndDataSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GDPR%20Compliance%20%26%20Data%20Security/Workbooks/GDPRComplianceAndDataSecurity.json)

**In solution [HIPAA Compliance](../solutions/hipaa-compliance.md):**
- [HIPAACompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HIPAA%20Compliance/Workbooks/HIPAACompliance.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [NISTSP80053](../solutions/nistsp80053.md):**
- [NISTSP80053](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Workbooks/NISTSP80053.json)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [NetworkSessionEssentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentials.json)
- [NetworkSessionEssentialsV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentialsV2.json)

**In solution [SentinelSOARessentials](../solutions/sentinelsoaressentials.md):**
- [AutomationHealth](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Workbooks/AutomationHealth.json)

**In solution [ThreatAnalysis&Response](../solutions/threatanalysis&response.md):**
- [DynamicThreatModeling&Response](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatAnalysis%26Response/Workbooks/DynamicThreatModeling%26Response.json)

**In solution [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md):**
- [ZeroTrustTIC3](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Workbooks/ZeroTrustTIC3.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
