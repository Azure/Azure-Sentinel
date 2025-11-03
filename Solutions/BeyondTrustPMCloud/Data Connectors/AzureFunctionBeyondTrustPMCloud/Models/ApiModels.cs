using System.Text.Json.Serialization;

namespace BeyondTrustPMCloud.Models;

// OAuth Token Response
public class OAuthTokenResponse
{
    [JsonPropertyName("access_token")]
    public string AccessToken { get; set; } = string.Empty;

    [JsonPropertyName("token_type")]
    public string TokenType { get; set; } = string.Empty;

    [JsonPropertyName("expires_in")]
    public int ExpiresIn { get; set; }

    [JsonPropertyName("scope")]
    public string Scope { get; set; } = string.Empty;
}

// Activity Audits Models
public class ActivityAuditsResponse
{
    [JsonPropertyName("pageNumber")]
    public int PageNumber { get; set; }

    [JsonPropertyName("pageSize")]
    public int PageSize { get; set; }

    [JsonPropertyName("totalRecordCount")]
    public int TotalRecordCount { get; set; }

    [JsonPropertyName("pageCount")]
    public int PageCount { get; set; }

    [JsonPropertyName("data")]
    public List<ActivityAudit> Data { get; set; } = new();
}

public class ActivityAudit
{
    [JsonPropertyName("id")]
    public int Id { get; set; }

    [JsonPropertyName("details")]
    public string Details { get; set; } = string.Empty;

    [JsonPropertyName("userId")]
    public string? UserId { get; set; }

    [JsonPropertyName("user")]
    public string User { get; set; } = string.Empty;

    [JsonPropertyName("entity")]
    public string Entity { get; set; } = string.Empty;

    [JsonPropertyName("entityName")]
    public string EntityName { get; set; } = string.Empty;

    [JsonPropertyName("auditType")]
    public string AuditType { get; set; } = string.Empty;

    [JsonPropertyName("created")]
    public DateTime Created { get; set; }

    [JsonPropertyName("changedBy")]
    public string ChangedBy { get; set; } = string.Empty;

    // Additional audit data properties (keeping as JsonElement for flexibility)
    [JsonPropertyName("apiClientDataAuditing")]
    public object? ApiClientDataAuditing { get; set; }

    [JsonPropertyName("computerDataAuditing")]
    public object? ComputerDataAuditing { get; set; }

    [JsonPropertyName("groupDataAuditing")]
    public object? GroupDataAuditing { get; set; }

    [JsonPropertyName("installationKeyDataAuditing")]
    public object? InstallationKeyDataAuditing { get; set; }

    [JsonPropertyName("policyDataAuditing")]
    public object? PolicyDataAuditing { get; set; }

    [JsonPropertyName("policyRevisionDataAuditing")]
    public object? PolicyRevisionDataAuditing { get; set; }

    [JsonPropertyName("settingsDataAuditing")]
    public object? SettingsDataAuditing { get; set; }

    [JsonPropertyName("userDataAuditing")]
    public object? UserDataAuditing { get; set; }

    [JsonPropertyName("mapToIdentityProviderGroupAuditing")]
    public object? MapToIdentityProviderGroupAuditing { get; set; }

    [JsonPropertyName("openIdConfigDataAuditing")]
    public object? OpenIdConfigDataAuditing { get; set; }

    [JsonPropertyName("mmcRemoteClientDataAuditing")]
    public object? MmcRemoteClientDataAuditing { get; set; }

    [JsonPropertyName("computerPolicyDataAuditing")]
    public object? ComputerPolicyDataAuditing { get; set; }

    [JsonPropertyName("azureADIntegrationDataAuditing")]
    public object? AzureADIntegrationDataAuditing { get; set; }

    [JsonPropertyName("authorizationRequestDataAuditing")]
    public object? AuthorizationRequestDataAuditing { get; set; }

    [JsonPropertyName("reputationSettingsDataAuditing")]
    public object? ReputationSettingsDataAuditing { get; set; }

    [JsonPropertyName("securitySettingsDataAuditing")]
    public object? SecuritySettingsDataAuditing { get; set; }

    [JsonPropertyName("siemIntegrationBaseDetailModel")]
    public object? SiemIntegrationBaseDetailModel { get; set; }

    [JsonPropertyName("siemIntegrationQradarAuditing")]
    public object? SiemIntegrationQradarAuditing { get; set; }

    [JsonPropertyName("siemIntegrationS3Auditing")]
    public object? SiemIntegrationS3Auditing { get; set; }

    [JsonPropertyName("siemIntegrationSentinelAuditing")]
    public object? SiemIntegrationSentinelAuditing { get; set; }

    [JsonPropertyName("siemIntegrationSplunkAuditing")]
    public object? SiemIntegrationSplunkAuditing { get; set; }

    [JsonPropertyName("agentDataAuditing")]
    public object? AgentDataAuditing { get; set; }

