# WithSecureElementsViaFunction

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | WithSecure |
| **Support Tier** | Partner |
| **Support Link** | [https://www.withsecure.com/en/support](https://www.withsecure.com/en/support) |
| **Categories** | domains |
| **First Published** | 2024-02-22 |
| **Last Updated** | 2025-04-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WithSecureElementsViaFunction](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WithSecureElementsViaFunction) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [WithSecure Elements API (Azure Function)](../connectors/withsecureelementsviafunction.md)

**Publisher:** WithSecure

WithSecure Elements is the unified cloud-based cyber security platform designed to reduce risk, complexity, and inefficiency.



Elevate your security from your endpoints to your cloud applications. Arm yourself against every type of cyber threat, from targeted attacks to zero-day ransomware.



WithSecure Elements combines powerful predictive, preventive, and responsive security capabilities - all managed and monitored through a single security center. Our modular structure and flexible pricing models give you the freedom to evolve. With our expertise and insight, you'll always be empowered - and you'll never be alone.



With Microsoft Sentinel integration, you can correlate [security events](https://connect.withsecure.com/api-reference/security-events#overview) data from the WithSecure Elements solution with data from other sources, enabling a rich overview of your entire environment and faster reaction to threats.



With this solution Azure Function is deployed to your tenant, polling periodically for the WithSecure Elements security events.



For more information visit our website at: [https://www.withsecure.com](https://www.withsecure.com).

| | |
|--------------------------|---|
| **Tables Ingested** | `WsSecurityEvents_CL` |
| **Connector Definition Files** | [WithSecureElementsViaFunction.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WithSecureElementsViaFunction/Data%20Connectors/WithSecureElementsViaFunction.json) |

[→ View full connector details](../connectors/withsecureelementsviafunction.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `WsSecurityEvents_CL` | [WithSecure Elements API (Azure Function)](../connectors/withsecureelementsviafunction.md) |

[← Back to Solutions Index](../solutions-index.md)
