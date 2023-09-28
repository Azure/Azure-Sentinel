"""STIX 2.0 Cyber Observable Objects.

Embedded observable object types, such as Email MIME Component, which is
embedded in Email Message objects, inherit from ``_STIXBase20`` instead of
_Observable and do not have a ``_type`` attribute.
"""

from collections import OrderedDict
import itertools

from ..custom import _custom_extension_builder, _custom_observable_builder
from ..exceptions import AtLeastOnePropertyError, DependentPropertiesError
from ..properties import (
    BinaryProperty, BooleanProperty, DictionaryProperty,
    EmbeddedObjectProperty, EnumProperty, ExtensionsProperty, FloatProperty,
    HashesProperty, HexProperty, IntegerProperty, ListProperty,
    ObjectReferenceProperty, StringProperty, TimestampProperty, TypeProperty,
)
from .base import _Extension, _Observable, _STIXBase20
from .vocab import HASHING_ALGORITHM


class Artifact(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716219>`__.
    """  # noqa

    _type = 'artifact'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('mime_type', StringProperty()),
        ('payload_bin', BinaryProperty()),
        ('url', StringProperty()),
        ('hashes', HashesProperty(HASHING_ALGORITHM, spec_version='2.0')),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])

    def _check_object_constraints(self):
        super(Artifact, self)._check_object_constraints()
        self._check_mutually_exclusive_properties(['payload_bin', 'url'])
        self._check_properties_dependency(['hashes'], ['url'])


class AutonomousSystem(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716221>`__.
    """  # noqa

    _type = 'autonomous-system'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('number', IntegerProperty(required=True)),
        ('name', StringProperty()),
        ('rir', StringProperty()),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])


class Directory(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716223>`__.
    """  # noqa

    _type = 'directory'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('path', StringProperty(required=True)),
        ('path_enc', StringProperty()),
        # these are not the created/modified timestamps of the object itself
        ('created', TimestampProperty()),
        ('modified', TimestampProperty()),
        ('accessed', TimestampProperty()),
        ('contains_refs', ListProperty(ObjectReferenceProperty(valid_types=['file', 'directory']))),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])