    [JsonPropertyName("managementRuleDataAuditing")]
    public object? ManagementRuleDataAuditing { get; set; }

    [JsonPropertyName("autoUpdateRateLimitDataAuditing")]
    public object? AutoUpdateRateLimitDataAuditing { get; set; }

    [JsonPropertyName("autoUpdateGroupConfigSettingsDataAuditing")]
    public object? AutoUpdateGroupConfigSettingsDataAuditing { get; set; }

    [JsonPropertyName("autoUpdateGroupClientSettingsDataAuditing")]
    public object? AutoUpdateGroupClientSettingsDataAuditing { get; set; }

    [JsonPropertyName("permissionGroupDataAuditing")]
    public object? PermissionGroupDataAuditing { get; set; }

    [JsonPropertyName("autoUpdateGroupMacClientSettingsDataAuditing")]
    public object? AutoUpdateGroupMacClientSettingsDataAuditing { get; set; }

    [JsonPropertyName("identityProviderGroupDataAuditing")]
    public object? IdentityProviderGroupDataAuditing { get; set; }
}

// Client Events Models
public class ClientEventsResponse
{
    [JsonPropertyName("totalRecordsReturned")]
    public int TotalRecordsReturned { get; set; }

    [JsonPropertyName("events")]
    public List<ClientEvent> Events { get; set; } = new();
}

public class ClientEvent
{
    [JsonPropertyName("agent")]
    public Agent Agent { get; set; } = new();

    [JsonPropertyName("@timestamp")]
    public DateTime Timestamp { get; set; }

    [JsonPropertyName("tags")]
    public List<string> Tags { get; set; } = new();

    [JsonPropertyName("ecs")]
    public Ecs Ecs { get; set; } = new();

    [JsonPropertyName("event")]
    public EventDetails Event { get; set; } = new();

    [JsonPropertyName("file")]
    public FileDetails? File { get; set; }

    [JsonPropertyName("host")]
    public HostDetails Host { get; set; } = new();

    [JsonPropertyName("related")]
    public RelatedDetails Related { get; set; } = new();

    [JsonPropertyName("user")]
    public UserDetails User { get; set; } = new();

    [JsonPropertyName("EPMWinMac")]
    public EPMWinMacDetails EPMWinMac { get; set; } = new();

    // Additional properties that might be present
    [JsonPropertyName("process")]
    public object? Process { get; set; }

    [JsonPropertyName("network")]
    public object? Network { get; set; }

    [JsonPropertyName("destination")]
    public object? Destination { get; set; }

    [JsonPropertyName("source")]
    public object? Source { get; set; }
}

public class Agent
{
    [JsonPropertyName("version")]
    public string Version { get; set; } = string.Empty;

    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("ephemeral_id")]
    public string EphemeralId { get; set; } = string.Empty;
}

public class Ecs
{
    [JsonPropertyName("version")]
    public string Version { get; set; } = string.Empty;
}

public class EventDetails
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("code")]
    public string Code { get; set; } = string.Empty;

    [JsonPropertyName("kind")]
    public string Kind { get; set; } = string.Empty;

    [JsonPropertyName("category")]
    public List<string> Category { get; set; } = new();

    [JsonPropertyName("action")]
    public string Action { get; set; } = string.Empty;

    [JsonPropertyName("outcome")]
    public string Outcome { get; set; } = string.Empty;

    [JsonPropertyName("type")]
    public List<string> Type { get; set; } = new();

    [JsonPropertyName("provider")]
    public string Provider { get; set; } = string.Empty;

    [JsonPropertyName("ingested")]
    public DateTime Ingested { get; set; }

    [JsonPropertyName("reason")]
    public string Reason { get; set; } = string.Empty;

    [JsonPropertyName("ReceivedAt")]
    public DateTime ReceivedAt { get; set; }
}

public class OwnerDetails
{
    [JsonPropertyName("Identifier")]
    public string Identifier { get; set; } = string.Empty;

    [JsonPropertyName("Name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("DomainIdentifier")]
    public string DomainIdentifier { get; set; } = string.Empty;

    [JsonPropertyName("DomainName")]
    public string DomainName { get; set; } = string.Empty;

    [JsonPropertyName("DomainNetBIOSName")]
    public string DomainNetBIOSName { get; set; } = string.Empty;
}

public class FileDetails
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("attributes")]
    public List<string> Attributes { get; set; } = new();

    [JsonPropertyName("directory")]
    public string Directory { get; set; } = string.Empty;

    [JsonPropertyName("drive_letter")]
    public string DriveLetter { get; set; } = string.Empty;

    [JsonPropertyName("path")]
    public string Path { get; set; } = string.Empty;

    [JsonPropertyName("extension")]
    public string Extension { get; set; } = string.Empty;

    [JsonPropertyName("uid")]
    public string Uid { get; set; } = string.Empty;

