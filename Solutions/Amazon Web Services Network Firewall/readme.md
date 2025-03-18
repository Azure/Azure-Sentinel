## Overview
This guide explains how to integrate AWS Network Firewall logs with Microsoft Sentinel using an AWS CloudFormation template. The template automates the deployment of necessary resources to collect, process, and forward logs to Sentinel.

## Prerequisites
Before deploying, ensure you have:
- An AWS account with permissions to deploy CloudFormation stacks.
- An existing AWS Network Firewall setup with logging enabled to S3 Bucket.
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
### Configuring Microsoft Sentinel
- In Microsoft Sentinel, navigate to Content Hub.
- Search for AWS Network Firewall and install it
- Navigate to Data Connectors Search AWS Network Firewall Connector Open Connector Page.
- Navigate to Add New Collector
- Provide the Requried Details Role ARN, Queue URL
  
## Verifying Logs in Sentinel
- Go to Log Analytics in Microsoft Sentinel.
- Run the following Kusto Query Language (KQL) query:
kql
Copy
Edit
- AWSNetworkFirewallLogs
| where TimeGenerated > ago(1h)
Ensure logs appear correctly.
## Troubleshooting
- No logs in Sentinel? Check Event Notifications in S3 Bucket Prefix path and S3 bucket logs path should be same.
- IAM permission errors? Ensure CloudFormation created the correct policies.
- Logs delayed? Verify the S3 Event Notification and SQS processing.
