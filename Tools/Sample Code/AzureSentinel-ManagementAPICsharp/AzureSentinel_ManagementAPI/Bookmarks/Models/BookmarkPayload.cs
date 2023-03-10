using Newtonsoft.Json;

namespace AzureSentinel_ManagementAPI.Bookmarks.Models
{
    public class BookmarkPayload
    {
        [JsonProperty("etag")]
        public string ETag { get; set; }
        
        [JsonProperty("properties")]
        public BookmarkPropertiesPayload PropertiesPayload { get; set; }
    }
}