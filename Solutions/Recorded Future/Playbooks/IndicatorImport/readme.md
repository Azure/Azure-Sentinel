# Recorded Future Indicator/Risk List playbooks

More information about Recorded Future Intelligence Solution for Microsoft Sentinel can be found in the main [readme](../readme.md).

All **IndicatorImport** playbooks have the RecordedFuture-ThreatIntelligenceImport as a prerequisite. So always setup the RecordedFuture-ThreatIntelligenceImport first as part och the solution installation or as a single playbook installation below.  

## RecordedFuture-ThreatIntelligenceImport
Type: Detection\
Included in Recorded Future Intelligence Solution: Yes\
Requires **/recordedfuturev2** API keys as described in the [Connector authorization](../readme.md#connectors-authorization) section. 

The parameter WorkspaceID can be found in Azure portal in the overview page of the Log Analytics Workspace. 

Retrieves Indicators Of Compromise (IoCs) from one of the indicator import logic apps, and store them in the ThreatIntelligenceIndicator table. All IndicatorImport playbooks use this playbook for batching. 

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-ThreatIntelligenceImport%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-ThreatIntelligenceImport%2Fazuredeploy.json)

## RecordedFuture-Domain-IndicatorImport
Type: Detection\
Included in Recorded Future Intelligence Solution: Yes\
Requires **/recordedfuturev2** API keys as described in the [Connector authorization](../readme.md##connectors-authorization) section. 

Retrieves the [Microsoft Sentinel Domain Default Risk List ](https://support.recordedfuture.com/hc/en-us/articles/115003793388-Domain-Risk-Rules) (requires login), Domain IOC with risk greater than 65 and adds the IOCs to the ThreatIntelligenceIndicator table.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FDomain-IndicatorImport%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FDomain-IndicatorImport%2Fazuredeploy.json)


## RecordedFuture-Hash-IndicatorImport
Type: Detection\
Included in Recorded Future Intelligence Solution: Yes\
Requires **/recordedfuturev2** API keys as described in the [Connector authorization](../readme.md##connectors-authorization) section. 

Retrieves the [Microsoft Sentinel Hash Observed in Underground Testing Risk List ](https://support.recordedfuture.com/hc/en-us/articles/115000846167-Hash-Risk-Rules) (requires login), Hashes based on the observedMalwareTesting Risk Rule and adds the IOCs to the ThreatIntelligenceIndicator table.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-Hash-IndicatorImport%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-Hash-IndicatorImport%2Fazuredeploy.json)

## RecordedFuture-IP-IndicatorImport
Type: Detection\
Included in Recorded Future Intelligence Solution: Yes\
Requires **/recordedfuturev2** API keys as described in the [Connector authorization](../readme.md##connectors-authorization) section. 

Retrieves the [Actively Communicating Validated C&C Server Risk List ](https://support.recordedfuture.com/hc/en-us/articles/115000894448-IP-Address-Risk-Rules) (requires login), Observing C2 communications with infected machines or adversary control by Recorded Future Network Traffic Analysis.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-IP-IndicatorImport%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-IP-IndicatorImport%2Fazuredeploy.json)

## RecordedFuture-URL-IndicatorImport
Type: Detection\
Included in Recorded Future Intelligence Solution: Yes\
Requires **/recordedfuturev2** API keys as described in the [Connector authorization](../readme.md##connectors-authorization) section. 

Retrieves the [Microsoft Sentinel URL Recently Reported by Insikt Group Risk List ](https://support.recordedfuture.com/hc/en-us/articles/115000894448-IP-Address-Risk-Rules) (requires login), URLs based on the Recently Reported by Insikt Group rule and adds the IOCs to the ThreatIntelligenceIndicator table.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-URL-IndicatorImport%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-URL-IndicatorImport%2Fazuredeploy.json)
