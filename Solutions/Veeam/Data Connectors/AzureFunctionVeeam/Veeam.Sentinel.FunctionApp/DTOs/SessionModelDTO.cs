using System.Text.Json.Serialization;

namespace Sentinel.DTOs
{
    public class SessionModelDTO
    {
        [JsonPropertyName("VbrHostName")]
        public string VbrHostName { get; set; }

        [JsonPropertyName("SessionType")]
        public string SessionType { get; set; }

        [JsonPropertyName("State")]
        public string State { get; set; }

        [JsonPropertyName("PlatformName")]
        public string? PlatformName { get; set; }

        [JsonPropertyName("Id")]
        public Guid Id { get; set; }

        [JsonPropertyName("Name")]
        public string Name { get; set; }

        [JsonPropertyName("JobId")]
        public Guid JobId { get; set; }

        [JsonPropertyName("CreationTime")]
        public DateTime CreationTime { get; set; }

        [JsonPropertyName("EndTime")]
        public DateTime? EndTime { get; set; }

        [JsonPropertyName("ProgressPercent")]
        public int? ProgressPercent { get; set; }

        [JsonPropertyName("Result")]
        public string Result { get; set; }

        [JsonPropertyName("ResourceId")]
        public Guid? ResourceId { get; set; }

        [JsonPropertyName("ResourceReference")]
        public string ResourceReference { get; set; }

        [JsonPropertyName("ParentSessionId")]
        public Guid? ParentSessionId { get; set; }

        [JsonPropertyName("Usn")]
        public long Usn { get; set; }

        [JsonPropertyName("PlatformId")]
        public Guid? PlatformId { get; set; }

        [JsonPropertyName("ResultStatus")]
        public string ResultStatus { get; set; } // Parsed Result status (Success/Failed/etc.)

        [JsonPropertyName("ResultMessage")]
        public string ResultMessage { get; set; } // Parsed Result message

        [JsonPropertyName("ResultIsCanceled")]
        public bool ResultIsCanceled { get; set; }
    }
}
