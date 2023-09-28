import importlib
import pkgutil
import re

# Collects information on which classes implement which STIX types, for the
# various STIX spec versions.
STIX2_OBJ_MAPS = {}


def _stix_vid_to_version(stix_vid):
    """
    Convert a python package name representing a STIX version in the form "vXX"
    to the dotted style used in the public APIs of this library, "X.X".

    :param stix_vid: A package name in the form "vXX"
    :return: A STIX version in dotted style
    """
    assert len(stix_vid) >= 3

    stix_version = stix_vid[1] + "." + stix_vid[2:]
    return stix_version


def _collect_stix2_mappings():
    """Navigate the package once and retrieve all object mapping dicts for each
    v2X package. Includes OBJ_MAP, OBJ_MAP_OBSERVABLE, EXT_MAP."""
    if not STIX2_OBJ_MAPS:
        top_level_module = importlib.import_module('stix2')
        path = top_level_module.__path__
        prefix = str(top_level_module.__name__) + '.'

        for module_loader, name, is_pkg in pkgutil.walk_packages(path=path, prefix=prefix):
            stix_vid = name.split('.')[1]
            if re.match(r'^stix2\.v2[0-9]$', name) and is_pkg:
                ver = _stix_vid_to_version(stix_vid)
                mod = importlib.import_module(name, str(top_level_module.__name__))
                STIX2_OBJ_MAPS[ver] = {}
                STIX2_OBJ_MAPS[ver]['objects'] = mod.OBJ_MAP
                STIX2_OBJ_MAPS[ver]['observables'] = mod.OBJ_MAP_OBSERVABLE
                STIX2_OBJ_MAPS[ver]['extensions'] = mod.EXT_MAP
            elif re.match(r'^stix2\.v2[0-9]\.common$', name) and is_pkg is False:
                ver = _stix_vid_to_version(stix_vid)
                mod = importlib.import_module(name, str(top_level_module.__name__))
                STIX2_OBJ_MAPS[ver]['markings'] = mod.OBJ_MAP_MARKING


def class_for_type(stix_type, stix_version, category=None):
    """
    Get the registered class which implements a particular STIX type for a
    particular STIX version.

    :param stix_type: A STIX type as a string, or for extension-definition
        style extensions, the STIX ID of the definition.
    :param stix_version: A STIX version as a string, e.g. "2.1"
    :param category: An optional "category" value, which is just used directly
        as a second key after the STIX version, and depends on how the types
        are internally categorized.  This would be useful if the same STIX type
        is used to mean two different things within the same STIX version.  So
        it's unlikely to be necessary.  Pass None to just search all the
        categories and return the first class found.
    :return: A registered python class which implements the given STIX type, or
        None if one is not found.
    """
    cls = None

    cat_map = STIX2_OBJ_MAPS.get(stix_version)
    if cat_map:
        if category:
            class_map = cat_map.get(category)
            if class_map:
                cls = class_map.get(stix_type)
        else:
            cls = (
                cat_map["objects"].get(stix_type) or
                cat_map["observables"].get(stix_type) or
                cat_map["markings"].get(stix_type) or
                cat_map["extensions"].get(stix_type)
            )

    return cls
