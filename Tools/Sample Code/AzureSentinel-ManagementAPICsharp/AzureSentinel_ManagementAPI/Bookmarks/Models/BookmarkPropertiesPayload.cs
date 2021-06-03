using System.Collections.Generic;

namespace AzureSentinel_ManagementAPI.Bookmarks.Models
{
    public class BookmarkPropertiesPayload
    {
        public string DisplayName { get; set; }
        public string Query { get; set; }
        public string Notes { get; set; }
        public List<string> Labels { get; set; }
        public string QueryResult { get; set; }
        
        public IncidentInfo IncidentInfo { get; set; }
    }
}