using System.Collections.Generic;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using MappingEntityType = Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.Internal.EntityType;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM
{
    public class EntityMapping
    {
        [JsonProperty("entityType", Required = Required.Always)]
        [JsonConverter(typeof(StringEnumConverter))]
        public MappingEntityType.EntityType EntityType { get; set; } // TODO (Alert Enrichment): remove the namespace once we use the Full enum for IncidentConfiguration as well

        [JsonProperty("fieldMappings", Required = Required.Always)]
        public List<FieldMapping> FieldMappings { get; set; }
    }
}
