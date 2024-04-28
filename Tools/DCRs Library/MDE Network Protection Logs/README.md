# Data Collection Rule for MDE Network protection events

[![Deploy To Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg?sanitize=true)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FTools%2FDCRs%2520Library%2FMDE%2520Network%2520Protection%2520Logs%2Fazuredeploy.json)

This template creates a data collection rule defining the data source (WindowsEvents) and the destination workspace. The rule will collect Windows Defender Events around Network Protections. EventIDs 5007 - config change, 1125 - network connection audited, 1126 - network connection blocked.

## Prerequisites

A log analytics workspace resource created. The resource ID will be the input of the deployment.

## Notes

For more information on **data collection rules**, please visit:

- [Data Collection Rules overview](https://docs.microsoft.com/azure/azure-monitor/agents/data-collection-rule-overview)
- [Data Collection Rule Associations](https://docs.microsoft.com/azure/azure-monitor/agents/data-collection-rule-azure-monitor-agent)
- [Azure Monitor agent overview](https://docs.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-overview)
- [Install Azure Monitor agent](https://docs.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-install)

`Tags: DCR, DCRA, Monitor, data collection, data collection rule, azure monitor, MDE, Network Protection`
