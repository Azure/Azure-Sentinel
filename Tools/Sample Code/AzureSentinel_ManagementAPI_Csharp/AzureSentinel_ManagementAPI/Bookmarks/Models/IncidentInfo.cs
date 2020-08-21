using AzureSentinel_ManagementAPI.Infrastructure.SharedModels.Enums;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace AzureSentinel_ManagementAPI.Bookmarks.Models
{
    public class IncidentInfo
    {
        public string IncidentId { get; set; }
        
        [JsonConverter(typeof(StringEnumConverter))]
        public Severity Severity { get; set; }
        public string Title { get; set; }
        public string RelationName { get; set; }
    }
}