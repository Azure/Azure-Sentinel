namespace AzureSentinel_ManagementAPI.Actions.Models
{
    public class ActionRequestPropertiesPayload
    {
        public string LogicAppResourceId { get; set; }
        public string TriggerUri { get; set; }
    }
}