# Recorded Future Indicator/Risk List playbooks

More information about Recorded Future Intelligence Solution for Microsoft Sentinel can be found in the main [readme](../readme.md).

All **IndicatorImport** playbooks have the RecordedFuture-ThreatIntelligenceImport as a prerequisite. So always setup the RecordedFuture-ThreatIntelligenceImport first as part och the solution installation or as a single playbook installation below.  

> [!IMPORTANT] 
> **Due to internal dependencies, always deploy and activate the ThreatIntelligenceImport playbook before any of the \*-IndicatorImport playbooks.**

## Risk list size limitations
The size and number of indicators imported is limited by logic apps file size and number of items. <a href="https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-limits-and-config?tabs=consumption%2Cazure-portal" target="_blank">Read more here</a>

## RecordedFuture-ThreatIntelligenceImport
Type: **Detection**\
Included in Recorded Future Intelligence Solution: **Yes**\
Requires authorization of **/azuresentinel** connector - <a href="https://learn.microsoft.com/en-us/connectors/azuresentinel/" target="_blank">Documentation on Microsoft power platform connectors</a>
 \
Connectors used: ***azuresentinel*** see [Connector authorization](../readme.md#connectors-authorization) for guidance.

The parameter WorkspaceID can be found in Azure portal in the overview page of the Log Analytics Workspace. 

Retrieves Indicators Of Compromise (IoCs) from one of the indicator import logic apps, and store them in the ThreatIntelligenceIndicator table. All IndicatorImport playbooks use this playbook for batching.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-ThreatIntelligenceImport%2Fazuredeploy.json" target="_blank">![Deploy to Azure](https://aka.ms/deploytoazurebutton)</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-ThreatIntelligenceImport%2Fazuredeploy.json" target="_blank">![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)</a>


## RecordedFuture-Domain-IndicatorImport
Type: **Detection**\
Included in Recorded Future Intelligence Solution: **Yes**\
Requires **/recordedfuturev2** API keys as described in the [Connector authorization](../readme.md##connectors-authorization) section. \
Connectors used: ***recordedfuturev2*** see [Connector authorization](../readme.md#connectors-authorization) for guidance. 

Retrieves the <a href="https://support.recordedfuture.com/hc/en-us/articles/115003793388-Domain-Risk-Rules" target="_blank">Microsoft Sentinel Domain Default Risk List </a> (requires Recorded Future login), Domain IOC with risk greater than 65 and adds the IOCs to the ThreatIntelligenceIndicator table.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-Domain-IndicatorImport%2Fazuredeploy.json" target="_blank">![Deploy to Azure](https://aka.ms/deploytoazurebutton)</a>
<a href="https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-Domain-IndicatorImport%2Fazuredeploy.json" target="_blank">![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)</a>


## RecordedFuture-Hash-IndicatorImport
Type: **Detection**\
Included in Recorded Future Intelligence Solution: **Yes**\
Requires **/recordedfuturev2** API keys as described in the [Connector authorization](../readme.md##connectors-authorization) section.  \
Connectors used: ***recordedfuturev2*** see [Connector authorization](../readme.md#connectors-authorization) for guidance.

Retrieves the <a href="https://support.recordedfuture.com/hc/en-us/articles/115000846167-Hash-Risk-Rules" target="_blank">Microsoft Sentinel Hash Observed in Underground Testing Risk List </a> (requires Recorded Future login), Hashes based on the observedMalwareTesting Risk Rule and adds the IOCs to the ThreatIntelligenceIndicator table.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-Hash-IndicatorImport%2Fazuredeploy.json" target="_blank">![Deploy to Azure](https://aka.ms/deploytoazurebutton)</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-Hash-IndicatorImport%2Fazuredeploy.json" target="_blank">![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)</a>

## RecordedFuture-IP-IndicatorImport
Type: **Detection**\
Included in Recorded Future Intelligence Solution: **Yes**\
Requires **/recordedfuturev2** API keys as described in the [Connector authorization](../readme.md##connectors-authorization) section.  \
Connectors used: ***recordedfuturev2*** see [Connector authorization](../readme.md#connectors-authorization) for guidance.

Retrieves the <a href="https://support.recordedfuture.com/hc/en-us/articles/115000894448-IP-Address-Risk-Rules" target="_blank">Actively Communicating Validated C&C Server Risk List </a> (requires Recorded Future login), Observing C2 communications with infected machines or adversary control by Recorded Future Network Traffic Analysis.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-IP-IndicatorImport%2Fazuredeploy.json" target="_blank">![Deploy to Azure](https://aka.ms/deploytoazurebutton)</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-IP-IndicatorImport%2Fazuredeploy.json" target="_blank">![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)</a>

## RecordedFuture-URL-IndicatorImport
Type: **Detection**\
Included in Recorded Future Intelligence Solution: **Yes**\
Requires **/recordedfuturev2** API keys as described in the [Connector authorization](../readme.md##connectors-authorization) section.  \
Connectors used: ***recordedfuturev2***, see [Connector authorization](../readme.md#connectors-authorization) for guidance.

Retrieves the <a href="https://support.recordedfuture.com/hc/en-us/articles/115000894448-IP-Address-Risk-Rules" traget="_blank">Microsoft Sentinel URL Recently Reported by Insikt Group Risk List </a> (requires Recorded Future login), URLs based on the Recently Reported by Insikt Group rule and adds the IOCs to the ThreatIntelligenceIndicator table.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-URL-IndicatorImport%2Fazuredeploy.json" target="_blank">![Deploy to Azure](https://aka.ms/deploytoazurebutton)</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%2520Future%2FPlaybooks%2FIndicatorImport%2FRecordedFuture-URL-IndicatorImport%2Fazuredeploy.json" target="_blank">![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)</a>

# Configuration 
## Risk list activation and configuration 
Verify that the **ThreatIntelligenceImport** logic app is installed and active in your environment before installing the TIProcessing risk lists.

From ```Automation -> Playbook Template```  Select any Recorded Future playbook that ends with IndicatorImport, like **RecordedFuture-IP-IndicatorImport**, press create playbook.
Note that it is possible to deploy several instances of the same template by giving them unique names. This is how you can pull several risk lists of the same type.

![](../Images/2023-04-19-16-49-53.png)

The parameter **PlaybookNameBatching** is the name of the ThreatIntelligenceImport playbook that will handle batch processing of indicators into Microsoft Sentinel. In the last step press **Create and continue to designer**.

![](../Images/2023-04-19-16-51-12.png)

In the designer, locate all steps that show a warning and authenticate these steps. Authentication looks different for each connection. More information on this can be found in the chapter above called Connector Authorization. [More information about playbook authentication](https://learn.microsoft.com/en-us/azure/sentinel/authenticate-playbooks-to-sentinel).

<img src="../Images/2023-04-18-14-39-40.png" width="500" />

## Change Risk List 
To can change Risk List to pull in to your environment. This can be done in the default playbook or you can install several instances of one playbook. 
Example: You would like to use both ```Actively Communicating Validated C&C Server``` and ```Recent Phishing Host``` IP Risk Lists. 
Select the **RecordedFuture-IP-IndicatorImport** template from ```Automation -> Playbook``` twice and save with different names like ```Recorded Future - Actively Communicating Validated C&C Server - IndicatorImport``` and ```Recorded Future - Phishing Host - IndicatorImport```. 

Change the Risk List to download and modify the description in the ```RecordedFuture-Threatlntelligencelmport``` step in the logic app. 
![](../Images/2023-09-08-12-01-37.png)

## Configure Cadence of Risk List Ingestion 
Its possible to adjust the cadence of Risk List download to reduce traffic and cost. Recorded Future have the following recommendations [Risk-List-Download-Recommendations](https://support.recordedfuture.com/hc/en-us/articles/115010401968-Risk-List-Download-Recommendations) (requires Recorded Future login).

The first step of IndicatorImport Playbooks is a recurrence step, adjust the cadence by modifying the interval and frequency parameters.\
<img src="../Images/2023-12-12-10-00-53.png" width="1000">

It is critical that you also adjust the expirationDateTime parameter in the final block of that logic app to be synchronized with the recurrence timing. Failure to do so can result in either:
* Duplication of indicators.
* Having no active Recorded Future indicators the majority of the time. 

If you are unsure of how to do this, please consult Recorded Future.

![](../Images/2023-12-12-10-02-11.png)

## Verify deployment
After successfully running indicator import, there should exist data in  the ThreatIntelligenceIndicator table.
![](../Images/2023-04-18-16-39-00.png)


