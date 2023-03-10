using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace AzureSentinel_ManagementAPI.DataConnectors.Models
{
    public abstract class DataConnectorPayload
    {
        [JsonProperty("etag")]
        public string ETag { get; set; }
        
        [JsonConverter(typeof(StringEnumConverter))]
        public DataConnectorKind Kind { get; set; }
    }
}