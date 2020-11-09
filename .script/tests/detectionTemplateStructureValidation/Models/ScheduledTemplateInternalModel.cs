using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.ModelValidations;
using Newtonsoft.Json;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model
{
    [PeriodGreaterThanOrEqualFrequency]
    [FrequencyLimitationForLongPeriodQuery]
    public class ScheduledTemplateInternalModel : AnalyticsTemplateInternalModelBase
    {
        [JsonProperty("requiredDataConnectors", Required = Required.Always)]
        public override List<DataConnectorInternalModel> RequiredDataConnectors { get; set; }

        [JsonProperty("severity", Required = Required.Always)]
        public Severity Severity { get; set; }

        [JsonProperty("query", Required = Required.Always)]
        [StringLength(10000, MinimumLength = 1)]
        public string Query { get; set; }

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
    }

    public enum Severity
    {
        Informational = 0,
        Low = 1,
        Medium = 2,
        High = 3
    }

    public enum AlertTriggerOperator
    {
        GreaterThan,
        LessThan,
        Equal,
        NotEqual
    }
}