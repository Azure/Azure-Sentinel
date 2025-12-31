# AzureActivity

Reference for AzureActivity table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Audit, Azure Resources, Security |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✗ No |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/azureactivity) |

## Solutions (15)

This table is used by the following solutions:

- [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md)
- [Azure Activity](../solutions/azure-activity.md)
- [AzureSecurityBenchmark](../solutions/azuresecuritybenchmark.md)
- [Cloud Service Threat Protection Essentials](../solutions/cloud-service-threat-protection-essentials.md)
- [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md)
- [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md)
- [NISTSP80053](../solutions/nistsp80053.md)
- [SOX IT Compliance](../solutions/sox-it-compliance.md)
- [SecurityThreatEssentialSolution](../solutions/securitythreatessentialsolution.md)
- [Threat Intelligence](../solutions/threat-intelligence.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)
- [ThreatAnalysis&Response](../solutions/threatanalysis&response.md)
- [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Azure Activity](../connectors/azureactivity.md)

---

## Content Items Using This Table (48)

### Analytic Rules (21)

**In solution [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md):**
- [Log4j vulnerability exploit aka Log4Shell IP IOC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Analytic%20Rules/Log4J_IPIOC_Dec112021.yaml)

**In solution [Azure Activity](../solutions/azure-activity.md):**
- [Azure Machine Learning Write Operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/Machine_Learning_Creation.yaml)
- [Creation of expensive computes in Azure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/Creation_of_Expensive_Computes_in_Azure.yaml)
- [Mass Cloud resource deletions Time Series Anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/TimeSeriesAnomaly_Mass_Cloud_Resource_Deletions.yaml)
- [Microsoft Entra ID Hybrid Health AD FS New Server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/AADHybridHealthADFSNewServer.yaml)
- [Microsoft Entra ID Hybrid Health AD FS Service Delete](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/AADHybridHealthADFSServiceDelete.yaml)
- [Microsoft Entra ID Hybrid Health AD FS Suspicious Application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/AADHybridHealthADFSSuspApp.yaml)
- [NRT Creation of expensive computes in Azure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/NRT_Creation_of_Expensive_Computes_in_Azure.yaml)
- [NRT Microsoft Entra ID Hybrid Health AD FS New Server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/NRT-AADHybridHealthADFSNewServer.yaml)
- [New CloudShell User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/New-CloudShell-User.yaml)
- [Rare subscription-level operations in Azure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/RareOperations.yaml)
- [Subscription moved to another tenant](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/SubscriptionMigration.yaml)
- [Suspicious Resource deployment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/NewResourceGroupsDeployedTo.yaml)
- [Suspicious granting of permissions to an account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/Granting_Permissions_To_Account_detection.yaml)
- [Suspicious number of resource creation or deployment activities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Analytic%20Rules/Creating_Anomalous_Number_Of_Resources_detection.yaml)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [M2131_DataConnectorAddedChangedRemoved](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Analytic%20Rules/M2131DataConnectorAddedChangedRemoved.yaml)

**In solution [SecurityThreatEssentialSolution](../solutions/securitythreatessentialsolution.md):**
- [Threat Essentials - Mass Cloud resource deletions Time Series Anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Analytic%20Rules/Threat_Essentials_TimeSeriesAnomaly_Mass_Cloud_Resource_Deletions.yaml)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI Map IP Entity to AzureActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureActivity.yaml)
- [TI map Email entity to AzureActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_AzureActivity.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI Map IP Entity to AzureActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AzureActivity.yaml)
- [TI map Email entity to AzureActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_AzureActivity.yaml)

### Hunting Queries (16)

**In solution [Azure Activity](../solutions/azure-activity.md):**
- [Anomalous Azure Operation Hunting Model](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AnomalousAzureOperationModel.yaml)
- [Azure Machine Learning Write Operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/Machine_Learning_Creation.yaml)
- [Azure Network Security Group NSG Administrative Operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AzureNSG_AdministrativeOperations.yaml)
- [Azure Virtual Network Subnets Administrative Operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AzureVirtualNetworkSubnets_AdministrativeOperationset.yaml)
- [Azure storage key enumeration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/Anomalous_Listing_Of_Storage_Keys.yaml)
- [AzureActivity Administration From VPS Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AzureAdministrationFromVPS.yaml)
- [Common deployed resources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/Common_Deployed_Resources.yaml)
- [Creation of an anomalous number of resources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/Creating_Anomalous_Number_Of_Resources.yaml)
- [Granting permissions to account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/Granting_Permissions_to_Account.yaml)
- [Microsoft Sentinel Analytics Rules Administrative Operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AnalyticsRulesAdministrativeOperations.yaml)
- [Microsoft Sentinel Connectors Administrative Operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AzureSentinelConnectors_AdministrativeOperations.yaml)
- [Microsoft Sentinel Workbooks Administrative Operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AzureSentinelWorkbooks_AdministrativeOperation.yaml)
- [Port opened for an Azure Resource](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/PortOpenedForAzureResource.yaml)
- [Rare Custom Script Extension](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/Rare_Custom_Script_Extension.yaml)

