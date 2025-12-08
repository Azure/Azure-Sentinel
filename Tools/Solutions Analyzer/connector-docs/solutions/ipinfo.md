# IPinfo

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | IPinfo |
| **Support Tier** | Partner |
| **Support Link** | [https://www.ipinfo.io/](https://www.ipinfo.io/) |
| **Categories** | domains |
| **First Published** | 2024-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IPinfo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IPinfo) |

## Data Connectors

This solution provides **17 data connector(s)**.

### [IPinfo ASN Data Connector](../connectors/ipinfoasndataconnector.md)

**Publisher:** IPinfo

### [IPinfo Abuse Data Connector](../connectors/ipinfoabusedataconnector.md)

**Publisher:** IPinfo

### [IPinfo Carrier Data Connector](../connectors/ipinfocarrierdataconnector.md)

**Publisher:** IPinfo

### [IPinfo Company Data Connector](../connectors/ipinfocompanydataconnector.md)

**Publisher:** IPinfo

### [IPinfo Country ASN Data Connector](../connectors/ipinfocountrydataconnector.md)

**Publisher:** IPinfo

### [IPinfo Domain Data Connector](../connectors/ipinfodomaindataconnector.md)

**Publisher:** IPinfo

### [IPinfo Iplocation Data Connector](../connectors/ipinfoiplocationdataconnector.md)

**Publisher:** IPinfo

### [IPinfo Iplocation Extended Data Connector](../connectors/ipinfoiplocationextendeddataconnector.md)

**Publisher:** IPinfo

### [IPinfo Privacy Data Connector](../connectors/ipinfoprivacydataconnector.md)

**Publisher:** IPinfo

### [IPinfo Privacy Extended Data Connector](../connectors/ipinfoprivacyextendeddataconnector.md)

**Publisher:** IPinfo

### [IPinfo RIRWHOIS Data Connector](../connectors/ipinforirwhoisdataconnector.md)

**Publisher:** IPinfo

### [IPinfo RWHOIS Data Connector](../connectors/ipinforwhoisdataconnector.md)

**Publisher:** IPinfo

### [IPinfo WHOIS ASN Data Connector](../connectors/ipinfowhoisasndataconnector.md)

**Publisher:** IPinfo

### [IPinfo WHOIS MNT Data Connector](../connectors/ipinfowhoismntdataconnector.md)

**Publisher:** IPinfo

### [IPinfo WHOIS NET Data Connector](../connectors/ipinfowhoisnetdataconnector.md)

**Publisher:** IPinfo

### [IPinfo WHOIS ORG Data Connector](../connectors/ipinfowhoisorgdataconnector.md)

**Publisher:** IPinfo

### [IPinfo WHOIS POC Data Connector](../connectors/ipinfowhoispocdataconnector.md)

**Publisher:** IPinfo

This IPinfo data connector installs an Azure Function app to download WHOIS_POC datasets and insert it into custom log table in Microsoft Sentinel

| | |
|--------------------------|---|
| **Tables Ingested** | `Ipinfo_WHOIS_POC_CL` |
| **Connector Definition Files** | [IPinfo_WHOIS_POC_API_AzureFunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IPinfo/Data%20Connectors/WHOIS%20POC/IPinfo_WHOIS_POC_API_AzureFunctionApp.json) |

[→ View full connector details](../connectors/ipinfowhoispocdataconnector.md)

## Tables Reference

This solution ingests data into **17 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Ipinfo_ASN_CL` | [IPinfo ASN Data Connector](../connectors/ipinfoasndataconnector.md) |
| `Ipinfo_Abuse_CL` | [IPinfo Abuse Data Connector](../connectors/ipinfoabusedataconnector.md) |
| `Ipinfo_Carrier_CL` | [IPinfo Carrier Data Connector](../connectors/ipinfocarrierdataconnector.md) |
| `Ipinfo_Company_CL` | [IPinfo Company Data Connector](../connectors/ipinfocompanydataconnector.md) |
| `Ipinfo_Country_CL` | [IPinfo Country ASN Data Connector](../connectors/ipinfocountrydataconnector.md) |
| `Ipinfo_Domain_CL` | [IPinfo Domain Data Connector](../connectors/ipinfodomaindataconnector.md) |
| `Ipinfo_Location_CL` | [IPinfo Iplocation Data Connector](../connectors/ipinfoiplocationdataconnector.md) |
| `Ipinfo_Location_extended_CL` | [IPinfo Iplocation Extended Data Connector](../connectors/ipinfoiplocationextendeddataconnector.md) |
| `Ipinfo_Privacy_CL` | [IPinfo Privacy Data Connector](../connectors/ipinfoprivacydataconnector.md) |
| `Ipinfo_Privacy_extended_CL` | [IPinfo Privacy Extended Data Connector](../connectors/ipinfoprivacyextendeddataconnector.md) |
| `Ipinfo_RIRWHOIS_CL` | [IPinfo RIRWHOIS Data Connector](../connectors/ipinforirwhoisdataconnector.md) |
| `Ipinfo_RWHOIS_CL` | [IPinfo RWHOIS Data Connector](../connectors/ipinforwhoisdataconnector.md) |
| `Ipinfo_WHOIS_ASN_CL` | [IPinfo WHOIS ASN Data Connector](../connectors/ipinfowhoisasndataconnector.md) |
| `Ipinfo_WHOIS_MNT_CL` | [IPinfo WHOIS MNT Data Connector](../connectors/ipinfowhoismntdataconnector.md) |
| `Ipinfo_WHOIS_NET_CL` | [IPinfo WHOIS NET Data Connector](../connectors/ipinfowhoisnetdataconnector.md) |
| `Ipinfo_WHOIS_ORG_CL` | [IPinfo WHOIS ORG Data Connector](../connectors/ipinfowhoisorgdataconnector.md) |
| `Ipinfo_WHOIS_POC_CL` | [IPinfo WHOIS POC Data Connector](../connectors/ipinfowhoispocdataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
