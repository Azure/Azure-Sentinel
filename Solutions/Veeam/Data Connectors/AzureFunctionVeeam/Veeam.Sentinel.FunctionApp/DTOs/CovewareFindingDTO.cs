using Newtonsoft.Json;

namespace Sentinel.DTOs
{
    public class CovewareFindingDTO
    {
        [JsonProperty("CovewareHostName")] public string CovewareHostName { get; set; } = "";

        [JsonProperty("Artifact")] public string Artifact { get; set; } = "";

        [JsonProperty("EventType")] public string EventType { get; set; } = "";

        [JsonProperty("TechniqueId")] public string TechniqueId { get; set; } = "";

        [JsonProperty("EventTime")] public DateTime EventTime { get; set; }

        [JsonProperty("FirstRunOrAccessed")] public DateTime? FirstRunOrAccessed { get; set; }

        [JsonProperty("Hostname")] public string Hostname { get; set; } = "";

        [JsonProperty("EventActivity")] public string EventActivity { get; set; } = "";

        [JsonProperty("Country")] public string Country { get; set; } = "";

        [JsonProperty("Id")] public string Id { get; set; } = "";

        [JsonProperty("Md5Hash")] public string Md5Hash { get; set; } = "";

        [JsonProperty("Sha1Hash")] public string Sha1Hash { get; set; } = "";

        [JsonProperty("Sha256Hash")] public string Sha256Hash { get; set; } = "";

        [JsonProperty("MachineId")] public string MachineId { get; set; } = "";

        [JsonProperty("RiskLevel")] public string RiskLevel { get; set; } = "";

        [JsonProperty("ScanTime")] public DateTime ScanTime { get; set; }

        [JsonProperty("Username")] public string? Username { get; set; }
    }
}