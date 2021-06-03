using Newtonsoft.Json;

namespace AzureSentinel_ManagementAPI.IncidentRelation.Models
{
    public class RelationPayload
    {
        public RelationPayload()
        {
        }
        [JsonProperty("properties")] public RelationPropertiesPayload PropertiesPayload { get; set; }   
    }
}
