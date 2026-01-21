# Integrating Imperva Cloud WAF into Microsoft Sentinel
## Table of contents
- [Introduction](#intro)
- [Prerequisites](#pre)
- [Deploy the Cloud Formation Templates](#template)
- [Configure Imperva to Forward Logs to Amazon S3](#logs)


<a name = "intro">

## Introduction
The Imperva Cloud WAF Codeless Connector for Microsoft Sentinel enables seamless integration of Imperva's Access Logs and Security Logs with Microsoft Sentinel without the need for custom code. Your Imperva WAF logs will be forwarded to an Amazon S3 bucket, which will then be used as the source for log ingestion into Microsoft Sentinel.

<a name = "pre">

## Prerequisites
- An active **AWS account** with permissions to create:
  - IAM roles and policies
  - S3 buckets
  - SQS queues

<a name = "template">
  
## Deploy the Cloud Formation Templates
- Download the [OIDC Web Identity Provider](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Data%20Connectors/Cloud%20Formation%20Templates/OIDCWebIdProvider.json) Template and the [AWS Resource Creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ImpervaCloudWAF/Data%20Connectors/Cloud%20Formation%20Templates/ImpervaCloudWAFConfig.json) Template provided in this repository.
- Open the **AWS Management Console** and navigate to the **CloudFormation** service.
- Click on **"Create stack"** and choose **"With new resources (standard)"**.
- Under the **Specify template** section, select **"Upload a template file"**, and upload the appropriate CloudFormation template (starting with the OIDC template).
- Click **Next**, provide a **Stack Name** of your choice, and review or modify the parameters as needed.
- Proceed by clicking **Next**, then **Submit** to initiate the stack creation.
- Wait until the status of the first stack (OIDC Web Identity Provider) changes to **"CREATE_COMPLETE"**.
- Once completed, repeat the same steps to deploy the second template **(AWS Resource Creation Template)** using CloudFormation.
- Upon successful stack creation, make a note of the **SQS Queue URL** and **Role ARN** available in the CloudFormation stack outputs.

<a name = "logs">

## Configure Imperva to Forward Logs to Amazon S3
To enable log forwarding from Imperva to Amazon S3, follow the steps below:
- Log in to the **Imperva Management Console**.
- Click on your profile icon and navigate to **Account Management**.
- In the left navigation pane, expand **SIEM Logs** and select **Log Configuration**.
- Click on **Add Connection**.
- Set the **Vendor** to **Microsoft Sentinel** and the **Delivery Method** to **Amazon S3**.
- For the **Access Method**, select **S3 ARN**, and provide a meaningful **Connection Name**.
- Enter the log folder path in the following format:
  ```
  <your-bucket-name>/ImpervaWafLogs
  ```
  Then click on **Test Connection**. It should show as **Available**.
- Click **Create** to establish the connection.
- After the connection is created, click on **Add Log Type**.
- Choose **Cloud WAF** and click **Next**.
- Under **Default Website Log Level**, select both **Access Logs** and **Security Logs**.
- **Uncheck** the option for **Compress Logs**.
- Ensure that the **Connection State** is set to **Enabled**.
- Click **Save** to finalize the configuration.