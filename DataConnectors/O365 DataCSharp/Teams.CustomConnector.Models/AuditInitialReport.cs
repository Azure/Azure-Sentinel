using System.Collections.Generic;

namespace Teams.CustomConnector.Models
{

    /// <summary></summary>
    public class AuditInitialReport
    {
        public string ContentUri { get; set; }
        public string ContentId { get; set; }
        public string ContentType { get; set; }
        public string ContentCreated { get; set; }
        public string ContentExpiration { get; set; }
    }


    /// <summary></summary>
    public class AuditInitialDataObject
    {
        public string AuditNextPageUri { get; set; }

        public List<AuditInitialReport> AuditInitialReports { get; set; }
    }
}
