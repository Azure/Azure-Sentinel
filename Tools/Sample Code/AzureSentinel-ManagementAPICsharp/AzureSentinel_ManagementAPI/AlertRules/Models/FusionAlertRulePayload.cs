using Newtonsoft.Json;

namespace AzureSentinel_ManagementAPI.AlertRules.Models
{
    public class FusionAlertRulePayload : AlertRulePayload
    {
        public FusionAlertRulePayload()
        {
            Kind = AlertRuleKind.Fusion;
        }
        
        [JsonProperty("properties")]
        public FusionAlertRulePropertiesPayload PropertiesPayload { get; set; }
    }
}