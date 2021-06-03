using Newtonsoft.Json;

namespace AzureSentinel_ManagementAPI.DataConnectors.Models
{
    public class ASCDataConnectorPayload : DataConnectorPayload
    {
         [JsonProperty("properties")] public ASCDataConnectorPropertiesPayload PropertiesPayload { get; set; }
    }
}