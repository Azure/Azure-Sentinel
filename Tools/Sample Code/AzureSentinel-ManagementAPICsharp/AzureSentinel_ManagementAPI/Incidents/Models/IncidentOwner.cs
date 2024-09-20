using System;
using System.Collections.Generic;
using System.Text;

namespace AzureSentinel_ManagementAPI.Incidents.Models
{
    public class IncidentOwner
    {
        public string ObjectId { get; set; }
        public string Email { get; set; }
        public string AssignedTo { get; set; }
        public string UserPrincipalName { get; set; }
    }
}
