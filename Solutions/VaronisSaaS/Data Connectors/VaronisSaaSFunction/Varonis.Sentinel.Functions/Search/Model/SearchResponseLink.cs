using Newtonsoft.Json.Converters;
using System.Text.Json.Serialization;

namespace Varonis.Sentinel.Functions.Search.Model
{
    internal class SearchResponseLink
    {
        public string Location { get; set; }

        [JsonConverter(typeof(JsonStringEnumConverter))]
        public SearchResultType DataType { get; set; }
    }
}
