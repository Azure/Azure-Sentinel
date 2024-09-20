# ASIM parsers for Microsoft Defender for IoT - Endpoint

This template deploys all [Microsoft Defender for IoT - Endpoint](https://azure.microsoft.com/services/azure-defender-for-iot/) Microsoft Sentinel ASIM parsers. The template is part of the [Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM).The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

When deploying the parsers, you make sure that telemetry from MD4IoT is analyzed using the built-in Microsoft Sentinel Analytics. You also enable analysts easier access to the telemetry using a known, standard, schema.

**Note: to get the best value from ASIM and make sure that Microsoft Defender for IoT - Endpoint telemetry is included in Microsoft Sentinel Analytics, deploy the [full ASIM parser suite](https://aka.ms/DeployASIM).**

For more information, see:

- [Microsoft Defender for IoT - Endpoint](https://azure.microsoft.com/services/azure-defender-for-iot/)
- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimMD4IoTARM)

<br>

The template deploys the following:

- ASIM Process Events parser for MD4IoT-Endpoint - vimProcessEventMD4IoT
- ASIM Authentication Events parser for MD4IoT-Endpoint - vimAuthenticationMD4IoT
- ASIM Network Session Events parser for MD4IoT-Endpoint - vimNetworkSessionMD4IoT

<br>
