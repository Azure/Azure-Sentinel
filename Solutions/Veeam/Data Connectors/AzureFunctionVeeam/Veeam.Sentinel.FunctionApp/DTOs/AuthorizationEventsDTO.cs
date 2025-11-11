using System.Text.Json.Serialization;

namespace Sentinel.DTOs
{
    public class AuthorizationEventsDTO
    {
        [JsonPropertyName("VbrHostName")]
        public string VbrHostName { get; set; }

        [JsonPropertyName("State")]
        public string? State { get; set; }

        [JsonPropertyName("Id")]
        public Guid? Id { get; set; }

        [JsonPropertyName("Name")]
        public string Name { get; set; }

        [JsonPropertyName("Description")]
        public string Description { get; set; }

        [JsonPropertyName("CreationTime")]
        public DateTime? CreationTime { get; set; }

        [JsonPropertyName("CreatedBy")]
        public string CreatedBy { get; set; }

        [JsonPropertyName("ExpirationTime")]
        public DateTime? ExpirationTime { get; set; }

        [JsonPropertyName("ProcessedBy")]
        public string ProcessedBy { get; set; }

        [JsonPropertyName("ProcessedTime")]
        public DateTime? ProcessedTime { get; set; }
    }
}
