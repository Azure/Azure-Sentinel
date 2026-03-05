# AWS CloudTrail Behaviors

List of behavior detection rules for AWS CloudTrail data source

**Total Behaviors**: 184

| Name | Title |
|------|-------|
| BehaviorAccessKeyCredentialManagement | IAM Principal Access Key And Service-Specific Credential Management Activity |
| BehaviorAccessKeyEnumeration | Credential Access – IAM Access Key Last-Used Enumeration Across Multiple Access Keys |
| BehaviorAmiLaunchRestriction | Impact via EC2 AMI Availability Restriction |
| BehaviorAmiSnapshotPolicyUpdate | EC2 AMI and Snapshot Sharing Settings Updated by AWS Declarative Policy |
| BehaviorAnonymousS3Burst | Burst of Anonymous Web-Based S3 Object Access from Single External IP |
| BehaviorAssumedRoleAccountAudit | IAM Account Summary Retrieval and Credential Report Generation by Assumed Role |
| BehaviorAssumedRolePolicySimulation | IAM Assumed Role Performing Multiple Policy Simulation Calls |
| BehaviorAssumedRolePublicAccessQuery | EC2 Image and Snapshot Public Access Configuration Queried by Assumed Role |
| BehaviorAwsPolicyEnumeration | Discovery – Paginated Enumeration of AWS-Managed IAM Policies via ListPolicies |
| BehaviorAwsVpnVpcEnumeration | Discovery – Broad AWS EC2 VPN and VPC Endpoint Permission Enumeration by Single Principal |
| BehaviorBrowserNonMfaEc2CapacityAccess | Discovery – Browser-Based Non-MFA Assumed Role Access to EC2 Capacity Management APIs |
| BehaviorBulkRouteTableReassignment | VPC Subnet Route Table Associations Replaced in Bulk by Single IAM Role |
| BehaviorBulkS3CopyActivity | Bulk S3 Object Copy and Replication Configuration Activity |
| BehaviorBulkS3Deletion | Bulk S3 Object Deletion Activity by Single Principal |
| BehaviorBulkS3Tagging | Impact – Bulk S3 Object Tagging Modifications by Single IAM Principal |
| BehaviorBulkSecretDeletion | Bulk Immediate Deletion of AWS Secrets Manager Secrets by IAM Principal |
| BehaviorBulkSnapshotCreation | Collection – Concentrated EC2 Snapshot and Image Creation Activity by Single IAM Role |
| BehaviorCloudCidrAllocation | Cloud Network Address Space Management via EC2 IPAM Pool CIDR Allocation |
| BehaviorCloudIPAMEnumeration | Discovery of Cloud Network Address Management via EC2 IPAM and IP Pool Enumeration |
| BehaviorCloudPermissionDiscovery | Cloud Permission Boundary Discovery via Repeated SCP-Denied EC2 Transit Gateway and VPC Peering Queries |
| BehaviorCloudPermissionsEnumeration | Cloud Permissions Discovery via IAM Access Reporting Features |
| BehaviorCloudPrivilegeEnumeration | Cloud Privilege Enumeration via Repeated Unauthorized EC2 Management API Calls by Single IAM Role |
| BehaviorCloudTopologyEnumeration | Cloud Discovery via EC2 VPC and Subnet Topology Enumeration |
| BehaviorConcentratedRouteChanges | Concentrated Transit Gateway-VPC Route Configuration Changes by Single Identity |
| BehaviorConcentratedUserPolicyChanges | AWS Actor Performing Concentrated Inline User Policy Management |
| BehaviorCoordinatedAccessRemoval | Impact - IAM Identity Access Deprovisioning via Coordinated Configuration Removal |
| BehaviorCredentialReportRetrieval | Credential Access – IAM Credential Report Generation and Retrieval |
| BehaviorCrossAccountAccessEnumeration | Cloud Discovery – Cross-Account EC2 Verified Access Resource Enumeration from Shared Public Source IP |
| BehaviorCrossAccountIAMDiscovery | Discovery – Cross-Account IAM Access Surface Enumeration from Shared Source IP |
| BehaviorCrossAccountInterfaceAttach | Cross-Account EC2 Network Interface Attachment for Lateral Movement |
| BehaviorCrossAccountPolicyEnumeration | IAM Policy Enumeration Across Multiple AWS Accounts by Single Client |
| BehaviorCrossAccountS3GrantsEnumeration | Discovery – Cross-Account S3 Access Grants Metadata Enumeration by Single Principal |
| BehaviorCrossServiceAccessEnumeration | Discovery – Broad Cross-Service IAM Access Enumeration via ListPoliciesGrantingServiceAccess |
| BehaviorCrossUserCredentialManagement | Credential Management – IAM Principals Managing Programmatic Credentials for Other IAM Users |
| BehaviorCrossUserMfaEnumeration | Credential Management Enumeration via Cross-User AWS IAM MFA Device Queries |
| BehaviorCrossplanePodIdentityChanges | EKS Pod Identity Association Changes by Crossplane Automation Client |
| BehaviorDedicatedHostModification | EC2 Dedicated Host Enumeration and Modification by Single IAM Role |
| BehaviorEBSConfigDiscovery | Cloud Discovery – EBS Recovery and Storage Lifecycle Configuration Enumeration by Single Principal |
| BehaviorEC2BulkDeletion | Concentrated EC2 Resource Deletion Activity by Single AWS Identity |
| BehaviorEC2DryRunDiscovery | Cloud Permission Discovery via Repeated EC2 Capacity Management DryRun Requests |
| BehaviorEC2ReadBurst | Concentrated EC2 Describe and Get API Usage by IAM Principal |
| BehaviorEC2ReservationModification | Concentrated EC2 Capacity Reservation and Fleet Modifications by Assumed Role |
| BehaviorEKSAccessAutomation | EKS Access Entry Configuration Changes by GitHub Actions Automation Across Clusters |
| BehaviorEKSAccessEnumeration | Permission Discovery – EKS Access Configuration Catalog Enumeration by Single Principal |
| BehaviorEKSAddonNodegroupDeletion | Impact – Sequential Deletion of EKS Addon and Nodegroup in the Same Cluster |
| BehaviorEKSConfigAndNodegroupUpdate | EKS Cluster Configuration Update Followed by Nodegroup Version Change by Same IAM Principal |
| BehaviorEKSIdentityEnumeration | Cloud Identity Discovery – EKS Identity Configuration Enumeration Sequence |
| BehaviorEKSPrivilegeProbe | Cloud Privilege Discovery – Repeated Unauthorized EKS Administrative Operations by Single Principal |
| BehaviorEbsConfigEnumeration | EC2 EBS Volume and Encryption Configuration Survey by IAM Role |
| BehaviorEbsEncryptionConfigChange | Defense Evasion – Sequence of EC2 EBS Default Encryption and KMS Key Configuration Changes |
| BehaviorEbsEncryptionToggle | AWS Account Toggles EBS Default Volume Encryption Setting |
| BehaviorEbsInventoryEnumeration | Cloud Discovery – Broad EBS Snapshot and Volume Inventory Enumeration by Single Principal |
| BehaviorEbsKmsKeyConfigBurst | Concentrated EBS Default KMS Key Configuration Activity by Single AWS Principal |
| BehaviorEbsResourceEnumeration | Cloud Discovery – EBS Snapshot or Volume Enumerated by Multiple Distinct Principals |
| BehaviorEbsSnapshotPermissionAudit | EBS Snapshot Sharing Permissions Modified and Evaluated by AWS Access Analyzer |
| BehaviorEc2AclTerraformBurst | EC2 Network ACL Management via Terraform from Single Source IP |
| BehaviorEc2InterfacePermissionDiscovery | Discovery – EC2 Network Interface Sharing Permission Enumeration via DescribeNetworkInterfacePermissions |
| BehaviorEc2NetworkEnumeration | Cloud Discovery – EC2 Network Topology and Performance Configuration Enumeration |
| BehaviorElasticIPAccessDenied | Repeated EC2 Elastic IP Management Access Denied Errors for Same Principal |
| BehaviorEndpointCreationEnumeration | EC2 Instance Connect Endpoint Creation Followed by Endpoint Enumeration |
| BehaviorEphemeralS3Endpoint | Short-Lived S3 Storage Endpoint Creation and Removal |
| BehaviorFederationProviderAutomation | IAM Federation Provider Configuration via Shared Automation Client Across AWS Accounts |
| BehaviorFederationProviderEnumeration | IAM Federation Provider Enumeration by Single Principal |
| BehaviorFocusedS3Enumeration | Data Discovery – Focused S3 Object Enumeration within Single Bucket Prefix |
| BehaviorFullAccessPolicyAttachment | Privilege Escalation via AWS Managed FullAccess Policy Attachment to IAM Identities |
| BehaviorGatewayAttach | EC2 Internet Gateway Created And Attached To VPC |
| BehaviorGatewayEnumerationBurst | Internet-Facing Gateway Enumeration via EC2 Describe APIs |
| BehaviorGatewayEnumerationModification | EC2 Customer Gateway Enumeration Followed by Configuration Change Operations |
| BehaviorGatewayPropagationToggle | Virtual Private Gateway Route Propagation Toggled for Single VPC Route Table |
| BehaviorGroupCreationRapidUserAdd | IAM Group Creation Followed by Rapid User Membership Assignment |
| BehaviorIaCSecurityGroupManagement | Infrastructure-as-Code EC2 Security Group Rule Management by Assumed Role |
| BehaviorIamAttributeEnumeration | Cloud Identity Discovery via IAM Attribute Enumeration |
| BehaviorIamEnumerationBurst | Cloud Discovery – Consolidated IAM Policy and Access Enumeration by Single Principal |
| BehaviorIamGroupPolicyEnumeration | Discovery – IAM Group Policy Enumeration Across Multiple Groups by Single Principal |
| BehaviorIamKeyCertificateEnumeration | Concentrated AWS IAM Key and Certificate Enumeration Activity |
| BehaviorIamKeyEnumeration | IAM Public Key Configuration Enumeration within AWS Account |
| BehaviorIamKeyMultiUserChange | Source IP Initiating Multiple IAM Access Key Lifecycle Changes Across Users |
| BehaviorIamMassDeletion | Impact - Concentrated IAM Identity and Configuration Deletion by Single Principal |
| BehaviorIamPermissionEnumeration | Discovery – IAM Identity Permission Enumeration |
| BehaviorIamProfileDisassociation | EC2 IAM Instance Profile Disassociation via SSM Automation Role |
| BehaviorIamRoleBurstChanges | Cloud IAM Role Configuration Changes by Single Assumed Role Session |
| BehaviorIamRoleDeletionStatusCheck | Cloud IAM service-linked role deletion with status check sequence |
| BehaviorIamTagEvasion | Defense Evasion via IAM Identity Tag Manipulation Activity |
| BehaviorIdentityPolicyEnumeration | IAM Identity Permission Association Enumeration via Group-Policy Listing |
| BehaviorImageEnumerationBurst | Cloud Infrastructure Discovery – Multi-API EC2 AMI and Image Metadata Enumeration by Single Principal |
| BehaviorImageSnapshotDeletion | Impact – EC2 Image Deregistration Followed by Snapshot Deletion by Same Role |
| BehaviorInstanceProfileBurst | EC2 Instance Profile Lifecycle Operations Clustered by Single IAM Principal |
| BehaviorInstanceProfileEscalation | Privilege Escalation via IAM Instance Profile Association Manipulation |
| BehaviorIpamAddressSpaceManagement | EC2 IPAM Address Space Management Activity by Single Principal |
| BehaviorIpv6PoolAssignment | EC2 IPv6 Pool Enumeration Followed by Network Interface IPv6 Assignment |
| BehaviorLoginProfilePasswordChange | Account Manipulation – IAM Login Profile Creation Followed by User-Initiated Password Change |
| BehaviorMassLoginProfileModification | Account Manipulation – Multiple IAM User Login Profiles Created or Reset by Single Principal |
| BehaviorMassTagModification | IAM Principal Modifies Tags on Multiple IAM Resources Within a Short Time Window |
| BehaviorMassVolumeDeletion | Impact – Multiple EBS Volume Deletions via VPC Endpoint by Assumed Role |
| BehaviorMetadataOptionsMassChange | EC2 Instance Metadata Options Modified by Same IAM Role Across Multiple Instances |
| BehaviorMirrorSessionErrorEnumeration | EC2 Traffic Mirroring Session Creation Error Followed by Traffic Mirroring Configuration Enumeration by Same IAM Role |
| BehaviorMissingS3Protections | Multiple S3 Buckets in Single Account Reporting Missing Protection Configurations |
| BehaviorMulticastGroupEnumeration | Cloud Multicast Group Membership Discovery via Repeated Transit Gateway Multicast Group Searches |
| BehaviorNetworkEnumerationBlocked | Network Access Control Enumeration Blocked by Service Control Policy |
| BehaviorNetworkInterfaceRapidReattach | EC2 Network Interface Rapid Reattachment to Different Instances in Single AWS Account |
| BehaviorNetworkVisibilityEnumeration | EC2 Network Insights with Traffic Mirroring Configuration Enumeration by Same IAM Role |
| BehaviorNonMFAPrivilegeEscalation | Privilege Escalation via IAM Permissions Changes from Non-MFA Sessions |
| BehaviorPasswordPolicyChange | AWS IAM Account Password Policy Read Followed by Modification |
| BehaviorPasswordRetrievalConsoleAccess | EC2 Instance Password Retrieval Followed by Console Data Access |
| BehaviorPermissionsBoundaryAbuse | IAM Permissions Boundary Account Manipulation by Single Principal |
| BehaviorPolicyChangeFailures | IAM Principal With Multiple Failed Policy Management Operations |
| BehaviorPolicyInspectionModification | Secrets Manager Secret Resource Policy Inspection Followed by Change by Same Principal |
| BehaviorPolicyReadDelete | S3 Bucket Policy Retrieval Followed by Policy Deletion for Same Bucket |
| BehaviorPrefixListEnumeration | EC2 Prefix List Resource Enumeration by Assumed Role |
| BehaviorPrivateConnectivityEnumeration | Cloud Private Connectivity Discovery via VPC Endpoint and Local Gateway Enumeration |
| BehaviorPrivateEndpointEnumeration | Cloud Private Endpoint Exposure Discovery via EC2 VPC Endpoint Enumeration |
| BehaviorRapidLifecyclePolicyFlip | Rapid S3 Bucket Lifecycle Policy Creation and Removal on Single Bucket |
| BehaviorRapidNetworkInsightsDeletion | EC2 Network Insights Path and Analysis Deleted by Same IAM Role in Short Interval |
| BehaviorRapidRoleChanges | Multiple IAM Role Management Operations on Single Role Within Short Interval |
| BehaviorRapidRuleChange | Cloud Firewall (Security Group) – Rapid Ingress and Egress Rule Modifications on Same Group |
| BehaviorRapidStoragePolicyAddition | Collection Staging via High-Frequency IAM Inline Storage Access Policy Additions |
| BehaviorRelaxedMetadataAccess | Credential Access via Relaxed EC2 Instance Metadata Service Controls |
| BehaviorRemoteAccessExposure | Lateral Movement – EC2 Remote Administration Port Exposure via Network Access Controls |
| BehaviorRepeatedAnonymousS3Preflight | Initial Access – Repeated Anonymous S3 CORS Preflight Requests for a Bucket Object Prefix |
| BehaviorRepeatedBlockAccessChange | Cloud Configuration: Repeated EC2 Snapshot and Image Block Public Access Setting Changes |
| BehaviorRepeatedEC2EnumerationDenied | Cloud Discovery – Repeated EC2 Enumeration Attempts Blocked by Authorization Policies |
| BehaviorRepeatedEC2PolicyUnauthorized | Repeated Unauthorized EC2 Network Access Policy Operations by Same IAM Role |
| BehaviorRepeatedEC2UnauthorizedManagement | Repeated Unauthorized EC2 Spot and Reserved Instance Management Operations |
| BehaviorRepeatedEKSAccessRemoval | Account Access Removal via Repeated EKS DeleteAccessEntry Operations by Same IAM Role |
| BehaviorRepeatedFlowLogsDeletion | Defense Evasion – Repeated VPC Flow Logs Deletion via EC2 DeleteFlowLogs API |
| BehaviorRepeatedGetLoginProfileFailures | AWS IAM Principal Performing Repeated GetLoginProfile Calls Without Existing Login Profiles |
| BehaviorRepeatedIAMWriteFailures | Privilege Escalation via Repeated Unauthorized IAM Configuration Modification Attempts |
| BehaviorRepeatedIamMgmtFailures | Repeated unauthorized IAM role and instance profile management by single principal |
| BehaviorRepeatedMirrorSessionFailures | Repeated EC2 Network Traffic Mirroring Session Creation Failures by Same IAM Role |
| BehaviorRepeatedNetworkAnalysisAdmin | Network Discovery – Repeated EC2 Network Insights Analyses by Privileged Administrator Role |
| BehaviorRepeatedNetworkInterfaceModificationFailures | Repeated EC2 Network Interface Attribute Modification Failures by IAM Role |
| BehaviorRepeatedObjectLockQueries | Repeated S3 Object Lock Retention Queries by Role on Single Bucket |
| BehaviorRepeatedPolicyStatusErrors | Repeated S3 Access Point Policy Status Queries for Non-Existent Policies by Single Principal |
| BehaviorRepeatedS3ConfigErrors | Repeated S3 Bucket Configuration Operations Returning Errors by Single AWS Principal |
| BehaviorRoleEnumerationBurst | IAM Role Enumeration and Configuration Retrieval by Assumed Role Session |
| BehaviorRoleTrustAndPermissionChange | Privilege Escalation via IAM Role Trust Policy Update Followed by Role Permission Modification |
| BehaviorS3AccessDeniedBurst | Repeated S3 Bucket Access Denied by Service Control Policy |
| BehaviorS3AccessEnumeration | S3 Access Point and Grants Configuration Enumeration by Single IAM Role |
| BehaviorS3AccessGrantAbuse | Collection via Repeated S3 GetDataAccess ReadWrite Grants on Broad Bucket Scope |
| BehaviorS3AccessGrantsEnumeration | Discovery – S3 Access Grants Metadata Enumeration by Multiple Principals in Same Account |
| BehaviorS3AccessPointDiscovery | Cloud Storage Discovery – S3 Access Point Configuration Enumeration |
| BehaviorS3AclPolicyEnumeration | S3 Bucket ACL and Policy Enumeration by Assumed Role |
| BehaviorS3BatchJobEnumeration | S3 Batch Operations Job Enumeration Via ListJobs And DescribeJob APIs |
| BehaviorS3BucketEnumeration | S3 Bucket Metadata Enumeration by Assumed Role |
| BehaviorS3ConfigEnumeration | S3 Bucket Configuration Enumeration via Multiple GetBucket Management APIs |
| BehaviorS3ConfigMissing | S3 Bucket Queried With Multiple Missing Protection Configurations |
| BehaviorS3CorsDiscovery | Cloud Storage Discovery – S3 CORS Configuration Read Following Anonymous Preflight Request |
| BehaviorS3GovernanceEnumeration | Cloud Service Discovery – S3 Governance Feature and Tag Enumeration via S3 Control |
| BehaviorS3LensRecon | Data Discovery – Focused S3 Storage Lens Dashboard Enumeration |
| BehaviorS3ObjectLockAfterCreate | S3 Object Creation Followed by Object Lock Retention Configuration |
| BehaviorS3PermissionUpdateFailures | S3 Cloud Storage Permission Update Failures Across Buckets |
| BehaviorS3RetentionAbuse | Inhibit System Recovery – Multiple S3 Object Lock Retention Modifications by Single Principal |
| BehaviorS3SecurityEnumeration | Cloud Storage Discovery – S3 Bucket Security Configuration Enumeration |
| BehaviorS3SelectQueryBurst | Concentrated S3 SelectObjectContent Queries by Single Role and Bucket |
| BehaviorSecretRotationDisruption | Defense Evasion – AWS Secrets Manager Secret Rotation Disruption |
| BehaviorSecretRotationUpdate | AWS Secrets Manager Secret Version Rotation via Value Update and Stage Change |
| BehaviorSecretsManagerBulkOperations | AWS Secrets Manager Secret Lifecycle Operations by IAM Principal |
| BehaviorSecretsManagerBulkUpdate | Credential Access – High-Frequency AWS Secrets Manager Secret Value Updates by Single Assumed Role Session |
| BehaviorSecretsManagerRapidRetrieval | AWS Secrets Manager High-Frequency Secret Value Retrieval on Single Secret by Same Role |
| BehaviorSecretsPolicyValidation | Privilege Management – AWS Secrets Manager Secret Resource Policy Retrieval Followed by Policy Validation |
| BehaviorSecretsReplicationExfiltration | Exfiltration – AWS Secrets Manager Secret Replicated to Additional Region via Authenticated Session |
| BehaviorSecretsTagRemoval | Defense Evasion – AWS Secrets Manager Secret Tags Removed by IAM User Session |
| BehaviorSerialConsoleMetadataQuery | EC2 Serial Console Status and Instance Metadata Defaults Queried by Same Principal |
| BehaviorServiceRoleDeletionPolling | Defense Evasion - AWS Service-Linked Role Deletion with Status Polling |
| BehaviorStorageLensReadModify | Storage Lens Configuration Read Followed by Modification by Same AWS Account |
| BehaviorSubnetEIPReconfig | Coordinated Subnet Route-Elastic IP Reconfiguration in Single Session |
| BehaviorTagEnumerationModification | IAM Principal Enumerates and Modifies Tags on IAM Resources Within a Short Interval |
| BehaviorTagRemovalEvasion | Defense Evasion – IAM Identity Resource Tag Removal of Ownership and Access Key Metadata |
| BehaviorTransitGatewayConfigBurst | AWS EC2 Transit Gateway Configuration Option Changes By Single Principal |
| BehaviorTransitGatewayEnumeration | AWS EC2 Transit Gateway Configuration Enumeration by Single Principal |
| BehaviorTransitGatewayRouteManipulation | AWS EC2 Transit Gateway Route Table Association and Propagation Changes by Single Principal |
| BehaviorTransitGatewayRouteModification | VPC Route Table Routes to Transit Gateway Modified by Single IAM Principal |
| BehaviorVPCDefaultRouteTableDeletion | VPC Default Route Removed Followed by Route Table Deletion by Single IAM Principal |
| BehaviorVPCPeeringDNSResolution | Lateral Movement via VPC Peering Acceptance and Remote DNS Resolution Enablement |
| BehaviorVpcBlockAccessEnumeration | AWS EC2 VPC Block Public Access Configuration Enumeration by Integration Role Session |
| BehaviorVpcBulkDeletion | Impact – EC2 VPC Network Infrastructure Bulk Deletion Sequence |
| BehaviorVpcCidrReassignment | AWS EC2 VPC CIDR Block Disassociation and Association by Same Role |
| BehaviorVpcEndpointAdminActivity | AWS VPC Endpoint Management Operations by Single IAM Role |
| BehaviorVpcEndpointPermissionChange | EC2 VPC Endpoint Service Permission Enumeration Followed by Modification |
| BehaviorVpcEndpointServiceCreation | Network Infrastructure: New Interface VPC Endpoint Service Backed by Network Load Balancer |
| BehaviorVpcGatewayAttachment | Cloud Network Configuration – VPC Internet Gateway Creation Followed by Attachment |
| BehaviorVpcSubnetDeletion | AWS EC2 VPC and Subnet Deletion by Same Role Session |
| BehaviorVpnConfigInspection | External Remote Services – AWS EC2 Site-to-Site VPN Configuration Follow-Up Inspection |
| BehaviorVpnEnumerationBurst | External Remote Services – AWS EC2 VPN Infrastructure Enumeration by Single IAM Principal |
