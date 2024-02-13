using System;

namespace Varonis.Sentinel.Functions.DatAlert
{
    internal record DatAlertParams
    (
        DateTime Start,
        DateTime End,
        string Severities,
        string ThreatModel,
        string Status
    );
}
