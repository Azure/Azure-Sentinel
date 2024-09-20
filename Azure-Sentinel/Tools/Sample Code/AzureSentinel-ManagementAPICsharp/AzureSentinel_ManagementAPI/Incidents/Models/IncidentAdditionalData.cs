using System;
using System.Collections.Generic;
using System.Text;

namespace AzureSentinel_ManagementAPI.Incidents.Models
{
    public class IncidentAdditionalData
    {
        public int AlertsCount { get; set; }
        public int BookmarksCount { get; set; }
        public int CommentsCount { get; set; }
        public string[] AlertProductNames { get; set; }
        public string[] Tactics { get; set; }
    }
}
