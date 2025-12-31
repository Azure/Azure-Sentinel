# Amazon Web Services

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services) |

## Data Connectors

This solution provides **3 data connector(s)**:

- [Amazon Web Services](../connectors/aws.md)
- [Amazon Web Services S3](../connectors/awss3.md)
- [Amazon Web Services S3 WAF](../connectors/awss3wafccpdefinition.md)

## Tables Reference

This solution uses **7 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AWSCloudTrail`](../tables/awscloudtrail.md) | [Amazon Web Services](../connectors/aws.md), [Amazon Web Services S3](../connectors/awss3.md) | Analytics, Hunting, Workbooks |
| [`AWSCloudWatch`](../tables/awscloudwatch.md) | [Amazon Web Services S3](../connectors/awss3.md) | - |
| [`AWSGuardDuty`](../tables/awsguardduty.md) | [Amazon Web Services S3](../connectors/awss3.md) | Analytics |
| [`AWSVPCFlow`](../tables/awsvpcflow.md) | [Amazon Web Services S3](../connectors/awss3.md) | - |
| [`AWSWAF`](../tables/awswaf.md) | [Amazon Web Services S3 WAF](../connectors/awss3wafccpdefinition.md) | - |
| [`FullAdminPolicyEvents`](../tables/fulladminpolicyevents.md) | - | Analytics |
| [`PutObject`](../tables/putobject.md) | - | Analytics |

## Content Items

This solution includes **100 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 62 |
| Hunting Queries | 36 |
| Workbooks | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [AWS Config Service Resource Deletion Attempts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_ConfigServiceResourceDeletion.yaml) | Low | DefenseEvasion | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [AWS Guard Duty Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_GuardDuty_template.yaml) | Medium | - | [`AWSGuardDuty`](../tables/awsguardduty.md) |
| [Automatic image scanning disabled for ECR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_ECRImageScanningDisabled.yaml) | Medium | DefenseEvasion | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Changes made to AWS CloudTrail logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_ClearStopChangeTrailLogs.yaml) | Low | DefenseEvasion | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Changes to AWS Elastic Load Balancer security groups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_LoadBalancerSecGroupChange.yaml) | Low | Persistence | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Changes to AWS Security Group ingress and egress settings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_IngressEgressSecurityGroupChange.yaml) | Low | Persistence | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Changes to Amazon VPC settings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_ChangeToVPC.yaml) | Low | PrivilegeEscalation, LateralMovement | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Changes to internet facing AWS RDS Database instances](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_ChangeToRDSDatabase.yaml) | Low | Persistence | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [CloudFormation policy created then used for privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedCloudFormationPolicytoPrivilegeEscalation.yaml) | High | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`FullAdminPolicyEvents`](../tables/fulladminpolicyevents.md) |
| [Created CRUD S3 policy and then privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedCRUDS3PolicytoPrivilegeEscalation.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`FullAdminPolicyEvents`](../tables/fulladminpolicyevents.md) |
| [Creating keys with encrypt policy without MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreationofEncryptKeysWithoutMFA.yaml) | Medium | Impact | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Creation of Access Key for IAM User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_UserAccessKeyCreated.yaml) | Medium | Persistence | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Creation of CRUD DynamoDB policy and then privilege escalation.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedCRUDDyanmoDBPolicytoPrivilegeEscalation.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`FullAdminPolicyEvents`](../tables/fulladminpolicyevents.md) |
| [Creation of CRUD KMS policy and then privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedCRUDKMSPolicytoPrivilegeEscalation.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`FullAdminPolicyEvents`](../tables/fulladminpolicyevents.md) |
| [Creation of CRUD Lambda policy and then privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedCURDLambdaPolicytoPrivilegEscalation.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`FullAdminPolicyEvents`](../tables/fulladminpolicyevents.md) |
| [Creation of DataPipeline policy and then privilege escalation.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedDataPipelinePolicytoPrivilegeEscalation.yaml) | High | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`FullAdminPolicyEvents`](../tables/fulladminpolicyevents.md) |
| [Creation of EC2 policy and then privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedEC2PolicytoPrivilegeEscalation.yaml) | High | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`FullAdminPolicyEvents`](../tables/fulladminpolicyevents.md) |
| [Creation of Glue policy and then privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedGluePolicytoPrivilegeEscalation.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`FullAdminPolicyEvents`](../tables/fulladminpolicyevents.md) |
| [Creation of Lambda policy and then privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedLambdaPolicytoPrivilegeEscalation.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`FullAdminPolicyEvents`](../tables/fulladminpolicyevents.md) |
| [Creation of SSM policy and then privilege escalation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedSSMPolicytoPrivilegeEscalation.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`FullAdminPolicyEvents`](../tables/fulladminpolicyevents.md) |
| [Creation of new CRUD IAM policy and then privilege escalation.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CreatedCRUDIAMtoPrivilegeEscalation.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`FullAdminPolicyEvents`](../tables/fulladminpolicyevents.md) |
| [EC2 Startup Shell Script Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_EC2StartupShellScriptChanged.yaml) | Medium | Execution | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [ECR image scan findings high or critical](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_ECRContainerHigh.yaml) | High | Execution | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Full Admin policy created and then attached to Roles, Users or Groups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_FullAdminPolicyAttachedToRolesUsersGroups.yaml) | Medium | PrivilegeEscalation, DefenseEvasion | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`FullAdminPolicyEvents`](../tables/fulladminpolicyevents.md) |
| [GuardDuty detector disabled or suspended](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_GuardDutyDisabled.yaml) | High | DefenseEvasion | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Login to AWS Management Console without MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_ConsoleLogonWithoutMFA.yaml) | Low | DefenseEvasion, PrivilegeEscalation, Persistence, InitialAccess | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Monitor AWS Credential abuse or hijacking](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_CredentialHijack.yaml) | Low | Discovery | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [NRT Login to AWS Management Console without MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/NRT_AWS_ConsoleLogonWithoutMFA.yaml) | Low | DefenseEvasion, PrivilegeEscalation, Persistence, InitialAccess | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Network ACL with all the open ports to a specified CIDR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_NetworkACLOpenToAllPorts.yaml) | High | DefenseEvasion | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Policy version set to default](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_SetDefaulyPolicyVersion.yaml) | Medium | InitialAccess | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Privilege escalation via CRUD DynamoDB policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationviaCRUDDynamoDB.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Privilege escalation via CRUD IAM policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaCRUDIAMPolicy.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Privilege escalation via CRUD KMS policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaCRUDKMSPolicy.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Privilege escalation via CRUD Lambda policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaCRUDLambdaPolicy.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Privilege escalation via CRUD S3 policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaCRUDS3Policy.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Privilege escalation via CloudFormation policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaCloudFormationPolicy.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Privilege escalation via DataPipeline policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaDataPipeline.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Privilege escalation via EC2 policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaEC2Policy.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Privilege escalation via Glue policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaGluePolicy.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Privilege escalation via Lambda policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaLambdaPolicy.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Privilege escalation via SSM policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationViaSSM.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Privilege escalation with AdministratorAccess managed policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationAdministratorAccessManagedPolicy.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Privilege escalation with FullAccess managed policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationFullAccessManagedPolicy.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Privilege escalation with admin managed policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_PrivilegeEscalationAdminManagedPolicy.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [RDS instance publicly exposed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_RDSInstancePubliclyExposed.yaml) | Medium | Exfiltration | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [S3 Object Exfiltration from Anonymous User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_S3ObjectExfiltrationByAnonymousUser.yaml) | Medium | Collection | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [S3 bucket access point publicly exposed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_S3BucketAccessPointExposed.yaml) | Medium | Exfiltration | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [S3 bucket exposed via ACL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_S3BucketExposedviaACL.yaml) | Medium | Exfiltration | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [S3 bucket exposed via policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_S3BucketExposedviaPolicy.yaml) | Medium | Exfiltration | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [S3 bucket suspicious ransomware activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_S3Ransomware.yaml) | High | Impact | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`PutObject`](../tables/putobject.md) |
| [S3 object publicly exposed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_S3ObjectPubliclyExposed.yaml) | Medium | Exfiltration | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [SAML update identity provider](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_SAMLUpdateIdentity.yaml) | High | Persistence | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [SSM document is publicly exposed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_SSMPubliclyExposed.yaml) | Medium | Discovery | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Successful API executed from a Tor exit node](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_APIfromTor.yaml) | High | Execution | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Successful brute force attack on S3 Bucket.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_S3BruteForce.yaml) | High | DefenseEvasion | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Suspicious AWS CLI Command Execution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/SuspiciousAWSCLICommandExecution.yaml) | Medium | Reconnaissance | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Suspicious AWS EC2 Compute Resource Deployments](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/SuspiciousAWSEC2ComputeResourceDeployments.yaml) | Medium | Impact | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Suspicious command sent to EC2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_SuspiciousCommandEC2.yaml) | High | Execution | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Suspicious overly permissive KMS key policy created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_OverlyPermessiveKMS.yaml) | High | Impact | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Tampering to AWS CloudTrail logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_LogTampering.yaml) | High | DefenseEvasion | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Unauthorized EC2 Instance Setup Attempt](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_UnauthorizedInstanceSetUpAttempt.yaml) | Medium | ResourceDevelopment | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [User IAM Enumeration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_UserIAMEnumeration.yaml) | Medium | Discovery | [`AWSCloudTrail`](../tables/awscloudtrail.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Bucket versioning suspended](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_BucketVersioningSuspended.yaml) | Impact | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Changes made to AWS IAM objects](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_IAMUserGroupChanges.yaml) | PrivilegeEscalation, DefenseEvasion | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Changes made to AWS IAM policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_IAM_PolicyChange.yaml) | PrivilegeEscalation, DefenseEvasion | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [CreateLoginProfile detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_CreateLoginProfile.yaml) | Persistence | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [CreatePolicyVersion with excessive permissions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_PolicywithExcessivePermissions.yaml) | Privilege Escalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [ECR image scan findings low](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_ECRContainerLow.yaml) | Execution | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [ECR image scan findings medium](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_ECRContainerMedium.yaml) | Execution | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Excessive execution of discovery events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_ExcessiveExecutionofDiscoveryEvents.yaml) | Discovery | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Failed brute force on S3 bucket](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_FailedBruteForceS3Bucket.yaml) | Discovery | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [IAM AccessDenied discovery events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_IAMAccsesDeniedDiscoveryEvents.yaml) | Discovery | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [IAM Privilege Escalation by Instance Profile attachment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_IAM_PrivilegeEscalationbyAttachment.yaml) | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [IAM assume role policy brute force](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_AssumeRoleBruteForce.yaml) | Credential Access | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Lambda UpdateFunctionCode](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_LambdaUpdateFunctionCode.yaml) | Execution | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Lambda function throttled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_LambdaFunctionThrottled.yaml) | Impact | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Lambda layer imported from external account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_LambdaLayerImportedExternalAccount.yaml) | Persistence | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Login profile updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_LoginProfileUpdated.yaml) | Persistence | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Modification of route-table attributes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_ModificationofRouteTableAttributes.yaml) | Defense Evasion | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Modification of subnet attributes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_ModificationofSubnetAttributes.yaml) | Defense Evasion | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Modification of vpc attributes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_ModificationofVPCAttributes.yaml) | Defense Evasion | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Multiple failed login attempts to an existing user without MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_FailedBruteForceWithoutMFA.yaml) | Credential Access | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Network ACL deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_NetworkACLDeleted.yaml) | Defense Evasion | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [New AccessKey created for Root user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_NewRootAccessKey.yaml) | Persistence | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [New access key created to user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_CreateAccessKey.yaml) | Persistence | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Privileged role attached to Instance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_PrivilegedRoleAttachedToInstance.yaml) | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [RDS instance master password changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_RDSMasterPasswordChanged.yaml) | Privilege Escalation | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Risky role name created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_RiskyRoleName.yaml) | Persistence | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [S3 bucket encryption modified](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_S3BucketEncryptionModified.yaml) | Impact | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [S3 bucket has been deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_S3BucketDeleted.yaml) | Impact | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Suspicious EC2 launched without a key pair](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_EC2_WithoutKeyPair.yaml) | Execution | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Suspicious activity of STS Token related to Kubernetes worker node](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_STStoKWN.yaml) | Credential Access | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Suspicious activity of STS token related to EC2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_STStoEC2.yaml) | Credential Access | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Suspicious activity of STS token related to ECS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_STStoECS.yaml) | Credential Access | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Suspicious activity of STS token related to Glue](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_STStoGlue.yaml) | Credential Access | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Suspicious activity of STS token related to Lambda](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_STStoLambda.yaml) | Credential Access | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Suspicious credential token access of valid IAM Roles](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_SuspiciousCredentialTokenAccessOfValid_IAM_Roles.yaml) | InitialAccess, DefenseEvasion | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [Unused or Unsupported Cloud Regions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Hunting%20Queries/AWS_Unused_UnsupportedCloudRegions.yaml) | DefenseEvasion | [`AWSCloudTrail`](../tables/awscloudtrail.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AmazonWebServicesNetworkActivities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Workbooks/AmazonWebServicesNetworkActivities.json) | [`AWSCloudTrail`](../tables/awscloudtrail.md) |
| [AmazonWebServicesUserActivities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Workbooks/AmazonWebServicesUserActivities.json) | [`AWSCloudTrail`](../tables/awscloudtrail.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.7       | 28-07-2025                     | Fix ChangeToVPC **Analytic Rule** to ensure it excludes changes to API Gateway |
| 3.0.6       | 13-06-2025                     | Updated Amazon Web Services S3 Data connector to include details for the default output format. |
| 3.0.5       | 10-02-2025                     | Repackaged to fix ccp grid showing only 1 record and rename of file   |
| 3.0.4       | 13-12-2024                     | Updated title of **Analytic Rule** - AWS_LogTampering.yaml   |
| 3.0.3       | 27-05-2024                     | Updated **Hunting Query** AWS_FailedBruteForceS3Bucket.yaml and **Analytic Rules** for missing TTP   |
| 3.0.2       | 05-04-2024                     | Updated awsS3 **Data connector**, added new Data Type CloudWatch     |
| 3.0.1       | 22-12-2023                     | Added new **Analytic Rule** (AWS Config Service Resource Deletion Attempts)     |
| 3.0.0       | 04-12-2023                     | Updated **Analytical Rule**  AWS_GuardDuty_template with entity mappings     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
