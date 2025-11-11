using System.Net.Security;
using System.Security.Cryptography.X509Certificates;

namespace Sentinel.Client
{
    internal class CertificateValidation
    {
        private readonly string _trustedThumbprint;

        public CertificateValidation(string trustedThumbPrint)
        {
            //if (string.IsNullOrEmpty(trustedThumbPrint))
            //    throw new ArgumentException($"'{nameof(trustedThumbPrint)}' cannot be null or empty.", nameof(trustedThumbPrint));
            _trustedThumbprint = trustedThumbPrint;
        }

        public bool Callback(object sender, X509Certificate certificate, X509Chain chain, SslPolicyErrors sslPolicyErrors)
        {
            return true;
            using var cert = new X509Certificate2(certificate);
            return string.Equals(cert.Thumbprint, _trustedThumbprint, StringComparison.OrdinalIgnoreCase);
        }
    }
}
