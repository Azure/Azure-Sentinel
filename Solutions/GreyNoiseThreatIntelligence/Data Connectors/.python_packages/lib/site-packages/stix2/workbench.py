"""Functions and class wrappers for interacting with STIX2 data at a high level.

.. autofunction:: create
.. autofunction:: set_default_creator
.. autofunction:: set_default_created
.. autofunction:: set_default_external_refs
.. autofunction:: set_default_object_marking_refs
.. autofunction:: get
.. autofunction:: all_versions
.. autofunction:: query
.. autofunction:: creator_of
.. autofunction:: relationships
.. autofunction:: related_to
.. autofunction:: save
.. autofunction:: add_filters
.. autofunction:: add_filter
.. autofunction:: parse
.. autofunction:: add_data_source
.. autofunction:: add_data_sources

"""

import functools

from . import AttackPattern as _AttackPattern
from . import Campaign as _Campaign
from . import CourseOfAction as _CourseOfAction
from . import Grouping as _Grouping
from . import Identity as _Identity
from . import Indicator as _Indicator
from . import Infrastructure as _Infrastructure
from . import IntrusionSet as _IntrusionSet
from . import Location as _Location
from . import Malware as _Malware
from . import MalwareAnalysis as _MalwareAnalysis
from . import Note as _Note
from . import OBJ_MAP
from . import ObservedData as _ObservedData
from . import Opinion as _Opinion
from . import Report as _Report
from . import ThreatActor as _ThreatActor
from . import Tool as _Tool
from . import Vulnerability as _Vulnerability
from .version import DEFAULT_VERSION

from . import (  # noqa: F401  isort:skip
    AlternateDataStream, ArchiveExt, Artifact, AutonomousSystem,
    Bundle, CustomExtension, CustomMarking, CustomObservable,
    Directory, DomainName, EmailAddress, EmailMessage,
    EmailMIMEComponent, Environment, ExternalReference, File,
    FileSystemSource, Filter, GranularMarking, HTTPRequestExt,
    ICMPExt, IPv4Address, IPv6Address, KillChainPhase, LanguageContent,
    MACAddress, MarkingDefinition, MemoryStore, Mutex, NetworkTraffic,
    NTFSExt, parse_observable, PDFExt, Process, RasterImageExt, Relationship,
    Sighting, SocketExt, Software, StatementMarking,
    TAXIICollectionSource, TCPExt, TLP_AMBER, TLP_GREEN, TLP_RED,
    TLP_WHITE, TLPMarking, UNIXAccountExt, URL, UserAccount,
    WindowsPEBinaryExt, WindowsPEOptionalHeaderType,
    WindowsPESection, WindowsProcessExt, WindowsRegistryKey,
    WindowsRegistryValueType, WindowsServiceExt, X509Certificate,
    X509V3ExtensionsType,
)
from .datastore.filters import FilterSet  # isort:skip


# Enable some adaptation to the current default supported STIX version.
_STIX_VID = "v" + DEFAULT_VERSION.replace(".", "")


# Use an implicit MemoryStore
_environ = Environment(store=MemoryStore())

create = _environ.create
set_default_creator = _environ.set_default_creator
set_default_created = _environ.set_default_created
set_default_external_refs = _environ.set_default_external_refs
set_default_object_marking_refs = _environ.set_default_object_marking_refs
get = _environ.get
all_versions = _environ.all_versions
query = _environ.query
creator_of = _environ.creator_of
relationships = _environ.relationships
related_to = _environ.related_to
save = _environ.add
add_filters = _environ.add_filters
add_filter = _environ.add_filter
parse = _environ.parse
add_data_source = _environ.source.add_data_source
add_data_sources = _environ.source.add_data_sources


# Wrap SDOs with helper functions


STIX_OBJS = [
    _AttackPattern, _Campaign, _CourseOfAction, _Identity, _Grouping,
    _Indicator, _Infrastructure, _IntrusionSet, _Location, _Malware,
    _MalwareAnalysis, _Note, _ObservedData, _Opinion, _Report,
    _ThreatActor, _Tool, _Vulnerability,
]

STIX_OBJ_DOCS = """s

.. method:: created_by(*args, **kwargs)

        {}

.. method:: relationships(*args, **kwargs)

        {}

.. method:: related(*args, **kwargs)

        {}

""".format(
    _environ.creator_of.__doc__,
    _environ.relationships.__doc__,
    _environ.related_to.__doc__,
)


