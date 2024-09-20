using System;
using System.Collections.Generic;
using System.Text;

namespace Kqlvalidations.Tests
{
    public class DataConnectorFilesTestData : JsonFilesTestData
    {
        public DataConnectorFilesTestData() : base(new DataConnectorFilesLoader())
        {
        }
    }
}