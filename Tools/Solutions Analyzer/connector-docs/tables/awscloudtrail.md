# AWSCloudTrail

Reference for AWSCloudTrail table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | AWS |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✓ Yes |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/awscloudtrail) |

## Solutions (7)

This table is used by the following solutions:

- [Amazon Web Services](../solutions/amazon-web-services.md)
- [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Multi Cloud Attack Coverage Essentials - Resource Abuse](../solutions/multi-cloud-attack-coverage-essentials---resource-abuse.md)
- [NISTSP80053](../solutions/nistsp80053.md)
- [Threat Intelligence](../solutions/threat-intelligence.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)

## Connectors (2)

This table is ingested by the following connectors:

- [Amazon Web Services](../connectors/aws.md)
- [Amazon Web Services S3](../connectors/awss3.md)

---

## Content Items Using This Table (108)

### Analytic Rules (68)

**In solution [Amazon Web Services](../solutions/amazon-web-services.md):**
- [AWS Config Service Resource Deletion Attempts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_ConfigServiceResourceDeletion.yaml)
- [Automatic image scanning disabled for ECR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_ECRImageScanningDisabled.yaml)
- [Changes made to AWS CloudTrail logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_ClearStopChangeTrailLogs.yaml)
- [Changes to AWS Elastic Load Balancer security groups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_LoadBalancerSecGroupChange.yaml)
- [Changes to AWS Security Group ingress and egress settings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_IngressEgressSecurityGroupChange.yaml)
- [Changes to Amazon VPC settings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_ChangeToVPC.yaml)
- [Changes to internet facing AWS RDS Database instances](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_ChangeToRDSDatabase.yaml)
- [CloudFormation policy created then used for privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedCloudFormationPolicytoPrivilegeEscalation.yaml)
- [Created CRUD S3 policy and then privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedCRUDS3PolicytoPrivilegeEscalation.yaml)
- [Creating keys with encrypt policy without MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreationofEncryptKeysWithoutMFA.yaml)
- [Creation of Access Key for IAM User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_UserAccessKeyCreated.yaml)
- [Creation of CRUD DynamoDB policy and then privilege escalation.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedCRUDDyanmoDBPolicytoPrivilegeEscalation.yaml)
- [Creation of CRUD KMS policy and then privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedCRUDKMSPolicytoPrivilegeEscalation.yaml)
- [Creation of CRUD Lambda policy and then privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedCURDLambdaPolicytoPrivilegEscalation.yaml)
- [Creation of DataPipeline policy and then privilege escalation.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedDataPipelinePolicytoPrivilegeEscalation.yaml)
- [Creation of EC2 policy and then privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedEC2PolicytoPrivilegeEscalation.yaml)
- [Creation of Glue policy and then privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedGluePolicytoPrivilegeEscalation.yaml)
- [Creation of Lambda policy and then privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedLambdaPolicytoPrivilegeEscalation.yaml)
- [Creation of SSM policy and then privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedSSMPolicytoPrivilegeEscalation.yaml)
- [Creation of new CRUD IAM policy and then privilege escalation.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedCRUDIAMtoPrivilegeEscalation.yaml)
- [EC2 Startup Shell Script Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_EC2StartupShellScriptChanged.yaml)
- [ECR image scan findings high or critical](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_ECRContainerHigh.yaml)
- [Full Admin policy created and then attached to Roles, Users or Groups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_FullAdminPolicyAttachedToRolesUsersGroups.yaml)
- [GuardDuty detector disabled or suspended](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_GuardDutyDisabled.yaml)
- [Login to AWS Management Console without MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_ConsoleLogonWithoutMFA.yaml)
- [Monitor AWS Credential abuse or hijacking](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CredentialHijack.yaml)
- [NRT Login to AWS Management Console without MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/NRT_AWS_ConsoleLogonWithoutMFA.yaml)
- [Network ACL with all the open ports to a specified CIDR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_NetworkACLOpenToAllPorts.yaml)
- [Policy version set to default](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_SetDefaulyPolicyVersion.yaml)
- [Privilege escalation via CRUD DynamoDB policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationviaCRUDDynamoDB.yaml)
- [Privilege escalation via CRUD IAM policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaCRUDIAMPolicy.yaml)
- [Privilege escalation via CRUD KMS policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaCRUDKMSPolicy.yaml)
- [Privilege escalation via CRUD Lambda policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaCRUDLambdaPolicy.yaml)
- [Privilege escalation via CRUD S3 policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaCRUDS3Policy.yaml)
- [Privilege escalation via CloudFormation policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaCloudFormationPolicy.yaml)
- [Privilege escalation via DataPipeline policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaDataPipeline.yaml)
- [Privilege escalation via EC2 policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaEC2Policy.yaml)
- [Privilege escalation via Glue policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaGluePolicy.yaml)
- [Privilege escalation via Lambda policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaLambdaPolicy.yaml)
- [Privilege escalation via SSM policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaSSM.yaml)
- [Privilege escalation with AdministratorAccess managed policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationAdministratorAccessManagedPolicy.yaml)
- [Privilege escalation with FullAccess managed policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationFullAccessManagedPolicy.yaml)
- [Privilege escalation with admin managed policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationAdminManagedPolicy.yaml)
- [RDS instance publicly exposed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_RDSInstancePubliclyExposed.yaml)
- [S3 Object Exfiltration from Anonymous User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_S3ObjectExfiltrationByAnonymousUser.yaml)
- [S3 bucket access point publicly exposed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_S3BucketAccessPointExposed.yaml)
- [S3 bucket exposed via ACL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_S3BucketExposedviaACL.yaml)
- [S3 bucket exposed via policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_S3BucketExposedviaPolicy.yaml)
- [S3 bucket suspicious ransomware activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_S3Ransomware.yaml)
- [S3 object publicly exposed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_S3ObjectPubliclyExposed.yaml)
- [SAML update identity provider](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_SAMLUpdateIdentity.yaml)
- [SSM document is publicly exposed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_SSMPubliclyExposed.yaml)
- [Successful API executed from a Tor exit node](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_APIfromTor.yaml)
- [Successful brute force attack on S3 Bucket.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_S3BruteForce.yaml)
- [Suspicious AWS CLI Command Execution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/SuspiciousAWSCLICommandExecution.yaml)
- [Suspicious AWS EC2 Compute Resource Deployments](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/SuspiciousAWSEC2ComputeResourceDeployments.yaml)
- [Suspicious command sent to EC2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_SuspiciousCommandEC2.yaml)
- [Suspicious overly permissive KMS key policy created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_OverlyPermessiveKMS.yaml)
- [Tampering to AWS CloudTrail logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_LogTampering.yaml)
- [Unauthorized EC2 Instance Setup Attempt](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_UnauthorizedInstanceSetUpAttempt.yaml)
- [User IAM Enumeration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_UserIAMEnumeration.yaml)