class DomainName(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716225>`__.
    """  # noqa

    _type = 'domain-name'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('value', StringProperty(required=True)),
        ('resolves_to_refs', ListProperty(ObjectReferenceProperty(valid_types=['ipv4-addr', 'ipv6-addr', 'domain-name']))),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])


class EmailAddress(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716227>`__.
    """  # noqa

    _type = 'email-addr'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('value', StringProperty(required=True)),
        ('display_name', StringProperty()),
        ('belongs_to_ref', ObjectReferenceProperty(valid_types='user-account')),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])


class EmailMIMEComponent(_STIXBase20):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716231>`__.
    """  # noqa

    _properties = OrderedDict([
        ('body', StringProperty()),
        ('body_raw_ref', ObjectReferenceProperty(valid_types=['artifact', 'file'])),
        ('content_type', StringProperty()),
        ('content_disposition', StringProperty()),
    ])

    def _check_object_constraints(self):
        super(EmailMIMEComponent, self)._check_object_constraints()
        self._check_at_least_one_property(['body', 'body_raw_ref'])


class EmailMessage(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716229>`__.
    """  # noqa

    _type = 'email-message'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('is_multipart', BooleanProperty(required=True)),
        ('date', TimestampProperty()),
        ('content_type', StringProperty()),
        ('from_ref', ObjectReferenceProperty(valid_types='email-addr')),
        ('sender_ref', ObjectReferenceProperty(valid_types='email-addr')),
        ('to_refs', ListProperty(ObjectReferenceProperty(valid_types='email-addr'))),
        ('cc_refs', ListProperty(ObjectReferenceProperty(valid_types='email-addr'))),
        ('bcc_refs', ListProperty(ObjectReferenceProperty(valid_types='email-addr'))),
        ('subject', StringProperty()),
        ('received_lines', ListProperty(StringProperty)),
        ('additional_header_fields', DictionaryProperty(spec_version='2.0')),
        ('body', StringProperty()),
        ('body_multipart', ListProperty(EmbeddedObjectProperty(type=EmailMIMEComponent))),
        ('raw_email_ref', ObjectReferenceProperty(valid_types='artifact')),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])

    def _check_object_constraints(self):
        super(EmailMessage, self)._check_object_constraints()
        self._check_properties_dependency(['is_multipart'], ['body_multipart'])
        if self.get('is_multipart') is True and self.get('body'):
            # 'body' MAY only be used if is_multipart is false.
            raise DependentPropertiesError(self.__class__, [('is_multipart', 'body')])


class ArchiveExt(_Extension):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716235>`__.
    """  # noqa

    _type = 'archive-ext'
    _properties = OrderedDict([
        ('contains_refs', ListProperty(ObjectReferenceProperty(valid_types='file'), required=True)),
        ('version', StringProperty()),
        ('comment', StringProperty()),
    ])


class AlternateDataStream(_STIXBase20):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716239>`__.
    """  # noqa

    _properties = OrderedDict([
        ('name', StringProperty(required=True)),
        ('hashes', HashesProperty(HASHING_ALGORITHM, spec_version="2.0")),
        ('size', IntegerProperty()),
    ])


class NTFSExt(_Extension):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716237>`__.
    """  # noqa

    _type = 'ntfs-ext'
    _properties = OrderedDict([
        ('sid', StringProperty()),
        ('alternate_data_streams', ListProperty(EmbeddedObjectProperty(type=AlternateDataStream))),
    ])


class PDFExt(_Extension):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716241>`__.
    """  # noqa

    _type = 'pdf-ext'
    _properties = OrderedDict([
        ('version', StringProperty()),
        ('is_optimized', BooleanProperty()),
        ('document_info_dict', DictionaryProperty(spec_version='2.0')),
        ('pdfid0', StringProperty()),
        ('pdfid1', StringProperty()),
    ])


class RasterImageExt(_Extension):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716243>`__.
    """  # noqa

    _type = 'raster-image-ext'
    _properties = OrderedDict([
        ('image_height', IntegerProperty()),
        ('image_width', IntegerProperty()),
        ('bits_per_pixel', IntegerProperty()),
        ('image_compression_algorithm', StringProperty()),
        ('exif_tags', DictionaryProperty(spec_version='2.0')),
    ])


class WindowsPEOptionalHeaderType(_STIXBase20):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716248>`__.
    """  # noqa

    _properties = OrderedDict([
        ('magic_hex', HexProperty()),
        ('major_linker_version', IntegerProperty()),
        ('minor_linker_version', IntegerProperty()),
        ('size_of_code', IntegerProperty()),
        ('size_of_initialized_data', IntegerProperty()),
        ('size_of_uninitialized_data', IntegerProperty()),
        ('address_of_entry_point', IntegerProperty()),
        ('base_of_code', IntegerProperty()),
        ('base_of_data', IntegerProperty()),
        ('image_base', IntegerProperty()),
        ('section_alignment', IntegerProperty()),
        ('file_alignment', IntegerProperty()),
        ('major_os_version', IntegerProperty()),
        ('minor_os_version', IntegerProperty()),
        ('major_image_version', IntegerProperty()),
        ('minor_image_version', IntegerProperty()),
        ('major_subsystem_version', IntegerProperty()),
        ('minor_subsystem_version', IntegerProperty()),
        ('win32_version_value_hex', HexProperty()),
        ('size_of_image', IntegerProperty()),
        ('size_of_headers', IntegerProperty()),
        ('checksum_hex', HexProperty()),
        ('subsystem_hex', HexProperty()),
        ('dll_characteristics_hex', HexProperty()),
        ('size_of_stack_reserve', IntegerProperty()),
        ('size_of_stack_commit', IntegerProperty()),
        ('size_of_heap_reserve', IntegerProperty()),
        ('size_of_heap_commit', IntegerProperty()),
        ('loader_flags_hex', HexProperty()),
        ('number_of_rva_and_sizes', IntegerProperty()),
        ('hashes', HashesProperty(HASHING_ALGORITHM, spec_version="2.0")),
    ])

    def _check_object_constraints(self):
        super(WindowsPEOptionalHeaderType, self)._check_object_constraints()
        self._check_at_least_one_property()


class WindowsPESection(_STIXBase20):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716250>`__.
    """  # noqa

    _properties = OrderedDict([
        ('name', StringProperty(required=True)),
        ('size', IntegerProperty()),
        ('entropy', FloatProperty()),
        ('hashes', HashesProperty(HASHING_ALGORITHM, spec_version="2.0")),
    ])


class WindowsPEBinaryExt(_Extension):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716245>`__.
    """  # noqa

    _type = 'windows-pebinary-ext'
    _properties = OrderedDict([
        ('pe_type', StringProperty(required=True)),  # open_vocab
        ('imphash', StringProperty()),
        ('machine_hex', HexProperty()),
        ('number_of_sections', IntegerProperty()),
        ('time_date_stamp', TimestampProperty(precision='second')),
        ('pointer_to_symbol_table_hex', HexProperty()),
        ('number_of_symbols', IntegerProperty()),
        ('size_of_optional_header', IntegerProperty()),
        ('characteristics_hex', HexProperty()),
        ('file_header_hashes', HashesProperty(HASHING_ALGORITHM, spec_version="2.0")),
        ('optional_header', EmbeddedObjectProperty(type=WindowsPEOptionalHeaderType)),
        ('sections', ListProperty(EmbeddedObjectProperty(type=WindowsPESection))),
    ])


class File(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716233>`__.
    """  # noqa

    _type = 'file'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('hashes', HashesProperty(HASHING_ALGORITHM, spec_version="2.0")),
        ('size', IntegerProperty()),
        ('name', StringProperty()),
        ('name_enc', StringProperty()),
        ('magic_number_hex', HexProperty()),
        ('mime_type', StringProperty()),
        # these are not the created/modified timestamps of the object itself
        ('created', TimestampProperty()),
        ('modified', TimestampProperty()),
        ('accessed', TimestampProperty()),
        ('parent_directory_ref', ObjectReferenceProperty(valid_types='directory')),
        ('is_encrypted', BooleanProperty()),
        ('encryption_algorithm', StringProperty()),
        ('decryption_key', StringProperty()),
        ('contains_refs', ListProperty(ObjectReferenceProperty)),
        ('content_ref', ObjectReferenceProperty(valid_types='artifact')),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])

    def _check_object_constraints(self):
        super(File, self)._check_object_constraints()
        self._check_properties_dependency(['is_encrypted'], ['encryption_algorithm', 'decryption_key'])
        self._check_at_least_one_property(['hashes', 'name'])


class IPv4Address(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716252>`__.
    """  # noqa

    _type = 'ipv4-addr'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('value', StringProperty(required=True)),
        ('resolves_to_refs', ListProperty(ObjectReferenceProperty(valid_types='mac-addr'))),
        ('belongs_to_refs', ListProperty(ObjectReferenceProperty(valid_types='autonomous-system'))),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])


class IPv6Address(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716254>`__.
    """  # noqa

    _type = 'ipv6-addr'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('value', StringProperty(required=True)),
        ('resolves_to_refs', ListProperty(ObjectReferenceProperty(valid_types='mac-addr'))),
        ('belongs_to_refs', ListProperty(ObjectReferenceProperty(valid_types='autonomous-system'))),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])


class MACAddress(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716256>`__.
    """  # noqa

    _type = 'mac-addr'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('value', StringProperty(required=True)),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])


class Mutex(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716258>`__.
    """  # noqa

    _type = 'mutex'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('name', StringProperty(required=True)),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])


class HTTPRequestExt(_Extension):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716262>`__.
    """  # noqa

    _type = 'http-request-ext'
    _properties = OrderedDict([
        ('request_method', StringProperty(required=True)),
        ('request_value', StringProperty(required=True)),
        ('request_version', StringProperty()),
        ('request_header', DictionaryProperty(spec_version='2.0')),
        ('message_body_length', IntegerProperty()),
        ('message_body_data_ref', ObjectReferenceProperty(valid_types='artifact')),
    ])


class ICMPExt(_Extension):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716264>`__.
    """  # noqa

    _type = 'icmp-ext'
    _properties = OrderedDict([
        ('icmp_type_hex', HexProperty(required=True)),
        ('icmp_code_hex', HexProperty(required=True)),
    ])


class SocketExt(_Extension):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716266>`__.
    """  # noqa

    _type = 'socket-ext'
    _properties = OrderedDict([
        (
            'address_family', EnumProperty(
                allowed=[
                    "AF_UNSPEC",
                    "AF_INET",
                    "AF_IPX",
                    "AF_APPLETALK",
                    "AF_NETBIOS",
                    "AF_INET6",
                    "AF_IRDA",
                    "AF_BTH",
                ], required=True,
            ),
        ),
        ('is_blocking', BooleanProperty()),
        ('is_listening', BooleanProperty()),
        (
            'protocol_family', EnumProperty(
                allowed=[
                    "PF_INET",
                    "PF_IPX",
                    "PF_APPLETALK",
                    "PF_INET6",
                    "PF_AX25",
                    "PF_NETROM",
                ],
            ),
        ),
        ('options', DictionaryProperty(spec_version='2.0')),
        (
            'socket_type', EnumProperty(
                allowed=[
                    "SOCK_STREAM",
                    "SOCK_DGRAM",
                    "SOCK_RAW",
                    "SOCK_RDM",
                    "SOCK_SEQPACKET",
                ],
            ),
        ),
        ('socket_descriptor', IntegerProperty()),
        ('socket_handle', IntegerProperty()),
    ])


class TCPExt(_Extension):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716271>`__.
    """  # noqa

    _type = 'tcp-ext'
    _properties = OrderedDict([
        ('src_flags_hex', HexProperty()),
        ('dst_flags_hex', HexProperty()),
    ])


class NetworkTraffic(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716260>`__.
    """  # noqa

    _type = 'network-traffic'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('start', TimestampProperty()),
        ('end', TimestampProperty()),
        ('is_active', BooleanProperty()),
        ('src_ref', ObjectReferenceProperty(valid_types=['ipv4-addr', 'ipv6-addr', 'mac-addr', 'domain-name'])),
        ('dst_ref', ObjectReferenceProperty(valid_types=['ipv4-addr', 'ipv6-addr', 'mac-addr', 'domain-name'])),
        ('src_port', IntegerProperty()),
        ('dst_port', IntegerProperty()),
        ('protocols', ListProperty(StringProperty, required=True)),
        ('src_byte_count', IntegerProperty()),
        ('dst_byte_count', IntegerProperty()),
        ('src_packets', IntegerProperty()),
        ('dst_packets', IntegerProperty()),
        ('ipfix', DictionaryProperty(spec_version='2.0')),
        ('src_payload_ref', ObjectReferenceProperty(valid_types='artifact')),
        ('dst_payload_ref', ObjectReferenceProperty(valid_types='artifact')),
        ('encapsulates_refs', ListProperty(ObjectReferenceProperty(valid_types='network-traffic'))),
        ('encapsulates_by_ref', ObjectReferenceProperty(valid_types='network-traffic')),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])

    def _check_object_constraints(self):
        super(NetworkTraffic, self)._check_object_constraints()
        self._check_at_least_one_property(['src_ref', 'dst_ref'])


class WindowsProcessExt(_Extension):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716275>`__.
    """  # noqa

    _type = 'windows-process-ext'
    _properties = OrderedDict([
        ('aslr_enabled', BooleanProperty()),
        ('dep_enabled', BooleanProperty()),
        ('priority', StringProperty()),
        ('owner_sid', StringProperty()),
        ('window_title', StringProperty()),
        ('startup_info', DictionaryProperty(spec_version='2.0')),
    ])


class WindowsServiceExt(_Extension):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716277>`__.
    """  # noqa

    _type = 'windows-service-ext'
    _properties = OrderedDict([
        ('service_name', StringProperty(required=True)),
        ('descriptions', ListProperty(StringProperty)),
        ('display_name', StringProperty()),
        ('group_name', StringProperty()),
        (
            'start_type', EnumProperty(
                allowed=[
                    "SERVICE_AUTO_START",
                    "SERVICE_BOOT_START",
                    "SERVICE_DEMAND_START",
                    "SERVICE_DISABLED",
                    "SERVICE_SYSTEM_ALERT",
                ],
            ),
        ),
        ('service_dll_refs', ListProperty(ObjectReferenceProperty(valid_types='file'))),
        (
            'service_type', EnumProperty(
                allowed=[
                    "SERVICE_KERNEL_DRIVER",
                    "SERVICE_FILE_SYSTEM_DRIVER",
                    "SERVICE_WIN32_OWN_PROCESS",
                    "SERVICE_WIN32_SHARE_PROCESS",
                ],
            ),
        ),
        (
            'service_status', EnumProperty(
                allowed=[
                    "SERVICE_CONTINUE_PENDING",
                    "SERVICE_PAUSE_PENDING",
                    "SERVICE_PAUSED",
                    "SERVICE_RUNNING",
                    "SERVICE_START_PENDING",
                    "SERVICE_STOP_PENDING",
                    "SERVICE_STOPPED",
                ],
            ),
        ),
    ])


class Process(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716273>`__.
    """  # noqa

    _type = 'process'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('is_hidden', BooleanProperty()),
        ('pid', IntegerProperty()),
        ('name', StringProperty()),
        # this is not the created timestamps of the object itself
        ('created', TimestampProperty()),
        ('cwd', StringProperty()),
        ('arguments', ListProperty(StringProperty)),
        ('command_line', StringProperty()),
        ('environment_variables', DictionaryProperty(spec_version='2.0')),
        ('opened_connection_refs', ListProperty(ObjectReferenceProperty(valid_types='network-traffic'))),
        ('creator_user_ref', ObjectReferenceProperty(valid_types='user-account')),
        ('binary_ref', ObjectReferenceProperty(valid_types='file')),
        ('parent_ref', ObjectReferenceProperty(valid_types='process')),
        ('child_refs', ListProperty(ObjectReferenceProperty('process'))),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])

    def _check_object_constraints(self):
        # no need to check windows-service-ext, since it has a required property
        super(Process, self)._check_object_constraints()
        try:
            self._check_at_least_one_property()
            if 'windows-process-ext' in self.get('extensions', {}):
                self.extensions['windows-process-ext']._check_at_least_one_property()
        except AtLeastOnePropertyError as enclosing_exc:
            if 'extensions' not in self:
                raise enclosing_exc
            else:
                if 'windows-process-ext' in self.get('extensions', {}):
                    self.extensions['windows-process-ext']._check_at_least_one_property()


class Software(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716282>`__.
    """  # noqa

    _type = 'software'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('name', StringProperty(required=True)),
        ('cpe', StringProperty()),
        ('languages', ListProperty(StringProperty)),
        ('vendor', StringProperty()),
        ('version', StringProperty()),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])


class URL(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716284>`__.
    """  # noqa

    _type = 'url'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('value', StringProperty(required=True)),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])


class UNIXAccountExt(_Extension):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716289>`__.
    """  # noqa

    _type = 'unix-account-ext'
    _properties = OrderedDict([
        ('gid', IntegerProperty()),
        ('groups', ListProperty(StringProperty)),
        ('home_dir', StringProperty()),
        ('shell', StringProperty()),
    ])


class UserAccount(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716286>`__.
    """  # noqa

    _type = 'user-account'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('user_id', StringProperty(required=True)),
        ('account_login', StringProperty()),
        ('account_type', StringProperty()),   # open vocab
        ('display_name', StringProperty()),
        ('is_service_account', BooleanProperty()),
        ('is_privileged', BooleanProperty()),
        ('can_escalate_privs', BooleanProperty()),
        ('is_disabled', BooleanProperty()),
        ('account_created', TimestampProperty()),
        ('account_expires', TimestampProperty()),
        ('password_last_changed', TimestampProperty()),
        ('account_first_login', TimestampProperty()),
        ('account_last_login', TimestampProperty()),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])


class WindowsRegistryValueType(_STIXBase20):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716293>`__.
    """  # noqa

    _type = 'windows-registry-value-type'
    _properties = OrderedDict([
        ('name', StringProperty(required=True)),
        ('data', StringProperty()),
        (
            'data_type', EnumProperty(
                allowed=[
                    "REG_NONE",
                    "REG_SZ",
                    "REG_EXPAND_SZ",
                    "REG_BINARY",
                    "REG_DWORD",
                    "REG_DWORD_BIG_ENDIAN",
                    "REG_LINK",
                    "REG_MULTI_SZ",
                    "REG_RESOURCE_LIST",
                    "REG_FULL_RESOURCE_DESCRIPTION",
                    "REG_RESOURCE_REQUIREMENTS_LIST",
                    "REG_QWORD",
                    "REG_INVALID_TYPE",
                ],
            ),
        ),
    ])


class WindowsRegistryKey(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716291>`__.
    """  # noqa

    _type = 'windows-registry-key'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('key', StringProperty(required=True)),
        ('values', ListProperty(EmbeddedObjectProperty(type=WindowsRegistryValueType))),
        # this is not the modified timestamps of the object itself
        ('modified', TimestampProperty()),
        ('creator_user_ref', ObjectReferenceProperty(valid_types='user-account')),
        ('number_of_subkeys', IntegerProperty()),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])


class X509V3ExtensionsType(_STIXBase20):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716298>`__.
    """  # noqa

    _type = 'x509-v3-extensions-type'
    _properties = OrderedDict([
        ('basic_constraints', StringProperty()),
        ('name_constraints', StringProperty()),
        ('policy_constraints', StringProperty()),
        ('key_usage', StringProperty()),
        ('extended_key_usage', StringProperty()),
        ('subject_key_identifier', StringProperty()),
        ('authority_key_identifier', StringProperty()),
        ('subject_alternative_name', StringProperty()),
        ('issuer_alternative_name', StringProperty()),
        ('subject_directory_attributes', StringProperty()),
        ('crl_distribution_points', StringProperty()),
        ('inhibit_any_policy', StringProperty()),
        ('private_key_usage_period_not_before', TimestampProperty()),
        ('private_key_usage_period_not_after', TimestampProperty()),
        ('certificate_policies', StringProperty()),
        ('policy_mappings', StringProperty()),
    ])


class X509Certificate(_Observable):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part4-cyber-observable-objects/stix-v2.0-cs01-part4-cyber-observable-objects.html#_Toc496716296>`__.
    """  # noqa

    _type = 'x509-certificate'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('is_self_signed', BooleanProperty()),
        ('hashes', HashesProperty(HASHING_ALGORITHM, spec_version="2.0")),
        ('version', StringProperty()),
        ('serial_number', StringProperty()),
        ('signature_algorithm', StringProperty()),
        ('issuer', StringProperty()),
        ('validity_not_before', TimestampProperty()),
        ('validity_not_after', TimestampProperty()),
        ('subject', StringProperty()),
        ('subject_public_key_algorithm', StringProperty()),
        ('subject_public_key_modulus', StringProperty()),
        ('subject_public_key_exponent', IntegerProperty()),
        ('x509_v3_extensions', EmbeddedObjectProperty(type=X509V3ExtensionsType)),
        ('extensions', ExtensionsProperty(spec_version='2.0')),
    ])


def CustomObservable(type='x-custom-observable', properties=None):
    """Custom STIX Cyber Observable Object type decorator.

    Example:
        >>> from stix2.v20 import CustomObservable
        >>> from stix2.properties import IntegerProperty, StringProperty
        >>> @CustomObservable('x-custom-observable', [
        ...     ('property1', StringProperty(required=True)),
        ...     ('property2', IntegerProperty()),
        ... ])
        ... class MyNewObservableType():
        ...     pass

    """
    def wrapper(cls):
        _properties = list(
            itertools.chain.from_iterable([
                [('type', TypeProperty(type, spec_version='2.0'))],
                properties,
                [('extensions', ExtensionsProperty(spec_version='2.0'))],
            ]),
        )
        return _custom_observable_builder(cls, type, _properties, '2.0', _Observable)
    return wrapper


def CustomExtension(type='x-custom-observable-ext', properties=None):
    """Decorator for custom extensions to STIX Cyber Observables.
    """
    def wrapper(cls):
        return _custom_extension_builder(cls, type, properties, '2.0', _Extension)
    return wrapper
