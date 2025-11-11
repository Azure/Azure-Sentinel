using System.Collections.Generic;
using System.Linq;

namespace Varonis.Sentinel.Functions.Helpers
{
    internal abstract class BaseMapper<T>
    {
        public IReadOnlyCollection<T> MapRowsToObject(IEnumerable<IDictionary<string, string>> rowsData)
        {
            return rowsData.Select(Map).Where(ev => ev != null).ToArray();
        }

        protected abstract T Map(IDictionary<string, string> row);
    }
}
