# Ingest-CanaryTokens
author: Nathan Swift

This Logic App connector will act as a Webhook listener, CanaryTokens can then send data upon an incident when the Canarytoken has been opened. This will send the data to Azure Sentinel - CanaryTokens_CL  

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIngest-CanaryTokens%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIngest-CanaryTokens%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

**HowTo Use**

Canary Tokens are digital artifacts that are a tripwire othat exposes a potential attacker. You can leave them in your network and file shares and in other places in your enviroment. Genrate and sprinkle them throughout, be sure to use enticing names like Finance Report or Customer Accounts. The goal is to make it look worthwhile to exploit and data exfiltrate. Upon execution of the Canarytoken like a MS Word Document a HTTP GET call is made to CanaryTokens.org which in turn can send an email and send data to a Webhook. In this case we want the data also enriched and sent to Azure Sentinel notifying us that a potential attacker had opened the Canarytoken to kick of an investiagetion and case using Azure Sentinel to help dive deeper into the logs.

When setting up [CanaryTokens Here](https://www.canarytokens.org/generate "CanaryTokens Here") here you will see the field "provide an email address and/or webhook URL", be sure to place your email address seperated by a SPACE with a copy of the complete HTTP Listener URL into the this field.

Example someone@someorg.com https://prod-79.eastus.logic.azure.com:443/workflows/579fb7927ab64ce7b4d34a4c85c65003/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=PsKBVi7LZgQ4y1ih59L5RWNpKzRd7hpkp9YiyH_WV4K


Implementation and testing details on How to use can be found [Here](https:// "Here")

[Information on Canary Tokens](https://docs.canarytokens.org/guide/ "Information on Canary Tokens")

For further reading on HoneyPots and HoneyTokens I recommend Chris Sander's book [Intrusion Detection Honeypots](https://chrissanders.org/2020/09/idh-release/ "Intrusion Detection Honeypots")

The following Canarytokens have been tested:

*Microsoft Word Document*

*Web bug / URL token*

*DNS token*

*Unique email Address*

*Custom Image Web bug*

*Acrobat Reader PDF Document*

*Custom exe / binary*

*Cloned Website*

*Slow Redirect*

more to be tested...