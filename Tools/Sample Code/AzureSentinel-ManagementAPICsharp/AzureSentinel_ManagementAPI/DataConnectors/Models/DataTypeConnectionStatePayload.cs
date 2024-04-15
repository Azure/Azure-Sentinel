using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace AzureSentinel_ManagementAPI.DataConnectors.Models
{
    public class DataTypeConnectionStatePayload
    {
        [JsonConverter(typeof(StringEnumConverter))]
        public DataConnectionState State { get; set; }
    }
}