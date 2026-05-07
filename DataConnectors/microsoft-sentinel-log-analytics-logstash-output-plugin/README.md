# Microsoft Sentinel Output Plugin for Logstash 

Microsoft Sentinel provides a new output plugin for Logstash. Use this output plugin to send any log via Logstash to the Microsoft Sentinel/Log Analytics workspace. This is done with the Log Analytics DCR-based API.
You may send logs to custom or standard tables.  

Plugin version: v2.2.0  
Released on: 2026-05-04  

This plugin is currently in development and is free to use. We request and appreciate feedback from users.  

## Installation Instructions
1) Install the plugin  
2) Create a sample file  
3) Create the required DCR-related resources  
4) Configure Logstash configuration file  


## 1. Install the plugin

Microsoft Sentinel provides Logstash output plugin to Log analytics workspace using DCR based logs API.  

The plugin is published on [RubyGems](https://rubygems.org/gems/microsoft-sentinel-log-analytics-logstash-output-plugin/versions/2.2.0-java). To install to an existing logstash installation, run `logstash-plugin install microsoft-sentinel-log-analytics-logstash-output-plugin`.  

If you do not have a direct internet connection, you can install the plugin to another logstash installation, and then export and import a plugin bundle to the offline host. For more information, see [Logstash Offline Plugin Management instruction](<https://www.elastic.co/guide/en/logstash/current/offline-plugins.html>).  

Microsoft Sentinel's Logstash output plugin supports the following versions  
- 7.0 - 7.17.13  
- 8.0 - 8.9  
- 8.11 - 8.15  
- 8.19.2  
- 9.0.8  
- 9.1.10  
- 9.2.4 - 9.2.5  

Please note that when using Logstash 8, it is recommended to disable ECS in the pipeline. For more information refer to [Logstash documentation.](<https://www.elastic.co/guide/en/logstash/8.4/ecs-ls.html>)  

## 2. Create a sample file
To create a sample file, follow the following steps:  
1)	Copy the output plugin configuration below to your Logstash configuration file:
    ```
    output {
        microsoft-sentinel-log-analytics-logstash-output-plugin {
            create_sample_file => true
            sample_file_path => "<enter the path to the file in which the sample data will be written>" #for example: "c:\\temp" (for windows) or "/var/log" for Linux.
        }
    }
    ```
Note: make sure that the path exists before creating the sample file.  
2) Start Logstash. The plugin will collect up to 10 records to a sample.  
3) The file named "sampleFile<epoch seconds>.json" in the configured path will be created once there are 10 events to sample or when the Logstash process exited gracefully. (for example: "c:\temp\sampleFile1648453501.json").  


### Configurations:
The following parameters are optional and should be used to create a sample file.  
- **create_sample_file** - Boolean, False by default. When enabled, up to 10 events will be written to a sample json file.  
- **sample_file_path** - Number, Empty by default. Required when create_sample_file is enabled. Should include a valid path in which to place the sample file generated.  

### Complete example
1. set the pipeline.conf with the following configuration:  
    ```
    input {
          generator {
            lines => [ "This is a test log message"]
            count => 10
          }
    }

    output {
        microsoft-sentinel-log-analytics-logstash-output-plugin {
            create_sample_file => true
            sample_file_path => "<enter the path to the file in which the sample data will be written>" #for example: "c:\\temp" (for windows) or "/var/log" for Linux.
        }
    }
    ```

2. the following sample file will be generated:  
    ```
    [
      {
        "host": "logstashMachine",
        "sequence": 0,
        "message": "This is a test log message",
        "ls_timestamp": "2022-10-29T13:19:28.116Z",
        "ls_version": "1"
      },
      ...
    ]
    ```

