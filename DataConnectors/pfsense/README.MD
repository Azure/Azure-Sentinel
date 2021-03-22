# pfSense Data Connecter
Author: Nicholas DiCola

This connector collects filterlog and nginx logs via RSYSLOG and parses them to CEF format so that they are ingested into Azure Sentinel in CommonEventFortmat.

## Instructions
1. Install the CEF collection agent from the Azure Sentinel Data connectors blade.
2. Download the .conf files to /etc/rsyslog.d/ using the following commands:
sudo wget -O /etc/rsyslog.d/51-pfsense-filterlog.conf https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/pfsense/51-pfsense-filterlog.conf
sudo wget -O /etc/rsyslog.d/52-pfsense-nginx.conf https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/pfsense/52-pfsense-nginx.conf
3. Restart rsyslog using the following command
systemctl restart rsyslog

There are parsers located [here](https://github.com/Azure/Azure-Sentinel/tree/master/Parsers/pfsense)