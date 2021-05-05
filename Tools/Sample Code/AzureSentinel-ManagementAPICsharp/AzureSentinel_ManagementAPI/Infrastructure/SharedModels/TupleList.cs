using System;
using System.Collections.Generic;
using System.Text;

namespace AzureSentinel_ManagementAPI.Infrastructure.SharedModels
{
    public class TupleList<T1, T2> : List<Tuple<T1, T2>>
    {
        public void Add(T1 item, T2 item2)
        {
            Add(new Tuple<T1, T2>(item, item2));
        }
    }
}
