# RecordedFuture - IP - Actively Communicating C&C Server
author: Adrian Porcescu, Recorded Future

These playbooks leverage the Recorded Future API to automate the ingestion of Recorded Future [Actively Communicating C&C Server IP RiskList](https://support.recordedfuture.com/hc/en-us/articles/115000894448-IP-Address-Risk-Rules), into the ThreatIntelligenceIndicator table, for detection (alert) actions in Microsoft Azure Sentinel. For additional information please visit [Recorded Future](https://www.recordedfuture.com/integrations/azure/).

Note: Due to internal Microsoft Logic Apps dependencies, please deploy first the ImportToSentinel playbook before the IndicatorProcessor one.


Links to deploy the RecordedFuture_IP_ActCommC2C_IndicatorProcessor playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_IP_ActCommC2C%2FRecordedFuture_IP_ActCommC2C_IndicatorProcessor.json)_
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_IP_ActCommC2C%2FRecordedFuture_IP_ActCommC2C_IndicatorProcessor.json)

Links to deploy the RecordedFuture_IP_ActCommC2C_ImportToSentinel playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_IP_ActCommC2C%2FRecordedFuture_IP_ActCommC2C_ImportToSentinel.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_IP_ActCommC2C%2FRecordedFuture_IP_ActCommC2C_ImportToSentinel.json)