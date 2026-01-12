# Behavior Rules Format Documentation

The behavior detection rules are organized into 3 data source files containing lists of behavior names and titles in markdown table format.

## File Structure

The `Behaviors-rules/` directory contains exactly 3 markdown files, one for each data source:

- `aws_cloudtrail_behaviors.md` - AWS CloudTrail behaviors
- `gcp_auditlogs_behaviors.md` - GCP Audit Logs behaviors
- `commonsecuritylog_behaviors.md` - CommonSecurityLog behaviors

## Markdown File Format

Each data source file contains a markdown table with the following structure:

```markdown
# Data Source Name

Description of the behavior detection rules for this data source

**Total Behaviors**: X

| Name | Title |
|------|-------|
| BehaviorName1 | Human-readable title for behavior 1 |
| BehaviorName2 | Human-readable title for behavior 2 |
| ... | ... |
```

## Field Descriptions

### Name
- **Type**: String
- **Description**: Unique behavior identifier
- **Format**: Always starts with "Behavior" followed by descriptive name
- **Example**: `BehaviorAccessKeyCredentialManagement`

### Title
- **Type**: String
- **Description**: Human-readable descriptive title for the behavior
- **Example**: `IAM Principal Access Key And Service-Specific Credential Management Activity`

## Data Sources

### AWS CloudTrail
- **File**: `aws_cloudtrail_behaviors.md`
- **Description**: Behaviors for AWS CloudTrail data source covering EC2, IAM, S3, EKS, Secrets Manager, and other AWS services

### GCP Audit Logs
- **File**: `gcp_auditlogs_behaviors.md`
- **Description**: Behaviors for GCP Audit Logs data source covering Data Catalog, BigQuery, Compute Engine, IAM, and Resource Manager

### CommonSecurityLog
- **File**: `commonsecuritylog_behaviors.md`
- **Description**: Behaviors for CommonSecurityLog data source covering CyberArk Vault, Palo Alto Threats, and other security appliances

## Example Complete File

```markdown
# AWS CloudTrail Behaviors

List of behavior detection rules for AWS CloudTrail data source

**Total Behaviors**: 184

| Name | Title |
|------|-------|
| BehaviorAccessKeyCredentialManagement | IAM Principal Access Key And Service-Specific Credential Management Activity |
| BehaviorAccessKeyEnumeration | Credential Access – IAM Access Key Last-Used Enumeration Across Multiple Access Keys |
| BehaviorAnonymousS3Burst | Burst of Anonymous Web-Based S3 Object Access from Single External IP |
| BehaviorAssumedRoleAccountAudit | Discovery – Cross-Account AWS Assumed Role Policy Simulation and Evaluation |
| ... | ... |
```

## Notes

- Behavior entries are sorted alphabetically by behavior name within each data source
- All behavior names follow the pattern `Behavior{DescriptiveName}`
- Each behavior includes both the technical name and human-readable title
- Titles provide clear descriptions of what each behavior detects
- Total of 3 markdown files instead of individual behavior files
- Structure focused on behavior name and title organization by data source in table format
