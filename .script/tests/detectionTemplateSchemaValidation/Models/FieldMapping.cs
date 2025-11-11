using Newtonsoft.Json;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM
{
    public class FieldMapping
    {
        [JsonProperty("identifier", Required = Required.Always)]
        public string Identifier { get; set; }

        [JsonProperty("columnName", Required = Required.Always)]
        public string ColumnName { get; set; }
    }
}
