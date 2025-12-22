# AzureActivity

Reference for AzureActivity table in Azure Monitor Logs.

| | |
|----------|-------|
| **Table Name** | `AzureActivity` |
| **Category** | Audit |
| **Solutions Using Table** | 1 |
| **Connectors Ingesting** | 1 |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✗ No |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/azureactivity) |

⚠️ **Note:** This table name is unique to specific connectors.

---

## Solutions (1)

This table is used by the following solutions:

- [Azure Activity](../solutions/azure-activity.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Azure Activity](../connectors/azureactivity.md)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.aad/domainservices`
- `<br>microsoft.azureadgraph/tenants`
- `<br>microsoft.containerservice/managedclusters`
- `<br>microsoft.apimanagement/service`
- `<br>microsoft.appconfiguration/configurationstores`
- `<br>microsoft.network/applicationgateways`
- `<br>microsoft.servicenetworking/trafficcontrollers`
- `<br>microsoft.web/sites`
- `<br>microsoft.kubernetes/connectedclusters`
- `<br>microsoft.toolchainorchestrator/diagnostics`
- `<br>microsoft.attestation/attestationproviders`
- `<br>microsoft.cache/redis`
- `<br>microsoft.cdn/profiles`
- `<br>microsoft.hardwaresecuritymodules/cloudhsmclusters`
- `<br>microsoft.communication/communicationservices`
- `<br>microsoft.documentdb/databaseaccounts`
- `<br>microsoft.datacollaboration/workspaces`
- `<br>microsoft.digitaltwins/digitaltwinsinstances`
- `<br>microsoft.network/dnsresolverpolicies`
- `<br>microsoft.eventgrid/namespaces`
- `<br>microsoft.eventgrid/topics`
- `<br>microsoft.eventhub/namespaces`
- `<br>microsoft.network/azurefirewalls`
- `<br>microsoft.dashboard/grafana`
- `<br>microsoft.keyvault/vaults`
- `<br>microsoft.loadtestservice/loadtests`
- `<br>microsoft.managednetworkfabric/networkdevices`
- `<br>microsoft.documentdb/cassandraclusters`
- `<br>microsoft.documentdb/mongoclusters`
- `<br>microsoft.networkcloud/baremetalmachines`
- `<br>microsoft.networkcloud/clustermanagers`
- `<br>microsoft.networkcloud/clusters`
- `<br>microsoft.networkcloud/storageappliances`
- `<br>microsoft.network/loadbalancers`
- `<br>microsoft.purview/accounts`
- `<br>microsoft.recoveryservices/vaults`
- `<br>microsoft.relay/namespaces`
- `<br>microsoft.servicebus/namespaces`
- `<br>microsoft.networkfunction/azuretrafficcollectors`
- `<br>microsoft.network/networkmanagers`
- `<br>microsoft.botservice/botservices`
- `<br>microsoft.chaos/experiments`
- `<br>microsoft.cognitiveservices/accounts`
- `<br>microsoft.connectedcache/cachenodes`
- `<br>microsoft.connectedvehicle/platformaccounts`
- `<br>microsoft.network/networkwatchers/connectionmonitors`
- `<br>microsoft.app/managedenvironments`
- `<br>microsoft.d365customerinsights/instances`
- `<br>microsoft.databricks/workspaces`
- `<br>microsoft.dbformysql/flexibleservers`
- `<br>microsoft.dbforpostgresql/flexibleservers`
- `<br>microsoft.devcenter/devcenters`
- `<br>microsoft.devopsinfrastructure/pools`
- `<br>microsoft.durabletask/schedulers`
- `<br>microsoft.experimentation/experimentworkspaces`
- `<br>microsoft.hdinsight/clusters`
- `<br>microsoft.compute/virtualmachines`
- `<br>microsoft.logic/integrationaccounts`
- `<br>microsoft.machinelearningservices/workspaces`
- `<br>microsoft.machinelearningservices/registries`
- `<br>microsoft.media/mediaservices`
- `<br>microsoft.azureplaywrightservice/accounts`
- `<br>microsoft.graph/tenants`
- `<br>microsoft.networkanalytics/dataproducts`
- `<br>microsoft.onlineexperimentation/workspaces`
- `<br>microsoft.storage/storageaccounts`
- `<br>microsoft.storagecache/amlfilesytems`
- `<br>microsoft.storagemover/storagemovers`
- `<br>microsoft.synapse/workspaces`
- `<br>microsoft.edge/diagnostics`
- `<br>microsoft.desktopvirtualization/hostpools`
- `<br>default`
- `<br>subscription`
- `<br>resourcegroup`
- `<br>microsoft.signalrservice/webpubsub`
- `<br>microsoft.insights/components`
- `<br>microsoft.desktopvirtualization/applicationgroups`
- `<br>microsoft.desktopvirtualization/workspaces`
- `<br>microsoft.timeseriesinsights/environments`
- `<br>microsoft.workloadmonitor/monitors`
- `<br>microsoft.analysisservices/servers`
- `<br>microsoft.batch/batchaccounts`
- `<br>microsoft.appplatform/spring`
- `<br>microsoft.signalrservice/signalr`
- `<br>microsoft.containerregistry/registries`
- `<br>microsoft.kusto/clusters`
- `<br>microsoft.blockchain/blockchainmembers`
- `<br>microsoft.eventgrid/domains`
- `<br>microsoft.eventgrid/partnernamespaces`
- `<br>microsoft.eventgrid/partnertopics`
- `<br>microsoft.eventgrid/systemtopics`
- `<br>microsoft.conenctedvmwarevsphere/virtualmachines`
- `<br>microsoft.azurestackhci/virtualmachines`
- `<br>microsoft.scvmm/virtualmachines`
- `<br>microsoft.compute/virtualmachinescalesets`
- `<br>microsoft.hybridcontainerservice/provisionedclusters`
- `<br>microsoft.insights/autoscalesettings`
- `<br>microsoft.devices/iothubs`
- `<br>microsoft.servicefabric/clusters`
- `<br>microsoft.logic/workflows`
- `<br>microsoft.automation/automationaccounts`
- `<br>microsoft.datafactory/factories`
- `<br>microsoft.datalakestore/accounts`
- `<br>microsoft.datalakeanalytics/accounts`
- `<br>microsoft.powerbidedicated/capacities`
- `<br>microsoft.datashare/accounts`
- `<br>microsoft.sql/managedinstances`
- `<br>microsoft.sql/servers`
- `<br>microsoft.sql/servers/databases`
- `<br>microsoft.dbformysql/servers`
- `<br>microsoft.dbforpostgresql/servers`
- `<br>microsoft.dbforpostgresql/serversv2`
- `<br>microsoft.dbformariadb/servers`
- `<br>microsoft.devices/provisioningservices`
- `<br>microsoft.network/expressroutecircuits`
- `<br>microsoft.network/frontdoors`
- `<br>microsoft.network/networkinterfaces`
- `<br>microsoft.network/networksecuritygroups`
- `<br>microsoft.network/publicipaddresses`
- `<br>microsoft.network/trafficmanagerprofiles`
- `<br>microsoft.network/virtualnetworkgateways`
- `<br>microsoft.network/vpngateways`
- `<br>microsoft.network/virtualnetworks`
- `<br>microsoft.search/searchservices`
- `<br>microsoft.streamanalytics/streamingjobs`
- `<br>microsoft.network/bastionhosts`
- `<br>microsoft.healthcareapis/services`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
