# AWS IAM Function App connector and playbook templates

<img src="./aws-logo.svg" alt="drawing" width="20%"/><br>

## Table of Contents

1. [Overview](#overview)
1. [Function App Connector + 3 Playbook templates deployment](#deployall)
1. [Authentication](#importantnotes)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post-Deployment Steps](#postdeployment)

<a name="overview">

# Overview

AWS IAM playbooks use [AWS IAM API](https://docs.aws.amazon.com/IAM/latest/APIReference/welcome.html) to manage resources in AWS.

<a name="deployall">

## Function App Connector + 3 Playbook templates deployment

This package includes:

* [Function App connector for AWS IAM API](./AWS_IAM_FunctionAppConnector/)


* These three playbook templates leverage AWS IAM connector:
  * [AWSIAM-EnrichIncidentWithUserInfo](./Playbooks/AWSIAM-EnrichIncidentWithUserInfo/)
  * [AWSIAM-AddTagToUser](./Playbooks/AWSIAM-AddTagToUser/)
  * [AWSIAM-DeleteAccessKeys](./Playbooks/AWSIAM-DeleteAccessKeys/)

You can choose to deploy the whole package: connector + all three playbook templates, or each one seperately from its specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAWS_IAM%2FPlaybooks%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAWS_IAM%2FPlaybooks%2Fazuredeploy.json)

# AWS IAM connector documentation 

<a name="authentication">

## Authentication

* custom authentication

<a name="prerequisites">

### Prerequisites in Vendor Product

AWS Access Key Id and AWS Secret Access Key are required. Check the [documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) to obtain these credentials.

<a name="deployment">

### Deployment instructions 

1. To deploy Custom Connectors and Playbooks, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters for deploying Custom Connectors and Playbooks

| Parameters | Description |
|----------------|--------------|
|**For Connector**|
|**AWS_AccessKeyId** | Access Key Id |
|**AWS_SecretAccessKey** | Secret Access Key |
|**For Playbooks**|
|**AWSIAM-AddTagToUser Playbook Name** | Name of the Playbook |
|**AWSIAM-EnrichIncidentWithUserInfo Playbook Name** | Name of the Playbook |
|**AWSIAM-DeleteAccessKeys Playbook Name** | Name of the Playbook |
|**TagKey** | Tag key which will be added to the incident in AWSIAM-AddTagToUser playbook |
|**TagValue** | Tag value which will be added to the incident in AWSIAM-AddTagToUser playbook |

<br>
<a name="postdeployment">

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections

#### b. Configurations in Sentinel

Each Playbook requires a different type of configuration. Check documentation for each Playbook.
