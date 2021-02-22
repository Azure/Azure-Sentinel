# HaveIBeenPwned-Email

This Playbook for Azure Sentinel uses the API for haveibeenpwned.com and checks to see if an email address entity in an Incident has been compromised online and returns a quick note to the Comments tab in the Incident as to whether or not the email address (or addresses) has been compromised.

The HaveIBeenPwned API is not free. There’s a nominal $3.50 per month recurring fee to continue using it, but you can also just pay for a single month to determine if it’s valuable enough to continue using it. The single month usage is also a handy option if your organization has recently been breached and you need to determine which accounts are compromised. To get the API key, go here: https://haveibeenpwned.com/API/Key

See <a href="https://secureinfra.blog/2020/08/24/how-to-query-haveibeenpwned-using-an-azure-sentinel-playbook/" target="_blank">How to Query HaveIBeenPwned Using an Azure Sentinel Playbook</a> for more information.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FHaveIBeenPwned-Email%2Fazuredeploy.json)
[![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FHaveIBeenPwned-Email%2Fazuredeploy.json)
