using DetectionTemplateSchemaValidation.Tests;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Runtime.Serialization;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model
{
    [NoTechniquesWithoutMatchingTactics]
    [KnownType("DerivedTypes")]
    [JsonConverter(typeof(AnalyticsTemplateConverter))]
    public abstract class AnalyticsTemplateInternalModelBase
    {
        [JsonProperty("id", Required = Required.Always)]
        public Guid Id { get; set; }

        [JsonProperty("kind", Required = Required.Always)]
        public abstract AlertRuleKind Kind { get; }

        [JsonProperty("name", Required = Required.Always)]
        [StringLength(256)]
        public string DisplayName { get; set; }

        [JsonProperty("description", Required = Required.Always)]
        [StringLength(5000)]
        public string Description { get; set; }

        [JsonProperty("tactics")]
        public List<AttackTactic> Tactics { get; set; }

        [JsonProperty("relevantTechniques")]
        public List<string> RelevantTechniques { get; set; }

        [JsonProperty("requiredDataConnectors", NullValueHandling = NullValueHandling.Ignore)]
        public virtual List<DataConnectorInternalModel> RequiredDataConnectors { get; set; } = new List<DataConnectorInternalModel>();
    }
}