# Zscaler Private Access (ZPA)
The [Zscaler Private Access (ZPA)](https://help.zscaler.com/zpa/what-zscaler-private-access) data connector provides the capability to ingest [Zscaler Private Access events](https://help.zscaler.com/zpa/log-streaming-service) into Microsoft Sentinel. Refer to [Zscaler Private Access documentation](https://help.zscaler.com/zpa) for more information.
# Requirements
1. ZPA device log forwarding configuration uses the port "**22033**" by default. Ensure this port is not being used by any other source on your server.
2. If you would like to change the default port for ZPA configuartion(**zpa.conf**) make sure that it should not get conflict with default AMA agent ports i.e. (For example CEF uses "**25226**" or "**25224**")
