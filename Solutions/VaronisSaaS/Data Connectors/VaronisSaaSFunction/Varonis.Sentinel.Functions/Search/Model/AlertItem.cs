using System;

namespace Varonis.Sentinel.Functions.Search.Model
{
    internal class AlertItem
    {
        public Guid ID { get; set; }
        public string Name { get; set; }
        public DateTime Time { get; set; }
        public string Severity { get; set; }
        public int SeverityId { get; set; }
        public string Category { get; set; }
        public string[] Country { get; set; }
        public string[] State { get; set; }
        public string Status { get; set; }
        public int StatusId { get; set; }
        public string CloseReason { get; set; }
        public bool? BlacklistLocation { get; set; }
        public string[] AbnormalLocation { get; set; }
        public int NumOfAlertedEvents { get; set; }
        public string[] UserName { get; set; }
        public string[] SamAccountName { get; set; }
        public string[] PrivilegedAccountType { get; set; }
        public bool? ContainMaliciousExternalIP { get; set; }
        public string[] IPThreatTypes { get; set; }
        public string[] Asset { get; set; }
        public bool?[] AssetContainsFlaggedData { get; set; }
        public bool?[] AssetContainsSensitiveData { get; set; }
        public string[] Platform { get; set; }
        public string[] FileServerOrDomain { get; set; }
        public DateTime? EventUTC { get; set; }
        public string[] DeviceName { get; set; }
        public DateTime IngestTime { get; set; }
    }
}
