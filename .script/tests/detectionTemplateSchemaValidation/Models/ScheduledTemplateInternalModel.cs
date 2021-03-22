using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.ModelValidations;
using Newtonsoft.Json;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model
{
    [PeriodGreaterThanOrEqualFrequency]
    [FrequencyLimitationForLongPeriodQuery]
    [NewEntityMappings]
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

        [JsonProperty("customDetails", Required = Required.Default, NullValueHandling = NullValueHandling.Ignore)]
        [DictionaryLength(20)]
        [DictionaryMaxKeyAndValueLengths(maxKeyLength: 20, maxValueLength: 500)] // 500 is the max length of a column name in LA
        [DictionaryKeyMatchesRegex("^[a-zA-Z]+\\w*$")] // The custom field key must start with an English letter and contain only alphanumeric characters (i.e. [a-zA-Z0-9_])
        [DictionaryValueMatchesRegex("^[a-zA-Z_]+\\w*$")] // The custom field value must start with an English letter or an underscore and contain only alphanumeric characters (i.e. [a-zA-Z0-9_])
        public Dictionary<string, string> CustomDetails { get; set; }

        [JsonProperty("entityMappings", Required = Required.Default, NullValueHandling = NullValueHandling.Ignore)]
        [ValidEntityMappings(entityMappingsMinLength: 1, entityMappingsMaxLength: 5, fieldMappingsMinLength: 1, fieldMappingsMaxLength: 3)]
        public List<EntityMapping> EntityMappings { get; set; }
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
