using Newtonsoft.Json;

namespace AzureSentinel_ManagementAPI.Incidents.Models.Comments
{
    public class IncidentCommentPayload
    {
        [JsonProperty("properties")]
        public IncidentCommentPropertiesPayload PropertiesPayload { get; set; }
    }
}