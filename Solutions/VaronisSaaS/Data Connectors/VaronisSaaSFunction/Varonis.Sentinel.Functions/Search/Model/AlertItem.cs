using System;

namespace Varonis.Sentinel.Functions.Search.Model
{
    internal class AlertItem
    {
        public Guid AlertId { get; set; }
        public string ThreatDetectionPolicyName { get; set; }
        public DateTime? AlertTime { get; set; }
        public string AlertSeverity { get; set; }
        public string AlertCategory { get; set; }
        public string[] Countries { get; set; }
        public string[] States { get; set; }
        public string Status { get; set; }
        public string CloseReason { get; set; }
        public bool? BlacklistedLocation { get; set; }
        public string[] AbnormalLocations { get; set; }
        public int? EventsCount { get; set; }
        public string[] PrivilegedAccountType { get; set; }
        public string[] UserNames { get; set; }
        public string[] UserSamAccountNames { get; set; }
        public bool? ContainsMaliciousExternalIPs { get; set; }
        public string[] AggregatedExternalIPThreatTypes { get; set; }
        public string[] Assets { get; set; }
        public bool?[] FlaggedDataExposed { get; set; }
        public bool?[] SensitiveDataExposed { get; set; }
        public string[] DataSourceTypes { get; set; }
        public string[] DataSources { get; set; }
        public string[] DeviceNames { get; set; }
        public DateTime? InitialEventTimeUTC { get; set; }
        public bool?[] AccountsHaveFollowUpIndicators { get; set; }
        public DateTime? AlertTimeUTC { get; set; }
        public DateTime? InitialEventTime { get; set; }
        public bool? AssignedtoVaronis { get; set; }
        public string EscalationType { get; set; }
        public string MitreTacticName { get; set; }
        public string ClosedBy { get; set; }
        public DateTime? IngestTime { get; set; }
    }
}
