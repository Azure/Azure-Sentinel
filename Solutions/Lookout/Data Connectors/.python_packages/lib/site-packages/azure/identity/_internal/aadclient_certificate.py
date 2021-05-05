# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
from typing import TYPE_CHECKING

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import six

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Optional


class AadClientCertificate(object):
    """Wraps 'cryptography' to provide the crypto operations AadClient requires for certificate authentication.

    :param bytes pem_bytes: bytes of a a PEM-encoded certificate including the private key
    :param bytes password: (optional) the certificate's password
    """
    def __init__(self, pem_bytes, password=None):
        # type: (bytes, Optional[bytes]) -> None
        cert = x509.load_pem_x509_certificate(pem_bytes, default_backend())
        fingerprint = cert.fingerprint(hashes.SHA1())  # nosec
        self._private_key = serialization.load_pem_private_key(pem_bytes, password=password, backend=default_backend())
        self._thumbprint = six.ensure_str(base64.urlsafe_b64encode(fingerprint), encoding="utf-8")

    @property
    def thumbprint(self):
        # type: () -> str
        """The certificate's SHA1 thumbprint as a base64url-encoded string"""
        return self._thumbprint

    def sign(self, plaintext):
        # type: (bytes) -> bytes
        """Sign bytes using RS256"""
        return self._private_key.sign(plaintext, padding.PKCS1v15(), hashes.SHA256())
