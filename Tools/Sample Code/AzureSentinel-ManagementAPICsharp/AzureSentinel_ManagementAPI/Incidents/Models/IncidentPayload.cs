using Newtonsoft.Json;
using System.Diagnostics.Tracing;

namespace AzureSentinel_ManagementAPI.Incidents.Models
{
    public class IncidentPayload
    {
        [JsonProperty("properties")]
        public IncidentPropertiesPayload PropertiesPayload { get; set; }

        [JsonProperty("etag")]
        public string Etag { get; set; }

        [JsonProperty("name")]
        public string Name { get; set; }
    }
}