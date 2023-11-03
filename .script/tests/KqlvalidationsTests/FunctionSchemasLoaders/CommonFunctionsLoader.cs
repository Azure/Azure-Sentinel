using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.Azure.Sentinel.KustoServices.Contract;
using YamlDotNet.Serialization;

namespace Kqlvalidations.Tests.FunctionSchemasLoaders
{
    public class CommonFunctionsLoader : IFunctionSchemaLoader
    {
        public IEnumerable<FunctionSchema> Load()
        {
            List<string> commonFunctionsYamlFiles = (new CommonFunctionsYamlFilesLoader()).GetFilesNames(true);
            return commonFunctionsYamlFiles.Select(GetFunction).ToList();
        }


        /// <summary>
        /// Extracts the fuction's name, parameters and result columns from the yaml file and creates the FunctionSchema.
        /// </summary>
        /// <param name="fileName">The parser's yaml file</param>
        /// <returns>The function schema</returns>
        private FunctionSchema GetFunction(string fileName)
        {
            var deserializer = new DeserializerBuilder().Build();
            var yaml = deserializer.Deserialize<Dictionary<string, object>>(File.ReadAllText(fileName));
            return new FunctionSchema((string)yaml["EquivalentBuiltInFunction"], (string)yaml["FunctionQuery"], GetFunctionParameters(yaml));
        }

        /// <summary>
        /// Extract fuction parameters from ymal file
        /// </summary>
        /// <param name="yaml">The yaml file</param>
        /// <returns>The function parameters</returns>
        private List<FunctionParameter> GetFunctionParameters(Dictionary<string, object> yaml)
        {
            List<object> functionParameters = (List<object>)yaml.GetValueOrDefault("FunctionParams");
            return functionParameters?.Select(ConvertObjectToFunctionParameter).ToList();
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
