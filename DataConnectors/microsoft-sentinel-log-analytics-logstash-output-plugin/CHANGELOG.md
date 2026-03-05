## 1.2.0
- Adds managed identity authentication support for Azure VMs/VMSS (system-assigned and user-assigned via IMDS).
- Adds AKS workload identity support via OIDC token exchange.
- Adds Azure Arc managed identity support for hybrid and on-premises servers.
- Auto-detects authentication method at runtime based on environment (workload identity env vars, Arc agent, or IMDS fallback).
- Migrates HTTP client from `excon` to `rest-client` for improved JRuby and Logstash plugin ecosystem compatibility.
- Renames Azure Active Directory references to Microsoft Entra ID.

## 1.1.4
-  Limit `excon` library version to lower than 1.0.0 to make sure port is always used when using a proxy.
  
## 1.1.3
-  Replaces the `rest-client` library used for connecting to Azure with the `excon` library.
 
## 1.1.1
- Adds support for Azure US Government cloud and Microsoft Azure operated by 21Vianet in China.
 
## 1.1.0 
- Allows setting different proxy values for API connections.
- Upgrades version for logs ingestion API to 2023-01-01.
- Renames the plugin to microsoft-sentinel-log-analytics-logstash-output-plugin.
 
## 1.0.0
- The initial release for the Logstash output plugin for Microsoft Sentinel. This plugin uses Data Collection Rules (DCRs) with Azure Monitor's Logs Ingestion API.
