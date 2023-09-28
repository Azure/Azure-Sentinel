"""STIX 2.0 API Objects.

.. autosummary::
   :toctree: v20

   bundle
   common
   observables
   sdo
   sro

|
"""

# flake8: noqa

from .base import (
    _DomainObject, _Extension, _Observable, _RelationshipObject, _STIXBase20,
)
from .bundle import Bundle
from .common import (
    TLP_AMBER, TLP_GREEN, TLP_RED, TLP_WHITE, CustomMarking, ExternalReference,
    GranularMarking, KillChainPhase, MarkingDefinition, StatementMarking,
    TLPMarking,
)
from .observables import (
    URL, AlternateDataStream, ArchiveExt, Artifact, AutonomousSystem,
    CustomExtension, CustomObservable, Directory, DomainName, EmailAddress,
    EmailMessage, EmailMIMEComponent, File, HTTPRequestExt, ICMPExt,
    IPv4Address, IPv6Address, MACAddress, Mutex, NetworkTraffic, NTFSExt,
    PDFExt, Process, RasterImageExt, SocketExt, Software, TCPExt,
    UNIXAccountExt, UserAccount, WindowsPEBinaryExt,
    WindowsPEOptionalHeaderType, WindowsPESection, WindowsProcessExt,
    WindowsRegistryKey, WindowsRegistryValueType, WindowsServiceExt,
    X509Certificate, X509V3ExtensionsType,
)
from .sdo import (
    AttackPattern, Campaign, CourseOfAction, CustomObject, Identity, Indicator,
    IntrusionSet, Malware, ObservedData, Report, ThreatActor, Tool,
    Vulnerability,
)
from .sro import Relationship, Sighting

OBJ_MAP = {
    'attack-pattern': AttackPattern,
    'bundle': Bundle,
    'campaign': Campaign,
    'course-of-action': CourseOfAction,
    'identity': Identity,
    'indicator': Indicator,
    'intrusion-set': IntrusionSet,
    'malware': Malware,
    'marking-definition': MarkingDefinition,
    'observed-data': ObservedData,
    'report': Report,
    'relationship': Relationship,
    'threat-actor': ThreatActor,
    'tool': Tool,
    'sighting': Sighting,
    'vulnerability': Vulnerability,
}

OBJ_MAP_OBSERVABLE = {
    'artifact': Artifact,
    'autonomous-system': AutonomousSystem,
    'directory': Directory,
    'domain-name': DomainName,
    'email-addr': EmailAddress,
    'email-message': EmailMessage,
    'file': File,
    'ipv4-addr': IPv4Address,
    'ipv6-addr': IPv6Address,
    'mac-addr': MACAddress,
    'mutex': Mutex,
    'network-traffic': NetworkTraffic,
    'process': Process,
    'software': Software,
    'url': URL,
    'user-account': UserAccount,
    'windows-registry-key': WindowsRegistryKey,
    'x509-certificate': X509Certificate,
}

EXT_MAP = {
    'archive-ext': ArchiveExt,
    'ntfs-ext': NTFSExt,
    'pdf-ext': PDFExt,
    'raster-image-ext': RasterImageExt,
    'windows-pebinary-ext': WindowsPEBinaryExt,
    'http-request-ext': HTTPRequestExt,
    'icmp-ext': ICMPExt,
    'socket-ext': SocketExt,
    'tcp-ext': TCPExt,
    'windows-process-ext': WindowsProcessExt,
    'windows-service-ext': WindowsServiceExt,
    'unix-account-ext': UNIXAccountExt,
}


# Ensure star-imports from this module get the right symbols.  "base" is a
# known problem, since there are multiple modules with that name and one can
# accidentally overwrite another.
__all__ = """
    Bundle,

    TLP_AMBER, TLP_GREEN, TLP_RED, TLP_WHITE, CustomMarking, ExternalReference,
    GranularMarking, KillChainPhase, MarkingDefinition, StatementMarking,
    TLPMarking,

    URL, AlternateDataStream, ArchiveExt, Artifact, AutonomousSystem,
    CustomExtension, CustomObservable, Directory, DomainName, EmailAddress,
    EmailMessage, EmailMIMEComponent, File, HTTPRequestExt, ICMPExt,
    IPv4Address, IPv6Address, MACAddress, Mutex, NetworkTraffic, NTFSExt,
    PDFExt, Process, RasterImageExt, SocketExt, Software, TCPExt,
    UNIXAccountExt, UserAccount, WindowsPEBinaryExt,
    WindowsPEOptionalHeaderType, WindowsPESection, WindowsProcessExt,
    WindowsRegistryKey, WindowsRegistryValueType, WindowsServiceExt,
    X509Certificate, X509V3ExtensionsType,

    AttackPattern, Campaign, CourseOfAction, CustomObject, Identity, Indicator,
    IntrusionSet, Malware, ObservedData, Report, ThreatActor, Tool,
    Vulnerability,

    Relationship, Sighting,

    OBJ_MAP, OBJ_MAP_OBSERVABLE, EXT_MAP
""".replace(",", " ").split()
