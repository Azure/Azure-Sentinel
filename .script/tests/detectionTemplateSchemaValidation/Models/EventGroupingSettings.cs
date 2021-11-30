using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model
{
    public class EventGroupingSettings
    {
        [JsonProperty("aggregationKind", Required = Required.Always)]
        [JsonConverter(typeof(StringEnumConverter))] //test to see if this works and is enough. Will probably not catch cases that enter an int as the aggregationKind. Are we ok with that? Will it catch an int that is out of the bounds of the enum such as 9 when there are only 2 values in the enum?
        public EventGroupingAggregationKind AggregationKind { get; set; }
    }

    public enum EventGroupingAggregationKind
    {
        SingleAlert = 0,
        AlertPerResult = 1
    }
}
