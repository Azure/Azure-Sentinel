namespace Kqlvalidations.Tests
{
    public class YamlFileProp
    {
        public string FileName { get; set; }
        public string FullPath { get; set; }

        public override string ToString()
        {
            return FileName;
        }
    }
}