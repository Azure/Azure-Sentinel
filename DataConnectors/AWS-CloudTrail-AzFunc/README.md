# Azure Native Data connector to ingest AWS CloudTrail Logs

AWS CloudTrail logs are audit type events from all/any AWS resources in a tenancy. Each AWS resource has a unique set of Request and Response Parameters. Azure Log Analytics has a column per table limit of 500, (plus some system columns) the aggregate of AWS parameter fields will exceed this quickly leading to potential loss of event records

Code does the following things with the logs it processes. 
1.	Takes the core fields of the record. i.e. all fields except for the Request and Response associated fields and puts them in a LogAnalyticsTableName_ALL. Providing a single table with all records with core event information.	
2.	Looks at each event and puts it into a table with an extension <AWSREsourceType> i.e. LogAnalyticsTableName_AWSResourceType  
	Ex: LogAnalyticsTableName_s3
3.	Exception to #2 above is for EC2 events, the volume of fields for EC2 Request and Response parameters exceeds 500 columns. EC2 data is split into 3 tables, Header, Request & Response. 
	Ex: LogAnalyticsTableName_EC2_Header
4.	In future if other AWS datatypes exceed 500 columns a similar split may be required for them as well. 

**Note**  

To avoid additional billing and duplication:
1. You can turn off LogAnalyticsTableName_ALL using additional Environment Variable **CoreFieldsAllTable** to **false**
2. You can turn off LogAnalyticsTableName_AWSREsourceType using additional Environment Variable **SplitAWSResourceTypeTables** to **false**

**Either CoreFieldsAllTable or SplitAWSResourceTypeTables must be true or both can be true**

## **Function Flow process**
**CloudTrail Logs --> AWS S3 --> Azure Function --> Azure Log Analytics**
![AWSCloudTrailAzFun](./images/AWSCloudTrailAzFun.PNG)
## Installation / Setup Guide

1. Click the "Deploy to Azure" button below.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2F%2FAWS-CloudTrail-AzFunc%2Fmain%2Fazuredeploy_awscloudtrail.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2F%2FAWS-CloudTrail-AzFunc%2Fmain%2Fazuredeploy_awscloudtrail.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

2. Select the preferred Subscription, Resource Group and Location

3. Enter the Workspace ID, Workspace Key, AWS AccesKey, AWS Acces SecretKey and AWS S3 Bucket Name  
   **Note**  
   
   Securely store Workspace ID,  Workspace Key, AWS AccesKey, AWS Acces SecretKey in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and  retrieve key values.  
   <a target="_blank" href="https://docs.microsoft.com/azure/app-service/app-service-key-vault-references" rel="noopener">Follow these instructions</a> to use Azure Key Vault with an Azure Function App.   
   If using Azure Key Vault secrets for any of the values above, use the @Microsoft.KeyVault(SecretUri={Security Identifier})schema in place of the string values.  Refer to <a target="_blank" href="https://docs.microsoft.com/azure/app-service/app-service-key-vault-references" rel="noopener">Key Vault references documentation</a> for further details. 
