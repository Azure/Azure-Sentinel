using Newtonsoft.Json;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model
{
    public class EventGroupingSettings
    {
        [JsonProperty("aggregationKind", Required = Required.Always)]
        public EventGroupingAggregationKind AggregationKind { get; set; }
    }

    public enum EventGroupingAggregationKind
    {
        SingleAlert = 0,
        AlertPerResult = 1
    }
}
