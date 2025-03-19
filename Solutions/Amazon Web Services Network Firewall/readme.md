## Overview
This guide explains how to integrate AWS Network Firewall logs with Microsoft Sentinel using an AWS CloudFormation template. The template automates the deployment of necessary resources to collect, process, and forward logs to Sentinel.

## Prerequisites
Before deploying, ensure you have:
- An AWS account with permissions to deploy CloudFormation stacks.
- An existing AWS Network Firewall setup.
- An active Microsoft Sentinel Log Analytics Workspace ID.
- Required IAM permissions to configure AWS services.

## CloudFormation Templates
- Download the CloudFormation templates and deploy them in your AWS environment.
  
1. OIDC Web Identity ProviderOIDC Web Identity Provider

   The OIDC (OpenID Connect) Web Identity Provider allows AWS services to securely authenticate using an external identity provider without managing long-term credentials. The CloudFormation template configures OIDC as a trusted identity provider in AWS, enabling secure role-based access for forwarding AWS Network Firewall logs to Microsoft Sentinel.
   
2. AWS Network Firewall Configuration

      The AWS Network Firewall Configuration template sets up logging for AWS Network Firewall by creating an S3 bucket, SQS queues, and event notifications. This ensures logs are captured and forwarded to Microsoft Sentinel for monitoring and threat detection.

## CloudFormation Deployment
### Deploying the Stack

- Navigate to the AWS CloudFormation console.
- Upload the provided CloudFormation template.
- Enter the required parameters:
     - Provide The Stack Name
    -  AWS Role Name
    -  Bucket Name
    -  Firewall Name 
    - Microsoft Sentinel Workspace ID
- Deploy the stack and wait for completion.
- Go to Outpts Tab in the stacks Save the output for future purpose
### Resources Created
The CloudFormation template will create:

- One S3 bucket to store AWS Network Firewall logs.
- Three SQS queues for log processing and forwarding.
- S3 Event Notifications to trigger log forwarding.
- IAM Roles & Policies with the necessary permissions.
### Configuring AWS Network Firewall Logs
- Go to the Firewall Service, navigate to the Logging tab, and enable the log types: FLOW, ALERT, and TLS.
- Select S3 as the log destination and enter the S3 bucket name created by the CloudFormation stack.
### Configuring Microsoft Sentinel
- Navigate to microsoft sentinel
- Go to AWS Netwrok Firewall Connector
- Navigate to Add New Collector
- Provide the Requried Details Role ARN, Queue URL
  
## Verifying Logs in Sentinel
- Go to Log Analytics in Microsoft Sentinel.
- Run the following Kusto Query Language (KQL) query:
  - For Flow Logs
    ```
    AWSNetworkFirewall_FlowLogV2_CL
    | where TimeGenerated > ago(1h)
    ```
  - For Alert Logs
    ```
    AWSNetworkFirewall_AlertLogV2_CL
    | where TimeGenerated > ago(1h)
    ```
  - For Tls Logs
    ```
    AWSNetworkFirewall_TlsLogV2_CL
    | where TimeGenerated > ago(1h)
    ```
- Ensure logs appear correctly.
## Troubleshooting
- No logs in Sentinel? Check Event Notifications in S3 Bucket to ensure the Prefix path matches the S3 bucket logs path.
- IAM permission errors? Ensure CloudFormation created the correct policies.
