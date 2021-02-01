using Newtonsoft.Json;
using System.Collections.Generic;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model
{
    public class DataConnectorInternalModel
    {
        [JsonProperty("connectorId")]
        public string ConnectorId { get; set; }

        [JsonProperty("dataTypes", Required = Required.Always)]
        public List<string> DataTypes { get; set; }
    }
}