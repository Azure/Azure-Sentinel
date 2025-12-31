# AWSGuardDuty

Reference for AWSGuardDuty table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | AWS |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✓ Yes |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/awsguardduty) |

## Solutions (3)

This table is used by the following solutions:

- [Amazon Web Services](../solutions/amazon-web-services.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Multi Cloud Attack Coverage Essentials - Resource Abuse](../solutions/multi-cloud-attack-coverage-essentials---resource-abuse.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Amazon Web Services S3](../connectors/awss3.md)

---

## Content Items Using This Table (5)

### Analytic Rules (4)

**In solution [Amazon Web Services](../solutions/amazon-web-services.md):**
- [AWS Guard Duty Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Analytic%20Rules/AWS_GuardDuty_template.yaml)

**In solution [Multi Cloud Attack Coverage Essentials - Resource Abuse](../solutions/multi-cloud-attack-coverage-essentials---resource-abuse.md):**
- [Cross-Cloud Suspicious Compute resource creation in GCP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/Cross-CloudSuspiciousComputeResourcecreationinGCP.yaml)
- [Cross-Cloud Unauthorized Credential Access Detection From AWS RDS Login](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/CrossCloudUnauthorizedCredentialsAccessDetection.yaml)
- [Unauthorized user access across AWS and Azure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/Unauthorized_user_access_across_AWS_and_Azure.yaml)

### Workbooks (1)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