**In solution [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md):**
- [Log4j vulnerability exploit aka Log4Shell IP IOC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Analytic%20Rules/Log4J_IPIOC_Dec112021.yaml)

**In solution [Multi Cloud Attack Coverage Essentials - Resource Abuse](../solutions/multi-cloud-attack-coverage-essentials---resource-abuse.md):**
- [High-Risk Cross-Cloud User Impersonation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/UserImpersonateByRiskyUser.yaml)
- [Successful AWS Console Login from IP Address Observed Conducting Password Spray](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/SuccessfulAWSConsoleLoginfromIPAddressObservedConductingPasswordSpray.yaml)
- [Suspicious AWS console logins by credential access alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/SuspiciousAWSConsolLoginByCredentialAceessAlerts.yaml)
- [User impersonation by Identity Protection alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/UserImpersonateByAAID.yaml)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI map IP entity to AWSCloudTrail](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AWSCloudTrail.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI map IP entity to AWSCloudTrail](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AWSCloudTrail.yaml)

### Hunting Queries (36)

**In solution [Amazon Web Services](../solutions/amazon-web-services.md):**
- [Bucket versioning suspended](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_BucketVersioningSuspended.yaml)
- [Changes made to AWS IAM objects](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_IAMUserGroupChanges.yaml)
- [Changes made to AWS IAM policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_IAM_PolicyChange.yaml)
- [CreateLoginProfile detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_CreateLoginProfile.yaml)
- [CreatePolicyVersion with excessive permissions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_PolicywithExcessivePermissions.yaml)
- [ECR image scan findings low](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_ECRContainerLow.yaml)
- [ECR image scan findings medium](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_ECRContainerMedium.yaml)
- [Excessive execution of discovery events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_ExcessiveExecutionofDiscoveryEvents.yaml)
- [Failed brute force on S3 bucket](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_FailedBruteForceS3Bucket.yaml)
- [IAM AccessDenied discovery events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_IAMAccsesDeniedDiscoveryEvents.yaml)
- [IAM Privilege Escalation by Instance Profile attachment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_IAM_PrivilegeEscalationbyAttachment.yaml)
- [IAM assume role policy brute force](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_AssumeRoleBruteForce.yaml)
- [Lambda UpdateFunctionCode](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_LambdaUpdateFunctionCode.yaml)
- [Lambda function throttled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_LambdaFunctionThrottled.yaml)
- [Lambda layer imported from external account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_LambdaLayerImportedExternalAccount.yaml)
- [Login profile updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_LoginProfileUpdated.yaml)
- [Modification of route-table attributes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_ModificationofRouteTableAttributes.yaml)
- [Modification of subnet attributes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_ModificationofSubnetAttributes.yaml)
- [Modification of vpc attributes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_ModificationofVPCAttributes.yaml)
- [Multiple failed login attempts to an existing user without MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_FailedBruteForceWithoutMFA.yaml)
- [Network ACL deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_NetworkACLDeleted.yaml)
- [New AccessKey created for Root user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_NewRootAccessKey.yaml)
- [New access key created to user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_CreateAccessKey.yaml)
- [Privileged role attached to Instance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_PrivilegedRoleAttachedToInstance.yaml)
- [RDS instance master password changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_RDSMasterPasswordChanged.yaml)
- [Risky role name created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_RiskyRoleName.yaml)
- [S3 bucket encryption modified](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_S3BucketEncryptionModified.yaml)
- [S3 bucket has been deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_S3BucketDeleted.yaml)
- [Suspicious EC2 launched without a key pair](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_EC2_WithoutKeyPair.yaml)
- [Suspicious activity of STS Token related to Kubernetes worker node](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_STStoKWN.yaml)
- [Suspicious activity of STS token related to EC2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_STStoEC2.yaml)
- [Suspicious activity of STS token related to ECS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_STStoECS.yaml)
- [Suspicious activity of STS token related to Glue](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_STStoGlue.yaml)
- [Suspicious activity of STS token related to Lambda](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_STStoLambda.yaml)
- [Suspicious credential token access of valid IAM Roles](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_SuspiciousCredentialTokenAccessOfValid_IAM_Roles.yaml)
- [Unused or Unsupported Cloud Regions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_Unused_UnsupportedCloudRegions.yaml)

### Workbooks (4)

**In solution [Amazon Web Services](../solutions/amazon-web-services.md):**
- [AmazonWebServicesNetworkActivities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Workbooks/AmazonWebServicesNetworkActivities.json)
- [AmazonWebServicesUserActivities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Workbooks/AmazonWebServicesUserActivities.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [NISTSP80053](../solutions/nistsp80053.md):**
- [NISTSP80053](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Workbooks/NISTSP80053.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
