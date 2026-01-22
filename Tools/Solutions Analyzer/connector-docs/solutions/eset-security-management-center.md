# Eset Security Management Center

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Eset |
| **Support Tier** | partner |
| **Support Link** | [https://support.eset.com/en](https://support.eset.com/en) |
| **Categories** | domains |
| **First Published** | 2022-05-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Eset%20Security%20Management%20Center](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Eset%20Security%20Management%20Center) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Eset Security Management Center](../connectors/esetsmc.md)

**Publisher:** Eset

Connector for [Eset SMC](https://help.eset.com/esmc_admin/72/en-US/) threat events, audit logs, firewall events and web sites filter.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Access to Eset SMC console**: Permissions to configure log export

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Install and onboard the agent for Linux**

Typically, you should install the agent on a different computer from the one on which the logs are generated.

>  Syslog logs are collected only from **Linux** agents.
**Choose where to install the agent:**

**Install agent on Azure Linux Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install agent on Linux Virtual Machine**

  **Install agent on a non-Azure Linux Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install agent on Linux (Non-Azure)**

**2. Configure the logs to be collected**

Configure rsyslog to accept logs from your Eset SMC IP address.

```
sudo -i

# Set ESET SMC source IP address
export ESETIP={Enter your IP address}

# Create rsyslog configuration file
cat > /etc/rsyslog.d/80-remote.conf << EOF
\$ModLoad imudp
\$UDPServerRun 514
\$ModLoad imtcp
\$InputTCPServerRun 514
\$AllowedSender TCP, 127.0.0.1, $ESETIP
\$AllowedSender UDP, 127.0.0.1, $ESETIP
user.=alert;user.=crit;user.=debug;user.=emerg;user.=err;user.=info;user.=notice;user.=warning  @127.0.0.1:25224
EOF

# Restart rsyslog
systemctl restart rsyslog```

**3. Configure OMS agent to pass Eset SMC data in API format**

In order to easily recognize Eset data we will push it to separate table and parse at agent so query in Azure Sentinel is easier and fast. To make it simple we will just modify ```match oms.**``` section to send data as API objects by changing type to out_oms_api. Modify file on /etc/opt/microsoft/omsagent/{REPLACEyourworkspaceid}/conf/omsagent.conf. Full ```match oms.**``` section looks like this:

```
<match oms.** docker.**>
  type out_oms_api
  log_level info
  num_threads 5
  run_in_background false

  omsadmin_conf_path /etc/opt/microsoft/omsagent/{REPLACEyourworkspaceid}/conf/omsadmin.conf
  cert_path /etc/opt/microsoft/omsagent/{REPLACEyourworkspaceid}/certs/oms.crt
  key_path /etc/opt/microsoft/omsagent/{REPLACEyourworkspaceid}/certs/oms.key

  buffer_chunk_limit 15m
  buffer_type file
  buffer_path /var/opt/microsoft/omsagent/{REPLACEyourworkspaceid}/state/out_oms_common*.buffer

  buffer_queue_limit 10
  buffer_queue_full_action drop_oldest_chunk
  flush_interval 20s
  retry_limit 10
  retry_wait 30s
  max_retry_wait 9m
</match>
```

**4. Change OMS agent configuration to catch tag oms.api.eset and parse structured data**

Modify file /etc/opt/microsoft/omsagent/{REPLACEyourworkspaceid}/conf/omsagent.d/syslog.conf
```
<source>
  type syslog
  port 25224
  bind 127.0.0.1
  protocol_type udp
  tag oms.api.eset
</source>

<filter oms.api.**>
  @type parser
  key_name message
  format /(?<message>.*?{.*})/
</filter>

<filter oms.api.**>
  @type parser
  key_name message
  format json
</filter>
```

**5. Disable automatic configuration and restart agent**

```bash
# Disable changes to configuration files from Portal
sudo su omsagent -c 'python /opt/microsoft/omsconfig/Scripts/OMS_MetaConfigHelper.py --disable'

# Restart agent
sudo /opt/microsoft/omsagent/bin/service_control restart

# Check agent logs
tail -f /var/opt/microsoft/omsagent/log/omsagent.log
```

**6. Configure Eset SMC to send logs to connector**

Configure Eset Logs using BSD style and JSON format.
- Go to Syslog server configuration as described in [Eset documentation](https://help.eset.com/esmc_admin/72/en-US/admin_server_settings.html?admin_server_settings_syslog.html) and configure Host (your connector), Format BSD, Transport TCP
- Go to Logging section as described in [Eset documentation](https://help.eset.com/esmc_admin/72/en-US/admin_server_settings.html?admin_server_settings_export_to_syslog.html) and enable JSON

| | |
|--------------------------|---|
| **Tables Ingested** | `eset_CL` |
| **Connector Definition Files** | [esetSmc.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Eset%20Security%20Management%20Center/Data%20Connectors/esetSmc.json) |

[→ View full connector details](../connectors/esetsmc.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `eset_CL` | [Eset Security Management Center](../connectors/esetsmc.md) |

[← Back to Solutions Index](../solutions-index.md)
