using System.Collections.Generic;

namespace AsimParserValidation.Models
{
    /// <summary>
    /// Represents schema information for ASIM (Advanced Security Information Model) schemas
    /// </summary>
    public class SchemaInfo
    {
        /// <summary>
        /// The name of the schema (e.g., Authentication, Dns, etc.)
        /// </summary>
        public string SchemaName { get; set; } = string.Empty;

        /// <summary>
        /// The version of the schema (e.g., 0.1.3)
        /// </summary>
        public string SchemaVersion { get; set; } = string.Empty;

        /// <summary>
        /// The title of the schema for documentation
        /// </summary>
        public string SchemaTitle { get; set; } = string.Empty;

        /// <summary>
        /// The documentation link for the schema
        /// </summary>
        public string SchemaLink { get; set; } = string.Empty;

        /// <summary>
        /// Gets the predefined ASIM schema information
        /// </summary>
        public static List<SchemaInfo> GetSchemaInfoList()
        {
            return new List<SchemaInfo>
            {
                new SchemaInfo { SchemaName = "AlertEvent", SchemaVersion = "0.1", SchemaTitle = "ASIM Alert Event Schema", SchemaLink = "https://aka.ms/ASimAlertEventDoc" },
                new SchemaInfo { SchemaName = "AuditEvent", SchemaVersion = "0.1", SchemaTitle = "ASIM Audit Event Schema", SchemaLink = "https://aka.ms/ASimAuditEventDoc" },
                new SchemaInfo { SchemaName = "Authentication", SchemaVersion = "0.1.3", SchemaTitle = "ASIM Authentication Schema", SchemaLink = "https://aka.ms/ASimAuthenticationDoc" },
                new SchemaInfo { SchemaName = "Dns", SchemaVersion = "0.1.7", SchemaTitle = "ASIM Dns Schema", SchemaLink = "https://aka.ms/ASimDnsDoc" },
                new SchemaInfo { SchemaName = "DhcpEvent", SchemaVersion = "0.1", SchemaTitle = "ASIM Dhcp Schema", SchemaLink = "https://aka.ms/ASimDhcpEventDoc" },
                new SchemaInfo { SchemaName = "FileEvent", SchemaVersion = "0.2.1", SchemaTitle = "ASIM File Schema", SchemaLink = "https://aka.ms/ASimFileEventDoc" },
                new SchemaInfo { SchemaName = "NetworkSession", SchemaVersion = "0.2.6", SchemaTitle = "ASIM Network Session Schema", SchemaLink = "https://aka.ms/ASimNetworkSessionDoc" },
                new SchemaInfo { SchemaName = "ProcessEvent", SchemaVersion = "0.1.4", SchemaTitle = "ASIM Process Schema", SchemaLink = "https://aka.ms/ASimProcessEventDoc" },
                new SchemaInfo { SchemaName = "RegistryEvent", SchemaVersion = "0.1.2", SchemaTitle = "ASIM Registry Schema", SchemaLink = "https://aka.ms/ASimRegistryEventDoc" },
                new SchemaInfo { SchemaName = "UserManagement", SchemaVersion = "0.1.1", SchemaTitle = "ASIM User Management Schema", SchemaLink = "https://aka.ms/ASimUserManagementDoc" },
                new SchemaInfo { SchemaName = "WebSession", SchemaVersion = "0.2.6", SchemaTitle = "ASIM Web Session Schema", SchemaLink = "https://aka.ms/ASimWebSessionDoc" }
            };
        }
    }
}
