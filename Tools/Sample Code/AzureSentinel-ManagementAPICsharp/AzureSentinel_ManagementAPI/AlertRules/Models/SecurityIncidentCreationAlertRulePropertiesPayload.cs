namespace AzureSentinel_ManagementAPI.AlertRules.Models
{
    public class SecurityIncidentCreationAlertRulePropertiesPayload
    {
        public string ProductFilter { get; set; }
        public string DisplayName { get; set; }
        public bool Enabled { get; set; }
    }
}