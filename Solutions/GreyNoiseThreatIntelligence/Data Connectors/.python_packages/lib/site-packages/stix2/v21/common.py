"""STIX 2.1 Common Data Types and Properties."""

from collections import OrderedDict

from . import _Extension
from ..custom import _custom_extension_builder, _custom_marking_builder
from ..exceptions import InvalidValueError, PropertyPresenceError
from ..markings import _MarkingsMixin
from ..markings.utils import check_tlp_marking
from ..properties import (
    BooleanProperty, DictionaryProperty, EnumProperty, ExtensionsProperty,
    HashesProperty, IDProperty, IntegerProperty, ListProperty, Property,
    ReferenceProperty, SelectorProperty, StringProperty, TimestampProperty,
    TypeProperty,
)
from ..utils import NOW, _get_dict
from .base import _STIXBase21
from .vocab import EXTENSION_TYPE, HASHING_ALGORITHM


class ExternalReference(_STIXBase21):
    """For more detailed information on this object's properties, see
    `the STIX 2.1 specification <https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html#_72bcfr3t79jx>`__.
    """

    _properties = OrderedDict([
        ('source_name', StringProperty(required=True)),
        ('description', StringProperty()),
        ('url', StringProperty()),
        ('hashes', HashesProperty(HASHING_ALGORITHM, spec_version="2.1")),
        ('external_id', StringProperty()),
    ])

    # This is hash-algorithm-ov
    _LEGAL_HASHES = {
        "MD5", "SHA-1", "SHA-256", "SHA-512", "SHA3-256", "SHA3-512", "SSDEEP",
        "TLSH",
    }

    def _check_object_constraints(self):
        super(ExternalReference, self)._check_object_constraints()
        self._check_at_least_one_property(['description', 'external_id', 'url'])

        if "hashes" in self:
            if any(
                hash_ not in self._LEGAL_HASHES
                for hash_ in self["hashes"]
            ):
                raise InvalidValueError(
                    ExternalReference, "hashes",
                    "Hash algorithm names must be members of hash-algorithm-ov",
                )


class KillChainPhase(_STIXBase21):
    """For more detailed information on this object's properties, see
    `the STIX 2.1 specification <https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html#_i4tjv75ce50h>`__.
    """

    _properties = OrderedDict([
        ('kill_chain_name', StringProperty(required=True)),
        ('phase_name', StringProperty(required=True)),
    ])


class GranularMarking(_STIXBase21):
    """For more detailed information on this object's properties, see
    `the STIX 2.1 specification <https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html#_robezi5egfdr>`__.
    """

    _properties = OrderedDict([
        ('lang', StringProperty()),
        ('marking_ref', ReferenceProperty(valid_types='marking-definition', spec_version='2.1')),
        ('selectors', ListProperty(SelectorProperty, required=True)),
    ])

    def _check_object_constraints(self):
        super(GranularMarking, self)._check_object_constraints()
        self._check_at_least_one_property(['lang', 'marking_ref'])


class LanguageContent(_STIXBase21):
    """For more detailed information on this object's properties, see
    `the STIX 2.1 specification <https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html#_z9r1cwtu8jja>`__.
    """

    _type = 'language-content'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.1')),
        ('spec_version', StringProperty(fixed='2.1')),
        ('id', IDProperty(_type, spec_version='2.1')),
        ('created_by_ref', ReferenceProperty(valid_types='identity', spec_version='2.1')),
        ('created', TimestampProperty(default=lambda: NOW, precision='millisecond', precision_constraint='min')),
        ('modified', TimestampProperty(default=lambda: NOW, precision='millisecond', precision_constraint='min')),
        ('object_ref', ReferenceProperty(valid_types=["SCO", "SDO", "SRO"], spec_version='2.1', required=True)),
        # TODO: 'object_modified' MUST be an exact match for the modified time of the STIX Object being referenced
        ('object_modified', TimestampProperty(precision='millisecond')),
        # TODO: Implement 'contents' property requirements as defined in STIX 2.1 CS02
        ('contents', DictionaryProperty(spec_version='2.1', required=True)),
        ('revoked', BooleanProperty(default=lambda: False)),
        ('labels', ListProperty(StringProperty)),
        ('confidence', IntegerProperty()),
        ('external_references', ListProperty(ExternalReference)),
        ('object_marking_refs', ListProperty(ReferenceProperty(valid_types='marking-definition', spec_version='2.1'))),
        ('granular_markings', ListProperty(GranularMarking)),
        ('extensions', ExtensionsProperty(spec_version='2.1')),
    ])


class ExtensionDefinition(_STIXBase21):
    """For more detailed information on this object's properties, see
    `the STIX 2.1 specification <https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html#_32j232tfvtly>`__.
    """

    _type = 'extension-definition'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.1')),
        ('spec_version', StringProperty(fixed='2.1')),
        ('id', IDProperty(_type, spec_version='2.1')),
        ('created_by_ref', ReferenceProperty(valid_types='identity', spec_version='2.1', required=True)),
        ('created', TimestampProperty(default=lambda: NOW, precision='millisecond', precision_constraint='min')),
        ('modified', TimestampProperty(default=lambda: NOW, precision='millisecond', precision_constraint='min')),
        ('name', StringProperty(required=True)),
        ('description', StringProperty()),
        ('schema', StringProperty(required=True)),
        ('version', StringProperty(required=True)),
        (
            'extension_types', ListProperty(
                EnumProperty(
                    allowed=EXTENSION_TYPE,
                ), required=True,
            ),
        ),
        ('extension_properties', ListProperty(StringProperty)),
        ('revoked', BooleanProperty(default=lambda: False)),
        ('labels', ListProperty(StringProperty)),
        ('external_references', ListProperty(ExternalReference)),
        ('object_marking_refs', ListProperty(ReferenceProperty(valid_types='marking-definition', spec_version='2.1'))),
        ('granular_markings', ListProperty(GranularMarking)),
    ])


