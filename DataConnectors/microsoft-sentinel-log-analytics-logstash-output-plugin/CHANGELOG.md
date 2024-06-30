## 1.0.0
* Initial release for output plugin for logstash to Microsoft Sentinel. This is done with the Log Analytics DCR based API.

## 1.1.0 
* Increase timeout for read/open connections to 120 seconds.
* Add error handling for when connection timeout occurs.
* Upgrade the rest-client dependency minimum version to 2.1.0.
* Allow setting different proxy values for api connections.
* Upgrade version for ingestion api to 2023-01-01.
* Rename the plugin to microsoft-sentinel-log-analytics-logstash-output-plugin.

## 1.1.1
* Support China and US Government Azure sovereign clouds.

## 1.1.2
* Replace rest-client with excon for connectivity.
* Change the default value for plugin_flush_interval from 5 seconds to 60 to batch more events per logs transmission.