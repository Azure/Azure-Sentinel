using System.Collections.Generic;
using System.Threading.Tasks;
using Varonis.Sentinel.Functions.Search.Model;

namespace Varonis.Sentinel.Functions.DatAlert
{
    internal interface IDatAlertClient
    {
        Task<IReadOnlyCollection<AlertItem>> GetDataAsync(DatAlertParams parameters);
    }
}