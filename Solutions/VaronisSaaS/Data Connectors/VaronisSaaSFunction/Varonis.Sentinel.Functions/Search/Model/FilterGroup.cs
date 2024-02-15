using Newtonsoft.Json.Converters;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace Varonis.Sentinel.Functions.Search.Model
{
    internal class FilterGroup
    {
        public List<Filter> Filters { get; set; }

        [JsonConverter(typeof(JsonStringEnumConverter))]
        public FilterOperator FilterOperator { get; set; }
    }
}
