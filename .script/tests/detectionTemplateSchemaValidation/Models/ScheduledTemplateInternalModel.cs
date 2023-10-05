using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.ModelValidations;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model
{
    [PeriodGreaterThanOrEqualFrequency]
    [FrequencyLimitationForLongPeriodQuery]
    [NewEntityMappings]
    public class ScheduledTemplateInternalModel : QueryBasedTemplateInternalModel
    {
        [JsonProperty("requiredDataConnectors", Required = Required.Always)]
        public override List<DataConnectorInternalModel> RequiredDataConnectors { get; set; }

        [JsonProperty("queryFrequency", Required = Required.Always)]
        [JsonConverter(typeof(ScheduledTemplateTimeSpanConverter))]
        [RangeTimeSpanIsoFormat("00:05:00", "14.00:00:00")]
        public TimeSpan QueryFrequency { get; set; }

        [JsonProperty("queryPeriod", Required = Required.Always)]
        [JsonConverter(typeof(ScheduledTemplateTimeSpanConverter))]
        [RangeTimeSpanIsoFormat("00:05:00", "14.00:00:00")]
        public TimeSpan QueryPeriod { get; set; }

        [JsonProperty("triggerOperator", Required = Required.Always)]
        [JsonConverter(typeof(ScheduledTemplateTriggerOperatorConverter))]
        public AlertTriggerOperator TriggerOperator { get; set; }

        [JsonProperty("triggerThreshold", Required = Required.Always)]
        [Range(0, 10000)]
        public int TriggerThreshold { get; set; }
        
        [JsonProperty("eventGroupingSettings", Required = Required.Default, NullValueHandling = NullValueHandling.Ignore)]
        public EventGroupingSettings EventGroupingSettings { get; set; }

        [JsonProperty("kind", Required = Required.Always)]
        public override AlertRuleKind Kind { get; } = AlertRuleKind.Scheduled;
    }

    public enum AlertTriggerOperator
    {
        GreaterThan,
        LessThan,
        Equal,
        NotEqual
    }
}
