| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.13      | 03-09-2026                     | Added new AWS GuardDuty **Hunting Queries** for high-severity findings, EKS privilege escalation and credential access, and S3 public exposure; repackaged the solution after incorporating the latest upstream changes. |
| 3.0.12      | 26-08-2026                     | Updated **Analytic Rules** AWS_LogTampering.yaml (successful log-tampering, High) and AWS_ClearStopChangeTrailLogs.yaml (failed log-tampering attempts, Low) with expanded event coverage and tiered severity; removed duplicate **Analytic Rule** AWS_ConfigServiceResourceDeletion.yaml; refreshed the Data Connectors section in the solution UI (createUiDefinition) |
| 3.0.11      | 11-08-2026                     | Fixed the AWS WAF Data Connector last-data-received query by removing an invalid test filter. |
| 3.0.10      | 19-05-2026                     | Added non-analytics tier queries to Amazon Web Services S3 **Data Connector** to support Basic/Auxiliary plan tables. |
| 3.0.9       | 18-05-2026                     | Update AWS **Hunting Queries** and **Workbooks** for Quality     |
| 3.0.8       | 13-01-2026                     | Updated non-functional links from **Analytic rules** and **Hunting query** |
| 3.0.7       | 28-07-2025                     | Fix ChangeToVPC **Analytic Rule** to ensure it excludes changes to API Gateway |
| 3.0.6       | 13-06-2025                     | Updated Amazon Web Services S3 Data connector to include details for the default output format. |
| 3.0.5       | 10-02-2025                     | Repackaged to fix ccp grid showing only 1 record and rename of file   |
| 3.0.4       | 13-12-2024                     | Updated title of **Analytic Rule** - AWS_LogTampering.yaml   |
| 3.0.3       | 27-05-2024                     | Updated **Hunting Query** AWS_FailedBruteForceS3Bucket.yaml and **Analytic Rules** for missing TTP   |
| 3.0.2       | 05-04-2024                     | Updated awsS3 **Data connector**, added new Data Type CloudWatch     |
| 3.0.1       | 22-12-2023                     | Added new **Analytic Rule** (AWS Config Service Resource Deletion Attempts)     |
| 3.0.0       | 04-12-2023                     | Updated **Analytical Rule**  AWS_GuardDuty_template with entity mappings     |
