using AzureSentinel_ManagementAPI.Infrastructure.SharedModels.Enums;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace AzureSentinel_ManagementAPI.AlertRules.Models
{
    public class ScheduledAlertRulePropertiesPayload
    {
        public string Query { get; set; }
        public string QueryFrequency { get; set; }
        public string QueryPeriod { get; set; }
        
        [JsonConverter(typeof(StringEnumConverter))]
        public Severity Severity { get; set; }
        
        [JsonConverter(typeof(StringEnumConverter))]
        public TriggerOperator TriggerOperator { get; set; }
        
        public int TriggerThreshold { get; set; }
        public string DisplayName { get; set; }
        public bool Enabled { get; set; }
        public string SuppressionDuration { get; set; }
        public bool SuppressionEnabled { get; set; }
        public string Description { get; set; }
    }
}