using Microsoft.Azure.Sentinel.KustoServices.Contract;
using Microsoft.Azure.Sentinel.KustoServices.Implementation;
using Newtonsoft.Json;
using System.Collections.Generic;

namespace Kqlvalidations.Tests.FunctionSchemasLoaders
{
    /// <summary>
    /// Manage the supported parameter types
    /// </summary>
    public static class TypesDatabase
    {
        /// <summary>
        /// Mapping between the type and its default value
        /// </summary>
        public static IReadOnlyDictionary<string, string> TypeToDefaultValueMapping = new Dictionary<string, string>()
        {
            { "string", "" },
            { "int", "0" },
            { "dynamic", "dynamic([])" },
            { "table:(TimeGenerated:datetime)", "range TimeGenerated from ago(3d) to now() step 1d" },
            { "table:(*)", "datatable() []" },
        };
    }
}
