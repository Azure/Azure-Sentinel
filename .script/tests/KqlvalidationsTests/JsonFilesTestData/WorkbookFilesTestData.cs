using System;
using System.Collections.Generic;
using System.Text;

namespace Kqlvalidations.Tests
{
    public class WorkbookFilesTestData : JsonFilesTestData
    {
        public WorkbookFilesTestData() : base(new WorkbookFilesLoader())
        {
        }
    }
}
