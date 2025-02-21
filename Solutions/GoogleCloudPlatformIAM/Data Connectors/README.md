# Integrating Google Cloud Platform IAM into Microsoft Sentinel
## Table of contents
- [Introduction](#intro)
- [Prerequisites](#step1)
- [Steps to execute Terraform Scripts for log setup](#log)
- [Steps to execute Terraform Scripts for Authentication setup](#auth)


<a name="intro">

## Introduction
The Google Cloud Platform IAM Codeless Connector for Microsoft Sentinel enables seamless integration of Google Cloud Platform's IAM logs with Microsoft Sentinel without the need for custom code. Developed as part of the Codeless Conector Platform(CCP), this connector simplifies the process of collecting and ingesting IAM query logs and IAM audit logs from Google Cloud Platform into Sentinel.

<a name="step1">
   
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

## Steps to execute Terrraform scripts for Log Setup
To access the terraform script for Log Setup [Click here](https://github.com/v-hkopparala/v-hkopparala/blob/main/CCPIAMLOGS%201.tf)
- After accessing the log setup file, edit the project id as per your project.
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
- Executes the actions proposed in the Terraform plan to create, update, or destroy resources in your infrastructure.
   ```
   terraform apply
   ```
- After successfully executing the Log Setup file, `topic name`, `subscription name` is generated in the GCP Project. Save those details for future reference.

<a name="auth">

## Steps to execute Terraform script for Authentication setup
- If the Authentication setup file is previously executed in the project, there is no need to execute the Authentication setup file again. You can use the existing `Workload Identity Pool ID` and `Workload Identity Provider ID` for authentication  purpose.
- If these fields are not generated previosuly, execute the Authentication Setup file with the same commands mentioned above.
- To access the Authentication Setup file [Click Here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPInitialAuthenticationSetup).
- After executing the authentication setup file, `Workload Identity Pool ID` and `Workload Identity Provider ID` are generated in the project.
