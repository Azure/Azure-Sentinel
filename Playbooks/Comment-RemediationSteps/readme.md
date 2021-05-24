# Comment-RemediationSteps
authors: Jordan Ross and Nicholas DiCola

This playbook will provide analysts with guidance to properly respond to an incident. This will add a comment to a Sentinel Incident with the remediation steps for alerts related to Microsoft Defender for Endpoint and Azure Security Center / Azure Defender. With these steps users will be able to respond to threats and prevent similar suspicious activity from occurring in the future. 

**NOTE:  This playbook requires the enablement of at least one of the following data connections: Microsoft Defender for Endpoint or Azure Defender. This playbook uses a managed identity to access the API.  You will need to add the playbook to the subscriptions or management group with Security Reader Role**

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FComment-RemediationSteps%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FComment-RemediationSteps%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>
