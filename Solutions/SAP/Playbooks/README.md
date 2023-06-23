# SAP automation scenarios

SAP automation scenarios with Logic Apps (Standard). Serve them from this repos in addition to the UI experience of the Microsoft Sentinel solution for SAP for playbooks based on Logic Apps (Consumption).

These playbooks allow [enterprise features](https://learn.microsoft.com/azure/logic-apps/single-tenant-overview-compare#resource-types-and-environments) such as private VNet injection, tenant isolation and more.

Find out more from our blog series [here](https://blogs.sap.com/2023/05/22/from-zero-to-hero-security-coverage-with-microsoft-sentinel-for-your-critical-sap-security-signals-blog-series/).

## Playbooks

| Playbook | Description |
| --- | --- |
| [lock User from Teams - Basic](./Basic-SAPLockUser-STD/) | Basic playbook with minimum integration effort for simple SAP user blocking on ERP via SOAP service |

The deployment process first creates the infrastructure and generates the IDs for the managed identity of your logic app (Standard). Due to that a two-step deployment is required to add the required Connections for your workflow. Find the managed identity properties on the `Output of your deployment process`.

> **Warning**
> Find the convenient "Deploy to Azure button" on the individual scenarios page from above table.

## Step-by-Step Installation

Find the the installation guide [here](./INSTALLATION.md).

## CI/CD

[DevOps deployment for single-tenant Azure Logic Apps](https://learn.microsoft.com/azure/logic-apps/devops-deployment-single-tenant-azure-logic-apps)

## Export Logic Apps (Consumption) to Logic Apps (Standard)

Find out more about the export process [here](https://learn.microsoft.com/azure/logic-apps/export-from-consumption-to-standard-logic-app)
