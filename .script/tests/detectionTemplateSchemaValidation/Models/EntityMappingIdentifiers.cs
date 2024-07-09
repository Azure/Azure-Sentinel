using System.Collections.Generic;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.Internal.EntityType;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM
{
    public static class EntityMappingIdentifiers
    {
        public static Dictionary<EntityType, EntityIdentifiers> EntityIdentifiersMap = new Dictionary<EntityType, EntityIdentifiers>()
        {
            {
                EntityType.Account,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "Name", "FullName", "NTDomain", "DnsDomain", "UPNSuffix", "Sid", "AadTenantId", "AadUserId", "PUID", "IsDomainJoined", "DisplayName", "ObjectGuid","CloudAppAccountId" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "FullName" },
                        new List<string>() { "Sid" },
                        new List<string>() { "Name" },
                        new List<string>() { "AadUserId" },
                        new List<string>() { "PUID" },
                        new List<string>() { "ObjectGuid" }
                    }
                }
            },
            {
                EntityType.AzureResource,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "ResourceId" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "ResourceId" }
                    }
                }
            },
            {
                EntityType.CloudApplication,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "AppId", "Name", "InstanceName" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "AppId" },
                        new List<string>() { "Name" }
                    }
                }
            },
            {
                EntityType.DNS,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "DomainName" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "DomainName" }
                    }
                }
            },
            {
                EntityType.File,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "Directory", "Name" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "Name" }
                    }
                }
            },
            {
                EntityType.FileHash,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "Algorithm", "Value" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "Algorithm", "Value" }
                    }
                }
            },
            {
                EntityType.Host,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "DnsDomain", "NTDomain", "HostName", "FullName", "NetBiosName", "AzureID", "OMSAgentID", "OSFamily", "OSVersion", "IsDomainJoined" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "FullName" },
                        new List<string>() { "HostName" },
                        new List<string>() { "NetBiosName" },
                        new List<string>() { "AzureID" },
                        new List<string>() { "OMSAgentID" }
                    }
                }
            },
            {
                EntityType.IoTDevice,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "DeviceId", "DeviceName", "Manufacturer", "Model", "FirmwareVersion", "OperatingSystem", "MacAddress", "Protocols", "SerialNumber", "Source", "IoTSecurityAgentId", "DeviceType" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "DeviceId" }
                    }
                }
            },
            {
                EntityType.IP,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "Address" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "Address" }
                    }
                }
            },
            {
                EntityType.Mailbox,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "MailboxPrimaryAddress", "DisplayName", "Upn", "ExternalDirectoryObjectId", "RiskLevel" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "MailboxPrimaryAddress" }
                    }
                }
            },
            {
                EntityType.MailCluster,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "NetworkMessageIds", "CountByDeliveryStatus", "CountByThreatType", "CountByProtectionStatus", "Threats", "Query", "QueryTime", "MailCount", "IsVolumeAnomaly", "Source", "ClusterSourceIdentifier", "ClusterSourceType", "ClusterQueryStartTime", "ClusterQueryEndTime", "ClusterGroup" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "Query" },
                        new List<string>() { "Source" }
                    }
                }
            },
            {
                EntityType.MailMessage,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "Recipient", "Urls", "Threats", "Sender", "P1Sender", "P1SenderDisplayName", "P1SenderDomain", "SenderIP", "P2Sender", "P2SenderDisplayName", "P2SenderDomain", "ReceivedDate", "NetworkMessageId", "InternetMessageId", "Subject", "BodyFingerprintBin1", "BodyFingerprintBin2", "BodyFingerprintBin3", "BodyFingerprintBin4", "BodyFingerprintBin5", "AntispamDirection", "DeliveryAction", "DeliveryLocation", "Language", "ThreatDetectionMethods" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "NetworkMessageId" },
                        new List<string>() { "Recipient" }
                    }
                }
            },
            {
                EntityType.Malware,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "Name", "Category" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "Name" }
                    }
                }
            },
            {
                EntityType.Process,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "ProcessId", "CommandLine", "ElevationToken", "CreationTimeUtc" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "CommandLine" },
                        new List<string>() { "ProcessId" }
                    }
                }
            },
            {
                EntityType.RegistryKey,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "Hive", "Key" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "Key" },
                        new List<string>() { "Hive" }
                    }
                }
            },
            {
                EntityType.RegistryValue,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "Name", "Value", "ValueType" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "Name" }
                    }
                }
            },
            {
                EntityType.SecurityGroup,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "DistinguishedName", "SID", "ObjectGuid" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "DistinguishedName" },
                        new List<string>() { "SID" },
                        new List<string>() { "ObjectGuid" }
                    }
                }
            },
            {
                EntityType.SubmissionMail,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "NetworkMessageId", "Timestamp", "Recipient", "Sender", "SenderIp", "Subject", "ReportType", "SubmissionId", "SubmissionDate", "Submitter" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "SubmissionId" },
                        new List<string>() { "NetworkMessageId" },
                        new List<string>() { "Recipient" },
                        new List<string>() { "Submitter" }
                    }
                }
            },
            {
                EntityType.URL,
                new EntityIdentifiers()
                {
                    Identifiers = new List<string>() { "Url" },
                    RequiredIdentifiers = new List<List<string>>()
                    {
                        new List<string>() { "Url" }
                    }
                }
            }
        };
    }
}
