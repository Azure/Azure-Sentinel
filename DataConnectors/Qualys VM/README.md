# Qualys Host Detections
Author: Microsoft

This function app will poll the Qualys Vulnerability Detection API for any new detection every five (5) minutes and then send them to Azure Log Analytics (ALA) via the API.
To deploy this function app you will need the ALA workspace ID, Primary Key, the Qulays username and password that has access to the Qualys API. 
The last part is the url for the Qualys region that your Qualys platform reports to. This can be found in your Qualys platform system setting or by contacting your Account Manager. Detail about the API and the regions can be found the link below.

https://www.qualys.com/docs/qualys-api-vmpc-user-guide.pdf

## To deploy, click on the link below.
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw%2Egithubusercontent%2Ecom%2FAzure%2FAzure%2DSentinel%2Fmaster%2FDataConnectors%2FQualys%2520VM%2Fazuredeploy%5FQualysVM%5FAPI%5FFunctionApp%2Ejson" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw%2Egithubusercontent%2Ecom%2FAzure%2FAzure%2DSentinel%2Fmaster%2FDataConnectors%2FQualys%2520VM%2Fazuredeploy%5FQualysVM%5FAPI%5FFunctionApp%2Ejson" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>
