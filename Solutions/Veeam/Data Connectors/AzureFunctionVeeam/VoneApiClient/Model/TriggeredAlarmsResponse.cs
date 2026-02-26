using System.Text.Json.Serialization;


namespace VoneApiClient.Models
{
    public class TriggeredAlarmsResponse
    {
        [JsonPropertyName("items")]
        public List<TriggeredAlarm> Items { get; set; } = new List<TriggeredAlarm>();
    }

}
