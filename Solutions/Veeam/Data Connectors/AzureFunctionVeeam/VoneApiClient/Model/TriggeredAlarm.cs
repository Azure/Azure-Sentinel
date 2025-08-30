using System.Text.Json.Serialization;

namespace VoneApiClient.Models
{
    public class TriggeredAlarm
    {
        [JsonPropertyName("triggeredAlarmId")]
        public int? TriggeredAlarmId { get; set; }

        [JsonPropertyName("name")]
        public string? Name { get; set; }

        [JsonPropertyName("alarmTemplateId")]
        public int? AlarmTemplateId { get; set; }

        [JsonPropertyName("predefinedAlarmId")]
        public int? PredefinedAlarmId { get; set; }

        [JsonPropertyName("triggeredTime")]
        public DateTime TriggeredTime { get; set; }

        [JsonPropertyName("status")]
        public string? Status { get; set; }

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("comment")]
        public string? Comment { get; set; }

        [JsonPropertyName("repeatCount")]
        public int? RepeatCount { get; set; }

        [JsonPropertyName("alarmAssignment")]
        public AlarmAssignment AlarmAssignment { get; set; }

        [JsonPropertyName("childAlarmsCount")]
        public int? ChildAlarmsCount { get; set; }

        [JsonPropertyName("remediation")]
        public List<Remediation> Remediation { get; set; }
    }

    public class AlarmAssignment
    {
        [JsonPropertyName("objectId")]
        public int? ObjectId { get; set; }

        [JsonPropertyName("objectName")]
        public string? ObjectName { get; set; }

        [JsonPropertyName("objectType")]
        public string? ObjectType { get; set; }
    }

    public class Remediation
    {
        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("mode")]
        public RemediationMode Mode { get; set; }
    }

    [JsonConverter(typeof(JsonStringEnumConverter))]
    public enum RemediationMode
    {
        Disable,
        Manual,
        Automatic
    }
}
