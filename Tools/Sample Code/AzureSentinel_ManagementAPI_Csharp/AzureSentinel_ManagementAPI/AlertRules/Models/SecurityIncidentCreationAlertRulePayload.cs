using Newtonsoft.Json;

namespace AzureSentinel_ManagementAPI.AlertRules.Models
{
    public class SecurityIncidentCreationAlertRulePayload: AlertRulePayload
    {
        public SecurityIncidentCreationAlertRulePayload()
        {
            Kind = AlertRuleKind.MicrosoftSecurityIncidentCreation;
        }
        
        [JsonProperty("properties")]
        public SecurityIncidentCreationAlertRulePropertiesPayload PropertiesPayload { get; set; }
    }
}