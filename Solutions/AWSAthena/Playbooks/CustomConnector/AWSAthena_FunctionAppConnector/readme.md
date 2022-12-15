# AWS Athena API Function App Connector

This Function App Connector is to connect AWS Athena API.

### Authentication methods supported by this connector

* Custom Authentication

### Prerequisites For AWS Athena API Function App Connector

* AWS Access Key ID, Secret Access Key and Region are required. 
* Check the [documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) to obtain above credentials.
* Check these [steps](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#using-regions-availability-zones-describe) to get the Region.


## Actions supported by AWS Athena API Function App Connector

| **Component** | **Description** |
| --------- | -------------- |
| **StartQueryExecution** | Start the query execution with specified QueryString, OutputLocation, Database and Catalog. Returns QueryExecutionId. |
| **GetQueryResults** | Get query results for specified QueryExecutionId. |
| **GetQueryExecution** | Get query execution state for specified QueryExecutionId. |
| **ListQueryExecution** | List QueryExecutionIds for all the query runs. |
| **ListDataCatalogs** | List all the Data Catalogs. |
| **ListDatabases** | List all databases for specified CatalogName. |

### Deployment Instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    - AWS Access Key ID 
    - AWS Secret Access Key
    - AWS Region

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAWSAthena%2FPlaybooks%2FCustomConnector%2FAWSAthena_FunctionAppConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAWSAthena%2FPlaybooks%2FCustomConnector%2FAWSAthena_FunctionAppConnector%2Fazuredeploy.json)

### Function App Settings (Access Key ID, Secret Access Key and Region) Update Instruction
1. Select the Function App.
2. Click on the Configuration blade under Settings.
3. Select the Application settings tab.
4. Click on the Edit for a setting.
5. Update the Values.
6. Click Ok to save.
