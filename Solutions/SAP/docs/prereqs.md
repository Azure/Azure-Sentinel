# Azure Sentinel SAP logs connector requirements

This article lists the system configurations and prerequisites required before you can install, configure, and start working with the Azure Sentinel SAP logs connector.

**Copyright (c) Microsoft Corporation**.  This preview software is Microsoft Confidential, and is subject to your Non-Disclosure Agreement with Microsoft.  You may use this preview software internally and only in accordance with the Azure preview terms, located at [Preview terms](https://azure.microsoft.com/support/legal/preview-supplemental-terms/).  Microsoft reserves all other rights.

## Azure services

You must have access to Azure Sentinel in the Azure portal. 

We also recommend that you use Azure Key Vault to store your credential secrets. 

For more information, see:

- [Azure Sentinel documentation](https://docs.microsoft.com/azure/sentinel/)
- [Azure Key Vault documentation](https://docs.microsoft.com/en-us/azure/key-vault/)

## Supported deployments

The Azure Sentinel SAP Logs connector supports the following deployments:

|Deployment  |Requirements  |
|---------|---------|
|**Azure Ubuntu Virtual Machine**     | - [Managed identity](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/) turned on <br>- [Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/) to store your credential secrets <br>- [Venv with Python version 3.8 or higher](https://docs.python.org/3.8/library/venv.html) <br>   - The [Azure CLI](https://docs.microsoft.com/cli/azure/), version 2.8.0 or higher <br><br>For more information, see [Deploy the Azure Sentinel SAP logs connector on Azure](deploy-azure.md).        |
|**Azure Container Instance**     |    - [Azure Container Registry](https://docs.microsoft.com/azure/container-registry) <br>- [Azure Key Vault](https://docs.microsoft.com/azure/key-vault/)<br>    - [Venv with Python version 3.8 or higher](https://docs.python.org/3.8/library/venv.html) <br>    - The [Azure CLI](https://docs.microsoft.com/cli/azure/), version 2.8.0 or higher <br><br>For more information, see [Deploy the Azure Sentinel SAP logs connector on Azure](deploy-azure.md).     |
|**On-premises machine**     | - Ubuntu latest <br>- [Python version 3.7 or higher](https://www.python.org/downloads/release/python-370/)      <br><br>    For more information, see [Deploy the Azure Sentinel SAP logs connector on Azure](deploy-onprem.md). |
|     |         |

**Important**: The Azure Sentinel SAP Logs connector is packaged as a Docker container, and can run on any virtual machine or Kubernetes container. However, we recommend using an Azure Virtual machine with managed identity, with Azure Key Vault to store your secrets.

Regardless of your deployment, you must have the following installed:

- [GitHub](https://github.com/)
- [Python3](https://www.python.org/download/releases/3.0/)
- [Python3-pip](https://pypi.org/project/pip/)
- [Docker](https://www.docker.com/) 

## SAP system requirements

The Azure Sentinel SAP Logs connector has the following requirements from your SAP system:

|Requirement  |Description  |
|---------|---------|
|**SAP version**     |  The Azure Sentinel SAP Logs connector requires a SAP version of 7.4 or higher.       |
| **SAP SDK** | The latest SAP NW RFC SDK zip file installed in the `<SAP Logs Connector repository>\inst` directory. <br><br>Find this SDK from [SAPNWRFCSDK](https://launchpad.support.sap.com/#/softwarecenter/template/products/_APP=00200682500000001943&_EVENT=DISPHIER&HEADER=Y&FUNCTIONBAR=N&EVENT=TREE&NE=NAVIGATE&ENR=01200314690100002214&V=MAINT) > **SAP NW RFC SDK** > **SAP NW RFC SDK 7.50** > **nwrfc750X_X-xxxxxxx.zip** <br><br>Make sure to download the **LINUX ON X86_64 65BIT** option.
|**SAP notes**     | Make sure to apply the following notes, as needed (unnecessary in recent SAP versions): <br>- [2502336](https://launchpad.support.sap.com/#/notes/2502336)<br>    - [2502336](https://launchpad.support.sap.com/#/notes/2502336)<br>    - [2641084](https://launchpad.support.sap.com/#/notes/2641084)        |
|**SAP system details**     |    Make a note of your SAP system IP address, system number, system ID, and client.     |
|**SAP change requests**     |  Import any required change requests for your logs from the [CR folder](../CR/) of this repository. <br>For more information, see [Required SAP Log change requests](../CR/README.MD).       |
|**SAP instance access**     | Access to your SAP instances must use one of the following options: <br>- User/password (less secure)<br> - A user with an X509 certificate (recommended)        |
|**sapcontrol configuration access**     |Access to the **sapcontrol** configuration must use one of the following options: <br>- User/password (less secure)<br>    - PKI certificate. <br>For more information see the [SAP documentation](https://launchpad.support.sap.com/#/notes/927637).         |
|**User permissions**     |  Assign any required [authorizations for the ABAP backend user](abap-backend-authorizations).  <br><br>**Tip**: To create the role with all required authorizations, deploy the SAP change request S4HK9000862 on your SAP system. This change request creates the **zsentinel_connector** role, and assigns the role to the ABAP connecting to Azure Sentinel.       |
|     |         |