    // Owner is sent by the API as capital "Owner" and can be either a string or an object
    [JsonPropertyName("Owner")]
    public System.Text.Json.JsonElement? Owner { get; set; }
    
    // Helper property to get owner as structured details
    [JsonIgnore]
    public OwnerDetails? OwnerAsDetails
    {
        get
        {
            if (Owner.HasValue && Owner.Value.ValueKind == System.Text.Json.JsonValueKind.Object)
            {
                return System.Text.Json.JsonSerializer.Deserialize<OwnerDetails>(Owner.Value.GetRawText());
            }
            return null;
        }
    }
    
    // Helper property to get owner as string (either from object.Name or direct string value)
    [JsonIgnore]
    public string? OwnerAsString
    {
        get
        {
            if (!Owner.HasValue) return null;
            
            if (Owner.Value.ValueKind == System.Text.Json.JsonValueKind.Object)
            {
                return OwnerAsDetails?.Name;
            }
            else if (Owner.Value.ValueKind == System.Text.Json.JsonValueKind.String)
            {
                return Owner.Value.GetString();
            }
            return null;
        }
    }

    [JsonPropertyName("created")]
    public DateTime? Created { get; set; }

    [JsonPropertyName("DriveType")]
    public string DriveType { get; set; } = string.Empty;

    [JsonPropertyName("ProductVersion")]
    public string ProductVersion { get; set; } = string.Empty;

    [JsonPropertyName("hash")]
    public FileHash Hash { get; set; } = new();
}

public class FileHash
{
    [JsonPropertyName("md5")]
    public string Md5 { get; set; } = string.Empty;

    [JsonPropertyName("sha1")]
    public string Sha1 { get; set; } = string.Empty;

    [JsonPropertyName("sha256")]
    public string Sha256 { get; set; } = string.Empty;
}

public class HostDetails
{
    [JsonPropertyName("hostname")]
    public string Hostname { get; set; } = string.Empty;

    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("ip")]
    public List<string> Ip { get; set; } = new();

    [JsonPropertyName("uptime")]
    public long Uptime { get; set; }

    [JsonPropertyName("architecture")]
    public string Architecture { get; set; } = string.Empty;

    [JsonPropertyName("domain")]
    public string Domain { get; set; } = string.Empty;

    [JsonPropertyName("DomainIdentifier")]
    public string DomainIdentifier { get; set; } = string.Empty;

    [JsonPropertyName("NetBIOSName")]
    public string NetBIOSName { get; set; } = string.Empty;

    [JsonPropertyName("DomainNetBIOSName")]
    public string DomainNetBIOSName { get; set; } = string.Empty;

    [JsonPropertyName("ChassisType")]
    public string ChassisType { get; set; } = string.Empty;

    [JsonPropertyName("os")]
    public OsDetails Os { get; set; } = new();
}

public class OsDetails
{
    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;

    [JsonPropertyName("platform")]
    public string Platform { get; set; } = string.Empty;

    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("full")]
    public string Full { get; set; } = string.Empty;

    [JsonPropertyName("family")]
    public string Family { get; set; } = string.Empty;

    [JsonPropertyName("version")]
    public string Version { get; set; } = string.Empty;

    [JsonPropertyName("ProductType")]
    public string ProductType { get; set; } = string.Empty;
}

public class RelatedDetails
{
    [JsonPropertyName("ip")]
    public List<string> Ip { get; set; } = new();

    [JsonPropertyName("user")]
    public List<string> User { get; set; } = new();

    [JsonPropertyName("hosts")]
    public List<string> Hosts { get; set; } = new();
}

public class UserDetails
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("domain")]
    public string Domain { get; set; } = string.Empty;

    [JsonPropertyName("DomainIdentifier")]
    public string DomainIdentifier { get; set; } = string.Empty;

    [JsonPropertyName("DomainNetBIOSName")]
    public string DomainNetBIOSName { get; set; } = string.Empty;
}

public class EPMWinMacDetails
{
    [JsonPropertyName("SchemaVersion")]
    public string SchemaVersion { get; set; } = string.Empty;

    [JsonPropertyName("GroupId")]
    public string GroupId { get; set; } = string.Empty;

    [JsonPropertyName("TenantId")]
    public string TenantId { get; set; } = string.Empty;

    [JsonPropertyName("Event")]
    public EPMEvent Event { get; set; } = new();

    [JsonPropertyName("Configuration")]
    public EPMConfiguration Configuration { get; set; } = new();
}

public class EPMEvent
{
    [JsonPropertyName("Action")]
    public string Action { get; set; } = string.Empty;

    [JsonPropertyName("Type")]
    public string Type { get; set; } = string.Empty;
}

public class EPMConfiguration
{
    [JsonPropertyName("Identifier")]
    public string Identifier { get; set; } = string.Empty;
}
