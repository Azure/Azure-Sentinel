using System.Text.Json.Serialization;

namespace Sentinel.DTOs
{
    public class TriggeredAlarmDTO
    {
        [JsonPropertyName("VoneHostName")]
        public string VoneHostName { get; set; }

        [JsonPropertyName("TriggeredAlarmId")]
        public int TriggeredAlarmId { get; set; }

        [JsonPropertyName("Name")]
        public string? Name { get; set; }

        [JsonPropertyName("AlarmTemplateId")]
        public int AlarmTemplateId { get; set; }

        [JsonPropertyName("PredefinedAlarmId")]
        public int PredefinedAlarmId { get; set; }

        [JsonPropertyName("TriggeredTime")]
        public DateTime TriggeredTime { get; set; }

        [JsonPropertyName("Status")]
        public string? Status { get; set; }

        [JsonPropertyName("Description")]
        public string? Description { get; set; }

        [JsonPropertyName("Comment")]
        public string? Comment { get; set; }

        [JsonPropertyName("RepeatCount")]
        public int RepeatCount { get; set; }

        [JsonPropertyName("ObjectId")]
        public int ObjectId { get; set; }

        [JsonPropertyName("ObjectName")]
        public string? ObjectName { get; set; }

        [JsonPropertyName("ObjectType")]
        public string? ObjectType { get; set; }

        [JsonPropertyName("ChildAlarmsCount")]
        public int ChildAlarmsCount { get; set; }

        [JsonPropertyName("RemediationDescription")]
        public string? RemediationDescription { get; set; }

        [JsonPropertyName("RemediationMode")]
        public string? RemediationMode { get; set; }
    }
}