def CustomExtension(type='x-custom-ext', properties=None):
    """Custom STIX Object Extension decorator.
    """
    def wrapper(cls):
        return _custom_extension_builder(cls, type, properties, '2.1', _Extension)

    return wrapper


class TLPMarking(_STIXBase21):
    """For more detailed information on this object's properties, see
    `the STIX 2.1 specification <https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html#_yd3ar14ekwrs>`__.
    """

    _type = 'tlp'
    _properties = OrderedDict([
        ('tlp', StringProperty(required=True)),
    ])


class StatementMarking(_STIXBase21):
    """For more detailed information on this object's properties, see
    `the STIX 2.1 specification <https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html#_3ru8r05saera>`__.
    """

    _type = 'statement'
    _properties = OrderedDict([
        ('statement', StringProperty(required=True)),
    ])

    def __init__(self, statement=None, **kwargs):
        # Allow statement as positional args.
        if statement and not kwargs.get('statement'):
            kwargs['statement'] = statement

        super(StatementMarking, self).__init__(**kwargs)


class MarkingProperty(Property):
    """Represent the marking objects in the ``definition`` property of
    marking-definition objects.
    """

    def clean(self, value, allow_custom=False):
        if type(value) in OBJ_MAP_MARKING.values():
            return value, False
        else:
            raise ValueError("must be a Statement, TLP Marking or a registered marking.")


class MarkingDefinition(_STIXBase21, _MarkingsMixin):
    """For more detailed information on this object's properties, see
    `the STIX 2.1 specification <https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html#_k5fndj2c7c1k>`__.
    """

    _type = 'marking-definition'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.1')),
        ('spec_version', StringProperty(fixed='2.1')),
        ('id', IDProperty(_type, spec_version='2.1')),
        ('created_by_ref', ReferenceProperty(valid_types='identity', spec_version='2.1')),
        ('created', TimestampProperty(default=lambda: NOW, precision='millisecond', precision_constraint='min')),
        ('definition_type', StringProperty()),
        ('name', StringProperty()),
        ('definition', MarkingProperty()),
        ('external_references', ListProperty(ExternalReference)),
        ('object_marking_refs', ListProperty(ReferenceProperty(valid_types='marking-definition', spec_version='2.1'))),
        ('granular_markings', ListProperty(GranularMarking)),
        ('extensions', ExtensionsProperty(spec_version='2.1')),
    ])

    def __init__(self, **kwargs):
        if {'definition_type', 'definition'}.issubset(kwargs.keys()):
            # Create correct marking type object
            try:
                marking_type = OBJ_MAP_MARKING[kwargs['definition_type']]
            except KeyError:
                raise ValueError("definition_type must be a valid marking type")

            if not isinstance(kwargs['definition'], marking_type):
                defn = _get_dict(kwargs['definition'])
                kwargs['definition'] = marking_type(**defn)

        super(MarkingDefinition, self).__init__(**kwargs)

    def _check_object_constraints(self):
        super(MarkingDefinition, self)._check_object_constraints()

        definition = self.get("definition")
        definition_type = self.get("definition_type")
        extensions = self.get("extensions")

        if not (definition_type and definition) and not extensions:
            raise PropertyPresenceError(
                "MarkingDefinition objects must have the properties "
                "'definition_type' and 'definition' if 'extensions' is not present",
                MarkingDefinition,
            )

        check_tlp_marking(self, '2.1')

    def serialize(self, pretty=False, include_optional_defaults=False, **kwargs):
        check_tlp_marking(self, '2.1')
        return super(MarkingDefinition, self).serialize(pretty, include_optional_defaults, **kwargs)


OBJ_MAP_MARKING = {
    'tlp': TLPMarking,
    'statement': StatementMarking,
}


def CustomMarking(type='x-custom-marking', properties=None):
    """Custom STIX Marking decorator.

    Example:
        >>> from stix2.v21 import CustomMarking
        >>> from stix2.properties import IntegerProperty, StringProperty
        >>> @CustomMarking('x-custom-marking', [
        ...     ('property1', StringProperty(required=True)),
        ...     ('property2', IntegerProperty()),
        ... ])
        ... class MyNewMarkingObjectType():
        ...     pass

    """
    def wrapper(cls):
        return _custom_marking_builder(cls, type, properties, '2.1', _STIXBase21)
    return wrapper


# TODO: don't allow the creation of any other TLPMarkings than the ones below

TLP_WHITE = MarkingDefinition(
    id='marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9',
    created='2017-01-20T00:00:00.000Z',
    definition_type='tlp',
    name='TLP:WHITE',
    definition=TLPMarking(tlp='white'),
)

TLP_GREEN = MarkingDefinition(
    id='marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da',
    created='2017-01-20T00:00:00.000Z',
    definition_type='tlp',
    name='TLP:GREEN',
    definition=TLPMarking(tlp='green'),
)

TLP_AMBER = MarkingDefinition(
    id='marking-definition--f88d31f6-486f-44da-b317-01333bde0b82',
    created='2017-01-20T00:00:00.000Z',
    definition_type='tlp',
    name='TLP:AMBER',
    definition=TLPMarking(tlp='amber'),
)

TLP_RED = MarkingDefinition(
    id='marking-definition--5e57c739-391a-4eb3-b6be-7d15ca92d5ed',
    created='2017-01-20T00:00:00.000Z',
    definition_type='tlp',
    name='TLP:RED',
    definition=TLPMarking(tlp='red'),
)
