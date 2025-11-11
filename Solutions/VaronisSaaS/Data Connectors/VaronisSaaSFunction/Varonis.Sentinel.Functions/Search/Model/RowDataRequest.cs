using System.Collections.Generic;

namespace Varonis.Sentinel.Functions.Search.Model
{
    internal class RowDataRequest
    {
        public IReadOnlyCollection<string> Columns { get; set; }
        public IReadOnlyCollection<object> Ordering { get; set; }
    }
}