## 3. Create the required DCR-related resources
To configure Microsoft Sentinel Logstash plugin you first need to create the DCR-related resources. To create these resources, follow one of the following tutorials:  
1) To ingest the data to a custom table use [Tutorial - Send custom logs to Azure Monitor Logs (preview) - Azure Monitor | Microsoft Docs](<https://docs.microsoft.com/azure/azure-monitor/logs/tutorial-custom-logs>) tutorial. Note that as part of creating the table and the DCR you will need to provide the sample file that you've created in the previous section.  
2) To ingest the data to a standard table like Syslog or CommonSecurityLog use [Tutorial - Send custom logs to Azure Monitor Logs using resource manager templates - Azure Monitor | Microsoft Docs](<https://docs.microsoft.com/azure/azure-monitor/logs/tutorial-custom-logs-api>).  

*Note:* The identity (service principal or managed identity) must have the **Monitoring Metrics Publisher** role on the target DCR:  

    az role assignment create \
      --assignee <object-id-of-identity> \
      --role "Monitoring Metrics Publisher" \
      --scope "/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Insights/dataCollectionRules/<dcr-name>"


## 4. Configure the Output Plugin

Add the `microsoft-sentinel-log-analytics-logstash-output-plugin` block to the `output` section of your Logstash configuration file (e.g., `logstash.conf`). The plugin requires three values from your Azure DCR resources plus authentication credentials depending on your method.  

### Required Config Values (needed for all methods)

| Key | Description |  
|---|---|  
| `data_collection_endpoint` | Your DCE logsIngestion URI |  
| `dcr_id` | The immutable ID of your Data Collection Rule |  
| `stream_name` | The stream name from your DCR (e.g., `Custom-MyTableRawData_CL`) |  

---

### Authentication Examples

The plugin auto-detects the auth method based on which config values are present.  

#### Option 1: Client Secret (App Registration)

Provide `client_id`, `client_secret`, and `tenant_id` for your Azure App Registration / service principal.  

    output {
      microsoft-sentinel-log-analytics-logstash-output-plugin {
        data_collection_endpoint => "https://<your-dce-name>.<region>.ingest.monitor.azure.com"
        dcr_id                   => "dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        stream_name              => "Custom-MyTableRawData_CL"
        client_id                => "<your-app-client-id>"
        client_secret            => "<your-app-client-secret>"
        tenant_id                => "<your-azure-tenant-id>"
      }
    }


#### Option 2: Managed Identity

When running on an Azure VM with a system-assigned managed identity, omit `client_id`, `client_secret`, and `tenant_id`. The plugin will automatically use the VM's managed identity.  

    output {
      microsoft-sentinel-log-analytics-logstash-output-plugin {
        data_collection_endpoint => "https://<your-dce-name>.<region>.ingest.monitor.azure.com"
        dcr_id                   => "dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        stream_name              => "Custom-MyTableRawData_CL"
      }
    }

#### Option 3: Client Secret + Sovereign Cloud

To authenticate against a sovereign cloud, add `azure_cloud`. Supported values: `AzurePublicCloud` (default), `AzureUSGovernment`, `AzureChinaCloud`, `AzureGermanyCloud`.  

    output {
      microsoft-sentinel-log-analytics-logstash-output-plugin {
        data_collection_endpoint => "https://<your-dce-ingestion-endpoint>"
        dcr_id                   => "dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        stream_name              => "Custom-MyTableRawData_CL"
        client_id                => "<your-app-client-id>"
        client_secret            => "<your-app-client-secret>"
        tenant_id                => "<your-tenant-id>"
        azure_cloud              => "AzureUSGovernment"
      }
    }

#### Option 4: Managed Identity + Sovereign Cloud

    output {
      microsoft-sentinel-log-analytics-logstash-output-plugin {
        data_collection_endpoint => "https://<your-dce-ingestion-endpoint>"
        dcr_id                   => "dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        stream_name              => "Custom-MyTableRawData_CL"
        azure_cloud              => "AzureUSGovernment"
      }
    }
---
Security notice: We recommend not to implicitly state client_id, client_secret, tenant_id, data_collection_endpoint, and dcr_id in your Logstash configuration for security reasons.  
                 It is best to store this sensitive information in a Logstash KeyStore as described here- ['Secrets Keystore'](<https://www.elastic.co/guide/en/logstash/current/keystore.html>)  

---

## Full Pipeline Example

A complete `logstash.conf` using client secret auth with a Beats input:  

    input {
      beats {
        port => 5044
      }
    }

    filter {
    }

    output {
      microsoft-sentinel-log-analytics-logstash-output-plugin {
        data_collection_endpoint => "https://my-dce.eastus2-1.ingest.monitor.azure.com"
        dcr_id                   => "dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        stream_name              => "Custom-MyTableRawData_CL"
        client_id                => "619c1731-15ca-4403-9c61-xxxxxxxxxxxx"
        client_secret            => "xxxxxxxxxxxxxxxx"
        tenant_id                => "72f988bf-86f1-41af-91ab-xxxxxxxxxxxx"
      }
    }
---

## Optional Config Values

| Key | Default | Description |  
|---|---|---|  
| `azure_cloud` | `AzurePublicCloud` | Azure cloud environment |  
| `keys_to_keep` | *(all)* | Array of field names to send (subset filtering) |  
| `max_retries_num` | `3` | Max retry attempts for failed sends |  
| `initial_wait_time_seconds` | `1` | Initial backoff between retries |  
| `max_graceful_shutdown_time_seconds` | `60` | Max wait for graceful shutdown |  
| `max_waiting_time_for_batch_seconds` | `10` | Max wait before flushing a batch |  
| `max_waiting_for_unifier_time_seconds` | `10` | Max wait before flushing the unifier |  
| `max_batch_size` | `10000` | Maximum number of events per batch. When a batch reaches this size it is flushed immediately, regardless of the time window |  
| `input_queue_capacity` | `50000` | Maximum capacity of the input queue. Bounds memory usage under high-volume ingestion. When full, back-pressure is applied to the Logstash pipeline |  
| `internal_queue_capacity` | `500` | Maximum capacity of the internal queues between batcher, unifier, and sender workers. Bounds memory usage for in-flight batches |  
| `worker_sleep_time_millis` | `10` | Delay between worker iterations |  
| `batcher_workers_count` | *(auto)* | Number of batcher threads |  
| `sender_workers_count` | *(auto)* | Number of sender threads |  
| `unifier_workers_count` | *(auto)* | Number of unifier threads |  

## Known issues
 
When using Logstash installed on a Docker image of Lite Ubuntu, the following warning may appear:  

    java.lang.RuntimeException: getprotobyname_r failed

To resolve it, use the following commands to install the *netbase* package within your Dockerfile:  
    ```
    USER root
    RUN apt install netbase -y
    ```  
For more information, see [JNR regression in Logstash 7.17.0 (Docker)](https://github.com/elastic/logstash/issues/13703).  
