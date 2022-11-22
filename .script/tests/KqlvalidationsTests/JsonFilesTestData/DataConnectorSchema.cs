using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Text;

namespace Kqlvalidations.Tests
{
    public partial class DataConnectorSchema
    {
        [JsonProperty("additionalRequirementBanner")]
        public string AdditionalRequirementBanner { get; set; }

        [JsonProperty("availability")]
        public Availability Availability { get; set; }

        [JsonProperty("connectivityCriterias")]
        public ConnectivityCriteria[] ConnectivityCriterias { get; set; }

        [JsonProperty("dataTypes")]
        public DataType[] DataTypes { get; set; }

        [JsonProperty("descriptionMarkdown")]
        public string DescriptionMarkdown { get; set; }

        [JsonProperty("graphQueries")]
        public GraphQuery[] GraphQueries { get; set; }

        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("instructionSteps")]
        public InstructionStep[] InstructionSteps { get; set; }

        [JsonProperty("permissions")]
        public Permissions Permissions { get; set; }

        [JsonProperty("publisher")]
        public string Publisher { get; set; }

        [JsonProperty("sampleQueries")]
        public SampleQuery[] SampleQueries { get; set; }

        [JsonProperty("title")]
        public string Title { get; set; }
    }

    public partial class Availability
    {
        [JsonProperty("isPreview")]
        public bool IsPreview { get; set; }

        [JsonProperty("status")]
        public long Status { get; set; }
    }

    public partial class ConnectivityCriteria
    {
        [JsonProperty("type")]
        public string Type { get; set; }

        [JsonProperty("value")]
        public string[] Value { get; set; }
    }

    public partial class DataType
    {
        [JsonProperty("lastDataReceivedQuery")]
        public string LastDataReceivedQuery { get; set; }

        [JsonProperty("name")]
        public string Name { get; set; }
    }

    public partial class GraphQuery
    {
        [JsonProperty("baseQuery")]
        public string BaseQuery { get; set; }

        [JsonProperty("legend")]
        public string Legend { get; set; }

        [JsonProperty("metricName")]
        public string MetricName { get; set; }
    }

    public partial class InstructionStep
    {
        [JsonProperty("description", NullValueHandling = NullValueHandling.Ignore)]
        public string Description { get; set; }

        [JsonProperty("instructions", NullValueHandling = NullValueHandling.Ignore)]
        public object[] Instructions { get; set; }

        [JsonProperty("title", NullValueHandling = NullValueHandling.Ignore)]
        public string Title { get; set; }
    }

    public partial class Permissions
    {
        [JsonProperty("customs", NullValueHandling = NullValueHandling.Ignore)]
        public Custom[] Customs { get; set; }

        [JsonProperty("resourceProvider")]
        public ResourceProvider[] ResourceProvider { get; set; }
    }

    public partial class Custom
    {
        [JsonProperty("description", NullValueHandling = NullValueHandling.Ignore)]
        public string Description { get; set; }

        [JsonProperty("name", NullValueHandling = NullValueHandling.Ignore)]
        public string Name { get; set; }
    }

    public partial class ResourceProvider
    {
        [JsonProperty("permissionsDisplayText", NullValueHandling = NullValueHandling.Ignore)]
        public string PermissionsDisplayText { get; set; }

        [JsonProperty("provider", NullValueHandling = NullValueHandling.Ignore)]
        public string Provider { get; set; }

        [JsonProperty("providerDisplayName", NullValueHandling = NullValueHandling.Ignore)]
        public string ProviderDisplayName { get; set; }

        [JsonProperty("requiredPermissions", NullValueHandling = NullValueHandling.Ignore)]
        public RequiredPermissions RequiredPermissions { get; set; }

        [JsonProperty("scope", NullValueHandling = NullValueHandling.Ignore)]
        public string Scope { get; set; }
    }

    public partial class RequiredPermissions
    {
        [JsonProperty("delete", NullValueHandling = NullValueHandling.Ignore)]
        public bool? Delete { get; set; }

        [JsonProperty("write", NullValueHandling = NullValueHandling.Ignore)]
        public bool? Write { get; set; }
    }

    public partial class SampleQuery
    {
        [JsonProperty("description")]
        public string Description { get; set; }

        [JsonProperty("query")]
        public string Query { get; set; }
    }
}
