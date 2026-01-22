using System.Text.Json.Serialization;

namespace Sentinel.Models
{
    public class WatchlistItemsResponse
    {
        [JsonPropertyName("value")]
        public List<WatchlistItem> Value { get; set; } = new();
    }

    public class WatchlistItem
    {
        [JsonPropertyName("id")]
        public string Id { get; set; } = string.Empty;

        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("etag")]
        public string Etag { get; set; } = string.Empty;

        [JsonPropertyName("type")]
        public string Type { get; set; } = string.Empty;

        [JsonPropertyName("systemData")]
        public SystemData SystemData { get; set; } = new();

        [JsonPropertyName("properties")]
        public WatchlistItemProperties Properties { get; set; } = new();
    }

    public class SystemData
    {
        [JsonPropertyName("createdAt")]
        public DateTime CreatedAt { get; set; }

        [JsonPropertyName("createdBy")]
        public string CreatedBy { get; set; } = string.Empty;

        [JsonPropertyName("createdByType")]
        public string CreatedByType { get; set; } = string.Empty;

        [JsonPropertyName("lastModifiedAt")]
        public DateTime LastModifiedAt { get; set; }

        [JsonPropertyName("lastModifiedBy")]
        public string LastModifiedBy { get; set; } = string.Empty;

        [JsonPropertyName("lastModifiedByType")]
        public string LastModifiedByType { get; set; } = string.Empty;
    }

    public class WatchlistItemProperties
    {
        [JsonPropertyName("watchlistItemType")]
        public string WatchlistItemType { get; set; } = string.Empty;

        [JsonPropertyName("watchlistItemId")]
        public string WatchlistItemId { get; set; } = string.Empty;

        [JsonPropertyName("tenantId")]
        public string TenantId { get; set; } = string.Empty;

        [JsonPropertyName("isDeleted")]
        public bool IsDeleted { get; set; }

        [JsonPropertyName("created")]
        public DateTime Created { get; set; }

        [JsonPropertyName("updated")]
        public DateTime Updated { get; set; }

        [JsonPropertyName("createdBy")]
        public UserInfo CreatedBy { get; set; } = new();

        [JsonPropertyName("updatedBy")]
        public UserInfo UpdatedBy { get; set; } = new();

        [JsonPropertyName("itemsKeyValue")]
        public Dictionary<string, object> ItemsKeyValue { get; set; } = new();

        [JsonPropertyName("entityMapping")]
        public Dictionary<string, object> EntityMapping { get; set; } = new();
    }

    public class UserInfo
    {
        [JsonPropertyName("objectId")]
        public string ObjectId { get; set; } = string.Empty;

        [JsonPropertyName("email")]
        public string Email { get; set; } = string.Empty;

        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;
    }
}
