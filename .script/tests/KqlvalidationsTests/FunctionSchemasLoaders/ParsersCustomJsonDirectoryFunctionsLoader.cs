using Microsoft.Azure.Sentinel.KustoServices.Contract;
using Microsoft.Azure.Sentinel.KustoServices.Implementation;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using YamlDotNet.Serialization;

namespace Kqlvalidations.Tests.FunctionSchemasLoaders
{
    public class ParsersCustomJsonDirectoryFunctionsLoader : CustomJsonDirectoryObjectsLoader<FunctionSchema>, IFunctionSchemaLoader
    {
        public ParsersCustomJsonDirectoryFunctionsLoader(string directoryPath) : base(directoryPath)
        {
        }

        public override IEnumerable<FunctionSchema> Load()
        {
            var sampleFunctions = base.Load();
            Dictionary<string, List<Column>> schemaToResultColumnsMapping = GetSchemaToResultColumnsMapping(sampleFunctions);
            var parsersFunctions = GetFunctions(schemaToResultColumnsMapping);
            var defaultFunctions = (new SentinelDefaultFunctionsLoader()).Load().Select(function => function.FunctionName);
            parsersFunctions = parsersFunctions.Where(function => !defaultFunctions.Contains(function.FunctionName));
            return parsersFunctions;
        }

        /// <summary>
        /// Currently there are 3 parser schemas: DNS, network sessions and web sessions.
        /// Parser functions with the same schema, should have the same result columns.
        /// CustomFunctions directory contains a sample function for each schema.
        /// This function extracts the result columns from the sample function and creates a mapping between the schema and the functions result columns.
        /// </summary>
        /// <param name="sampleFunctions">The sample functions</param>
        /// <returns>Mapping between the schema and the functions result columns</returns>
        private Dictionary<string, List<Column>> GetSchemaToResultColumnsMapping(IEnumerable<FunctionSchema> sampleFunctions)
        {
            Dictionary<string, string> sampleFunctionToSchemaMapping = ParsersDatabase.Parsers.ToDictionary(keySelector: parser => parser.SampleFunctionName, elementSelector: parser => parser.Schema);
            var sampleSchemaFunctions = sampleFunctions.Where(function => sampleFunctionToSchemaMapping.ContainsKey(function.FunctionName));
            return sampleSchemaFunctions.ToDictionary(keySelector: sampleFunction => sampleFunctionToSchemaMapping[sampleFunction.FunctionName], elementSelector: sampleFunction => sampleFunction.FunctionResultColumns);
        }

        /// <summary>
        /// Generates the FunctionSchema for each parser.
        /// </summary>
        /// <param name="schemaToResultColumnsMapping">Mapping between schema and its result columns</param>
        /// <returns>FunctionSchema foreach parser</returns>
        private IEnumerable<FunctionSchema> GetFunctions(Dictionary<string, List<Column>> schemaToResultColumnsMapping)
        {
            var parsersYamlFilesLoader = new ParsersYamlFilesLoader();
            var parsersYamlFiles = parsersYamlFilesLoader.GetFilesNames(true);

            return parsersYamlFiles.Select(fileName =>
            {
                var schema = fileName.Split(Path.DirectorySeparatorChar)[^3];
                var resultColumns = schemaToResultColumnsMapping[schema];
                return GetParserFunctionSchema(fileName, resultColumns);
            });
        }

        /// <summary>
        /// Extracts the parser name and parameters from the yaml file and creates the FunctionSchema.
        /// </summary>
        /// <param name="fileName">The parser's yaml file</param>
        /// <param name="resultColumns">The parser's result columns (taken from the sample data)</param>
        /// <returns>The parser's function schema</returns>
        private FunctionSchema GetParserFunctionSchema(string fileName, List<Column> resultColumns)
        {
            var deserializer = new DeserializerBuilder().Build();
            var yaml = deserializer.Deserialize<dynamic>(File.ReadAllText(fileName));
            return new FunctionSchema()
            {
                FunctionName = yaml["ParserName"],
                FunctionParameters = GetFunctionParameters(yaml),
                FunctionResultColumns = resultColumns,
            };
        }

        /// <summary>
        /// Extract fuction parameters from parser's ymal file
        /// </summary>
        /// <param name="yaml">The parser's yaml file</param>
        /// <returns>The parser's function parameters</returns>
        private List<FunctionParameter> GetFunctionParameters(dynamic yaml)
        {
            var functionParameters = new List<FunctionParameter>();
            if (yaml.TryGetValue("ParserParams", out object functionParamsObject))
            {
                var parserParams = (List<object>)functionParamsObject;
                functionParameters = parserParams.Select(ConvertObjectToFunctionParameter).ToList();
            }

            return functionParameters;
        }

        /// <summary>
        /// Convert object to function parameter
        /// </summary>
        /// <param name="parameter">The function parameter as an object</param>
        /// <returns>The function parameter</returns>
        private FunctionParameter ConvertObjectToFunctionParameter(object parameter)
        {
            var dictionary = (Dictionary<object, object>)parameter;
            return new FunctionParameter()
            {
                Name = (string)dictionary["Name"],
                Type = (string)dictionary["Type"],
                IsRequired = false,
            };
        }
    }
}
