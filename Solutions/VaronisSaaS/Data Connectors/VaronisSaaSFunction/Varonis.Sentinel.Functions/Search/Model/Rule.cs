using System.Text.Json.Serialization;

namespace Varonis.Sentinel.Functions.Search.Model
{
    internal class Rule
    {
        [JsonPropertyName("dataField")]
        public int RuleID { get; set; }
        [JsonPropertyName("displayField")]
        public string RuleName { get; set; }
    }
}
