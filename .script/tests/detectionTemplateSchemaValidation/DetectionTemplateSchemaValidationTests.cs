using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.IO;
using System;
using System.Linq;
using FluentAssertions;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Xunit;
using YamlDotNet.Serialization;

namespace Kqlvalidations.Tests
{
    public class DetectionTemplateSchemaValidationTests
    {
        private static readonly string DetectionPath = DetectionsYamlFilesTestData.GetDetectionPath();

        [Theory]
        [ClassData(typeof(DetectionsYamlFilesTestData))]
        public void Validate_DetectionTemplates_HasValidTemplateStructure(string detectionsYamlFileName)
        {
            var yaml = GetYamlFileAsString(detectionsYamlFileName);

            //we ignore known issues (in progress)
            foreach (var templateToSkip in TemplatesSchemaValidationsReader.WhiteListStructureTestsTemplateIds)
            {
                if (yaml.Contains(templateToSkip))
                {
                    return;
                }
            }

            var jObj = JObject.Parse(ConvertYamlToJson(yaml));

            var exception = Record.Exception(() =>
            {
                var templateObject = jObj.ToObject<ScheduledTemplateInternalModel>();
                var validationContext = new ValidationContext(templateObject);
                Validator.ValidateObject(templateObject, validationContext, true);
            });

            exception.Should().BeNull();
        }

        [Theory]
        [ClassData(typeof(DetectionsYamlFilesTestData))]
        public void Validate_DetectionTemplates_HasValidConnectorIds(string detectionsYamlFileName)
        {
            var yaml = GetYamlFileAsString(detectionsYamlFileName);
            var deserializer = new DeserializerBuilder().Build();
            Dictionary<object, object> res = deserializer.Deserialize<dynamic>(yaml);
            string id = (string)res["id"];

            if (TemplatesSchemaValidationsReader.ValidConnectorIds.Contains(id) /*|| !res.ContainsKey("requiredDataConnectors")*/)
            {
                return;
            }

            List<dynamic> requiredDataConnectors = (List<dynamic>)res["requiredDataConnectors"];
            List<string> connectorIds = requiredDataConnectors
                .Select(requiredDataConnectors => (string)requiredDataConnectors["connectorId"])
                .ToList();

            var intersection =  TemplatesSchemaValidationsReader.ValidConnectorIds.Intersect(connectorIds);
            connectorIds.RemoveAll(connectorId => intersection.Contains(connectorId));
            var isValid = connectorIds.Count() == 0;
            Assert.True(isValid, isValid ? string.Empty : $"Template Id:'{id}' doesn't have valid connectorIds:'{string.Join(",", connectorIds)}'. If a new connector is used and already configured in the Portal, please add it's Id to the list in 'ValidConnectorIds.json' file.");
        }

        private string GetYamlFileAsString(string detectionsYamlFileName)
        {
            var detectionsYamlFile = Directory.GetFiles(DetectionPath, detectionsYamlFileName, SearchOption.AllDirectories).Single();
            return File.ReadAllText(detectionsYamlFile);
        }

        public static string ConvertYamlToJson(string yaml)
        {
            var deserializer = new Deserializer();
            var yamlObject = deserializer.Deserialize<object>(yaml);

            using (var jsonObject = new StringWriter())
            {
                var serializer = new JsonSerializer();
                serializer.Serialize(jsonObject, yamlObject);
                return jsonObject.ToString();
            }
        }
    }
}
