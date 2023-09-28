import re

from . import registry, version
from .base import _DomainObject
from .exceptions import DuplicateRegistrationError
from .properties import (
    ListProperty, ObjectReferenceProperty, ReferenceProperty, _validate_type,
)
from .utils import PREFIX_21_REGEX


def _validate_ref_props(props_map, is_observable20=False):
    """
    Validate that reference properties contain an expected type.

    Properties ending in "_ref/s" need to be instances of specific types to
    meet the specification requirements. For 2.0 and 2.1 conformance, these
    properties are expected to be implemented with `ReferenceProperty` (or a
    subclass thereof), except for the special case of STIX 2.0 observables
    which must be implemented with `ObjectReferenceProperty`.

    Args:
        props_map (mapping): A mapping of STIX object properties to be checked.
        is_observable20 (bool): Flag for the STIX 2.0 observables special case.

    Raises:
        ValueError: If the properties do not conform.
    """
    if is_observable20:
        ref_prop_type = ObjectReferenceProperty
    else:
        ref_prop_type = ReferenceProperty
    for prop_name, prop_obj in props_map.items():
        tail = prop_name.rsplit("_", 1)[-1]
        if tail == "ref" and not isinstance(prop_obj, ref_prop_type):
            raise ValueError(
                f"{prop_name!r} is named like a reference property but is not "
                f"a subclass of {ref_prop_type.__name__!r}.",
            )
        elif tail == "refs" and not (
            isinstance(prop_obj, ListProperty)
            and isinstance(prop_obj.contained, ref_prop_type)
        ):
            raise ValueError(
                f"{prop_name!r} is named like a reference list property but is not "
                f"a 'ListProperty' containing a subclass of {ref_prop_type.__name__!r}.",
            )


def _validate_props(props_map, version, **kwargs):
    """
    Validate that a map of properties is conformant for this STIX `version`.

    Args:
        props_map (mapping): A mapping of STIX object properties to be checked.
        version (str): Which STIX2 version the properties must confirm to.
        kwargs (mapping): Arguments to pass on to specific property validators.

    Raises:
        ValueError: If the properties do not conform.
    """
    # Confirm conformance with STIX 2.1+ requirements for property names
    if version != "2.0":
        for prop_name, prop_value in props_map.items():
            if not re.match(PREFIX_21_REGEX, prop_name):
                raise ValueError("Property name '%s' must begin with an alpha character." % prop_name)
    # Confirm conformance of reference properties
    _validate_ref_props(props_map, **kwargs)


def _register_object(new_type, version=version.DEFAULT_VERSION):
    """Register a custom STIX Object type.

    Args:
        new_type (class): A class to register in the Object map.
        version (str): Which STIX2 version to use. (e.g. "2.0", "2.1"). If
            None, use latest version.

    Raises:
        ValueError: If the class being registered wasn't created with the
            @CustomObject decorator.
        DuplicateRegistrationError: If the class has already been registered.

    """

    if not issubclass(new_type, _DomainObject):
        raise ValueError(
            "'%s' must be created with the @CustomObject decorator." %
            new_type.__name__,
        )

    if not version:
        version = version.DEFAULT_VERSION

    _validate_props(new_type._properties, version)

    OBJ_MAP = registry.STIX2_OBJ_MAPS[version]['objects']
    if new_type._type in OBJ_MAP.keys():
        raise DuplicateRegistrationError("STIX Object", new_type._type)
    OBJ_MAP[new_type._type] = new_type


def _register_marking(new_marking, version=version.DEFAULT_VERSION):
    """Register a custom STIX Marking Definition type.

    Args:
        new_marking (class): A class to register in the Marking map.
        version (str): Which STIX2 version to use. (e.g. "2.0", "2.1"). If
            None, use latest version.

    """
    if not version:
        version = version.DEFAULT_VERSION

    mark_type = new_marking._type
    _validate_type(mark_type, version)
    _validate_props(new_marking._properties, version)

    OBJ_MAP_MARKING = registry.STIX2_OBJ_MAPS[version]['markings']
    if mark_type in OBJ_MAP_MARKING.keys():
        raise DuplicateRegistrationError("STIX Marking", mark_type)
    OBJ_MAP_MARKING[mark_type] = new_marking


def _register_observable(new_observable, version=version.DEFAULT_VERSION):
    """Register a custom STIX Cyber Observable type.

    Args:
        new_observable (class): A class to register in the Observables map.
        version (str): Which STIX2 version to use. (e.g. "2.0", "2.1"). If
            None, use latest version.

    """
    if not version:
        version = version.DEFAULT_VERSION

    _validate_props(
        new_observable._properties, version,
        is_observable20=(version == "2.0"),
    )

    OBJ_MAP_OBSERVABLE = registry.STIX2_OBJ_MAPS[version]['observables']
    if new_observable._type in OBJ_MAP_OBSERVABLE.keys():
        raise DuplicateRegistrationError("Cyber Observable", new_observable._type)
    OBJ_MAP_OBSERVABLE[new_observable._type] = new_observable


def _register_extension(
    new_extension, version=version.DEFAULT_VERSION,
):
    """Register a custom extension to any STIX Object type.

    Args:
        new_extension (class): A class to register in the Extensions map.
        version (str): Which STIX2 version to use. (e.g. "2.0", "2.1").
            Defaults to the latest supported version.

    """
    ext_type = new_extension._type

    _validate_type(ext_type, version)
    if version == "2.1":
        if not (ext_type.endswith('-ext') or ext_type.startswith('extension-definition--')):
            raise ValueError(
                "Invalid extension type name '%s': must end with '-ext' or start with 'extension-definition--<UUID>'." %
                ext_type,
            )

    tl_props = getattr(new_extension, "_toplevel_properties", None)
    if any((
        # There must always be at least one property in an extension. This
        # holds for instances of both custom object extensions which must
        # contain one or more custom properties, and `extension-definition`s
        # which must contain an `extension_type` property.
        not new_extension._properties,
        # If a top-level properties mapping is provided, it cannot be empty
        tl_props is not None and not tl_props,
    )):
        raise ValueError(
            "Invalid extension: must define at least one property: " +
            ext_type,
        )
    # We need to validate all properties related to this extension
    combined_props = dict(new_extension._properties, **(tl_props or dict()))
    _validate_props(combined_props, version)

    EXT_MAP = registry.STIX2_OBJ_MAPS[version]['extensions']

    if ext_type in EXT_MAP:
        raise DuplicateRegistrationError("Extension", ext_type)
    EXT_MAP[ext_type] = new_extension
