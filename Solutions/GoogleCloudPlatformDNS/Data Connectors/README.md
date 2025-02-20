# Integrating Google Cloud Platform DNS into Microsoft Sentinel
## Table of contents
- [Introduction](#intro)
- [Setting up Logs](#step2)
- [Steps to execute Terraform Scripts](#terraform)


<a name="intro">

## Introduction
The Google Cloud Platform DNS Codeless Connector for Microsoft Sentinel enables seamless integration of Google Cloud Platform's DNS logs with Microsoft Sentinel without the need for custom code. Developed as part of the Codeless Conector Platform(CCP), this connector simplifies the process of collecting and ingesting DNS query logs and DNS audit logs from Google Cloud Platform into Sentinel.


<a name="step2">

## Setting up Logs
The below mentioned resources are required to connect GCP with Sentinel.
- Project ID
- Project Number
- GCP Subscription Name
- Workload Identity Pool ID
- Service Account
- Workload Identity Provider ID

<a name="terraform">

## Steps to execute Terrraform scripts for Log Setup
[Click here](https://github.com/v-pmalreddy/GCPDNS_CCP/tree/main/GCPDNSLogsSetup) to access the terraform script for Log Setup.
- After accessing the log setup file, edit the project id as per your project.
- Execute the below mentioned commands after editing the script.
- Launch the cloud shell and create a directory
  ```
  mkdir <dir_name>
  ```
- Navigate to the directory
  ```
  cd <dir_name>
  ```
- Copy the raw link of the Terraform script and get the content of the file into a shell using the following command:
   ```
   wget <raw link of the file> -O <filename.tf>
   ```
- Now run the following commands

   Initializes your terraform working directory, downloads provider plugins, and configures the backend for state storage.
   ```
   terraform init
   ```
   Creates an execution plan to show what actions terraform will take to achieve the desired state of your infrastructure.
   ```
   terraform plan
   ```
   Executes the actions proposed in the Terraform plan to create, update, or destroy resources in your infrastructure.
   ```
   terraform apply
   ```
- After successfully executing the Log Setup file, `topic name`, `subscription name` is generated in the GCP Project. Save those details for future reference.
- If the Authentication setup file is previously executed in the project, there is no need to execute the Authentication setup file again. You can use the existing `Workload Identity Pool ID` and `Workload Identity Provider ID`.
- If these fields are not generated previosuly, execute the Authentication Setup file with the same commands mentioned above.
- [Click Here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPInitialAuthenticationSetup) to access the Authentication Setup file.
- After executing the authentication setup file, `Workload Identity Pool ID` and `Workload Identity Provider ID` are generated in the project.

