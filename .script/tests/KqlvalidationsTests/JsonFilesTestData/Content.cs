using Kusto.Language;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Text;

namespace Kqlvalidations.Tests
{
    public class Content
    {
        [JsonProperty("query")]
        public string Query { get; set; }

        public List<Item> items { get; set; }
    }

    public class Item
    {
        [JsonProperty("type")]
        public string type { get; set; }

        [JsonProperty("content")]
        public Content content { get; set; }

        [JsonProperty("required")]
        public List<string> required { get; set; }

        [JsonProperty("additionalProperties")]
        public bool additionalProperties { get; set; }

        [JsonProperty("minLength")]
        public int minLength { get; set; }

        [JsonProperty("description")]
        public string description { get; set; }
    }
}
