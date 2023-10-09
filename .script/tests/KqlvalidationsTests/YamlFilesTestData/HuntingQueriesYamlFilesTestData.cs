using System;
using System.Collections.Generic;
using System.Text;

namespace Kqlvalidations.Tests
{
    public class HuntingQueriesYamlFilesTestData : YamlFilesTestData
    {
        public HuntingQueriesYamlFilesTestData() : base(new HuntingQueriesYamlFilesLoader())
        {
        }
    }
}
