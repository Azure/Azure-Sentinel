export var TenantPermissions;
(function (TenantPermissions) {
    TenantPermissions["GlobalAdmin"] = "GlobalAdmin";
    TenantPermissions["SecurityAdmin"] = "SecurityAdmin";
    TenantPermissions["SecurityReader"] = "SecurityReader";
    TenantPermissions["InformationProtection"] = "InformationProtection";
})(TenantPermissions || (TenantPermissions = {}));
export var RequiredLicense;
(function (RequiredLicense) {
    RequiredLicense["OfficeATP"] = "OfficeATP";
    RequiredLicense["Office365"] = "Office365";
    RequiredLicense["AadP1P2"] = "AadP1P2";
    RequiredLicense["Mcas"] = "Mcas";
    RequiredLicense["Aatp"] = "Aatp";
    RequiredLicense["Asc"] = "Asc";
    RequiredLicense["Mdatp"] = "Mdatp";
    RequiredLicense["Mtp"] = "Mtp";
    RequiredLicense["IoT"] = "IoT";
})(RequiredLicense || (RequiredLicense = {}));
export var ConnectorAvailabilityStatus;
(function (ConnectorAvailabilityStatus) {
    ConnectorAvailabilityStatus[ConnectorAvailabilityStatus["Available"] = 1] = "Available";
    ConnectorAvailabilityStatus[ConnectorAvailabilityStatus["FeatureFlag"] = 2] = "FeatureFlag";
    ConnectorAvailabilityStatus[ConnectorAvailabilityStatus["ComingSoon"] = 3] = "ComingSoon";
    ConnectorAvailabilityStatus[ConnectorAvailabilityStatus["Internal"] = 4] = "Internal";
})(ConnectorAvailabilityStatus || (ConnectorAvailabilityStatus = {}));
export var ExplicitFeatureState;
(function (ExplicitFeatureState) {
    ExplicitFeatureState[ExplicitFeatureState["PrivatePreview"] = 0] = "PrivatePreview";
    ExplicitFeatureState[ExplicitFeatureState["Disabled"] = 1] = "Disabled";
})(ExplicitFeatureState || (ExplicitFeatureState = {}));
export var ExtensionEnvironment;
(function (ExtensionEnvironment) {
    ExtensionEnvironment[ExtensionEnvironment["Local"] = 1] = "Local";
    ExtensionEnvironment[ExtensionEnvironment["Dogfood"] = 2] = "Dogfood";
    ExtensionEnvironment[ExtensionEnvironment["MPAC"] = 3] = "MPAC";
    ExtensionEnvironment[ExtensionEnvironment["Prod"] = 4] = "Prod";
    ExtensionEnvironment[ExtensionEnvironment["Fairfax"] = 5] = "Fairfax";
    ExtensionEnvironment[ExtensionEnvironment["USSec"] = 6] = "USSec";
    ExtensionEnvironment[ExtensionEnvironment["USNat"] = 7] = "USNat";
})(ExtensionEnvironment || (ExtensionEnvironment = {}));
export var ConnectivityCriteriaType;
(function (ConnectivityCriteriaType) {
    ConnectivityCriteriaType["IsConnectedQuery"] = "IsConnectedQuery";
    ConnectivityCriteriaType["OmsSolutions"] = "OmsSolutions";
    ConnectivityCriteriaType["SentinelKinds"] = "SentinelKinds";
    ConnectivityCriteriaType["AzureActiveDirectory"] = "AzureActiveDirectory";
    ConnectivityCriteriaType["SecurityEvents"] = "SecurityEvents";
    ConnectivityCriteriaType["AzureGraph"] = "AzureGraph";
})(ConnectivityCriteriaType || (ConnectivityCriteriaType = {}));
export var InstructionType;
(function (InstructionType) {
    InstructionType["SentinelResourceProvider"] = "SentinelResourceProvider";
    InstructionType["ThreatIntelligenceTaxii"] = "ThreatIntelligenceTaxii";
    InstructionType["CopyableLabel"] = "CopyableLabel";
    InstructionType["OmsSolution"] = "OmsSolutions";
    InstructionType["InstallAgent"] = "InstallAgent";
    InstructionType["InstructionStepsGroup"] = "InstructionStepsGroup";
    InstructionType["InfoMessage"] = "InfoMessage";
    // Internal
    InstructionType["Office365"] = "Office365";
    InstructionType["OfficeATP"] = "OfficeATP";
    InstructionType["AzureSecurityCenterSubscriptions"] = "AzureSecurityCenterSubscriptions";
    InstructionType["AWS"] = "AWS";
    InstructionType["AzureActiveDirectory"] = "AzureActiveDirectory";
    InstructionType["SecurityEvents"] = "SecurityEvents";
    InstructionType["FilterAlert"] = "FilterAlert";
    InstructionType["MicrosoftDefenderATP"] = "MicrosoftDefenderATP";
    InstructionType["MicrosoftDefenderATPEvents"] = "MicrosoftDefenderATPEvents";
    InstructionType["MicrosoftThreatProtection"] = "MicrosoftThreatProtection";
    InstructionType["MicrosoftThreatIntelligence"] = "MicrosoftThreatIntelligence";
    InstructionType["IoT"] = "IoT";
    InstructionType["OfficeDataTypes"] = "OfficeDataTypes";
    InstructionType["MCasDataTypes"] = "MCasDataTypes";
    InstructionType["AADDataTypes"] = "AADDataTypes";
    InstructionType["OAuth"] = "OAuth";
})(InstructionType || (InstructionType = {}));
export class ConnectorInstructionModelBase {
    constructor(parameters) {
        this.parameters = parameters;
    }
}
export var ConnectorCategory;
(function (ConnectorCategory) {
    ConnectorCategory["CEF"] = "CEF";
    ConnectorCategory["SysLog"] = "Syslog";
    ConnectorCategory["Event"] = "Event";
    ConnectorCategory["RestAPI"] = "REST_API";
    ConnectorCategory["AzureFunction"] = "Azure_Function";
    ConnectorCategory["AzureDiagnostics"] = "AzureDiagnostics";
    ConnectorCategory["AzureDevOpsAuditing"] = "AzureDevOpsAuditing";
    ConnectorCategory["ThreatIntelligenceIndicator"] = "ThreatIntelligenceIndicator";
    ConnectorCategory["MicrosoftPurviewInformationProtection"] = "MicrosoftPurviewInformationProtection";
    ConnectorCategory["Dynamics365Activity"] = "Dynamics365Activity";
    ConnectorCategory["CrowdstrikeReplicatorV2"] = "CrowdstrikeReplicatorV2";
    ConnectorCategory["BloodHoundEnterprise"] = "BloodHoundEnterprise";
    ConnectorCategory["Corelight"] = "Corelight";
    ConnectorCategory["CorelightConnectorExporter"] = "CorelightConnectorExporter";
    ConnectorCategory["AwsS3"] = "AwsS3";
    ConnectorCategory["AWS"] = "AWS";
    ConnectorCategory["AzureActiveDirectory"] = "AzureActiveDirectory";
    ConnectorCategory["SecurityAlert"] = "SecurityAlert";
    ConnectorCategory["AzureActivity"] = "AzureActivity";
    ConnectorCategory["PowerBIActivity"] = "PowerBIActivity";
    ConnectorCategory["SecurityAlertOATP"] = "SecurityAlert(OATP)";
    ConnectorCategory["SecurityAlertASC"] = "SecurityAlert(ASC)";
    ConnectorCategory["CybleThreatIntel"] = "CybleThreatIntel";
    ConnectorCategory["CrowdStrikeFalconIOC"] = "CrowdStrikeFalconIOC";
    ConnectorCategory["Wiz"] = "Wiz";
    ConnectorCategory["VectraStreamAma"] = "VectraStreamAma";
})(ConnectorCategory || (ConnectorCategory = {}));
//# sourceMappingURL=dataConnector.js.map