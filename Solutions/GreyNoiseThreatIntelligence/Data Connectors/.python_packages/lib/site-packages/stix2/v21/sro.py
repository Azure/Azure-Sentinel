"""STIX 2.1 Relationship Objects."""

from collections import OrderedDict

from ..properties import (
    BooleanProperty, ExtensionsProperty, IDProperty, IntegerProperty,
    ListProperty, ReferenceProperty, StringProperty, TimestampProperty,
    TypeProperty,
)
from ..utils import NOW
from .base import _RelationshipObject
from .common import ExternalReference, GranularMarking


class Relationship(_RelationshipObject):
    """For more detailed information on this object's properties, see
    `the STIX 2.1 specification <https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html#_e2e1szrqfoan>`__.
    """

    _invalid_source_target_types = ['bundle', 'language-content', 'marking-definition', 'relationship', 'sighting']

    _type = 'relationship'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.1')),
        ('spec_version', StringProperty(fixed='2.1')),
        ('id', IDProperty(_type, spec_version='2.1')),
        ('created_by_ref', ReferenceProperty(valid_types='identity', spec_version='2.1')),
        ('created', TimestampProperty(default=lambda: NOW, precision='millisecond', precision_constraint='min')),
        ('modified', TimestampProperty(default=lambda: NOW, precision='millisecond', precision_constraint='min')),
        ('relationship_type', StringProperty(required=True)),
        ('description', StringProperty()),
        ('source_ref', ReferenceProperty(invalid_types=_invalid_source_target_types, spec_version='2.1', required=True)),
        ('target_ref', ReferenceProperty(invalid_types=_invalid_source_target_types, spec_version='2.1', required=True)),
        ('start_time', TimestampProperty()),
        ('stop_time', TimestampProperty()),
        ('revoked', BooleanProperty(default=lambda: False)),
        ('labels', ListProperty(StringProperty)),
        ('confidence', IntegerProperty()),
        ('lang', StringProperty()),
        ('external_references', ListProperty(ExternalReference)),
        ('object_marking_refs', ListProperty(ReferenceProperty(valid_types='marking-definition', spec_version='2.1'))),
        ('granular_markings', ListProperty(GranularMarking)),
        ('extensions', ExtensionsProperty(spec_version='2.1')),
    ])

    # Explicitly define the first three kwargs to make readable Relationship declarations.
    def __init__(
        self, source_ref=None, relationship_type=None,
        target_ref=None, **kwargs
    ):
        # Allow (source_ref, relationship_type, target_ref) as positional args.
        if source_ref and not kwargs.get('source_ref'):
            kwargs['source_ref'] = source_ref
        if relationship_type and not kwargs.get('relationship_type'):
            kwargs['relationship_type'] = relationship_type
        if target_ref and not kwargs.get('target_ref'):
            kwargs['target_ref'] = target_ref

        super(Relationship, self).__init__(**kwargs)

    def _check_object_constraints(self):
        super(self.__class__, self)._check_object_constraints()

        start_time = self.get('start_time')
        stop_time = self.get('stop_time')

        if start_time and stop_time and stop_time <= start_time:
            msg = "{0.id} 'stop_time' must be later than 'start_time'"
            raise ValueError(msg.format(self))


class Sighting(_RelationshipObject):
    """For more detailed information on this object's properties, see
    `the STIX 2.1 specification <https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html#_a795guqsap3r>`__.
    """

    _type = 'sighting'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.1')),
        ('spec_version', StringProperty(fixed='2.1')),
        ('id', IDProperty(_type, spec_version='2.1')),
        ('created_by_ref', ReferenceProperty(valid_types='identity', spec_version='2.1')),
        ('created', TimestampProperty(default=lambda: NOW, precision='millisecond', precision_constraint='min')),
        ('modified', TimestampProperty(default=lambda: NOW, precision='millisecond', precision_constraint='min')),
        ('description', StringProperty()),
        ('first_seen', TimestampProperty()),
        ('last_seen', TimestampProperty()),
        ('count', IntegerProperty(min=0, max=999999999)),
        ('sighting_of_ref', ReferenceProperty(valid_types="SDO", spec_version='2.1', required=True)),
        ('observed_data_refs', ListProperty(ReferenceProperty(valid_types='observed-data', spec_version='2.1'))),
        ('where_sighted_refs', ListProperty(ReferenceProperty(valid_types=['identity', 'location'], spec_version='2.1'))),
        ('summary', BooleanProperty(default=lambda: False)),
        ('revoked', BooleanProperty(default=lambda: False)),
        ('labels', ListProperty(StringProperty)),
        ('confidence', IntegerProperty()),
        ('lang', StringProperty()),
        ('external_references', ListProperty(ExternalReference)),
        ('object_marking_refs', ListProperty(ReferenceProperty(valid_types='marking-definition', spec_version='2.1'))),
        ('granular_markings', ListProperty(GranularMarking)),
        ('extensions', ExtensionsProperty(spec_version='2.1')),
    ])

    # Explicitly define the first kwargs to make readable Sighting declarations.
    def __init__(self, sighting_of_ref=None, **kwargs):
        # Allow sighting_of_ref as a positional arg.
        if sighting_of_ref and not kwargs.get('sighting_of_ref'):
            kwargs['sighting_of_ref'] = sighting_of_ref

        super(Sighting, self).__init__(**kwargs)

    def _check_object_constraints(self):
        super(self.__class__, self)._check_object_constraints()

        first_seen = self.get('first_seen')
        last_seen = self.get('last_seen')

        if first_seen and last_seen and last_seen < first_seen:
            msg = "{0.id} 'last_seen' must be greater than or equal to 'first_seen'"
            raise ValueError(msg.format(self))
