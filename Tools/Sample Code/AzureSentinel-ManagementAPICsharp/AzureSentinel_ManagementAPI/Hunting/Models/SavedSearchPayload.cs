using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Text;

namespace AzureSentinel_ManagementAPI.Hunting.Models
{
    public class SavedSearchPayload
    {
        [JsonProperty("etag")]
        public string Etag { get; set; }

        [JsonProperty("properties")]
        public SavedSearchPropertiesPayload PropertiesPayload { get; set; }
    }
}
