# AWS Systems Manager API Functions App Connector

This Functions App Connector is to connect AWS Systems Manager API.

### Authentication methods supported by this connector

* Custom Authentication

### Prerequisites For AWS Systems Manager API Functions App Connector

* AWS Access Key ID, Secret Access Key and Region are required. 
* Check the [documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) to obtain above credentials.
* Check these [steps](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#using-regions-availability-zones-describe) to get the Region.


## Actions supported by AWS Systems Manager API Functions App Connector

| **Component** | **Description** |
| --------- | -------------- |
| **AddTagsToResource** | Adds or overwrites one or more tags for the specified resource. |
| **CreateDocument** | Creates a AWS Systems Manager (SSM document). An SSM document defines the actions that Systems Manager performs on your managed nodes. |
| **DeleteDocuemnt** | Deletes the AWS Systems Manager document (SSM document) and all managed node associations to the document. |
| **DescribeDocument** | Describes the specified AWS Systems Manager document (SSM document). |
| **DescribeInstanceInformation** | Describes one or more of your managed nodes, including information about the operating system platform, the version of SSM Agent installed on the managed node, node status, and so on. |
| **DescribeInstancePatches** | Retrieves information about the patches on the specified managed node and their state relative to the patch baseline being used for the node. |
| **GetAutomationExecution** | Get detailed information about a particular Automation execution. |
| **GetDocument** | Gets the contents of the specified AWS Systems Manager document (SSM document). |
| **GetInventory** | Query inventory information. This includes managed node status, such as Stopped or Terminated. |
| **ListDocuments** | Returns all Systems Manager (SSM) documents in the current AWS account and AWS Region. You can limit the results of this request by using a filter. |
| **ListTagsForResource** | Returns a list of the tags assigned to the specified resource. |
| **RemoveTagFromResource** | Removes tag keys from the specified resource. |
| **StartAutomationExecution** | Initiates execution of an Automation runbook. |
| **StopAutomationExecution** | Stop an Automation that is currently running. |

### Deployment Instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    - AWS Access Key ID 
    - AWS Secret Access Key
    - AWS Region

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAWS%2520Systems%2520Manager%2FPlaybooks%2FCustomConnector%2FAWS_SSM_FunctionAppConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAWS%2520Systems%2520Manager%2FPlaybooks%2FCustomConnector%2FAWS_SSM_FunctionAppConnector%2Fazuredeploy.json)

### Function App Settings (Access Key ID, Secret Access Key and Region) Update Instruction
1. Select the Function App.
2. Click on the Configuration blade under Settings.
3. Select the Application settings tab.
4. Click on the Edit for a setting.
5. Update the Values.
6. Click Ok to save.

### References
- [AWS Systems Manager API Documentation](https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_DeleteDocument.html)
- [AWS Systems Manager User Guide](https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html)
- [AWS Systems Manager Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html)