**In solution [Cloud Service Threat Protection Essentials](../solutions/cloud-service-threat-protection-essentials.md):**
- [Azure Resources Assigned Public IP Addresses](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Service%20Threat%20Protection%20Essentials/Hunting%20Queries/AzureResourceAssignedPublicIP.yaml)

**In solution [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md):**
- [Insider Risk_Possible Sabotage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Hunting%20Queries/InsiderPossibleSabotage.yaml)

### Workbooks (11)

**In solution [Azure Activity](../solutions/azure-activity.md):**
- [AzureActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Workbooks/AzureActivity.json)
- [AzureServiceHealthWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Workbooks/AzureServiceHealthWorkbook.json)

**In solution [AzureSecurityBenchmark](../solutions/azuresecuritybenchmark.md):**
- [AzureSecurityBenchmark](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/Workbooks/AzureSecurityBenchmark.json)

**In solution [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md):**
- [CybersecurityMaturityModelCertification_CMMCV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CybersecurityMaturityModelCertification%28CMMC%292.0/Workbooks/CybersecurityMaturityModelCertification_CMMCV2.json)

**In solution [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md):**
- [Lumen-Threat-Feed-Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Workbooks/Lumen-Threat-Feed-Overview.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md):**
- [InsiderRiskManagement](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Workbooks/InsiderRiskManagement.json)

**In solution [NISTSP80053](../solutions/nistsp80053.md):**
- [NISTSP80053](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Workbooks/NISTSP80053.json)

**In solution [SOX IT Compliance](../solutions/sox-it-compliance.md):**
- [SOXITCompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOX%20IT%20Compliance/Workbooks/SOXITCompliance.json)

**In solution [ThreatAnalysis&Response](../solutions/threatanalysis&response.md):**
- [DynamicThreatModeling&Response](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatAnalysis%26Response/Workbooks/DynamicThreatModeling%26Response.json)

