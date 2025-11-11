using Newtonsoft.Json;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation;
using System.ComponentModel.DataAnnotations;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model
{

    public class AlertDetailsOverride
    {
        [JsonProperty("alertDisplayNameFormat", Required = Required.Default)]
        [NonEmptyString]
        [StringLength(256, MinimumLength = 1)]
        [MaxAmountOfDynamicContentPlaceHolders(3)]
        public string AlertDisplayNameFormat { get; set; }

        [JsonProperty("alertDescriptionFormat", Required = Required.Default)]
        [NonEmptyString]
        [StringLength(5000, MinimumLength = 1)]
        [MaxAmountOfDynamicContentPlaceHolders(3)]
        public string AlertDescriptionFormat { get; set; }

        [JsonProperty("alertTacticsColumnName", Required = Required.Default)]
        public string AlertTacticsColumnName { get; set; }

        [JsonProperty("alertSeverityColumnName", Required = Required.Default)]
        public string AlertSeverityColumnName { get; set; }
    }
}
