# Azure Log Analytics output plugin for Logstash 

Azure Sentinel provides a new output plugin for Logstash. Using this output plugin, you will be able to send any log you want using Logstash to the Azure Sentinel/Log Analytics workspace
Today you will be able to send messages to custom logs table that you will define in the output plugin. 
[Getting started with Logstash](<https://www.elastic.co/guide/en/logstash/current/getting-started-with-logstash.html>) 

Azure Sentinel output plugin uses the rest API integration to Log Analytics, in order to ingest the logs into custom logs tables [What are custom logs tables](<https://docs.microsoft.com/azure/azure-monitor/platform/data-sources-custom-logs>)

Plugin version: v1.0.0 
Released on: 2020-08-25 

This plugin is currently in development and is free to use. We welcome contributions from the open source community on this project, and we request and appreciate feedback from users.

## Support

For issues regarding the output plugin please open a support ticket here - https://ms.portal.azure.com/#create/Microsoft.Support
As the service type select- "Azure Sentinel"

## Installation

Azure Sentinel provides Logstash output plugin to Log analytics workspace. 
Install the microsoft-logstash-output-azure-loganalytics, use [Logstash Working with plugins](<https://www.elastic.co/guide/en/logstash/current/working-with-plugins.html>) document. 
For offline setup follow [Logstash Offline Plugin Management instruction](<https://www.elastic.co/guide/en/logstash/current/offline-plugins.html>). 

This plugin supports the following versions
- 7.0 - 7.17.13
- 8.0 - 8.9
- 8.11


Please note that when using Logstash 8, it is recommended to disable ECS in pipeline. For more information refer to [Logstash documentation.](<https://www.elastic.co/guide/en/logstash/8.4/ecs-ls.html>)

## Configuration

in your Logstash configuration file, add the Azure Sentinel output plugin to the configuration with following values: 
- workspace_id – your workspace ID guid 
- workspace_key (primary key) – your workspace primary key guid. You can find your workspace key and id the following path: Home > Log Analytics workspace > Advanced settings
- custom_log_table_name – table name, in which the logs will be ingested, limited to one table, the log table will be presented in the logs blade under the custom logs label, with a _CL suffix. 
	Table name must be only alpha characters, and shoud not exceed 100 characters.
- endpoint – Optional field by default set as log analytics endpoint.  
- time_generated_field – Optional field, this property is used to override the default TimeGenerated field in Log Analytics. Populate this property with the name of the sent data time field. 
- key_names – list of Log analytics output schema fields. 
- plugin_flash_interval – Optional filed, define the maximal time difference (in seconds) between sending two messages to Log Analytics. 
- Max_items – Optional field, 2000 by default. this parameter will control the maximum batch size. This value will be changed if the user didn’t specify “amount_resizing = false” in the configuration. 

Note: View the GitHub to learn more about the sent message’s configuration, performance settings and mechanism

Security notice: We recommend not to implicitly state the workspace_id and workspace_key in your Logstash configuration for security reasons.
                 It is best to store this sensitive information in a Logstash KeyStore as described here- https://www.elastic.co/guide/en/elasticsearch/reference/current/get-started-logstash-user.html

## Tests

Here is an example configuration who parse Syslog incoming data into a custom table named "logstashCustomTableName".

### Example Configuration

<u>Basic configuration</u>

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
    microsoft-logstash-output-azure-loganalytics {
      workspace_id => "4g5tad2b-a4u4-147v-a4r7-23148a5f2c21" # <your workspace id>
      workspace_key => "u/saRtY0JGHJ4Ce93g5WQ3Lk50ZnZ8ugfd74nk78RPLPP/KgfnjU5478Ndh64sNfdrsMni975HJP6lp==" # <your workspace key>
      custom_log_table_name => "tableName"
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
    microsoft-logstash-output-azure-loganalytics {
      workspace_id => "4g5tad2b-a4u4-147v-a4r7-23148a5f2c21" # <your workspace id>
      workspace_key => "u/saRtY0JGHJ4Ce93g5WQ3Lk50ZnZ8ugfd74nk78RPLPP/KgfnjU5478Ndh64sNfdrsMni975HJP6lp==" # <your workspace key>
      custom_log_table_name => "tableName"
    }
}
```

<u>Advanced Configuration</u>
```
input {
  tcp {
    port => 514
    type => syslog
  }
}

filter {
    grok {
      match => { "message" => "<%{NUMBER:PRI}>1 (?<TIME_TAG>[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}T[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2})[^ ]* (?<HOSTNAME>[^ ]*) %{GREEDYDATA:MSG}" }
    }
}

output {
        microsoft-logstash-output-azure-loganalytics {
                workspace_id => "<WS_ID>"
                workspace_key => "${WS_KEY}"
                custom_log_table_name => "logstashCustomTableName"
                key_names => ['PRI','TIME_TAG','HOSTNAME','MSG']
                plugin_flush_interval => 5
        }
}
```

Now you are able to run logstash with the example configuration and send mock data using the 'logger' command.

For example: 
```
logger -p local4.warn -t CEF: "0|Microsoft|Device|cef-test|example|data|1|here is some more data for the example" -P 514 -d -n 127.0.0.1

```

Alternativly you can use netcat to test your configuration:

```
echo "test string" | netcat localhost 514
```
