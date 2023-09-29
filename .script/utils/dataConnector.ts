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
  logo?: string ;
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

export enum TenantPermissions {
  GlobalAdmin = "GlobalAdmin",
  SecurityAdmin = "SecurityAdmin",
  SecurityReader = "SecurityReader",
  InformationProtection = "InformationProtection",
}

export enum RequiredLicense {
  OfficeATP = "OfficeATP",
  Office365 = "Office365",
  AadP1P2 = "AadP1P2",
  Mcas = "Mcas",
  Aatp = "Aatp",
  Asc = "Asc",
  Mdatp = "Mdatp",
  Mtp = "Mtp",
  IoT = "IoT",
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

export enum ConnectorAvailabilityStatus {
  Available = 1,
  FeatureFlag,
  ComingSoon,
  Internal,
}

export enum ExplicitFeatureState {
  PrivatePreview,
  Disabled,
}

export enum ExtensionEnvironment {
  Local = 1,
  Dogfood,
  MPAC,
  Prod,
  Fairfax,
  USSec,
  USNat,
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
  feature: string /* The string to be used in the URL in order to control the flag */;
  defaultValue?: boolean /* Default: false */;
  featureStateOverrides?: FeatureStateOverride[];
}

export enum ConnectivityCriteriaType {
  IsConnectedQuery = "IsConnectedQuery",
  OmsSolutions = "OmsSolutions",
  SentinelKinds = "SentinelKinds",
  AzureActiveDirectory = "AzureActiveDirectory",
  SecurityEvents = "SecurityEvents",
  AzureGraph = "AzureGraph",
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

export enum InstructionType {
  SentinelResourceProvider = "SentinelResourceProvider",
  ThreatIntelligenceTaxii = "ThreatIntelligenceTaxii",
  CopyableLabel = "CopyableLabel",
  OmsSolution = "OmsSolutions",
  InstallAgent = "InstallAgent",
  InstructionStepsGroup = "InstructionStepsGroup",
  InfoMessage = "InfoMessage",

  // Internal
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
  OAuth = "OAuth",
}

export abstract class ConnectorInstructionModelBase<T extends {}> {
  public abstract type: InstructionType;

  public parameters?: T;

  constructor(parameters: T) {
      this.parameters = parameters;
  }
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

export enum ConnectorCategory {
  CEF="CEF",
  SysLog="Syslog",
  Event="Event",
  RestAPI="REST_API",
  AzureFunction="Azure_Function",
  AzureDiagnostics="AzureDiagnostics",
  AzureDevOpsAuditing="AzureDevOpsAuditing",
  ThreatIntelligenceIndicator="ThreatIntelligenceIndicator",
  MicrosoftPurviewInformationProtection="MicrosoftPurviewInformationProtection",
  Dynamics365Activity="Dynamics365Activity",
  CrowdstrikeReplicatorV2="CrowdstrikeReplicatorV2",
  BloodHoundEnterprise="BloodHoundEnterprise",
  AwsS3="AwsS3",
  AWS="AWS"
}