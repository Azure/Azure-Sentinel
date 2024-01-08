# Microsoft Sentinel output plugin for Logstash 

Microsoft Sentinel provides a new output plugin for Logstash. Use this output plugin to send any log via Logstash to the Microsoft Sentinel/Log Analytics workspace. This is done with the Log Analytics DCR-based API.
You may send logs to custom or standard tables.

Plugin version: v1.1.0  
Released on: 2023-07-23

This plugin is currently in development and is free to use. We welcome contributions from the open source community on this project, and we request and appreciate feedback from users.


## Steps to implement the output plugin
1) Install the plugin
2) Create a sample file
3) Create the required DCR-related resources
4) Configure Logstash configuration file
5) Basic logs transmission


## 1. Install the plugin

Microsoft Sentinel provides Logstash output plugin to Log analytics workspace using DCR based logs API. 
Install the microsoft-sentinel-log-analytics-logstash-output-plugin, use [Logstash Offline Plugin Management instruction](<https://www.elastic.co/guide/en/logstash/current/offline-plugins.html>). 

Microsoft Sentinel's Logstash output plugin supports the following versions
- 7.0 - 7.17.13
- 8.0 - 8.9
- 8.11

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


## 4. Configure Logstash configuration file

Use the tutorial from the previous section to retrieve the following attributes: 
- **client_app_Id** - String, The 'Application (client) ID' value created in step #3 of the "Configure Application" section of the tutorial you used in the previous step.
- **client_app_secret** -String, The value of the client secret created in step #5 of the "Configure Application" section of the tutorial you used in the previous step.
- **tenant_id** - String, Your subscription's tenant id. You can find in the following path: Home -> Azure Active Directory -> Overview Under 'Basic Information'.
- **data_collection_endpoint** - String, - The value of the logsIngestion URI (see step #3 of the "Create data collection endpoint" section in Tutorial [Tutorial - Send custom logs to Azure Monitor Logs using resource manager templates - Azure Monitor | Microsoft Docs](<https://docs.microsoft.com/azure/azure-monitor/logs/tutorial-custom-logs-api#create-data-collection-endpoint>).
- **dcr_immutable_id** - String, The value of the DCR immutableId (see the "Collect information from DCR" section in [Tutorial - Send custom logs to Azure Monitor Logs (preview) - Azure Monitor | Microsoft Docs](<https://docs.microsoft.com/azure/azure-monitor/logs/tutorial-custom-logs#collect-information-from-dcr>).
- **dcr_stream_name** - String, The name of the data stream (Go to the json view of the DCR as explained in the "Collect information from DCR" section in [Tutorial - Send custom logs to Azure Monitor Logs (preview) - Azure Monitor | Microsoft Docs](<https://docs.microsoft.com/azure/azure-monitor/logs/tutorial-custom-logs#collect-information-from-dcr>) and copy the value of the "dataFlows -> streams" property (see circled in red in the below example).

After retrieving the required values replace the output section of the Logstash configuration file created in the previous steps with the example below. Then, replace the strings in the brackets below with the corresponding values. Make sure you change the "create_sample_file" attribute to false.

Here is an example for the output plugin configuration section:
```
output {
    microsoft-sentinel-log-analytics-logstash-output-plugin {
        client_app_Id => "<enter your client_app_id value here>"
        client_app_secret => "<enter your client_app_secret value here>"
        tenant_id => "<enter your tenant id here>"
        data_collection_endpoint => "<enter your DCE logsIngestion URI here>"
        dcr_immutable_id => "<enter your DCR immutableId here>"
        dcr_stream_name => "<enter your stream name here>"
        create_sample_file=> false
        sample_file_path => "c:\\temp"
    }
}

```
### Optional configuration 
- **key_names** – Array of strings, if you wish to send a subset of the columns to Log Analytics.
- **plugin_flush_interval** – Number, 5 by default. Defines the maximal time difference (in seconds) between sending two messages to Log Analytics. 
- **retransmission_time** - Number, 10 by default. This will set the amount of time in seconds given for retransmitting messages once sending has failed. 
- **compress_data** - Boolean, false by default. When this field is true, the event data is compressed before using the API. Recommended for high throughput pipelines
- **proxy** - String, Empty by default. Specify which proxy URL to use for API calls for all of the communications with Azure.
- **proxy_aad** - String, Empty by default. Specify which proxy URL to use for API calls for the Azure Active Directory service. Overrides the proxy setting.
- **proxy_endpoint** - String, Empty by default. Specify which proxy URL to use when sending log data to the endpoint. Overrides the proxy setting.

#### Note: When setting an empty string as a value for a proxy setting, it will unset any system wide proxy setting.

Security notice: We recommend not to implicitly state client_app_Id, client_app_secret, tenant_id, data_collection_endpoint, and dcr_immutable_id in your Logstash configuration for security reasons.
                 It is best to store this sensitive information in a Logstash KeyStore as described here- ['Secrets Keystore'](<https://www.elastic.co/guide/en/logstash/current/keystore.html>)


## 5. Basic logs transmission

Here is an example configuration that parses Syslog incoming data into a custom stream named "Custom-MyTableRawData".

### Example Configuration

- Using filebeat input pipe

```
input {
    beats {
        port => "5044"
    }
}
 filter {
}
output {
    microsoft-sentinel-log-analytics-logstash-output-plugin {
      client_app_Id => "619c1731-15ca-4403-9c61-xxxxxxxxxxxx"
      client_app_secret => "xxxxxxxxxxxxxxxx"
      tenant_id => "72f988bf-86f1-41af-91ab-xxxxxxxxxxxx"
      data_collection_endpoint => "https://my-customlogsv2-test-jz2a.eastus2-1.ingest.monitor.azure.com"
      dcr_immutable_id => "dcr-xxxxxxxxxxxxxxxxac23b8978251433a"
      dcr_stream_name => "Custom-MyTableRawData"
      proxy_aad => "http://proxy.example.com"
    }
}

```
- Or using the tcp input pipe

```
input {
    tcp {
        port => "514"
        type => syslog #optional, will effect log type in table
    }
}
 filter {
}
output {
    microsoft-sentinel-log-analytics-logstash-output-plugin {
      client_app_Id => "619c1731-15ca-4403-9c61-xxxxxxxxxxxx"
      client_app_secret => "xxxxxxxxxxxxxxxx"
      tenant_id => "72f988bf-86f1-41af-91ab-xxxxxxxxxxxx"
      data_collection_endpoint => "https://my-customlogsv2-test-jz2a.eastus2-1.ingest.monitor.azure.com"
      dcr_immutable_id => "dcr-xxxxxxxxxxxxxxxxac23b8978251433a"
      dcr_stream_name => "Custom-MyTableRawData"
    }
}
```

<u>Advanced Configuration</u>
```
input {
  syslog {
    port => 514
  }
}

output {
    microsoft-sentinel-log-analytics-logstash-output-plugin {
      client_app_Id => "${CLIENT_APP_ID}"
      client_app_secret => "${CLIENT_APP_SECRET}"
      tenant_id => "${TENANT_ID}"
      data_collection_endpoint => "${DATA_COLLECTION_ENDPOINT}"
      dcr_immutable_id => "${DCR_IMMUTABLE_ID}"
      dcr_stream_name => "Custom-MyTableRawData"
	  key_names => ['PRI','TIME_TAG','HOSTNAME','MSG']
    }
}

```

Now you are able to run logstash with the example configuration and send mock data using the 'logger' command.

For example: 
```
logger -p local4.warn --rfc3164 --tcp -t CEF "0|Microsoft|Device|cef-test|example|data|1|here is some more data for the example" -P 514 -d -n 127.0.0.1
```

Which will produce this content in the sample file:

```
[
	{
		"logsource": "logstashMachine",
		"facility": 20,
		"severity_label": "Warning",
		"severity": 4,
		"timestamp": "Apr  7 08:26:04",
		"program": "CEF:",
		"host": "127.0.0.1",
		"facility_label": "local4",
		"priority": 164,
		"message": "0|Microsoft|Device|cef-test|example|data|1|here is some more data for the example",
		"ls_timestamp": "2022-04-07T08:26:04.000Z",
		"ls_version": "1"
	}
]
```
