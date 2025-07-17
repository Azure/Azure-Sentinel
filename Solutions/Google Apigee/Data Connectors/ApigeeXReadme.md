# Integrating Google ApigeeX into Microsoft Sentinel
## Table of contents
- [Introduction](#intro)
- [Prerequisites](#step2)
- [Steps to execute Terraform Scripts for log setup](#log)
- [Steps to execute Terraform Scripts for Authentication setup](#auth)


<a name="intro">

## Introduction
The Google ApigeeX Codeless Connector for Microsoft Sentinel enables seamless integration of Google ApigeeX logs with Microsoft Sentinel without the need for custom code. Developed as part of the Codeless Connector Platform(CCP), this connector simplifies the process of collecting and ingesting Google ApigeeX audit logs from Google Cloud Platform into Sentinel.


<a name="step2">

## Prerequisites
The below mentioned resources are required to connect GCP with Sentinel.
- Project ID
- Project Number
- GCP Subscription Name
- Workload Identity Pool ID
- Service Account
- Workload Identity Provider ID

To generate the above resources, you must execute the following terraform scripts.

- Log Setup File
- Authentication setup file

<a name="log">

## Steps to execute Terraform scripts for Log Setup
To access the terraform script for Log Setup [Click here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPApigeeLogSetup).
- Launch the cloud shell in Google Cloud Console.
- Execute the below mentioned commands.
- create a directory
  ```
  mkdir <dir_name>
  ```
- Navigate to the directory
  ```
  cd <dir_name>
  ```
- Copy the github raw link of the Terraform script and get the content of the file into a shell using the following command:
   ```
   wget <raw link of the file> -O <filename.tf>
   ```
- Initializes your terraform working directory, downloads provider plugins, and configures the backend for state storage.
   ```
   terraform init
   ```
- Creates an execution plan to show what actions terraform will take to achieve the desired state of your infrastructure.
   ```
   terraform plan
   ```
   Once you execute this command it will ask to "Enter your project ID". Please enter your GCP Project ID.
  
- Executes the actions proposed in the Terraform plan to create, update, or destroy resources in your infrastructure.
   ```
   terraform apply
   ```
   Once you execute this command it will again ask to "Enter your project ID". Please enter your GCP Project ID one more time.
  
- After successfully executing the Log Setup file, `topic name`, `subscription name` is generated in the GCP Project. Save those details for future reference.

<a name="auth">
  
## Steps to execute Terraform script for Authentication setup
- If the Authentication setup file is previously executed in the project while configuring any other GCP data connectors, there is no need to execute the Authentication setup file again. You can use the existing `Workload Identity Pool ID` and `Workload Identity Provider ID` for authentication  purpose.
- If these fields are not generated previously, execute the Authentication Setup file.
- To access the Authentication Setup file [Click Here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPInitialAuthenticationSetup).
- To Execute the Authentication Setup file [Click Here](https://learn.microsoft.com/en-us/azure/sentinel/connect-google-cloud-platform?tabs=terraform%2Cauditlogs#gcp-authentication-setup).
- After executing the authentication setup file, `Workload Identity Pool ID` and `Workload Identity Provider ID` are generated in the project.Save those details for future reference.