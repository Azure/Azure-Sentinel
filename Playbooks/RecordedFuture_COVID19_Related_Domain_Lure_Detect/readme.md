# RecordedFuture - COVID19 Related Domain Lure Detection
author: Adrian Porcescu, Recorded Future

These playbook leverage the Recorded Future API to automate the import of the Recorded Future [Recent COVID-19-Related Domain Lure: Malicious](https://support.recordedfuture.com/hc/en-us/articles/115003793388-Domain-Risk-Rules) Risklist, as tiIndicators, into the ThreatIntelligenceIndicator table, for detection (alerting) purposes in Azure Sentinel.  For additional information please visit [Recorded Future](https://www.recordedfuture.com/integrations/azure/).

Note: Due to internal Microsoft Logic Apps dependencies, please deploy first the ImportToSentinel playbook before the IndicatorProcessor one.

Links to deploy the RecordedFuture_COVID19_Related_Domain_Lure_ImportToSentinel playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_COVID19_Related_Domain_Lure_Detect%2FRecordedFuture_COVID19_Related_Domain_Lure_ImportToSentinel.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_COVID19_Related_Domain_Lure_Detect%2FRecordedFuture_COVID19_Related_Domain_Lure_ImportToSentinel.json)

Links to deploy the RecordedFuture_COVID19_Related_Domain_Lure_IndicatorProcessor playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_COVID19_Related_Domain_Lure_Detect%2FRecordedFuture_COVID19_Related_Domain_Lure_IndicatorProcessor.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_COVID19_Related_Domain_Lure_Detect%2FRecordedFuture_COVID19_Related_Domain_Lure_IndicatorProcessor.json)