using Newtonsoft.Json.Converters;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace Varonis.Sentinel.Functions.Search.Model
{
    internal class Filter
    {
        [JsonConverter(typeof(JsonStringEnumConverter))]
        public EmOperator Operator { get; set; }

        public string Path { get; set; }

        public IReadOnlyCollection<object> Values { get; set; }
    }
}