# AWS-SSM-GetInstancePatches-IPEntityTrigger

## Summary

The playbook can be triggered manually from an IP Entity to get the missing patches on a managed EC2 instance. This playbook performs the following actions:

 1. Get the Private IP from the IP Entity.
 2. Get the Instance ID of Managed EC2 instance for given private IP.
 3. Get the missing patches for the Instance ID.
 4. Add the missing patches to the incident comment.

<img src="./images/AWS-SSM-GetInstancePatches-IPTrigger_light.jpg" width="50%"/><br>
<img src="./images/AWS-SSM-GetInstancePatches-IPEntityTrigger_IncidentComment.jpg" width="50%"/><br>

### Prerequisites

1. Prior to the deployment of this playbook, [AWS Systems Manager API Function App Connector](../../CustomConnector/AWS_SSM_FunctionAppConnector/) needs to be deployed under the same subscription.
2. Refer to [AWS Systems Manager API Function App Connector](../../CustomConnector/AWS_SSM_FunctionAppConnector/readme.md) documentation to obtain AWS Access Key ID, Secret Access Key and Region. 

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name
    * Functions App Name

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAWS%2520Systems%2520Manager%2FPlaybooks%2FAWSSystemsManagerPlaybooks%2FAWS-SSM-GetInstancePatches-IPEntityTrigger%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAWS%2520Systems%2520Manager%2FPlaybooks%2FAWSSystemsManagerPlaybooks%2FAWS-SSM-GetInstancePatches-IPEntityTrigger%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections

#### b. Assign Playbook Microsoft Sentinel Responder Role
1. Select the Playbook (Logic App) resource
2. Click on Identity Blade
3. Choose System assigned tab
4. Click on Azure role assignments
5. Click on Add role assignments
6. Select Scope - Resource group
7. Select Subscription - where Playbook has been created
8. Select Resource group - where Playbook has been created
9. Select Role - Microsoft Sentinel Responder
10. Click Save

#### c. Function App Settings Update Instructions
Refer to [AWS Systems Manager API Function App Connector](../../CustomConnector/AWS_SSM_FunctionAppConnector/readme.md) documentation for Function App **Application Settings (Access Key ID, Secret Access Key and Region)** update instruction.

#  References
- [AWS Systems Manager API Documentation](https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_DeleteDocument.html)
- [AWS Systems Manager User Guide](https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html)
- [AWS Systems Manager Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html)