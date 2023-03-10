using Newtonsoft.Json;

namespace AzureSentinel_ManagementAPI.AlertRules.Models
{
    public class ScheduledAlertRulePayload : AlertRulePayload
    {
        public ScheduledAlertRulePayload()
        {
            Kind = AlertRuleKind.Scheduled;
        }
        
        [JsonProperty("properties")]
        public ScheduledAlertRulePropertiesPayload PropertiesPayload { get; set; }

        public string Playbook { get; set; }
    }
}