# Microsoft Sentinel Playbooks for Illumio Integration

Playbooks are collections of procedures that can be run from Microsoft Sentinel.  

---

## Containment Switch Playbook

The **Containment Switch** playbook is designed to help isolate workloads. It includes the following procedures:

1. **Run an Explorer Query**  
   Queries Illumio PCE for potentially blocked or unknown traffic for a given port-protocol combination over the last week.
2. **Get a List of Visibility-Only Workloads**  
   Parses the query response to identify workloads marked as visibility-only.
3. **Create a Deny Rule**  
   Creates and provisions a deny rule from all IPs to all workloads for the specified port-protocol combination.
4. **Create a Virtual Service**  
   Creates and provisions a virtual service for the given port-protocol combination.
5. **Create Workload Bindings**  
   Binds workloads to the virtual service created in Step 4.
6. **Create an Allow Rule**  
   Creates and provisions an allow rule from workloads to the virtual service.
7. **Change Enforcement State**  
   Changes the enforcement state of visibility-only workloads to selective state.

Each procedure is implemented as a function within an Azure Function App.

---

### How It Works

The playbook provides the following capabilities:

- Queries Illumio PCE for traffic matching the specified port-protocol combination.
- Parses the response to identify visibility-only workloads.
- Provisions rules and objects in the PCE based on the parsed data.

#### Example Input to the Playbook:
```json
{
  "protocol": 17,
  "port": 5354,
  "applyChanges": true
}
```

Regarding "applyChanges":
If true, the playbook will create and provision changes (including workload enforcement changes).
If false, it skips object creation/modification steps and only provides a summary of actions, but traffic query results and parsed workloads will still be available.



# To deploy, follow the below link 
Deploy the function app first:
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FIllumioSaaS%2FPlaybooks%2FCustomConnector%2FIllumioSaaS_FunctionAppConnector%2Fazuredeploy.json)

Deploy logic app next:
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FIllumioSaaS%2FPlaybooks%2FIllumio-Port-Blocking-Switch%2Fazuredeploy.json)


User can modify the playbook name, function app name as per requirements.

PCE fqdn, port, org id, api key and secret are needed for communicating with the pce.
Once these are entered, click on next and follow steps to deploy.