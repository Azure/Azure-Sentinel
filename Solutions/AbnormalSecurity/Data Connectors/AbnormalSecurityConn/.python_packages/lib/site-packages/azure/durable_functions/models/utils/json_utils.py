from typing import Dict, Any

from ...constants import DATETIME_STRING_FORMAT


def add_attrib(json_dict: Dict[str, Any], object_,
               attribute_name: str, alt_name: str = None):
    """Add the value of the attribute from the object to the dictionary.

    Used to dynamically add the value of the attribute if the value is present.

    Parameters
    ----------
    json_dict: The dictionary to add the attribute to
    object_: The object to look for the attribute on
    attribute_name: The name of the attribute to look for
    alt_name: An alternate name to provide to the attribute in the in the dictionary
    """
    if hasattr(object_, attribute_name):
        json_dict[alt_name or attribute_name] = \
            getattr(object_, attribute_name)


def add_datetime_attrib(json_dict: Dict[str, Any], object_,
                        attribute_name: str, alt_name: str = None):
    """Add the value of the attribute from the object to the dictionary converted into a string.

    Parameters
    ----------
    json_dict: The dictionary to add the attribute to
    object_: The object to look for the attribute on
    attribute_name: The name of the attribute to look for
    alt_name: An alternate name to provide to the attribute in the in the dictionary
    """
    if hasattr(object_, attribute_name):
        json_dict[alt_name or attribute_name] = \
            getattr(object_, attribute_name).strftime(DATETIME_STRING_FORMAT)


def add_json_attrib(json_dict: Dict[str, Any], object_,
                    attribute_name: str, alt_name: str = None):
    """Add the results of the to_json() function call of the attribute from the object to the dict.

    Used to dynamically add the JSON converted value of the attribute if the value is present.

    Parameters
    ----------
    json_dict: The dictionary to add the attribute to
    object_: The object to look for the attribute on
    attribute_name: The name of the attribute to look for
    alt_name: An alternate name to provide to the attribute in the in the dictionary
    """
    if hasattr(object_, attribute_name):
        attribute_value = getattr(object_, attribute_name)
        if attribute_value:
            json_dict[alt_name or attribute_name] = attribute_value.to_json()
