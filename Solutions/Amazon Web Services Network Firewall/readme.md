## Overview
This guide explains how to integrate AWS Network Firewall logs with Microsoft Sentinel using an AWS CloudFormation template. The template automates the deployment of necessary resources to collect, process, and forward logs to Sentinel.

## Prerequisites
Before deploying, ensure you have:
- An AWS account with permissions to deploy CloudFormation stacks.
- An existing AWS Network Firewall setup.
- An active Microsoft Sentinel Log Analytics Workspace ID.
- Required IAM permissions to configure AWS services.

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
- In Microsoft Sentinel, navigate to Content Hub.
- Search for AWS Network Firewall and install it
- Navigate to Data Connectors Search AWS Network Firewall Connector Open Connector Page.
- Navigate to Add New Collector
- Provide the Requried Details Role ARN, Queue URL
  
## Verifying Logs in Sentinel
- Go to Log Analytics in Microsoft Sentinel.
- Run the following Kusto Query Language (KQL) query:
- AWSNetworkFirewall_FlowLogV2_CL
  | where TimeGenerated > ago(1h)
- AWSNetworkFirewall_AlertLogV2_CL
  | where TimeGenerated > ago(1h)
- AWSNetworkFirewall_TlsLogV2_CL
  | where TimeGenerated > ago(1h)
- Ensure logs appear correctly.
## Troubleshooting
- No logs in Sentinel? Check Event Notifications in S3 Bucket to ensure the Prefix path matches the S3 bucket logs path.
- IAM permission errors? Ensure CloudFormation created the correct policies.
