namespace Sentinel.Helpers
{
    public static class BackupObjectHelper
    {
        public static string ExtractHostName(string path)
        {
            // extracts hostName from path
            // e.g. pdcqa51.qahv1.veeam.local from pdcqa51.qahv1.veeam.local\ga12dc_replica 

            if (string.IsNullOrEmpty(path))
                throw new ArgumentNullException("Unable to extract host name from path, because path is empty.");

            int idx = path.IndexOf(@"\");
            if (idx < 0)
                return path;

            return path.Substring(0, idx);
        }
    }
}
