using System;

namespace Varonis.Sentinel.Functions.DatAlert
{
    internal record DatAlertParams
    (
        DateTime Start,
        DateTime End,
        string AlertSeverity,
        string ThreatDetectionPolicies,
        string AlertStatus,
        int MaxAlertRetrieval
    );
}
