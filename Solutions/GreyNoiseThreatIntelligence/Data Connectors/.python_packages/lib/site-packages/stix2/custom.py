from collections import OrderedDict

from .base import _cls_init
from .properties import EnumProperty
from .registration import (
    _register_extension, _register_marking, _register_object,
    _register_observable,
)
from .registry import class_for_type


def _get_properties_dict(properties):
    try:
        return OrderedDict(properties)
    except TypeError as e:
        raise ValueError(
            "properties must be dict-like, e.g. a list "
            "containing tuples.  For example, "
            "[('property1', IntegerProperty())]",
        ) from e


def _custom_object_builder(cls, type, properties, version, base_class):
    prop_dict = _get_properties_dict(properties)

    class _CustomObject(cls, base_class):

        _type = type
        _properties = prop_dict

        def __init__(self, **kwargs):
            base_class.__init__(self, **kwargs)
            _cls_init(cls, self, kwargs)
            ext = getattr(self, 'with_extension', None)
            if ext and version != '2.0':
                if 'extensions' not in self._inner:
                    self._inner['extensions'] = {}
                self._inner['extensions'][ext] = class_for_type(ext, version, "extensions")()

    _CustomObject.__name__ = cls.__name__

    _register_object(_CustomObject, version=version)
    return _CustomObject


def _custom_marking_builder(cls, type, properties, version, base_class):
    prop_dict = _get_properties_dict(properties)

    class _CustomMarking(cls, base_class):

        _type = type
        _properties = prop_dict

        def __init__(self, **kwargs):
            base_class.__init__(self, **kwargs)
            _cls_init(cls, self, kwargs)

    _CustomMarking.__name__ = cls.__name__

    _register_marking(_CustomMarking, version=version)
    return _CustomMarking


def _custom_observable_builder(cls, type, properties, version, base_class, id_contrib_props=None):
    if id_contrib_props is None:
        id_contrib_props = []

    prop_dict = _get_properties_dict(properties)

    class _CustomObservable(cls, base_class):

        _type = type
        _properties = prop_dict
        if version != '2.0':
            _id_contributing_properties = id_contrib_props

        def __init__(self, **kwargs):
            base_class.__init__(self, **kwargs)
            _cls_init(cls, self, kwargs)
            ext = getattr(self, 'with_extension', None)
            if ext and version != '2.0':
                if 'extensions' not in self._inner:
                    self._inner['extensions'] = {}
                self._inner['extensions'][ext] = class_for_type(ext, version, "extensions")()

    _CustomObservable.__name__ = cls.__name__

    _register_observable(_CustomObservable, version=version)
    return _CustomObservable


def _custom_extension_builder(cls, type, properties, version, base_class):

    properties = _get_properties_dict(properties)
    toplevel_properties = None

    # Auto-create an "extension_type" property from the class attribute, if
    # it exists.  How to treat the other properties which were given depends on
    # the extension type.
    extension_type = getattr(cls, "extension_type", None)
    if extension_type:
        # I suppose I could also go with a plain string property, since the
        # value is fixed... but an enum property seems more true to the
        # property's semantics.  Also, I can't import a vocab module for the
        # enum values without circular import errors. :(
        extension_type_prop = EnumProperty(
            [
                "new-sdo", "new-sco", "new-sro", "property-extension",
                "toplevel-property-extension",
            ],
            required=False,
            fixed=extension_type,
        )

        nested_properties = {
            "extension_type": extension_type_prop,
        }

        if extension_type == "toplevel-property-extension":
            toplevel_properties = properties
        else:
            nested_properties.update(properties)

    else:
        nested_properties = properties

    class _CustomExtension(cls, base_class):

        _type = type
        _properties = nested_properties
        if extension_type == "toplevel-property-extension":
            _toplevel_properties = toplevel_properties

        def __init__(self, **kwargs):
            base_class.__init__(self, **kwargs)
            _cls_init(cls, self, kwargs)

    _CustomExtension.__name__ = cls.__name__

    _register_extension(_CustomExtension, version=version)
    return _CustomExtension
