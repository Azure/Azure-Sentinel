using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model
{
    public abstract class QueryBasedTemplateInternalModel : AnalyticsTemplateInternalModelBase
    {
        [JsonProperty("severity", Required = Required.Always)]
        public Severity Severity { get; set; }

        [JsonProperty("query", Required = Required.Always)]
        [StringLength(10000, MinimumLength = 1)]
        public string Query { get; set; }

        [JsonProperty("customDetails", Required = Required.Default, NullValueHandling = NullValueHandling.Ignore)]
        [DictionaryLength(20)]
        [DictionaryMaxKeyAndValueLengths(maxKeyLength: 20, maxValueLength: 500)] // 500 is the max length of a column name in LA
        [DictionaryKeyMatchesRegex("^[a-zA-Z]+\\w*$")] // The custom field key must start with an English letter and contain only alphanumeric characters (i.e. [a-zA-Z0-9_])
        [DictionaryValueMatchesRegex("^[a-zA-Z_]+\\w*$")] // The custom field value must start with an English letter or an underscore and contain only alphanumeric characters (i.e. [a-zA-Z0-9_])
        public Dictionary<string, string> CustomDetails { get; set; }

        [JsonProperty("entityMappings", Required = Required.Default, NullValueHandling = NullValueHandling.Ignore)]
        [ValidEntityMappings(entityMappingsMinLength: 1, entityMappingsMaxLength: 10, fieldMappingsMinLength: 1, fieldMappingsMaxLength: 3)] // max for entityMappings is 10 - https://learn.microsoft.com/en-us/azure/sentinel/sentinel-service-limits, max for field mappings is 3, look for "three" in the docs - https://learn.microsoft.com/en-us/azure/sentinel/entities-reference
        public List<EntityMapping> EntityMappings { get; set; }

        [JsonProperty("alertDetailsOverride", Required = Required.Default, NullValueHandling = NullValueHandling.Ignore)]
        public AlertDetailsOverride AlertDetailsOverride { get; set; }

        [JsonProperty("version", Required = Required.Default)]
        [StringLength(20)] //Version should be quite short (for example "1.2.2")
        [QueryBasedTemplateVersionValidator]
        public string Version { get; set; }
    }

    public enum Severity
    {
        Informational = 0,
        Low = 1,
        Medium = 2,
        High = 3
    }
}
