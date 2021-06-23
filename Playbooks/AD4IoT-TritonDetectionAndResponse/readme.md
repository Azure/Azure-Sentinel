# AD4IoT - Triton Attack Playbook
Author: Amit Sheps and Lior Tamir

In December 2017, it was reported that safety systems of an unidentified power station, believed to be in Saudi Arabia, were compromised when a Triconex industrial a safety system made by Schneider Electric SE was targeted. It is believed that this was a state-sponsored attack. 

Attackers used sophisticated malware called Triton. Using stolen credentials of one of the workstations on the IT domain, they managed to establish a remote desktop connection to the engineering workstation; program the PLCs and change its logic in a way that could have led to a disaster.

This playbook allows users to validate any PLC programming command which is performed to prevent a Triton attack.   

### Note: This playbook offers a complex flow, and requires configuration by the specific environment.


## Deploy to Azure

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)]("https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAD4IoT-TritonDetectionAndResponse%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)]("https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAD4IoT-TritonDetectionAndResponse%2Fazuredeploy.json)