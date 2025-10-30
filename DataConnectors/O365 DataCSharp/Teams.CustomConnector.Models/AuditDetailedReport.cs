using System;

namespace Teams.CustomConnector.Models
{
    /// <summary></summary>
    public partial class Member
    {
        public string DisplayName { get; set; }
        public string Role { get; set; }
        public string Upn { get; set; }
    }

    /// <summary></summary>
    public class AuditDetailedReport
    {
        public DateTimeOffset CreationTime { get; set; }
        public string Id { get; set; }

        public string Version { get; set; }
        public string Workload { get; set; }
        public string UserId { get; set; }
        public string TeamGuid { get; set; }
        public string TeamName { get; set; }
        public string CommunicationType { get; set; }

        public string Operation { get; set; }
        public string OrganizationId { get; set; }
        public string RecordType { get; set; }
        public string UserKey { get; set; }
        public string UserType { get; set; }

        public string ItemName { get; set; }
        public string RecordTypeName { get; set; }
        public string EventSource { get; set; }
        public string SiteUrl { get; set; }
        public string Site { get; set; }
        public string WebId { get; set; }
        public string WebSiteName { get; set; }
        public string ListId { get; set; }

        public Member[] Members { get; set; }
        public string ListName { get; set; }
        public string ListItemUniqueId { get; set; }
        public string ItemType { get; set; }
        public string SourceFileExtension { get; set; }
        public string SourceFileName { get; set; }
        public string SourceRelativeUrl { get; set; }
        public string UserAgent { get; set; }
        public string EventData { get; set; }
        public string TargetUserOrGroupType { get; set; }
        public string TargetUserOrGroupName { get; set; }
        public string TargetExtUserName { get; set; }
        public string UniqueSharingId { get; set; }
        public string ClientIP { get; set; }
        public string CorrelationId { get; set; }
    }

}
