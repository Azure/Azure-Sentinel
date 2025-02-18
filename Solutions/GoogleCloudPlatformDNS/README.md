# Integrating Google Cloud Platform DNS into Microsoft Sentinel
## Table of contents
- [Introduction](#intro)
- [Steps to install The Connector](#step1)
- [Steps to add the new Collector](#step2)
- [Steps to execute Terraform Scripts](#terraform)


<a name="intro">

## Introduction
The Google Cloud Platform DNS Codeless Connector for Microsoft Sentinel enables seamless integration of Google Cloud Platform's DNS logs with Microsoft Sentinel without the need for custom code. Developed as part of the Codeless Conector Platform(CCP), this connector simplifies the process of collecting and ingesting DNS query logs and DNS audit logs from Google Cloud Platform into Sentinel.

<a name="step1">
   
## Steps to install the connector
- Install the **Google Cloud Platform DNS** connector from `Content Hub`

<a name="step2">

## Steps to add the new Collector
- After installing the connector, navigate to `Data Connectors` and select on the **Google Cloud Platform DNS** Connector.

- A new window pops up in the bottom, and click on `Open Connector Page`. 

- Now, click on `Add new collector` button.
- Navigate to Google Cloud Console and select the project you want to monitor and fetch the following resources

- `Project ID` and `Project Number` : You can find these details in the home page of the project.

- `GCP subscription name` : To fetch this name, you must run the terraform script for DNS Log setup in cloud shell of Google Cloud Platform. After executing the terraform script, navigate to **Pub/Sub** section from the search bar, and navigate to Subscriptions from the left panel to fetch Subscription name.   
  
- `Workload identity pool ID` and `Workload identity provider ID` : To get this ID, you must run the terraform script for DNS authentication setup in cloud shell of Google Cloud Platform. After executing the terraform script, navigate to **Workload Identity Federation** section from the search bar where you can find these details.

You can find the script files in the home page of the connector or find them in the steps provided below.

<a name="terraform">

### Steps to execute Terrraform scripts
[Click here](https://github.com/v-pmalreddy/GCPDNS_CCP/tree/main/GCPDNSLogsSetup) to access the terraform scripts.
- Execute the below mentioned commands for both Log Setup file and Authentication Setup file.
- Launch the cloud shell and create a directory using **mkdir <dir_name>** and navigate to the directory using **cd<dir_name>**.
- Copy the raw link of the Terraform script and get the content of the file into a shell using the following command:
   ```
   wget <link of the file> -O <filename.tf>
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
- After successfully executing the Log Setup file, Subscription name is created in the Google Cloud Platform.
- After successfully executing the Authentication setup file, the workload Identity Pool ID and Provider ID is created.
- Search for **Workload Identity Federation** in the search bar and find the Workload Identity pool ID and Provider ID.
- `Service account email` : Navigate to **Service accounts** section from the search bar and use the appropriate service account for authentication.

After filling all the details accurately click on `Connect`, then you will be able to connect the Google Cloud Platform DNS connector to monitor DNS logs.