def _created_by_wrapper(self, *args, **kwargs):
    return _environ.creator_of(self, *args, **kwargs)


def _relationships_wrapper(self, *args, **kwargs):
    return _environ.relationships(self, *args, **kwargs)


def _related_wrapper(self, *args, **kwargs):
    return _environ.related_to(self, *args, **kwargs)


def _setup_workbench():
    for obj_type in STIX_OBJS:

        # The idea here was originally to dynamically create subclasses which
        # were cleverly customized such that instantiating them would actually
        # invoke _environ.create().  This turns out to be impossible, since
        # __new__ can never create the class in the normal way, since that
        # invokes __new__ again, resulting in infinite recursion.  And
        # _environ.create() does exactly that.
        #
        # So instead, we create something "class-like", in that calling it
        # produces an instance of the desired class.  But these things will
        # be functions instead of classes.  One might think this trickery will
        # have undesirable side-effects, but actually it seems to work.
        # So far...
        new_class_dict = {
            '__doc__': 'Workbench wrapper around the `{0} <stix2.{1}.sdo.rst#stix2.{1}.sdo.{0}>`__ object. {2}'.format(
                obj_type.__name__,
                _STIX_VID,
                STIX_OBJ_DOCS,
            ),
            'created_by': _created_by_wrapper,
            'relationships': _relationships_wrapper,
            'related': _related_wrapper,
        }

        new_class = type(obj_type.__name__, (obj_type,), new_class_dict)
        factory_func = functools.partial(_environ.create, new_class)

        # Copy over some class attributes that other code expects to find
        factory_func._type = obj_type._type
        factory_func._properties = obj_type._properties
        if hasattr(obj_type, "_id_contributing_properties"):
            factory_func._id_contributing_properties = \
                obj_type._id_contributing_properties

        # Add our new "class" to this module's globals and to the library-wide
        # mapping.  This allows parse() to use the wrapped classes.
        globals()[obj_type.__name__] = factory_func
        OBJ_MAP[obj_type._type] = factory_func


_setup_workbench()


# Functions to get all objects of a specific type


def attack_patterns(filters=None):
    """Retrieve all Attack Pattern objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'attack-pattern'))
    return query(filter_list)


def campaigns(filters=None):
    """Retrieve all Campaign objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'campaign'))
    return query(filter_list)


def courses_of_action(filters=None):
    """Retrieve all Course of Action objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'course-of-action'))
    return query(filter_list)


def groupings(filters=None):
    """Retrieve all Grouping objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'grouping'))
    return query(filter_list)


def identities(filters=None):
    """Retrieve all Identity objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'identity'))
    return query(filter_list)


def indicators(filters=None):
    """Retrieve all Indicator objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'indicator'))
    return query(filter_list)


def infrastructures(filters=None):
    """Retrieve all Infrastructure objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'infrastructure'))
    return query(filter_list)


def intrusion_sets(filters=None):
    """Retrieve all Intrusion Set objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'intrusion-set'))
    return query(filter_list)


def locations(filters=None):
    """Retrieve all Location objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'location'))
    return query(filter_list)


def malware(filters=None):
    """Retrieve all Malware objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'malware'))
    return query(filter_list)


def malware_analyses(filters=None):
    """Retrieve all Malware Analysis objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'malware-analysis'))
    return query(filter_list)


def notes(filters=None):
    """Retrieve all Note objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'note'))
    return query(filter_list)


def observed_data(filters=None):
    """Retrieve all Observed Data objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'observed-data'))
    return query(filter_list)


def opinions(filters=None):
    """Retrieve all Opinion objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'opinion'))
    return query(filter_list)


def reports(filters=None):
    """Retrieve all Report objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'report'))
    return query(filter_list)


def threat_actors(filters=None):
    """Retrieve all Threat Actor objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'threat-actor'))
    return query(filter_list)


def tools(filters=None):
    """Retrieve all Tool objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'tool'))
    return query(filter_list)


def vulnerabilities(filters=None):
    """Retrieve all Vulnerability objects.

    Args:
        filters (list, optional): A list of additional filters to apply to
            the query.

    """
    filter_list = FilterSet(filters)
    filter_list.add(Filter('type', '=', 'vulnerability'))
    return query(filter_list)
