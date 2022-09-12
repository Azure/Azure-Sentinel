# AWS IAM API Function App connector

This Function App Connector is used for connection to AWS IAM API.

### Authentication methods supported by this connector

* custom authentication

### Prerequisites in AWS IAM

AWS Access Key Id and AWS Secret Access Key are required. Check the [documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) to obtain these credentials.

## Actions supported by AWS IMA API Function App Connector

| **Component** | **Description** |
| --------- | -------------- |
| **DeleteAccessKey** | Deletes the access key pair associated with the specified IAM user. |
| **DeleteUserPolicy** | Deletes the specified inline policy that is embedded in the specified IAM user. |
| **DetachUserPolicy** | Removes the specified managed policy from the specified user. |
| **GetUser** | Retrieves information about the specified IAM user, including the user's creation date, path, unique ID, and ARN. |
| **ListAccessKeys** | Returns information about the access key IDs associated with the specified IAM user. |
| **ListAttachedUserPolicies** | Lists all managed policies that are attached to the specified IAM user. |
| **ListGroupsForUser** | Lists the IAM groups that the specified IAM user belongs to. |
| **ListUserPolicies** | Lists the names of the inline policies embedded in the specified IAM user. |
| **TagUser** | Adds tag to an IAM user. |


### Deployment instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    - AWS_AccessKeyId 
    - AWS_SecretAccessKey

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAWS_IAM%2FPlaybooks%2FAWS_IAM_FunctionAppConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAWS_IAM%2FPlaybooks%2FAWS_IAM_FunctionAppConnector%2Fazuredeploy.json)