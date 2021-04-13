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

            if (TemplatesSchemaValidationsReader.WhiteListConnectorIdsTestsTemplateIds.Contains(id) || !res.ContainsKey("requiredDataConnectors"))
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

        [Theory]
        [ClassData(typeof(DetectionsYamlFilesTestData))]
        public void Validate_DetectionTemplates_TemplatesThatAreInTheWhiteListShouldNotPassTheValidation(string detectionsYamlFileName)
        {
            var yaml = GetYamlFileAsString(detectionsYamlFileName);

            //we ignore known issues (in progress)
            foreach (var templateToSkip in TemplatesSchemaValidationsReader.WhiteListStructureTestsTemplateIds)
            {
                Exception exception = null;
                if (yaml.Contains(templateToSkip))
                {//This file is in the white list
                    try{
                        var jObj = JObject.Parse(ConvertYamlToJson(yaml));

                        exception = Record.Exception(() =>
                        {
                            var templateObject = jObj.ToObject<ScheduledTemplateInternalModel>();
                            var validationContext = new ValidationContext(templateObject);
                            Validator.ValidateObject(templateObject, validationContext, true);
                        });
                        
                    }
                    catch (Exception)
                    {
                        //We expect a failure, since this query is in the white list.
                    }
                    exception.Should().NotBeNull("Template that is in the white list should not pass the validations. If it passes, please remove it from the whitelist.");
                }
                else
                {
                    return;
                }
            }
        }
        
        [Fact]
        public void Validate_DetectionTemplates_AllFilesAreYamls()
        {
            string detectionPath = DetectionsYamlFilesTestData.GetDetectionPath();
            var yamlFiles = Directory.GetFiles(detectionPath, "*.yaml", SearchOption.AllDirectories).ToList();
            var AllFiles = Directory.GetFiles(detectionPath,"*", SearchOption.AllDirectories).ToList();
            var numberOfNotYamlFiles = 1; //This is the readme.md file in the directory
            Assert.True(AllFiles.Count == yamlFiles.Count + numberOfNotYamlFiles,  "All the files in detections folder are supposed to end with .yaml");
        }
        
        [Fact]
        public void Validate_DetectionTemplates_NoSameTemplateIdTwice()
        {
            string detectionPath = DetectionsYamlFilesTestData.GetDetectionPath();
            var yamlFiles = Directory.GetFiles(detectionPath, "*.yaml", SearchOption.AllDirectories);
            var templatesAsStrings = yamlFiles.Select(yaml => GetYamlFileAsString(Path.GetFileName(yaml)));

            var templatesAsObjects = templatesAsStrings.Select(yaml => JObject.Parse(ConvertYamlToJson(yaml)));
            var duplicationsById = templatesAsObjects.GroupBy(a => a["id"]).Where(group => group.Count() > 1); //Finds duplications -> ids that there are more than 1 template from
            var duplicatedId = "";
            if (duplicationsById.Count() > 0){
                
                duplicatedId = duplicationsById.Last().Select(x => x["id"]).First().ToString();
            }
            Assert.True(duplicationsById.Count() == 0, $"There should not be 2 templates with the same ID, but the id {duplicatedId} is duplicated.");
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
