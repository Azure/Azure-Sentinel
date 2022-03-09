namespace AzureSentinel_ManagementAPI.Infrastructure.Configuration
{
    public class AzureSentinelApiConfiguration
    {
        public string InstanceName { get; set; }
        public string TenantId { get; set; }
        public string AppId { get; set; }
        public string AppSecret { get; set; }
        public string SubscriptionId { get; set; }
        public string ResourceGroupName { get; set; }
        public string WorkspaceName { get; set; }
        public string ApiVersion { get; set; }
        public string PreviewApiVersion { get; set; }
        public string UrlTemplate { get; set; }
        public string OperationInsightUrlTemplate { get; set; }
        public string BaseUrl => string.Format(UrlTemplate, SubscriptionId, ResourceGroupName, WorkspaceName);
        public string OperationInsightBaseUrl => string.Format(OperationInsightUrlTemplate, SubscriptionId, ResourceGroupName, WorkspaceName);
        public string WorkflowId { get; set; }
        public string FilterQuery { get; set; }

        public string LastCreatedAction { get; set; }
        public string LastCreatedAlertRule { get; set; }
        public string LastCreatedBookmark { get; set; }
        public string LastCreatedIncident { get; set; }
        public string LastCreatedDataConnector { get; set; }
    }
}