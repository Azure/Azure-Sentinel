using Newtonsoft.Json;

namespace CovewareApiClient.Models
{
    public class CovewareFinding
    {
        [JsonProperty("artifact")] 
        public string Artifact { get; set; } = "";

        [JsonProperty("eventType")] 
        public string EventType { get; set; } = "";

        [JsonProperty("techniqueId")] 
        public string TechniqueId { get; set; } = "";

        [JsonProperty("eventTime")] 
        public DateTime EventTime { get; set; }

        [JsonProperty("firstRunOrAccessed")] 
        public DateTime? FirstRunOrAccessed { get; set; }

        [JsonProperty("hostname")] 
        public string Hostname { get; set; } = "";

        [JsonProperty("eventActivity")] 
        public string EventActivity { get; set; } = "";

        [JsonProperty("country")] 
        public string Country { get; set; } = "";

        [JsonProperty("id")] 
        public string Id { get; set; } = "";

        [JsonProperty("fileHashes")] 
        public CovewareFileHashes FileHashes { get; set; } = new();

        [JsonProperty("machineId")] 
        public string MachineId { get; set; } = "";

        [JsonProperty("riskLevel")] 
        public string RiskLevel { get; set; } = "";

        [JsonProperty("scanTime")] 
        public DateTime ScanTime { get; set; }

        [JsonProperty("username")] 
        public string? Username { get; set; }
    }

    public class CovewareFileHashes
    {
        [JsonProperty("md5")] 
        public string Md5 { get; set; } = "";

        [JsonProperty("sha1")] 
        public string Sha1 { get; set; } = "";

        [JsonProperty("sha256")] 
        public string Sha256 { get; set; } = "";
    }
}