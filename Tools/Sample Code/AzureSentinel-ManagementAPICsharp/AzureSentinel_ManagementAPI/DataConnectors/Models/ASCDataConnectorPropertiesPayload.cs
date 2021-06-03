using Newtonsoft.Json;

namespace AzureSentinel_ManagementAPI.DataConnectors.Models
{
    public class ASCDataConnectorPropertiesPayload
    {
        public string SubscriptionId { get; set; }

        public string TenantId { get; set; }
        
        [JsonProperty("dataTypes")]
        public ASCDataConnectorDataTypesPayload DataTypesPayload { get; set; }
    }
}