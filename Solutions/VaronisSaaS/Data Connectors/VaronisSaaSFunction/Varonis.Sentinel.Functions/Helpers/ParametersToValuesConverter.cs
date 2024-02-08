using System.Collections.Generic;
using System.Linq;

namespace Varonis.Sentinel.Functions.Helpers
{
    public static class ParametersToValuesConverter
    {
        public static List<dynamic> CreateMappedFilterValuesList(IEnumerable<string> values, IDictionary<string, int> valuesMapping)
        {
            var filterValues = values.Select(value =>
                new
                {
                    Value = valuesMapping[value].ToString(),
                    DisplayValue = value
                } as dynamic).ToList();

            return filterValues;
        }

        public static List<dynamic> CreateValuesListFromList<T>(IEnumerable<T> values)
        {
            var filterValues = values.Select(value =>
                new
                {
                    Value = value.ToString()
                } as dynamic).ToList();

            return filterValues;
        }

        public static List<dynamic> CreateValuesListFromParameter<T>(T value)
        {
            var filterValues = new List<dynamic>
            {
                new
                {
                    Value = value.ToString(),
                }
            };

            return filterValues;
        }
    }
}
