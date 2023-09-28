"""STIX 2.0 Relationship Objects."""

from collections import OrderedDict

from ..properties import (
    BooleanProperty, IDProperty, IntegerProperty, ListProperty,
    ReferenceProperty, StringProperty, TimestampProperty, TypeProperty,
)
from ..utils import NOW
from .base import _RelationshipObject
from .common import ExternalReference, GranularMarking


class Relationship(_RelationshipObject):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part2-stix-objects/stix-v2.0-cs01-part2-stix-objects.html#_Toc496714340>`__.
    """

    _invalid_source_target_types = ['bundle', 'language-content', 'marking-definition', 'relationship', 'sighting']

    _type = 'relationship'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('id', IDProperty(_type, spec_version='2.0')),
        ('created_by_ref', ReferenceProperty(valid_types='identity', spec_version='2.0')),
        ('created', TimestampProperty(default=lambda: NOW, precision='millisecond')),
        ('modified', TimestampProperty(default=lambda: NOW, precision='millisecond')),
        ('relationship_type', StringProperty(required=True)),
        ('description', StringProperty()),
        ('source_ref', ReferenceProperty(invalid_types=_invalid_source_target_types, spec_version='2.0', required=True)),
        ('target_ref', ReferenceProperty(invalid_types=_invalid_source_target_types, spec_version='2.0', required=True)),
        ('revoked', BooleanProperty(default=lambda: False)),
        ('labels', ListProperty(StringProperty)),
        ('external_references', ListProperty(ExternalReference)),
        ('object_marking_refs', ListProperty(ReferenceProperty(valid_types='marking-definition', spec_version='2.0'))),
        ('granular_markings', ListProperty(GranularMarking)),
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


class Sighting(_RelationshipObject):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part2-stix-objects/stix-v2.0-cs01-part2-stix-objects.html#_Toc496714343>`__.
    """

    _type = 'sighting'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('id', IDProperty(_type, spec_version='2.0')),
        ('created_by_ref', ReferenceProperty(valid_types='identity', spec_version='2.0')),
        ('created', TimestampProperty(default=lambda: NOW, precision='millisecond')),
        ('modified', TimestampProperty(default=lambda: NOW, precision='millisecond')),
        ('first_seen', TimestampProperty()),
        ('last_seen', TimestampProperty()),
        ('count', IntegerProperty(min=0, max=999999999)),
        ('sighting_of_ref', ReferenceProperty(valid_types="SDO", spec_version='2.0', required=True)),
        ('observed_data_refs', ListProperty(ReferenceProperty(valid_types='observed-data', spec_version='2.0'))),
        ('where_sighted_refs', ListProperty(ReferenceProperty(valid_types='identity', spec_version='2.0'))),
        ('summary', BooleanProperty(default=lambda: False)),
        ('revoked', BooleanProperty(default=lambda: False)),
        ('labels', ListProperty(StringProperty)),
        ('external_references', ListProperty(ExternalReference)),
        ('object_marking_refs', ListProperty(ReferenceProperty(valid_types='marking-definition', spec_version='2.0'))),
        ('granular_markings', ListProperty(GranularMarking)),
    ])

    # Explicitly define the first kwargs to make readable Sighting declarations.
    def __init__(self, sighting_of_ref=None, **kwargs):
        # Allow sighting_of_ref as a positional arg.
        if sighting_of_ref and not kwargs.get('sighting_of_ref'):
            kwargs['sighting_of_ref'] = sighting_of_ref

        super(Sighting, self).__init__(**kwargs)
