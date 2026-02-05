using System.Text.Json.Serialization;

namespace Sentinel.DTOs
{
    class BackupObjectDTO
    {
        [JsonPropertyName("ViType")]
        public required string ViType { get; set; }

        [JsonPropertyName("VmHostName")]
        public required string VmHostName { get; set; }

        [JsonPropertyName("VmName")]
        public required string VmName { get; set; }

        [JsonPropertyName("ObjectId")]
        public required string ObjectId { get; set; }
    }
}
