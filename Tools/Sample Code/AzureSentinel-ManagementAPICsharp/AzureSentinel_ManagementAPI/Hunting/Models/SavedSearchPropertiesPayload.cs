using System;
using System.Collections.Generic;
using System.Text;

namespace AzureSentinel_ManagementAPI.Hunting.Models
{
    public class SavedSearchPropertiesPayload
    {
        public string Category { get; set; }
        public string DisplayName { get; set; }
        public int Version { get; set; }
        public string FunctionAlias { get; set; }
        public string FunctionParameters { get; set; }
        public List<SavedSearchTag> Tags { get; set; }
        public string Query { get; set; }
    }
}
