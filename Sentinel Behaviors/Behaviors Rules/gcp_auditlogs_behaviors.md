# GCP Audit Logs Behaviors

List of behavior detection rules for GCP Audit Logs data source

**Total Behaviors**: 103

| Name | Title |
|------|-------|
| BehaviorAnonymousMlflowRunCreation | Execution: Anonymous Browser-Based MLflow Run Creation via Kubernetes API |
| BehaviorAutomationShutdown | Impact – Automation-Initiated Shutdown of Compute Engine Instances via Compute API |
| BehaviorBackupExportCollection | Collection – Managed Service Data Extraction via Backup-Export Operations |
| BehaviorBackupRepoEnumeration | Collection – Cloud Storage Backup Repository Enumeration via Metadata Operations |
| BehaviorBigQueryConfigEnumeration | Discovery – BigQuery Configuration Metadata Enumeration by Single Principal |
| BehaviorBigQueryPatchEvasion | Defense Evasion via High-Frequency BigQuery Observability Table Patch Operations |
| BehaviorBulkBackupDeletion | Impact – Velero DeleteBackupRequest Bulk Modification by Backup Service Accounts |
| BehaviorBulkExternalSecretsDeletion | Defense Evasion – Kubernetes Namespace Controller Bulk Deletion of External Secrets Resources |
| BehaviorBulkGCPDeletion | Impact – Kubernetes-Orchestrated Bulk Deletion of GCP Resources via Config Connector |
| BehaviorBulkInstanceProvisioning | Cloud Compute Bulk Instance Provisioning by Service Account Using Zonal and Regional APIs |
| BehaviorBulkNetworkDeletion | Defense Evasion – Bulk Deletion of Cloud Firewall, VPN, and Load Balancer Resources |
| BehaviorCentralizedAssetEnumeration | Cloud Discovery – Centralized Asset Inventory Enumeration via Cloud Asset APIs |
| BehaviorCloudDataExportSetup | Exfiltration – Managed Cloud Data Export Pipeline Configuration by Service Account |
| BehaviorCloudFederationEnumeration | Identity Discovery – Combined Cloud Identity Toolkit Workload Identity Pool Federation Configuration Enumeration |
| BehaviorCloudIdentityTenantEnumeration | Identity Discovery – Cloud Identity Toolkit Identity Provider Configuration with Tenant Enumeration |
| BehaviorCloudInstanceRecreation | Defense Evasion – Automated Cloud Compute Instance Recreation via Repair and Managed Instance Group APIs |
| BehaviorCloudLoggingExportEnumeration | Cloud Logging Export Configuration Enumeration by Service Account |
| BehaviorCloudPubSubSubscriptionByDefaultServiceAccount | Command and Control – Cloud Pub/Sub Subscription Creation via Compute Engine Default Service Account |
| BehaviorCloudRecommendationEnumeration | Discovery – Cloud Recommender Recommendation Enumeration via Recommender API by Single GCP Principal |
| BehaviorCloudRunJobBurst | Cloud Execution: Repeated Cloud Run Job Creation by Service Account from External IP Address |
| BehaviorCloudStorageAclEnumeration | Cloud Discovery: Principal Enumerates GCP Cloud Storage ACL Custom Resources via Kubernetes API |
| BehaviorCloudTagEnumeration | Discovery – Cloud Resource Tag Configuration Enumeration via Tag APIs |
| BehaviorClusteredAdminScopeChange | Concentrated Google Admin User Access Scope Reconfiguration |
| BehaviorConfigConnectorBurst | Impact – Config Connector Burst Reconfiguration of GCP Compute Network-Security Resources |
| BehaviorContainerVulnEnumeration | Discovery – Container Analysis Vulnerability Occurrence Enumeration via Grafeas ListOccurrences |
| BehaviorCoordinatedCloudVeleroDeletion | Impact – Coordinated Deletion of Cloud SQL Backup Runs and Kubernetes Velero DeleteBackupRequests |
| BehaviorCrossNamespaceIngressWatch | Discovery – Cross-Namespace NGINX Ingress Policy Watch Operations by Kubernetes Service Account |
| BehaviorCrossProjectProvisioning | Cloud Compute Cross-Project Instance Provisioning by Service Account via API |
| BehaviorDatabaseBackupEnumeration | Discovery – Managed Database Backup Resource Enumeration Across GCP Projects |
| BehaviorDataprocEnumeration | Discovery – Dataproc Cluster Agent and Job Status Enumeration via AgentService GetAgent and JobController GetJob |
| BehaviorDataprocNodeBurst | Resource Hijacking – Burst of Dataproc Node Group Creations via NodeGroupController API |
| BehaviorExternalKmsAccess | Credential Access – Cloud KMS Key Read and Management Operations from External IP Addresses |
| BehaviorExternalSecretCreation | Credential Access – Kubernetes ExternalSecret Resource Creation from Kubectl Client |
| BehaviorGCPProjectWideEnumeration | Discovery – Single GCP Principal Enumerates Data Catalog, BigLake, BigQuery Reservations, and Notebook Environments in One Project |
| BehaviorGCPResourceCreation | Resource Development – GCP Organization, Project, or Tag Creation via Cloud Resource Manager |
| BehaviorGKEConfigEnumeration | Discovery – GKE ClusterPodMonitoring and ClusterNodeMonitoring Configuration Enumeration in Kubernetes Cluster |
| BehaviorGKEConfigSyncDiscovery | Kubernetes Configuration Source Discovery via GKE ConfigSync RootSync Resources |
| BehaviorGcpKeyDeletionEvasion | Defense Evasion – Repeated GCP Service Account Key Deletions via gcloud CLI |
| BehaviorGcsfuseBucketEnumeration | Collection – Cloud Storage Bucket Layout Enumeration via gcsfuse by Single GCP Principal |
| BehaviorGitOpsCRDDiscovery | Discovery – Kubernetes Application CRD Enumeration by Unattributed GitOps Controller Client |
| BehaviorGitOpsMassResourcePatch | Execution – GitOps Controller Service Account Patching GitHub Actions Runner Autoscaler, RunnerDeployment, and Namespace Resources |
| BehaviorGitOpsOperatorDiscovery | Discovery: GitOps Controller Enumeration of Confluent Kafka and F5 AppProtect DoS Operator Resources |
| BehaviorGkeMultiClusterDiscovery | Discovery – GKE Multi-Cluster Service Import and Ingress Configuration Enumeration in Kubernetes Cluster |
| BehaviorGkeTrafficEnumeration | Discovery – GKE Load Balancer Traffic Policy Enumeration in Kubernetes Cluster |
| BehaviorHighFrequencyDnsDeletion | Defense Evasion via High-Frequency Cloud DNS Resource Record Set Deletions by GKE Robot Service Accounts |
| BehaviorHighVolumeKMSOperations | Key Management – High-Volume Cloud KMS Cryptographic Operations by Service Accounts |
| BehaviorIamAccountDiscovery | Cloud Account Discovery via Repeated IAM GetServiceAccount Operations on Service Accounts |
| BehaviorIamRoleEnumeration | Permission Groups Discovery in GCP via IAM Role Listing and Grantable Role Queries |
| BehaviorIngressLeasePersistence | Persistence via Update Operations on Kubernetes Ingress Controller Leader Election Lease Objects |
| BehaviorInternalServicePolicyTag | Internal Network Service Account Administration of Cloud Data Catalog PolicyTagManager Resources |
| BehaviorK8sAdmissionEnumeration | Discovery – Enumeration of Kubernetes Admission Control and Policy Configuration by Cluster Service Account |
| BehaviorK8sAppDeliveryDiscovery | Discovery – Kubernetes Principal Enumeration of Application Delivery and Autoscaling Configuration Resources |
| BehaviorK8sPolicyEnumeration | Security Policy Discovery: Principal Enumerates Kubernetes Gatekeeper Constraints and Istio Authorization Policies |
| BehaviorK8sPolicyModification | Defense Evasion – Kubernetes Security Policy Custom Resource Modification |
| BehaviorK8sSecurityEnumeration | Discovery – Kubernetes Security Posture Custom Resource Enumeration |
| BehaviorK8sSecurityFleetDiscovery | Discovery – Enumeration of Kubernetes Security, Fleet, and Observability Custom Resources |
| BehaviorK8sTokenReuse | Credential Access – Kubernetes Service Account Token Reuse from Public and In-Cluster IP Addresses |
| BehaviorKubeCustomScan | Discovery – Kubernetes Service Account Initiates Wiz Scanning via Custom Resource Creation |
| BehaviorKubectlServiceAccountWrite | Lateral Movement – Kubectl Client Use of Kubernetes Service Account Credentials for Kubernetes Resource Writes |
| BehaviorKubernetesCRDEnumeration | Discovery – Kubernetes API Extension Schema Enumeration via CustomResourceDefinitions |
| BehaviorKubernetesCloudTeardown | Impact – Kubernetes‑Orchestrated Deletion of Google Cloud Load Balancing and Data Transfer Infrastructure |
| BehaviorKubernetesCrossplaneDiscovery | Discovery – Kubernetes Principal Enumeration of Crossplane Configuration & Managed Cloud Resources |
| BehaviorKubernetesReplicaEnumeration | Discovery – Kubernetes Workload Replica/Revision Enumeration |
| BehaviorKubernetesResourceEnumeration | Discovery – Kubernetes Workload and Storage Resource Enumeration by Monitoring Service Accounts |
| BehaviorKyvernoUpdateRequestEnumeration | Defense Discovery – Kyverno Policy Execution State Enumeration via UpdateRequest Resources in Kubernetes |
| BehaviorMultipartUploadGCS | Multipart Object Upload Sequence to Google Cloud Storage by Service Account |
| BehaviorMultipleIPAdminActivity | IAM Admin Activity by a Single GCP Service Account From Multiple Source IP Addresses |
| BehaviorMultipleUsersBackupAccess | Collection – Multiple Interactive GCP Users Access Cloud Storage Backup Buckets and Managed Backup Folders |
| BehaviorNetworkResourceDiscovery | GKE Networking Control Plane Resource Discovery |
| BehaviorOrgPolicyClearGCP | Defense Evasion – GCP Organization Policy Constraint Cleared on Project via Config Connector |
| BehaviorOsConfigEnumeration | Discovery – OSConfig API Enumeration of VM OS Inventories and Policy Assignments by Single GCP Principal |
| BehaviorPodLogEnumeration | Collection – Kubernetes Pod Log Access Across Multiple Pods by a Single Principal |
| BehaviorPubSubAuditLogMetadataAccess | Collection – Pub/Sub Audit Log Subscription Metadata Access by Single GCP Principal |
| BehaviorPublicAccessK8sToken | Credential Access – Public IP Access to Kubernetes Service Account Token Secrets in System Namespaces |
| BehaviorRapidIamModification | Privilege Management – Rapid IAM Policy Changes Across Multiple GCP Resources by Single Identity |
| BehaviorRapidSSLCertCreation | Credential Access – Rapid Compute Engine SSL Certificate Creation by Container Engine Robot Accounts |
| BehaviorRapidSecretDestruction | Impact – Rapid Destruction of Cloud Secret Manager Secret Versions by Single Principal |
| BehaviorRepeatedBigQueryCancellations | Impact – Repeated BigQuery Job Cancellations by GCP Principal |
| BehaviorRepeatedWorkflowTaskResultDeletion | Defense Evasion – Repeated DeleteCollection of Kubeflow Workflow Task Results by Argo Workflow Controller Service Account |
| BehaviorRuntimeClassEnumeration | Discovery – RuntimeClass Configuration Enumeration via Kubernetes Principals |
| BehaviorSecretEnumeration | Credential Access – Secret Manager Secret Inventory Enumeration |
| BehaviorSequentialIamPolicyRetrieval | Cloud Discovery – Sequential IAM Policy Retrieval for Database Instance and Child Resource by Same Principal |
| BehaviorServerlessEnvironmentDiscovery | Cloud Discovery – Serverless Execution Environment Enumeration via Sequential List and Get Operations |
| BehaviorServiceAccountAnalyticsDeletion | Impact – Service Account Deletion of Cloud Analytics and Machine Learning Resources |
| BehaviorServiceAccountDualResourcePolicyChange | Privilege Management – Service Account IAM Policy Changes on GCP Compute Disk and Snapshot in Same Project |
| BehaviorServiceAccountIamEnumeration | Identity Discovery – Service Account Performs Cloud Asset IAM Policy Search Across Multiple Projects |
| BehaviorServiceAccountKeyEnumeration | Credential Access – Service Account Key Listing Followed by Service Account Enumeration by Same Principal |
| BehaviorServiceAccountPolicyChange | Privilege Management – Service Account IAM Policy Change on GCP Service Account via IAM API |
| BehaviorServiceAccountRBACAdmin | Kubernetes Service Account Performing RBAC Role and High-Privilege Binding Administration |
| BehaviorServiceAccountRunEnumeration | Cloud Discovery – Service Account Enumerating Cloud Run Services via Services.ListServices |
| BehaviorServiceAccountWatch | Credential Access – Targeted Watch Operations on Specific Kubernetes ServiceAccount Resources |
| BehaviorSharedIPEnumeration | Discovery – Shared Client IP Enumerates Compute Subnet and Database Backup Storage Bucket Across GCP Admin Accounts |
| BehaviorSparkPodProvisioning | Execution – Kubernetes Spark Application Pod and Service Provisioning Sequence |
| BehaviorSubjectAccessReviewEnumeration | Kubernetes Scheduler Permission Discovery via Repeated SubjectAccessReview Creation |
| BehaviorTerraformIamModification | Privilege Management – Terraform-Orchestrated IAM Configuration Across GCP Resources |
| BehaviorUnattributedKubeStateEnumeration | Collection – Unattributed Kube-State-Metrics Enumeration of Cluster Workload, Storage, and Policy Resources |
| BehaviorUserSuspensionNoClientMeta | Account Management & Defense Evasion – Workspace User Suspension via Admin API with Missing Client Metadata |
| BehaviorUserUnsuspendPhoneChange | Account Manipulation – GCP Directory User Unsuspension Followed by Phone Number Change |
| BehaviorVeleroBackupDeletion | Impact – Velero Backup Deletion Followed by Delete-Request Resource Creation |
| BehaviorVertexAIDeletion | Impact – Terraform/Config Connector Service Account Deletion of Vertex AI Index and Endpoint Resources via AI Platform API |
| BehaviorVpcSubnetworkProvisioning | VPC Network Creation Followed by Subnetwork Provisioning via Deployment Manager Service Account |
| BehaviorWebhookConfigReplace | Kubernetes Mutating Admission Webhook Configuration In-Place Replacement |
| BehaviorWorkloadIdentityEnumeration | Identity Discovery – Workload Identity Pool and Provider Configuration Enumeration by Same Principal |
