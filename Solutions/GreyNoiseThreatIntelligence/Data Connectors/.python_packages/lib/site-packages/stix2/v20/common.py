"""STIX 2.0 Common Data Types and Properties."""

from collections import OrderedDict
import copy

from ..custom import _custom_marking_builder
from ..markings import _MarkingsMixin
from ..markings.utils import check_tlp_marking
from ..properties import (
    HashesProperty, IDProperty, ListProperty, Property, ReferenceProperty,
    SelectorProperty, StringProperty, TimestampProperty, TypeProperty,
)
from ..utils import NOW, _get_dict
from .base import _STIXBase20
from .vocab import HASHING_ALGORITHM


def _should_set_millisecond(cr, marking_type):
    # TLP instances in the 2.0 spec have millisecond precision unlike other markings
    if marking_type == TLPMarking:
        return True
    # otherwise,  precision is kept from how it was given
    if isinstance(cr, str):
        if '.' in cr:
            return True
        else:
            return False
    if cr.precision == 'millisecond':
        return True
    return False


class ExternalReference(_STIXBase20):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part1-stix-core/stix-v2.0-cs01-part1-stix-core.html#_Toc496709261>`__.
    """

    _properties = OrderedDict([
        ('source_name', StringProperty(required=True)),
        ('description', StringProperty()),
        ('url', StringProperty()),
        ('hashes', HashesProperty(HASHING_ALGORITHM, spec_version='2.0')),
        ('external_id', StringProperty()),
    ])

    def _check_object_constraints(self):
        super(ExternalReference, self)._check_object_constraints()
        self._check_at_least_one_property(['description', 'external_id', 'url'])


class KillChainPhase(_STIXBase20):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part1-stix-core/stix-v2.0-cs01-part1-stix-core.html#_Toc496709267>`__.
    """

    _properties = OrderedDict([
        ('kill_chain_name', StringProperty(required=True)),
        ('phase_name', StringProperty(required=True)),
    ])


class GranularMarking(_STIXBase20):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part1-stix-core/stix-v2.0-cs01-part1-stix-core.html#_Toc496709290>`__.
    """

    _properties = OrderedDict([
        ('marking_ref', ReferenceProperty(valid_types='marking-definition', spec_version='2.0', required=True)),
        ('selectors', ListProperty(SelectorProperty, required=True)),
    ])


class TLPMarking(_STIXBase20):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part1-stix-core/stix-v2.0-cs01-part1-stix-core.html#_Toc496709287>`__.
    """

    _type = 'tlp'
    _properties = OrderedDict([
        ('tlp', StringProperty(required=True)),
    ])


class StatementMarking(_STIXBase20):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part1-stix-core/stix-v2.0-cs01-part1-stix-core.html#_Toc496709286>`__.
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


class MarkingDefinition(_STIXBase20, _MarkingsMixin):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part1-stix-core/stix-v2.0-cs01-part1-stix-core.html#_Toc496709284>`__.
    """

    _type = 'marking-definition'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('id', IDProperty(_type, spec_version='2.0')),
        ('created_by_ref', ReferenceProperty(valid_types='identity', spec_version='2.0')),
        ('created', TimestampProperty(default=lambda: NOW)),
        ('definition_type', StringProperty(required=True)),
        ('definition', MarkingProperty(required=True)),
        ('external_references', ListProperty(ExternalReference)),
        ('object_marking_refs', ListProperty(ReferenceProperty(valid_types='marking-definition', spec_version='2.0'))),
        ('granular_markings', ListProperty(GranularMarking)),
    ])

    def __init__(self, **kwargs):
        if {'definition_type', 'definition'}.issubset(kwargs.keys()):
            # Create correct marking type object
            try:
                marking_type = OBJ_MAP_MARKING[kwargs['definition_type']]
            except KeyError:
                raise ValueError("definition_type must be a valid marking type")

            if 'created' in kwargs:
                if _should_set_millisecond(kwargs['created'], marking_type):
                    self._properties = copy.deepcopy(self._properties)
                    self._properties.update([
                        ('created', TimestampProperty(default=lambda: NOW, precision='millisecond')),
                    ])

            if not isinstance(kwargs['definition'], marking_type):
                defn = _get_dict(kwargs['definition'])
                kwargs['definition'] = marking_type(**defn)

        super(MarkingDefinition, self).__init__(**kwargs)

    def _check_object_constraints(self):
        super(MarkingDefinition, self)._check_object_constraints()
        check_tlp_marking(self, '2.0')

    def serialize(self, pretty=False, include_optional_defaults=False, **kwargs):
        check_tlp_marking(self, '2.0')
        return super(MarkingDefinition, self).serialize(pretty, include_optional_defaults, **kwargs)


OBJ_MAP_MARKING = {
    'tlp': TLPMarking,
    'statement': StatementMarking,
}


def CustomMarking(type='x-custom-marking', properties=None):
    """Custom STIX Marking decorator.

    Example:
        >>> from stix2 import CustomMarking
        >>> from stix2.properties import IntegerProperty, StringProperty
        >>> @CustomMarking('x-custom-marking', [
        ...     ('property1', StringProperty(required=True)),
        ...     ('property2', IntegerProperty()),
        ... ])
        ... class MyNewMarkingObjectType():
        ...     pass

    """
    def wrapper(cls):
        return _custom_marking_builder(cls, type, properties, '2.0', _STIXBase20)
    return wrapper


# TODO: don't allow the creation of any other TLPMarkings than the ones below

TLP_WHITE = MarkingDefinition(
    id='marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9',
    created='2017-01-20T00:00:00.000Z',
    definition_type='tlp',
    definition=TLPMarking(tlp='white'),
)

TLP_GREEN = MarkingDefinition(
    id='marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da',
    created='2017-01-20T00:00:00.000Z',
    definition_type='tlp',
    definition=TLPMarking(tlp='green'),
)

TLP_AMBER = MarkingDefinition(
    id='marking-definition--f88d31f6-486f-44da-b317-01333bde0b82',
    created='2017-01-20T00:00:00.000Z',
    definition_type='tlp',
    definition=TLPMarking(tlp='amber'),
)

TLP_RED = MarkingDefinition(
    id='marking-definition--5e57c739-391a-4eb3-b6be-7d15ca92d5ed',
    created='2017-01-20T00:00:00.000Z',
    definition_type='tlp',
    definition=TLPMarking(tlp='red'),
)
