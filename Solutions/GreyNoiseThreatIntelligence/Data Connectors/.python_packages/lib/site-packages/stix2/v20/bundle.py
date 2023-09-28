"""STIX 2.0 Bundle Representation."""

from collections import OrderedDict

from ..properties import (
    IDProperty, ListProperty, STIXObjectProperty, StringProperty, TypeProperty,
)
from .base import _STIXBase20


class Bundle(_STIXBase20):
    """For more detailed information on this object's properties, see
    `the STIX 2.0 specification <http://docs.oasis-open.org/cti/stix/v2.0/cs01/part1-stix-core/stix-v2.0-cs01-part1-stix-core.html#_Toc496709293>`__.
    """

    _type = 'bundle'
    _properties = OrderedDict([
        ('type', TypeProperty(_type, spec_version='2.0')),
        ('id', IDProperty(_type, spec_version='2.0')),
        # Not technically correct: STIX 2.0 spec doesn't say spec_version must
        # have this value, but it's all we support for now.
        ('spec_version', StringProperty(fixed='2.0')),
        ('objects', ListProperty(STIXObjectProperty(spec_version='2.0'))),
    ])

    def __init__(self, *args, **kwargs):
        # Add any positional arguments to the 'objects' kwarg.
        if args:
            obj_list = []
            for arg in args:
                if isinstance(arg, list):
                    obj_list = obj_list + arg
                else:
                    obj_list.append(arg)

            kwargs['objects'] = obj_list + kwargs.get('objects', [])

        super(Bundle, self).__init__(**kwargs)

    def get_obj(self, obj_uuid):
        if "objects" in self._inner:
            found_objs = [elem for elem in self.objects if elem['id'] == obj_uuid]
            if found_objs == []:
                raise KeyError("'%s' does not match the id property of any of the bundle's objects" % obj_uuid)
            return found_objs
        else:
            raise KeyError("There are no objects in this empty bundle")

    def __getitem__(self, key):
        try:
            return super(Bundle, self).__getitem__(key)
        except KeyError:
            try:
                return self.get_obj(key)
            except KeyError:
                raise KeyError("'%s' is neither a property on the bundle nor does it match the id property of any of the bundle's objects" % key)
