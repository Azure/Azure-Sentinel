# Proofpoint POD MailLog ASIM EmailEvent Normalization Parser

ARM template for ASIM EmailEvent schema parser for Proofpoint POD MailLog.

Filters and normalizes ProofpointPODMailLog_CL SMTP receipt and delivery records to EmailEvent.
Uses the CCP table schema and repository samples; live validation is deferred.
Header sender, header recipients, subject and delivery location are unavailable;
nonempty filters for these fields return no records.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM EmailEvent normalization schema reference](https://aka.ms/ASimEmailEventDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimEmailEvent/CHANGELOG/vimEmailEventProofpointPODMailLog.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FvimEmailEventProofpointPODMailLog%2FvimEmailEventProofpointPODMailLog.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimEmailEvent%2FARM%2FvimEmailEventProofpointPODMailLog%2FvimEmailEventProofpointPODMailLog.json)
