# Get-TenableVulns
author: Rich Lilly with credit to Younes Khaldi https://techcommunity.microsoft.com/t5/azure-sentinel/how-to-integrate-vulnerability-management-in-azure-sentinel/ba-p/1635728

This playbook will get vulnerability data from the Tenable.io Cloud API. You must first create and retrieve an API key in the Tenable.io portal before you deploy this LogicApp. It must be in the format 'accessKey=xxxxxx;secretKey=xxxxxx'

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Frichlilly2004%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-TenableVulns%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Frichlilly2004%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-TenableVulns%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>