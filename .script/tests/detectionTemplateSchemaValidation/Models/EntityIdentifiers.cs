using System.Collections.Generic;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM
{
    public class EntityIdentifiers
    {
        public List<string> Identifiers { get; set; }

        public List<List<string>> RequiredIdentifiers { get; set; }
    }
}
