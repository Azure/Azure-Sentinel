# Google Cloud Platform Identity and Access Management Logic Apps Custom connector

<img src="https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Logos/google_logo.svg" alt="Google" style="width:150px; height:150px"/><br>

This custom connector connects to Google Cloud Platform (GCP) BigQuery Service API to execute actions supported by API returns response in JSON format.

### Authentication methods this connector supports

*  OAuth2.0 Authentication

### Prerequisites to deploy Custom Connector 
1. Get/Verify GCP BigQuery API Endpoint Url (Default: https://bigquery.googleapis.com)
2. Enable BigQuery API in GCP Console (see [instructions](https://developers.google.com/identity/protocols/oauth2/web-server#enable-apis)).
3. Create authorization credentials (see [instructions](https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred)). As a redirection url, use the redirection url that you can find on the connector page (in Azure go to **Logic Apps Custom Connector** -> **GCPBigQueryCustomConnector** -> click **Edit** -> **Security** -> copy *Redirect URL*). If this is your first time creating a client ID, you can also configure your consent screen by clicking Consent Screen. (The [following procedure](https://support.google.com/cloud/answer/6158849?hl=en#userconsent) explains how to set up the Consent screen.) You won't be prompted to configure the consent screen after you do it the first time. Note that [the following scope](https://developers.google.com/identity/protocols/oauth2/scopes#iam) has to be enabled in the consent screen.
4. In Azure go to **Logic Apps Custom Connector** -> **GCPBigQueryCustomConnector** -> click **Edit** -> **Security** -> fill the *Client id* and *Client secret*, obtained in the previous step -> click **Update connector**.


### Deployment instructions 
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogle%2520Cloud%2520Platform%2520BigQuery%2FPlaybooks%2FCustomConnector%2FGCPBigQueryCustomConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogle%2520Cloud%2520Platform%2520BigQuery%2FPlaybooks%2FCustomConnector%2FGCPBigQueryCustomConnector%2Fazuredeploy.json)


## Actions supported by GCP BigQuery Logic App Connector

| **Component** | **Description** |
| --------- | -------------- |
| **Get Dataset Details** | Returns the dataset specified by datasetID. |
| **Delete Dataset** | Deletes the dataset specified by the datasetId value. Before you can delete a dataset, you must delete all its tables, either manually or by specifying deleteContents. |
| **Replace Dataset** | Updates information in an existing dataset. This method replaces the entire dataset resource. |
| **Update Dataset** | Updates information in an existing dataset. This method only replaces fields that are provided in the submitted dataset resource. |
| **List Dataset** | Lists all datasets in the specified project to which the user has been granted the READER dataset role. |
| **Create Dataset** | Creates a new empty dataset. |
| **List Projects** | Lists all projects to which the user has been granted any project role. |
| **Get Service Account of Project** | RPC to get the service account for the project. |
| **List Jobs** | Lists all jobs that you started in the specified project. Job information is available for a six month period after creation. The job list is sorted in reverse chronological order, by job creation time. |
| **Get Job Details** | Returns information about a specific job. Job information is available for a six month period after creation. |
| **Cancel Job** | Requests that a job be cancelled. This call will return immediately, and the client will need to poll for the job status to see if the cancel completed successfully. |
| **Run Query Job** | Runs a BigQuery SQL query synchronously and returns query results if the query completes within a specified timeout. |
| **Get Query Result** | RPC to get the results of a query job. |
| **Delete Job** | Requests the deletion of the metadata of a job. This call returns when the job's metadata is deleted. |
| **Insert Data Into Table** | Streams data into BigQuery one record at a time without needing to run a load job. |
| **Get Table Data** | Gets the content of a table in rows. |
| **Get Table Details** | Gets the specified table resource by table ID. This method does not return the data in the table, it only returns the table resource, which describes the structure of this table. |
| **Delete Table** | Deletes the table specified by tableId from the dataset. If the table contains data, all the data will be deleted. |
| **Replace Table** | Updates information in an existing table. This method replaces the entire Table resource. |
| **Update Table** | Updates information in an existing table. This method only replaces fields that are provided in the submitted table resource. |
| **List Tables** | Lists all tables in the specified dataset. Requires the READER dataset role. |
| **Create Table** | Creates a new, empty table in the dataset. |


#  References
 - [BigQuery API Quick Reference](https://cloud.google.com/bigquery/docs/reference/rest)
 - [BigQuery Documnetation](https://cloud.google.com/bigquery/docs)
 - [Configure Authorization Credetials](https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred)
