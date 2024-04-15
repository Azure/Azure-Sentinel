Microsoft released threat indicators related to Covid19 as described at https://www.microsoft.com/security/blog/2020/05/14/open-sourcing-covid-threat-intelligence/

These playbooks automate the ingest of these threat indicators into the ThreatIntelligenceIndicator table of an Azure Sentinel workspace. Detailed instructions for deploying these workbooks can be found at https://aka.ms/sentinelc19blog
**Note**: You must deploy the **C19ImportToSentinel** playbook before deploying the **C19IndicatorProcessor** playbook. You must also make sure the Playbook2Name parameter uses the exact name you chose when importing the **C19ImportToSentinel** playbook.

![parameters](./playbookparameter.png)

Here is the order of deployment:

1. Deploy the C19ImportToSentinel playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-Microsoft-Covid19-Indicators%2FC19ImportToSentinel.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-Microsoft-Covid19-Indicators%2FC19ImportToSentinel.json)

2. Deploy the C19IndicatorProcessor playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-Microsoft-Covid19-Indicators%2FC19IndicatorProcessor.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-Microsoft-Covid19-Indicators%2FC19IndicatorProcessor.json)
