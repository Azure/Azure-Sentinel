# ASIM parsers for Microsoft Defender for IoT - Endpoint

This template deploys all [Microsoft Defender for IoT - Endpoint](https://azure.microsoft.com/services/azure-defender-for-iot/) Azure Sentinel ASIM parsers. The template is part of the [Azure Sentinel Information Mode (ASIM)](https://aka.ms/AzSentinelNormalization).The Azure Sentinel Information Mode (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Azure Sentinel workspace.

When deploying the parsers, you make sure that telemetry from MD4IoT is analyzed using the built-in Azure Sentinel Analytics. You also enable analysts easier access to the telemetry using a known, standard, schema.

**Note: to get the best value from ASIM and make sure that Microsoft Defender for IoT - Endpoint telemetry is included in Azure Sentinel Analytics, deploy the [full ASIM parser suite](https://aka.ms/AzSentinelASim).**

For more information, see:

- [Microsoft Defender for IoT - Endpoint](https://azure.microsoft.com/services/azure-defender-for-iot/)
- [Normalization and the Azure Sentinel Information Model (ASIM)](https://aka.ms/AzSentinelNormalization)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/AzSentinelMD4IoTARM)

<br>

The template deploys the following:

- ASIM Process Events parser for MD4IoT-Endpoint - vimProcessEventMD4IoT
- ASIM Authentication Events parser for MD4IoT-Endpoint - vimAuthenticationMD4IoT
- ASIM Network Session Events parser for MD4IoT-Endpoint - vimNetworkSessionMD4IoT

<br>
