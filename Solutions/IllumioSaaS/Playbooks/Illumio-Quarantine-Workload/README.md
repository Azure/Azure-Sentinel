# Microsoft Sentinel Playbooks for Illumio Integration

Playbooks are collections of procedures that can be run from Microsoft Sentinel.  

---

## Quarantine Workload Playbook

1. The logic app can be invoked as a http request.
2. The payload should contain workload hostname/s and label/s. 
3. Function app is called with the above payload which makes a call to the PCE and applies labels to the workloads mentioned in payload. 

# To deploy, follow the below steps

Deploy the function app first
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FIllumioSaaS%2FPlaybooks%2FCustomConnector%2FIllumioSaaS_FunctionAppConnector%2Fazuredeploy.json)



Deploy the logic app next:
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FIllumioSaaS%2FPlaybooks%2FIllumio-Quarantine-Workload%2Fazuredeploy.json)