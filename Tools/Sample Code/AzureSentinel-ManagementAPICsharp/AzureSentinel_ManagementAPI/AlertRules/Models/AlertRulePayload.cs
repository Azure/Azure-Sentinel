using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace AzureSentinel_ManagementAPI.AlertRules.Models
{
    public abstract class AlertRulePayload
    {
        public string Etag { get; set; }

        [JsonConverter(typeof(StringEnumConverter))]
        public AlertRuleKind Kind { get; set; }

    }
}