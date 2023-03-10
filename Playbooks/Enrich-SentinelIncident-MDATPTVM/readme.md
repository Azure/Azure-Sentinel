# Enrich-SentinelIncident-MDATPTVM
author: Yaniv Shasha

This playbook will enrich the Client machine that is part of sentinel incident with thread vulnerabilities data (TVM) with CVE that their score is grater then 7.5.
Also it automatically add this information to the incident as comments and change the incident severity to High.
<br>
This logic app use Oauth2 to authenticate against MDATP API. [Learn more about authenticating with Oauth2 in Logic Apps](https://docs.microsoft.com/windows/security/threat-protection/microsoft-defender-atp/apis-intro)

## Prerequisite:

* Create AAD app and give the Permissions based on [this article](
https://docs.microsoft.com/windows/security/threat-protection/microsoft-defender-atp/get-all-vulnerabilities#permissions)

## Deploy to Azure
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FEnrich-SentinelIncident-MDATPTVM%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FEnrich-SentinelIncident-MDATPTVM%2Fazuredeploy.json)


