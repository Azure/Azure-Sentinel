# Azure Defender for IoT ASIM parsers

This template deploys all [Azure Defender for IoT](https://azure.microsoft.com/en-us/services/azure-defender-for-iot/) Azure Sentinel ASIM parsers. The template is part of the [Azure Sentinel Information Mode (ASIM)](https://aka.ms/AzSentinelNormalization).The Azure Sentinel Information Mode (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Azure Sentinel workspace.

When deploying the parsers, you make sure that telemetry from AD4IoT is analyzed using the built-in Azure Sentinel Analytics. You also enable analysts easier access to the telemetry using a known, standard, schema.

For more information, see:

- [Azure Defender for IoT](https://azure.microsoft.com/en-us/services/azure-defender-for-iot/) 
- [Normalization and the Azure Sentinel Information Model (ASIM)](https://aka.ms/AzSentinelNormalization)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/AzSentinelAD4IoTARM)

<br>

The template deploys the following:
 - ASIM Process Events parser for AD4IoT - vimProcessEventAD4IoT 
 - ASIM Autnetication Events parser for AD4IoT - vimAuthenticationAD4IoT 
 - ASIM Netwrork Session Events parser for AD4IoT - vimNetworkSessionAD4IoT 

<br>
