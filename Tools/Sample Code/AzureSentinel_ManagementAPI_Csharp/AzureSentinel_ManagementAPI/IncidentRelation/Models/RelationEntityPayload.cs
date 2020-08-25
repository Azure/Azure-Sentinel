using Newtonsoft.Json;

namespace AzureSentinel_ManagementAPI.IncidentRelation.Models
{
    public class RelationEntityPayload
    {
        [JsonProperty("expansionId")]
        public string ExpansionId { get; set; }
    }
}
