"""Filters for Python STIX2 DataSources, DataSinks, DataStores"""

import collections
from datetime import datetime

import stix2.utils

"""Supported filter operations"""
FILTER_OPS = ['=', '!=', 'in', '>', '<', '>=', '<=', 'contains']

"""Supported filter value types"""
FILTER_VALUE_TYPES = (
    bool, dict, float, int, list, tuple, str, datetime,
)


def _check_filter_components(prop, op, value):
    """Check that filter meets minimum validity.

    Note:
        Currently can create Filters that are not valid STIX2 object common
        properties, as filter.prop value is not checked, only filter.op,
        filter value are checked here. They are just ignored when applied
        within the DataSource API. For example, a user can add a TAXII Filter,
        that is extracted and sent to a TAXII endpoint within TAXIICollection
        and not applied locally (within this API).

    """
    if op not in FILTER_OPS:
        # check filter operator is supported
        raise ValueError("Filter operator '%s' not supported for specified property: '%s'" % (op, prop))

    if not isinstance(value, FILTER_VALUE_TYPES):
        # check filter value type is supported
        raise TypeError("Filter value of '%s' is not supported. The type must be a Python immutable type or dictionary" % type(value))

    if prop == 'type' and '_' in value:
        # check filter where the property is type, value (type name) cannot have underscores
        raise ValueError("Filter for property 'type' cannot have its value '%s' include underscores" % value)

    return True


class Filter(collections.namedtuple('Filter', ['property', 'op', 'value'])):
    """STIX 2 filters that support the querying functionality of STIX 2
    DataStores and DataSources.

    Initialized like a Python tuple.

    Args:
        property (str): filter property name, corresponds to STIX 2 object property
        op (str): operator of the filter
        value (str): filter property value

    Example:
        Filter("id", "=", "malware--0f862b01-99da-47cc-9bdb-db4a86a95bb1")

    """
    __slots__ = ()

    def __new__(cls, prop, op, value):
        # If value is a list, convert it to a tuple so it is hashable.
        if isinstance(value, list):
            value = tuple(value)

        _check_filter_components(prop, op, value)

        self = super(Filter, cls).__new__(cls, prop, op, value)
        return self

    def _check_property(self, stix_obj_property):
        """Check a property of a STIX Object against this filter.

        Args:
            stix_obj_property: value to check this filter against

        Returns:
            True if property matches the filter,
            False otherwise.
        """
        # If filtering on a timestamp property and the filter value is a string,
        # try to convert the filter value to a datetime instance.
        if isinstance(stix_obj_property, datetime) and \
                isinstance(self.value, str):
            filter_value = stix2.utils.parse_into_datetime(self.value)
        else:
            filter_value = self.value

        if self.op == "=":
            return stix_obj_property == filter_value
        elif self.op == "!=":
            return stix_obj_property != filter_value
        elif self.op == "in":
            return stix_obj_property in filter_value
        elif self.op == "contains":
            if isinstance(filter_value, dict):
                return filter_value in stix_obj_property.values()
            else:
                return filter_value in stix_obj_property
        elif self.op == ">":
            return stix_obj_property > filter_value
        elif self.op == "<":
            return stix_obj_property < filter_value
        elif self.op == ">=":
            return stix_obj_property >= filter_value
        elif self.op == "<=":
            return stix_obj_property <= filter_value
        else:
            raise ValueError("Filter operator: {0} not supported for specified property: {1}".format(self.op, self.property))


def apply_common_filters(stix_objs, query):
    """Evaluate filters against a set of STIX 2.0 objects.

    Supports only STIX 2.0 common property properties.

    Args:
        stix_objs (iterable): iterable of STIX objects to apply the query to
        query (non-iterator iterable): iterable of filters.  Can't be an
            iterator (e.g. generator iterators won't work), since this is
            used in an inner loop of a nested loop.  So we require the ability
            to traverse the filters repeatedly.

    Yields:
        STIX objects that successfully evaluate against the query.

    """
    for stix_obj in stix_objs:
        clean = True
        for filter_ in query:
            match = _check_filter(filter_, stix_obj)

            if not match:
                clean = False
                break

        # if object unmarked after all filters, add it
        if clean:
            yield stix_obj


def _check_filter(filter_, stix_obj):
    """Evaluate a single filter against a single STIX 2.0 object.

    Args:
        filter_ (Filter): filter to match against
        stix_obj: STIX object to apply the filter to

    Returns:
        True if the stix_obj matches the filter,
        False if not.

    """
    # For properties like granular_markings and external_references
    # need to extract the first property from the string.
    prop = filter_.property.split('.')[0]

    if prop not in stix_obj.keys():
        # check filter "property" is in STIX object - if cant be
        # applied to STIX object, STIX object is discarded
        # (i.e. did not make it through the filter)
        return False

    if '.' in filter_.property:
        # Check embedded properties, from e.g. granular_markings or external_references
        sub_property = filter_.property.split('.', 1)[1]
        sub_filter = filter_._replace(property=sub_property)

        if isinstance(stix_obj[prop], list):
            for elem in stix_obj[prop]:
                if _check_filter(sub_filter, elem) is True:
                    return True
            return False

        else:
            return _check_filter(sub_filter, stix_obj[prop])

    elif isinstance(stix_obj[prop], list):
        # Check each item in list property to see if it matches
        for elem in stix_obj[prop]:
            if filter_._check_property(elem) is True:
                return True
        return False

    else:
        # Check if property matches
        return filter_._check_property(stix_obj[prop])


class FilterSet(object):
    """Internal STIX2 class to facilitate the grouping of Filters
    into sets. The primary motivation for this class came from the problem
    that Filters that had a dict as a value could not be added to a Python
    set as dicts are not hashable. Thus this class provides set functionality
    but internally stores filters in a list.
    """

    def __init__(self, filters=None):
        """
        Args:
            filters: see FilterSet.add()
        """
        self._filters = []
        if filters:
            self.add(filters)

    def __iter__(self):
        """Provide iteration functionality of FilterSet."""
        for f in self._filters:
            yield f

    def __len__(self):
        """Provide built-in len() utility of FilterSet."""
        return len(self._filters)

    def add(self, filters=None):
        """Add a Filter, FilterSet, or list of Filters to the FilterSet.

        Operates like set, only adding unique stix2.Filters to the FilterSet

        Note:
            method designed to be very accomodating (i.e. even accepting filters=None)
            as it allows for blind calls (very useful in DataStore)

        Args:
            filters: stix2.Filter OR list of stix2.Filter OR stix2.FilterSet

        """
        if not filters:
            # so add() can be called blindly, useful for
            # DataStore/Environment usage of filter operations
            return

        if not isinstance(filters, (FilterSet, list)):
            filters = [filters]

        for f in filters:
            if f not in self._filters:
                self._filters.append(f)

    def remove(self, filters=None):
        """Remove a Filter, list of Filters, or FilterSet from the FilterSet.

        Note:
            method designed to be very accomodating (i.e. even accepting filters=None)
            as it allows for blind calls (very useful in DataStore)

        Args:
            filters: stix2.Filter OR list of stix2.Filter or stix2.FilterSet

        """
        if not filters:
            # so remove() can be called blindly, useful for
            # DataStore/Environemnt usage of filter ops
            return

        if not isinstance(filters, (FilterSet, list)):
            filters = [filters]

        for f in filters:
            self._filters.remove(f)