**In solution [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md):**
- [ZeroTrustTIC3](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Workbooks/ZeroTrustTIC3.json)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.aad/domainservices`
- `microsoft.azureadgraph/tenants`
- `microsoft.containerservice/managedclusters`
- `microsoft.apimanagement/service`
- `microsoft.appconfiguration/configurationstores`
- `microsoft.network/applicationgateways`
- `microsoft.servicenetworking/trafficcontrollers`
- `microsoft.web/sites`
- `microsoft.kubernetes/connectedclusters`
- `microsoft.toolchainorchestrator/diagnostics`
- `microsoft.attestation/attestationproviders`
- `microsoft.cache/redis`
- `microsoft.cdn/profiles`
- `microsoft.hardwaresecuritymodules/cloudhsmclusters`
- `microsoft.communication/communicationservices`
- `microsoft.documentdb/databaseaccounts`
- `microsoft.datacollaboration/workspaces`
- `microsoft.digitaltwins/digitaltwinsinstances`
- `microsoft.network/dnsresolverpolicies`
- `microsoft.eventgrid/namespaces`
- `microsoft.eventgrid/topics`
- `microsoft.eventhub/namespaces`
- `microsoft.network/azurefirewalls`
- `microsoft.dashboard/grafana`
- `microsoft.keyvault/vaults`
- `microsoft.loadtestservice/loadtests`
- `microsoft.managednetworkfabric/networkdevices`
- `microsoft.documentdb/cassandraclusters`
- `microsoft.documentdb/mongoclusters`
- `microsoft.networkcloud/baremetalmachines`
- `microsoft.networkcloud/clustermanagers`
- `microsoft.networkcloud/clusters`
- `microsoft.networkcloud/storageappliances`
- `microsoft.network/loadbalancers`
- `microsoft.purview/accounts`
- `microsoft.recoveryservices/vaults`
- `microsoft.relay/namespaces`
- `microsoft.servicebus/namespaces`
- `microsoft.networkfunction/azuretrafficcollectors`
- `microsoft.network/networkmanagers`
- `microsoft.botservice/botservices`
- `microsoft.chaos/experiments`
- `microsoft.cognitiveservices/accounts`
- `microsoft.connectedcache/cachenodes`
- `microsoft.connectedvehicle/platformaccounts`
- `microsoft.network/networkwatchers/connectionmonitors`
- `microsoft.app/managedenvironments`
- `microsoft.d365customerinsights/instances`
- `microsoft.databricks/workspaces`
- `microsoft.dbformysql/flexibleservers`
- `microsoft.dbforpostgresql/flexibleservers`
- `microsoft.devcenter/devcenters`
- `microsoft.devopsinfrastructure/pools`
- `microsoft.durabletask/schedulers`
- `microsoft.experimentation/experimentworkspaces`
- `microsoft.hdinsight/clusters`
- `microsoft.compute/virtualmachines`
- `microsoft.logic/integrationaccounts`
- `microsoft.machinelearningservices/workspaces`
- `microsoft.machinelearningservices/registries`
- `microsoft.media/mediaservices`
- `microsoft.azureplaywrightservice/accounts`
- `microsoft.graph/tenants`
- `microsoft.networkanalytics/dataproducts`
- `microsoft.onlineexperimentation/workspaces`
- `microsoft.storage/storageaccounts`
- `microsoft.storagecache/amlfilesytems`
- `microsoft.storagemover/storagemovers`
- `microsoft.synapse/workspaces`
- `microsoft.edge/diagnostics`
- `microsoft.desktopvirtualization/hostpools`
- `default`
- `subscription`
- `resourcegroup`
- `microsoft.signalrservice/webpubsub`
- `microsoft.insights/components`
- `microsoft.desktopvirtualization/applicationgroups`
- `microsoft.desktopvirtualization/workspaces`
- `microsoft.timeseriesinsights/environments`
- `microsoft.workloadmonitor/monitors`
- `microsoft.analysisservices/servers`
- `microsoft.batch/batchaccounts`
- `microsoft.appplatform/spring`
- `microsoft.signalrservice/signalr`
- `microsoft.containerregistry/registries`
- `microsoft.kusto/clusters`
- `microsoft.blockchain/blockchainmembers`
- `microsoft.eventgrid/domains`
- `microsoft.eventgrid/partnernamespaces`
- `microsoft.eventgrid/partnertopics`
- `microsoft.eventgrid/systemtopics`
- `microsoft.conenctedvmwarevsphere/virtualmachines`
- `microsoft.azurestackhci/virtualmachines`
- `microsoft.scvmm/virtualmachines`
- `microsoft.compute/virtualmachinescalesets`
- `microsoft.hybridcontainerservice/provisionedclusters`
- `microsoft.insights/autoscalesettings`
- `microsoft.devices/iothubs`
- `microsoft.servicefabric/clusters`
- `microsoft.logic/workflows`
- `microsoft.automation/automationaccounts`
- `microsoft.datafactory/factories`
- `microsoft.datalakestore/accounts`
- `microsoft.datalakeanalytics/accounts`
- `microsoft.powerbidedicated/capacities`
- `microsoft.datashare/accounts`
- `microsoft.sql/managedinstances`
- `microsoft.sql/servers`
- `microsoft.sql/servers/databases`
- `microsoft.dbformysql/servers`
- `microsoft.dbforpostgresql/servers`
- `microsoft.dbforpostgresql/serversv2`
- `microsoft.dbformariadb/servers`
- `microsoft.devices/provisioningservices`
- `microsoft.network/expressroutecircuits`
- `microsoft.network/frontdoors`
- `microsoft.network/networkinterfaces`
- `microsoft.network/networksecuritygroups`
- `microsoft.network/publicipaddresses`
- `microsoft.network/trafficmanagerprofiles`
- `microsoft.network/virtualnetworkgateways`
- `microsoft.network/vpngateways`
- `microsoft.network/virtualnetworks`
- `microsoft.search/searchservices`
- `microsoft.streamanalytics/streamingjobs`
- `microsoft.network/bastionhosts`
- `microsoft.healthcareapis/services`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
