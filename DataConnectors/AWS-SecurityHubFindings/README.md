# Ingest AWS Security Hub Events to Azure Sentinel

Authors: Sreedhar Ande, Håkon Drange, Truls Dahlsveen

## Introduction

AWS SecurityHub is a service that centralizes and organizes alerts and findings from across services. Services include GuardDuty, Macie, IAM Access Analyzer, and AWS Firewall Manager. You can use SecurityHub to continuously monitor your environment and perform automated compliance checks.  

Security Hub is region-specific by default, which means you need to turn it on and configure it separately for every region in your account. You can also [enable cross-region aggregation.](https://docs.aws.amazon.com/securityhub/latest/userguide/finding-aggregation.html)
Ingest all the SecurityHub findings returned by SecurityHub API, ingests only fresh findings based on the LastObservedAt timestamp

## Deploy AWS SecurityHub Data connector

### Azure

1. Click  "Deploy To Azure" (For both Commercial & Azure GOV)  
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FAWS-SecurityHubFindings%2Fazuredeploy_awssecurityhub.json)

2. Fill in the required fields:
```
WorkspaceId = Id of the Log Analytics-workspace you want to send logs to.
WorkspaceKey = The access key of the Log Analytics-workspace you want to send logs to.
AWSRegion = AWS Region your AWS Account is set to.
AWSRoleArn = RoleArn is a combination of AWSAccountNumber and RoleName ("arn:aws:iam::<AWSAccountNumber>:role/SecurityHubIntegrationRole").
AWSRoleSessionName = Name of the session variable. //Leave default
```
3. In the function under Settings, go to Identity and turn on Managed Identity.
4. Go to Azure AD, Enterprise Applications and find the Managed Identity. 
   * Note the ApplicationId (ClientId).
6. Under Settings, go to Configuration and paste the ApplicationId (ClientId) into the ClientID parameter.

### AWS

1. [Obtain the thumbprint for Azure AD](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc_verify-thumbprint.html).
*The openid endpoint for Azure AD can be found at https://login.microsoftonline.com/$tenantId/v2.0/.well-known/openid-configuration*
2. Deploy the [CloudFormation template](https://raw.githubusercontent.com/infernuxmonster/Azure-Sentinel/AWS-SecurityHub-AuthUpgrade/DataConnectors/AWS-SecurityHubFindings/CloudFormation.template.json) and fill in the required fields:
```
IdP ID (TenantId of your Azure AD tenant)
ClientID (ApplicationId of the Managed Identity created for the Azure Function)
Thumbprint (Obtained in step 1)
```
Leave everything else to default.

### Azure

1. For the first time run, change the FreshEventTimeStamp variable in configuration to a higher value (in minutes) to populate the log - recommended 3600.
2. After the function runs, change the above value back to 10.

## Post Deployment Steps

### 1. Edit TimerTrigger

The `TimerTrigger` makes it incredibly easy to have your functions executed on a schedule. This sample demonstrates a simple use case of calling your function based on your schedule provided while deploying. If the time interval needs to be modified, it is recommended to change the Function App Timer Trigger accordingly update environment variable **"Schedule**" (post deployment) to prevent overlapping data ingestion.

```
   a.	Go to your Resource Group --> Click on Function App `awssecurityhub<<uniqueid>>`
   b.	Click on Function App "Configuration" under Settings 
   c.	Click on "Schedule" under "Application Settings"
   d.	Update your own schedule using cron expression.
```

**Note: For a `TimerTrigger` to work, you provide a schedule in the form of a [cron expression](https://en.wikipedia.org/wiki/Cron#CRON_expression)(See the link for full details). A cron expression is a string with 6 separate expressions which represent a given schedule via patterns. The pattern we use to represent every 10 minutes is `0 */10 * * * *`. This, in plain text, means: "When seconds is equal to 0, minutes is divisible by 10, for any hour, day of the month, month, day of the week, or year".**
   
### 2. Edit Filter-parameter

Parameterized finding attributes using a environment variable "SecurityHubFilters" which is used to define a condition to filter the returned findings. You can filter by up to 10 finding attributes. For each attribute, you can provide up to 20 filter values.

**Current configured filter:**

 ```json 
 {"SeverityLabel": [{"Value": "HIGH", "Comparison": "EQUALS"},{"Value": "CRITICAL", "Comparison": "EQUALS"}],"RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}]}  
 ```
 
**Another filter:**

```json

{
# look for findings that belong to current account
# will help deconflict checks run in a master account
"AwsAccountId": [{"Value": awsAccountId, "Comparison": "EQUALS"}],
# look for high or critical severity findings
"SeverityLabel": [
	{"Value": "HIGH", "Comparison": "EQUALS"},
	{"Value": "CRITICAL", "Comparison": "EQUALS"},
],
# look for AWS security hub integrations
# company can be AWS or Amazon depending on service
"CompanyName": [
	{"Value": "AWS", "Comparison": "EQUALS"},
	{"Value": "Amazon", "Comparison": "EQUALS"},
],
# check for Active Records
"RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}]
}
```

**Note**  
If you want to update/change SecurityHubFilters environment variable, please convert the filter value into single line
   
### 3. Edit FreshEventTimeStamp

Parameterized SecurityHub fresh event duration using environment variable "FreshEventTimeStamp". Value must be in minutes.  
   
**Note**  
Azure Function trigger schedule and FreshEventTimeStamp  
Ex: If you want to trigger function every 30 min then values must be  
**FreshEventTimeStamp=30**  
Schedule=0 */30 * * * *  
   
      
### 4. Secret management

All secrets will be placed as "Secrets" in the Azure KeyVault `awssecurityhub<<uniqueid>>` with only Azure Function access policy. If you want to see/update these secrets,

```
a. Go to Azure KeyVault "awssecurityhub<<uniqueid>>"
b. Click on "Access Policies" under Settings
c. Click on "Add Access Policy"
	i. Configure from template : Secret Management
	ii. Key Permissions : GET, LIST, SET
	iii. Select Prinicpal : <<Your Account>>
	iv. Add
d. Click "Save"
```
