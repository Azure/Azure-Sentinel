export interface DataConnectorModel {
    id: string;
    title: string;
    publisher: string;
    descriptionMarkdown: string;
    graphQueries: GraphQuery[];
    sampleQueries: SampleQuery[];
    dataTypes: DataType[];
    availability: ConnectorAvailability;
    instructionSteps: InstructionStep[];
    permissions: RequiredConnectorPermissions;
    isConnectivityCriteriasMatchSome?: boolean;
    connectivityCriterias: ConnectivityCriteriaModel<any>[];
    additionalRequirementBanner?: string;
    logo?: string;
}
export interface GraphQuery {
    metricName: string;
    legend: string;
    baseQuery: string;
}
export interface SampleQuery {
    description?: string;
    query: string;
}
export interface DataType {
    name: string;
    lastDataReceivedQuery: string;
}
export declare enum TenantPermissions {
    GlobalAdmin = "GlobalAdmin",
    SecurityAdmin = "SecurityAdmin",
    SecurityReader = "SecurityReader",
    InformationProtection = "InformationProtection"
}
export declare enum RequiredLicense {
    OfficeATP = "OfficeATP",
    Office365 = "Office365",
    AadP1P2 = "AadP1P2",
    Mcas = "Mcas",
    Aatp = "Aatp",
    Asc = "Asc",
    Mdatp = "Mdatp",
    Mtp = "Mtp",
    IoT = "IoT"
}
export interface CustomPreCondition {
    name: string;
    description: string;
}
export interface RequiredPermissionSet {
    read?: boolean;
    write?: boolean;
    delete?: boolean;
    action?: boolean;
}
export interface ResourceProviderPermissions {
    provider: string;
    providerDisplayName: string;
    permissionsDisplayText: string;
    requiredPermissions: RequiredPermissionSet;
    scope: string;
}
export interface RequiredConnectorPermissions {
    tenant?: TenantPermissions[];
    licenses?: RequiredLicense[];
    customs?: CustomPreCondition[];
    resourceProvider?: ResourceProviderPermissions[];
}
export declare enum ConnectorAvailabilityStatus {
    Available = 1,
    FeatureFlag = 2,
    ComingSoon = 3,
    Internal = 4
}
export declare enum ExplicitFeatureState {
    PrivatePreview = 0,
    Disabled = 1
}
export declare enum ExtensionEnvironment {
    Local = 1,
    Dogfood = 2,
    MPAC = 3,
    Prod = 4,
    Fairfax = 5,
    USSec = 6,
    USNat = 7
}
export interface FeatureStateOverride {
    cloudEnvironment: ExtensionEnvironment;
    explicitFeatureState: ExplicitFeatureState;
}
interface FeatureState {
    defaultValue?: boolean;
    featureStateOverrides?: FeatureStateOverride[];
}
export interface FeatureConfig extends FeatureState {
    feature: string;
    defaultValue?: boolean;
    featureStateOverrides?: FeatureStateOverride[];
}
export declare enum ConnectivityCriteriaType {
    IsConnectedQuery = "IsConnectedQuery",
    OmsSolutions = "OmsSolutions",
    SentinelKinds = "SentinelKinds",
    AzureActiveDirectory = "AzureActiveDirectory",
    SecurityEvents = "SecurityEvents",
    AzureGraph = "AzureGraph"
}
export interface ConnectivityCriteriaModel<T> {
    type: ConnectivityCriteriaType;
    value?: T;
}
export interface ConnectorAvailability {
    status: ConnectorAvailabilityStatus;
    isPreview?: boolean;
    featureFlag?: FeatureConfig;
    previewRegistrationLink?: string;
    isComingSoon?: boolean;
}
export declare enum InstructionType {
    SentinelResourceProvider = "SentinelResourceProvider",
    ThreatIntelligenceTaxii = "ThreatIntelligenceTaxii",
    CopyableLabel = "CopyableLabel",
    OmsSolution = "OmsSolutions",
    InstallAgent = "InstallAgent",
    InstructionStepsGroup = "InstructionStepsGroup",
    InfoMessage = "InfoMessage",
    Office365 = "Office365",
    OfficeATP = "OfficeATP",
    AzureSecurityCenterSubscriptions = "AzureSecurityCenterSubscriptions",
    AWS = "AWS",
    AzureActiveDirectory = "AzureActiveDirectory",
    SecurityEvents = "SecurityEvents",
    FilterAlert = "FilterAlert",
    MicrosoftDefenderATP = "MicrosoftDefenderATP",
    MicrosoftDefenderATPEvents = "MicrosoftDefenderATPEvents",
    MicrosoftThreatProtection = "MicrosoftThreatProtection",
    MicrosoftThreatIntelligence = "MicrosoftThreatIntelligence",
    IoT = "IoT",
    OfficeDataTypes = "OfficeDataTypes",
    MCasDataTypes = "MCasDataTypes",
    AADDataTypes = "AADDataTypes",
    OAuth = "OAuth"
}
export declare abstract class ConnectorInstructionModelBase<T extends {}> {
    abstract type: InstructionType;
    parameters?: T;
    constructor(parameters: T);
}
export interface InstructionStep {
    title?: string;
    description?: string;
    instructions?: ConnectorInstructionModelBase<any>[];
    innerSteps?: InstructionStep[];
    featureFlag?: FeatureConfig;
    bottomBorder?: boolean;
    isComingSoon?: boolean;
}
export declare enum ConnectorCategory {
    CEF = "CEF",
    SysLog = "Syslog",
    Event = "Event",
    RestAPI = "REST_API",
    AzureFunction = "Azure_Function",
    AzureDiagnostics = "AzureDiagnostics",
    AzureDevOpsAuditing = "AzureDevOpsAuditing",
    ThreatIntelligenceIndicator = "ThreatIntelligenceIndicator",
    MicrosoftPurviewInformationProtection = "MicrosoftPurviewInformationProtection",
    Dynamics365Activity = "Dynamics365Activity",
    CrowdstrikeReplicatorV2 = "CrowdstrikeReplicatorV2",
    BloodHoundEnterprise = "BloodHoundEnterprise",
    Corelight = "Corelight",
    CorelightConnectorExporter = "CorelightConnectorExporter",
    AwsS3 = "AwsS3",
    AWS = "AWS",
    AzureActiveDirectory = "AzureActiveDirectory",
    SecurityAlert = "SecurityAlert",
    AzureActivity = "AzureActivity",
    PowerBIActivity = "PowerBIActivity",
    SecurityAlertOATP = "SecurityAlert(OATP)",
    SecurityAlertASC = "SecurityAlert(ASC)",
    CybleThreatIntel = "CybleThreatIntel",
    CrowdStrikeFalconIOC = "CrowdStrikeFalconIOC",
    Wiz = "Wiz",
    VectraStreamAma = "VectraStreamAma"
}
export {};
//# sourceMappingURL=dataConnector.d.ts.map