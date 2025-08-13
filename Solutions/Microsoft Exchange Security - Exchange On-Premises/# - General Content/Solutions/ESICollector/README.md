# **Exchange Security Insight Collector Download**

## Description

The Exchange Security Insight Collector is a PowerShell script that collects data from Exchange Servers and Exchange Online. The script is designed to be run on a Windows machine and can be scheduled to run at regular intervals. The script collects data from Exchange Servers and Exchange Online and sends it to the Microsoft Exchange Security Insight solution for Microsoft Sentinel.

You can refer to the Exchange Securitty Insight Collector [here](./../../Documentations/ESICollector.md)

Parameters are described in the Configuration file. Explanation of the parameters is available in the [the Parameters description document](./Parameters.md)

## Versioning

## Actual Version : 7.6.0.1

## Upgrade paths

### From 7.6.0.0 to 7.6.0.1

#### **Configuration File**

Nothing to change

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

### From 7.5.2.2 to 7.6.0.0

#### **Configuration File**

Notning to change

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

### From 7.5.2.1 to 7.5.2.2

#### **Configuration File**

Update Config File to the new version. Be carefull to keep your custom parameters.

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

### From 7.5.2.1 to 7.5.2.2

#### **Configuration File**

Nothing to change

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

### From 7.5.2.0 to 7.5.2.1

#### **Configuration File**

Parameter "PaginationErrorThreshold": 5 is added in the Advanced part

A new category OnlineMessageTracking could be added. The segment can be added in InstanceConfiguration part : 
    "ExchangeOnlineMessageTracking":{
			"All":"true",
			"Category":"OnlineMessageTracking",
			"Capabilities":"OL",
			"OutputName":"ExchangeOnlineMessageTracking"
		}

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

### From 7.5.1.1 to 7.5.2.0

#### **Configuration File**

Nothing changed

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

### From 7.5.0 to 7.5.1.1

#### **Configuration File**

Parameter "PaginationErrorThreshold": 5 is added in the Advanced part

A new category OnlineMessageTracking could be added. The segment can be added in InstanceConfiguration part : 
    "ExchangeOnlineMessageTracking":{
			"All":"true",
			"Category":"OnlineMessageTracking",
			"Capabilities":"OL",
			"OutputName":"ExchangeOnlineMessageTracking"
		}

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.


### From 7.4.2 to 7.5.0

#### **Configuration File**

Nothing changed

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.


### From 7.3.2 to 7.4.2

#### **Configuration File**

Parameters added in Advanced Section

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.
Attention, now ManagedIdentity is used for Exchange Online instead of RunAs Account.
Assign rights to Managed Identity following Standard Procedure : [EXO for ManagedIdentity](https://learn.microsoft.com/en-us/powershell/exchange/connect-exo-powershell-managed-identity?view=exchange-ps#step-4-grant-the-exchangemanageasapp-api-permission-for-the-managed-identity-to-call-exchange-online)

### From 7.3.1 to 7.3.2

#### **Configuration File**

Parameters added in Advanced Section

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.


### From 7.3.0 to 7.3.1

#### **Configuration File**

No changes in Configuration file

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

### From 7.2.0 to 7.3.0

#### **Configuration File**

The only change on the configuration file is adding a "Beta" Property in "Advanced" part. By default "Beta" is "False". If you decide to use Beta off Add-On files, you can switch this parameter to true. Attention, bugs can be present in Beta mode.

#### **ESI Collector Script**

Replace the old script version with the new one. nothing to modifiy in the script.

## Download availability/Rules

Only 2 major versions are kept on the public repository.
The zip file without versioning correspond to the latest version of the Collector.
