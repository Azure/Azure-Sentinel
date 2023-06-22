# SAP automation scenarios

SAP automation scenarios with Logic Apps (Standard). Serve them from this repos in addition to the UI experience of the Microsoft Sentinel solution for SAP for playbooks based on Logic Apps (Consumption).

These playbooks allow [enterprise features](https://learn.microsoft.com/azure/logic-apps/single-tenant-overview-compare#resource-types-and-environments) such as private VNet injection, tenant isolation and more.

Find out more from our blog series [here](https://blogs.sap.com/2023/05/22/from-zero-to-hero-security-coverage-with-microsoft-sentinel-for-your-critical-sap-security-signals-blog-series/).

## Playbooks

| Playbook | Description | 🪂 |
| --- | --- | --- |
| [lock User from Teams - Basic](./Basic-SAPLockUser-STD/) | Basic playbook with minimum integration effort for simple SAP user blocking on ERP via SOAP service | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FMartinPankraz%2FAzure-Sentinel%2Fadd-sap-playbooks-standard%2FSolutions%2FSAP%2FPlaybooks%2FBasic-SAPLockUser-STD%2Fazuredeploy.json) |

## Step-by-Step Installation

[🪂Custom Deployment](https://portal.azure.com/?feature.customportal=false#create/Microsoft.Template)

1. Choose "Custom deployment" from the Azure Portal or above link.
2. Click "Build your own template in the editor" and paste the content of the ´template.json´ file of your desired playbook folder.
3. Fill in the required parameters and click "Review + create".
4. Click "Create" to deploy the ARM template.
5. After the deployment is finished, navigate to the created Logic App and click "Edit".
6. Click "Edit API connection" and work through the all the required connections till the Logic App can be saved.

## Export Logic Apps (Consumption) to Logic Apps (Standard)

Find out more about the export process [here](https://learn.microsoft.com/azure/logic-apps/export-from-consumption-to-standard-logic-app)
