using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Text;

namespace AzureSentinel_ManagementAPI.IncidentRelation.Models
{
    public class RelationEntityPayload
    {
        [JsonProperty("expansionId")]
        public string ExpansionId { get; set; }
    }
}
