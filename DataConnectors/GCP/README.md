# GCP Microsoft Sentinel Connector

## Introduction

GCP Sentinel connector is a platform for ingesting GCP service logs into Azure Sentinel. Currently supported logs: Audit logs.

This connector requires that each GCP service will publish its logs to a pub/sub. In addition you must configure workload identity pool and workload identity provider with permissions for the connector to receive an access token as well as a service account with permissions for the connector to read the logs from the pub/sub subscription.

More information on the connector and configuration instructions can be found on the Azure Sentinel data connector page in the Azure portal.

## Configuration process

This set of Terraform scripts can be used to automatically configure the necessary resources.

At a high level, these scripts do the following:

### `GCPInitialAuthenticationSetup.tf` script:

1. Create a workload identity pool (only if marked as not exist) with azure tenant id as its id.
2. Create a workload identity provider with Sentinel's application settings.
3. Create a service account with permissions to read from pub/sub subscription.

### `Script that configures data to subscription` (for example GCPAuditLogsSetup.tf script):

1. Create a topic.
2. Create a subscription.
3. Configure the GCP service (for example: auditlogs) to export logs to the pub/sub.
   
## Using the scripts

Go to Terraform/sentinel_resource_creation folder, copy the GCPInitialAuthenticationSetup.tf script and the relevant script for configuring logs to pub/sub and paste it in the [GCP CloudShell](https://cloud.google.com/shell/) one by one, save them in *tf* format.

Then run the following from GCP CloudShell:
1. Run:
    ```
    gcloud config set project {your project Id}
    ```
    Select `authorize` in the pop-up window.

2. Run:
    ```
    terraform init
    ```
3. Choose the script you want to run one by one and run:
    ```
    terraform apply
    ```
    Follow the prompts to complete the configuration.
    
When the scripts complete, you must complete the Azure Sentinel data connector configuration in the Azure portal.

## Advanced usage

The `GCPAuditLogsSetup.tf` script has two parameters:
- `-topic-name` in case there is an existing topic, please set the topic name and it will be used in the script.
- `-organization-id` If this parameter is specified, the logs of the entire organization will be exported to the pub/sub.

