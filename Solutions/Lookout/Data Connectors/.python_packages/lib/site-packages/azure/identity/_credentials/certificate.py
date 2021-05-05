# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from binascii import hexlify
from typing import TYPE_CHECKING

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import six

from .._internal import validate_tenant_id
from .._internal.client_credential_base import ClientCredentialBase

if TYPE_CHECKING:
    from typing import Any


class CertificateCredential(ClientCredentialBase):
    """Authenticates as a service principal using a certificate.

    :param str tenant_id: ID of the service principal's tenant. Also called its 'directory' ID.
    :param str client_id: the service principal's client ID
    :param str certificate_path: path to a PEM-encoded certificate file including the private key.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
          defines authorities for other clouds.
    :keyword password: The certificate's password. If a unicode string, it will be encoded as UTF-8. If the certificate
          requires a different encoding, pass appropriately encoded bytes instead.
    :paramtype password: str or bytes
    :keyword bool send_certificate_chain: if True, the credential will send the public certificate chain in the x5c
          header of each token request's JWT. This is required for Subject Name/Issuer (SNI) authentication. Defaults
          to False.
    """

    def __init__(self, tenant_id, client_id, certificate_path, **kwargs):
        # type: (str, str, str, **Any) -> None
        validate_tenant_id(tenant_id)
        if not certificate_path:
            raise ValueError(
                "'certificate_path' must be the path to a PEM file containing an x509 certificate and its private key"
            )

        password = kwargs.pop("password", None)
        if isinstance(password, six.text_type):
            password = password.encode(encoding="utf-8")

        with open(certificate_path, "rb") as f:
            pem_bytes = f.read()

        cert = x509.load_pem_x509_certificate(pem_bytes, default_backend())
        fingerprint = cert.fingerprint(hashes.SHA1())  # nosec

        client_credential = {"private_key": pem_bytes, "thumbprint": hexlify(fingerprint).decode("utf-8")}
        if password:
            client_credential["passphrase"] = password

        if kwargs.pop("send_certificate_chain", False):
            try:
                # the JWT needs the whole chain but load_pem_x509_certificate deserializes only the signing cert
                chain = extract_cert_chain(pem_bytes)
                client_credential["public_certificate"] = six.ensure_str(chain)
            except ValueError as ex:
                # we shouldn't land here, because load_pem_private_key should have raised when given a malformed file
                message = 'Found no PEM encoded certificate in "{}"'.format(certificate_path)
                six.raise_from(ValueError(message), ex)

        super(CertificateCredential, self).__init__(
            client_id=client_id, client_credential=client_credential, tenant_id=tenant_id, **kwargs
        )


def extract_cert_chain(pem_bytes):
    # type: (bytes) -> bytes
    """Extract a certificate chain from a PEM file's bytes, removing line breaks."""

    # if index raises ValueError, there's no PEM-encoded cert
    start = pem_bytes.index(b"-----BEGIN CERTIFICATE-----")
    footer = b"-----END CERTIFICATE-----"
    end = pem_bytes.rindex(footer)
    chain = pem_bytes[start:end + len(footer) + 1]

    return b"".join(chain.splitlines())
