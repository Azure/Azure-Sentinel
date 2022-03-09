using Newtonsoft.Json;

namespace AzureSentinel_ManagementAPI.Actions.Models
{
    public class ActionRequestPayload
    {
        [JsonProperty("etag")]
        public string ETag { get; set; }
        
        [JsonProperty("properties")]
        public ActionRequestPropertiesPayload PropertiesPayload { get; set; }
    }
}