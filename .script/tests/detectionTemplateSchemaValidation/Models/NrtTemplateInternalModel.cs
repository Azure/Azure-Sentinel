

using Newtonsoft.Json;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model
{
    public class NrtTemplateInternalModel : QueryBasedTemplateInternalModel
    {
        [JsonProperty("kind", Required = Required.Always)]
        public override AlertRuleKind Kind { get; } = AlertRuleKind.NRT;
    }
}
