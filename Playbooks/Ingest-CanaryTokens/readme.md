# Ingest-CanaryTokens
author: Nathan Swift

This Logic App connector will act as a Webhook listener, CanaryTokens can then send data upon an incident when the Canarytoken has been opened. This will send the data to Azure Sentinel - CanaryTokens_CL  

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIngest-CanaryTokens%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIngest-CanaryTokens%2Fazuredeploy.json)

**HowTo Use**

Canary Tokens are digital artifacts that are a tripwire othat exposes a potential attacker. You can leave them in your network and file shares and in other places in your enviroment. Generate and sprinkle them throughout, be sure to use enticing names like Finance Report or Customer Accounts. The goal is to make it look worthwhile to exploit and data exfiltrate. Upon execution of the Canarytoken like a MS Word Document a HTTP GET call is made to CanaryTokens.org which in turn can send an email and send data to a Webhook. In this case we want the data also enriched and sent to Azure Sentinel notifying us that a potential attacker had opened the Canarytoken to kick of an investiagetion and case using Azure Sentinel to help dive deeper into the logs.

When setting up [CanaryTokens Here](https://www.canarytokens.org/generate "CanaryTokens Here") here you will see the field "provide an email address and/or webhook URL", be sure to place your email address seperated by a SPACE with a copy of the complete HTTP Listener URL into the this field.

Example someone@someorg.com https://prod-79.eastus.logic.azure.com:443/workflows/579fb7927ab64ce7b4d34a4c85c65003/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=PsKBVi7LZgQ4y1ih59L5RWNpKzRd7hpkp9YiyH_WV4K


Implementation and testing details on How to use can be found [Here](https://techcommunity.microsoft.com/t5/azure-sentinel/how-to-setup-a-canarytoken-and-receive-incident-alerts-on-azure/ba-p/1964076 "Here")

[Information on Canary Tokens](https://docs.canarytokens.org/guide/ "Information on Canary Tokens")

For further reading on HoneyPots and HoneyTokens I recommend Chris Sander's book [Intrusion Detection Honeypots](https://chrissanders.org/2020/09/idh-release/ "Intrusion Detection Honeypots")

**An example of a Scheduled Query Rule for Azure Sentinel:**

```id: 27dda424-1dbe-4236-9dd5-c484b23111a5
name: Canarytoken Triggered
description: |
  'A Canarytoken has been triggered in your enviroment, this may be an early sign of attacker intent and activity, 
    please follow up with Azure Sentinel logs and incidents accordingly along with the Server this Canarytoken was hosted on.
    Reference: https://blog.thinkst.com/p/canarytokensorg-quick-free-detection.html'
severity: High
requiredDataConnectors:
  - connectorId: Custom
    dataTypes:
      - CanaryTokens_CL
queryFrequency: 15m
queryPeriod: 15m
triggerOperator: gt
triggerThreshold: 0
tactics:
  - Discovery
  - Collection
  - Exfiltration
relevantTechniques:
query: |
CanaryTokens_CL
| extend Canarydata = parse_csv(memo_s)
| extend CanaryHost = tostring(Canarydata[0]), CanaryPublicIP = tostring(Canarydata[1]), CanaryPrivateIP = tostring(Canarydata[2]), CanaryShare = tostring(Canarydata[3]), CanaryDescription = tostring(Canarydata[4])
| extend CanaryExcutedonHost = iif(CanaryPublicIP == src_ip_s, true, false)
| extend timestamp = TimeGenerated, IPCustomEntity = src_ip_s //,AccountCustomEntity = user_s, HostCustomEntity = computer_s
entityMappings:
  - entityType: IP
    fieldMappings:
      - identifier: Address
        columnName: IPCustomEntity


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