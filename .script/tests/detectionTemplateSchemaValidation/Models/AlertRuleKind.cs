

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model
{
    public enum AlertRuleKind
    {
        Undefined = 0,
        Scheduled = 1,
        BlackBox = 2,
        Fusion = 4,
        MLBehaviorAnalytics = 5,
        MicrosoftSecurityIncidentCreation = 6,
        ThreatIntelligence = 7,
        Anomaly = 8,
        NRT = 9
    }
}
