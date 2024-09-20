# SIEM data migration accelerator

The SIEM data migration accelerator helps you with the setup of the different tools and Azure services needed to perform the migration of historical logs from other SIEM vendors to Azure.

This tool is deployed through an ARM template and performs the following steps:

- Deploys a Windows Virtual Machine that will be used to move the logs from source to target

- Downloads and extracts the following tools into the Virtual Machine's desktop:

    + [LightIngest](https://docs.microsoft.com/azure/data-explorer/lightingest) (used to migrate data to ADX)

    + [Azure Monitor Custom log ingestion tool](https://github.com/Azure/Azure-Sentinel/tree/master/Tools/CustomLogsIngestion-DCE-DCR) (used to migrate data to Log Analytics)

    + [AzCopy](https://docs.microsoft.com/azure/storage/common/storage-use-azcopy-v10) (used to migrate data to Azure Blob Storage)

- Deploys the target platform that will host your historical logs. To choose from:

    + Azure Storage account
    
    + Azure Data Explorer cluster and database

    + Azure Monitor Logs workspace (enabled with Microsoft Sentinel)

    + Skip. You also have the option to skip this step if your target platform has been already created.

## Usage

To deploy this tool, just click on the link below and follow the wizard steps:

[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fjaviersoriano%2Fsiem-data-migration%2Fmaster%2Fazuredeploy.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2Fjaviersoriano%2Fsiem-data-migration%2Fmaster%2FcreateUiDefinition.json)