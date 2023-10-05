using AzureSentinel_ManagementAPI.Infrastructure.SharedModels.Enums;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace AzureSentinel_ManagementAPI.Incidents.Models
{
    public class IncidentPropertiesPayload
    {
        [JsonConverter(typeof(StringEnumConverter))]
        public Severity Severity { get; set; } 

        [JsonConverter(typeof(StringEnumConverter))]
        public IncidentStatus Status { get; set; }
        
        public string Title { get; set; }

        public string Classification { get; set; }

        public string ClassificationComment { get; set; }

        public string ClassificationReason { get; set; }

        public string Description { get; set; }

        [JsonProperty("owner")]
        public IncidentOwner Owner { get; set; }
    }
}