using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Text;

namespace Kqlvalidations.Tests
{
    public class DataConnectorSchema
    {
        [JsonProperty("connectivityCriterias")]
        public ConnectivityCriteria[] ConnectivityCriterias { get; set; }

        [JsonProperty("dataTypes")]
        public DataType[] DataTypes { get; set; }


        [JsonProperty("graphQueries")]
        public GraphQuery[] GraphQueries { get; set; }

        [JsonProperty("id")]
        public string Id { get; set; }


        [JsonProperty("sampleQueries")]
        public SampleQuery[] SampleQueries { get; set; }



        public partial class ConnectivityCriteria
        {
            [JsonProperty("type")]
            public string Type { get; set; }

            [JsonProperty("value")]
            public string[] Value { get; set; }
        }

        public partial class DataType
        {
            [JsonProperty("lastDataReceivedQuery")]
            public string LastDataReceivedQuery { get; set; }

            [JsonProperty("name")]
            public string Name { get; set; }
        }

        public partial class GraphQuery
        {
            [JsonProperty("baseQuery")]
            public string BaseQuery { get; set; }

            [JsonProperty("legend")]
            public string Legend { get; set; }

            [JsonProperty("metricName")]
            public string MetricName { get; set; }
        }



        public partial class SampleQuery
        {
            [JsonProperty("description")]
            public string Description { get; set; }

            [JsonProperty("query")]
            public string Query { get; set; }
        }
    }
}