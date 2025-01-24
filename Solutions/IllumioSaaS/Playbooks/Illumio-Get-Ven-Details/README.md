# Microsoft Sentinel Playbooks for Illumio Integration

Playbooks are collections of procedures that can be run from Microsoft Sentinel.  

---

## Get VEN Details Playbook

This playbook can be configured to respond to Microsoft Sentinel alerts.

1. Once an alert is triggered, its body is sent to a function app.
2. The function talks to the PCE with the help of api key/secret.
3. Once VEN details are fetched from PCE, then the playbook constructs a table with the relevant information.
4. Table comprises of, alert title, severity, ven details like ip address, hostname and labels and alert description.
5. This is sent out as an email.

# To deploy, follow the below link 
Deploy the function app first:
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FIllumioSaaS%2FPlaybooks%2FCustomConnector%2FIllumioSaaS_FunctionAppConnector%2Fazuredeploy.json)


Deploy logic app next:
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FIllumioSaaS%2FPlaybooks%2FIllumio-Get-Ven-Details%2Fazuredeploy.json)


This playbook creates API connections, since it needs to query/interact with Outlook 365 and Microsoft Sentinel.

Hence, ensure to provide "Deployers User name" as an email address. 

Provide PCE fqdn, port, org id, api key and secret, click Next and follow next steps to deploy playbook.

Once deployed, authorize the api connections.