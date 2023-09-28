"""Python STIX2 TAXIICollection Source/Sink"""

from requests.exceptions import HTTPError

from stix2 import v20, v21
from stix2.base import _STIXBase
from stix2.datastore import (
    DataSink, DataSource, DataSourceError, DataStoreMixin,
)
from stix2.datastore.filters import Filter, FilterSet, apply_common_filters
from stix2.parsing import parse
from stix2.utils import deduplicate

try:
    from taxii2client import v20 as tcv20
    from taxii2client import v21 as tcv21
    from taxii2client.exceptions import ValidationError
    _taxii2_client = True
except ImportError:
    _taxii2_client = False


TAXII_FILTERS = ['added_after', 'id', 'type', 'version']


class TAXIICollectionStore(DataStoreMixin):
    """Provides an interface to a local/remote TAXII Collection
    of STIX data. TAXIICollectionStore is a wrapper
    around a paired TAXIICollectionSink and TAXIICollectionSource.

    Args:
        collection (taxii2.Collection): TAXII Collection instance
        allow_custom (bool): whether to allow custom STIX content to be
            pushed/retrieved. Defaults to True for TAXIICollectionSource
            side(retrieving data) and False for TAXIICollectionSink
            side(pushing data). However, when parameter is supplied, it will
            be applied to both TAXIICollectionSource/Sink.
        items_per_page (int): How many STIX objects to request per call
            to TAXII Server. The value can be tuned, but servers may override
            if their internal limit is surpassed. Used by TAXIICollectionSource

    """
    def __init__(self, collection, allow_custom=None, items_per_page=5000):
        if allow_custom is None:
            allow_custom_source = True
            allow_custom_sink = False
        else:
            allow_custom_sink = allow_custom_source = allow_custom

        super(TAXIICollectionStore, self).__init__(
            source=TAXIICollectionSource(collection, allow_custom=allow_custom_source, items_per_page=items_per_page),
            sink=TAXIICollectionSink(collection, allow_custom=allow_custom_sink),
        )


class TAXIICollectionSink(DataSink):
    """Provides an interface for pushing STIX objects to a local/remote
    TAXII Collection endpoint.

    Args:
        collection (taxii2.Collection): TAXII2 Collection instance
        allow_custom (bool): Whether to allow custom STIX content to be
            added to the TAXIICollectionSink. Default: False

    """
    def __init__(self, collection, allow_custom=False):
        super(TAXIICollectionSink, self).__init__()
        if not _taxii2_client:
            raise ImportError("taxii2client library is required for usage of TAXIICollectionSink")

        try:
            if collection.can_write:
                self.collection = collection
            else:
                raise DataSourceError(
                    "The TAXII Collection object provided does not have write access"
                    " to the underlying linked Collection resource",
                )

        except (HTTPError, ValidationError) as e:
            raise DataSourceError(
                "The underlying TAXII Collection resource defined in the supplied TAXII"
                " Collection object provided could not be reached. Receved error:", e,
            )

        self.allow_custom = allow_custom

    def add(self, stix_data, version=None):
        """Add/push STIX content to TAXII Collection endpoint

        Args:
            stix_data (STIX object OR dict OR str OR list): valid STIX2
                content in a STIX object (or Bundle), STIX object dict (or
                Bundle dict), or a STIX2 json encoded string, or list of
                any of the following.
            version (str): If present, it forces the parser to use the version
                provided. Otherwise, the library will make the best effort based
                on checking the "spec_version" property.

        """
        if isinstance(stix_data, _STIXBase):
            # adding python STIX object
            if stix_data['type'] == 'bundle':
                bundle = stix_data.serialize(encoding='utf-8', ensure_ascii=False)
            elif 'spec_version' in stix_data:
                # If the spec_version is present, use new Bundle object...
                bundle = v21.Bundle(stix_data, allow_custom=self.allow_custom).serialize(encoding='utf-8', ensure_ascii=False)
            else:
                bundle = v20.Bundle(stix_data, allow_custom=self.allow_custom).serialize(encoding='utf-8', ensure_ascii=False)

        elif isinstance(stix_data, dict):
            # adding python dict (of either Bundle or STIX obj)
            if stix_data['type'] == 'bundle':
                bundle = parse(stix_data, allow_custom=self.allow_custom, version=version).serialize(encoding='utf-8', ensure_ascii=False)
            elif 'spec_version' in stix_data:
                # If the spec_version is present, use new Bundle object...
                bundle = v21.Bundle(stix_data, allow_custom=self.allow_custom).serialize(encoding='utf-8', ensure_ascii=False)
            else:
                bundle = v20.Bundle(stix_data, allow_custom=self.allow_custom).serialize(encoding='utf-8', ensure_ascii=False)

        elif isinstance(stix_data, list):
            # adding list of something - recurse on each
            for obj in stix_data:
                self.add(obj, version=version)
            return

        elif isinstance(stix_data, str):
            # adding json encoded string of STIX content
            stix_data = parse(stix_data, allow_custom=self.allow_custom, version=version)
            if stix_data['type'] == 'bundle':
                bundle = stix_data.serialize(encoding='utf-8', ensure_ascii=False)
            elif 'spec_version' in stix_data:
                # If the spec_version is present, use new Bundle object...
                bundle = v21.Bundle(stix_data, allow_custom=self.allow_custom).serialize(encoding='utf-8', ensure_ascii=False)
            else:
                bundle = v20.Bundle(stix_data, allow_custom=self.allow_custom).serialize(encoding='utf-8', ensure_ascii=False)

        else:
            raise TypeError("stix_data must be as STIX object(or list of),json formatted STIX (or list of), or a json formatted STIX bundle")

        self.collection.add_objects(bundle)


class TAXIICollectionSource(DataSource):
    """Provides an interface for searching/retrieving STIX objects
    from a local/remote TAXII Collection endpoint.

    Args:
        collection (taxii2.Collection): TAXII Collection instance
        allow_custom (bool): Whether to allow custom STIX content to be
            added to the FileSystemSink. Default: True
        items_per_page (int): How many STIX objects to request per call
            to TAXII Server. The value can be tuned, but servers may override
            if their internal limit is surpassed.

    """
    def __init__(self, collection, allow_custom=True, items_per_page=5000):
        super(TAXIICollectionSource, self).__init__()
        if not _taxii2_client:
            raise ImportError("taxii2client library is required for usage of TAXIICollectionSource")

        try:
            if collection.can_read:
                self.collection = collection
            else:
                raise DataSourceError(
                    "The TAXII Collection object provided does not have read access"
                    " to the underlying linked Collection resource",
                )

        except (HTTPError, ValidationError) as e:
            raise DataSourceError(
                "The underlying TAXII Collection resource defined in the supplied TAXII"
                " Collection object provided could not be reached. Recieved error:", e,
            )

        self.allow_custom = allow_custom
        self.items_per_page = items_per_page

    def get(self, stix_id, version=None, _composite_filters=None):
        """Retrieve STIX object from local/remote STIX Collection
        endpoint.

        Args:
            stix_id (str): The STIX ID of the STIX object to be retrieved.
            version (str): If present, it forces the parser to use the version
                provided. Otherwise, the library will make the best effort based
                on checking the "spec_version" property.
            _composite_filters (FilterSet): collection of filters passed from
                the parent CompositeDataSource, not user supplied

        Returns:
            (STIX object): STIX object that has the supplied STIX ID.
                The STIX object is received from TAXII has dict, parsed into
                a python STIX object and then returned

        """
        # combine all query filters
        query = FilterSet()

        if self.filters:
            query.add(self.filters)
        if _composite_filters:
            query.add(_composite_filters)

        # don't extract TAXII filters from query (to send to TAXII endpoint)
        # as directly retrieving a STIX object by ID
        try:
            stix_objs = self.collection.get_object(stix_id)['objects']
            stix_obj = list(apply_common_filters(stix_objs, query))

        except HTTPError as e:
            if e.response.status_code == 404:
                # if resource not found or access is denied from TAXII server,
                # return None
                stix_obj = []
            else:
                raise DataSourceError("TAXII Collection resource returned error", e)

        if len(stix_obj):
            stix_obj = parse(stix_obj[0], allow_custom=self.allow_custom, version=version)
            if stix_obj['id'] != stix_id:
                # check - was added to handle erroneous TAXII servers
                stix_obj = None
        else:
            stix_obj = None

        return stix_obj

    def all_versions(self, stix_id, version=None, _composite_filters=None):
        """Retrieve STIX object from local/remote TAXII Collection
        endpoint, all versions of it

        Args:
            stix_id (str): The STIX ID of the STIX objects to be retrieved.
            version (str): If present, it forces the parser to use the version
                provided. Otherwise, the library will make the best effort based
                on checking the "spec_version" property.
            _composite_filters (FilterSet): collection of filters passed from the parent
                CompositeDataSource, not user supplied

        Returns:
            (see query() as all_versions() is just a wrapper)

        """
        # make query in TAXII query format since 'id' is TAXII field
        query = [
            Filter('id', '=', stix_id),
            Filter('version', '=', 'all'),
        ]

        all_data = self.query(query=query, _composite_filters=_composite_filters)

        # parse STIX objects from TAXII returned json
        all_data = [parse(stix_obj, allow_custom=self.allow_custom, version=version) for stix_obj in all_data]

        # check - was added to handle erroneous TAXII servers
        all_data_clean = [stix_obj for stix_obj in all_data if stix_obj['id'] == stix_id]

        return all_data_clean

    def query(self, query=None, version=None, _composite_filters=None):
        """Search and retreive STIX objects based on the complete query

        A "complete query" includes the filters from the query, the filters
        attached to MemorySource, and any filters passed from a
        CompositeDataSource (i.e. _composite_filters)

        Args:
            query (list): list of filters to search on
            version (str): If present, it forces the parser to use the version
                provided. Otherwise, the library will make the best effort based
                on checking the "spec_version" property.
            _composite_filters (FilterSet): collection of filters passed from
                the CompositeDataSource, not user supplied

        Returns:
            (list): list of STIX objects that matches the supplied
                query. The STIX objects are received from TAXII as dicts,
                parsed into python STIX objects and then returned.

        """
        query = FilterSet(query)

        # combine all query filters
        if self.filters:
            query.add(self.filters)
        if _composite_filters:
            query.add(_composite_filters)

        # parse taxii query params (that can be applied remotely)
        taxii_filters = self._parse_taxii_filters(query)

        # taxii2client requires query params as keywords
        taxii_filters_dict = dict((f.property, f.value) for f in taxii_filters)

        # query TAXII collection
        all_data = []
        paged_request = tcv21.as_pages if isinstance(self.collection, tcv21.Collection) else tcv20.as_pages
        try:
            for resource in paged_request(self.collection.get_objects, per_request=self.items_per_page, **taxii_filters_dict):
                all_data.extend(resource.get("objects", []))
        except HTTPError as e:
            # if resources not found or access is denied from TAXII server, return empty list
            if e.response.status_code == 404:
                raise DataSourceError(
                    "The requested STIX objects for the TAXII Collection resource defined in"
                    " the supplied TAXII Collection object are either not found or access is"
                    " denied. Received error: ", e,
                )

            # TAXII 2.0 paging can result in a 416 (Range Not Satisfiable) if
            # the server isn't sending Content-Range headers, so the pager just
            # goes until it runs out of pages.  So 416 can't be treated as a
            # real error, just an end-of-pages condition.  For other codes,
            # propagate the exception.
            elif e.response.status_code != 416:
                raise

        # deduplicate data (before filtering as reduces wasted filtering)
        all_data = deduplicate(all_data)

        # apply local (CompositeDataSource, TAXIICollectionSource and query) filters
        query.remove(taxii_filters)
        all_data = list(apply_common_filters(all_data, query))

        # parse python STIX objects from the STIX object dicts
        stix_objs = [parse(stix_obj_dict, allow_custom=self.allow_custom, version=version) for stix_obj_dict in all_data]

        return stix_objs

    def _parse_taxii_filters(self, query):
        """Parse out TAXII filters that the TAXII server can filter on

        Does not put in TAXII spec format as the TAXII2Client (that we use)
        does this for us.

        Note:
            Currently, the TAXII2Client can handle TAXII filters where the
            filter value is list, as both a comma-seperated string or python
            list.

            For instance - "?match[type]=indicator,sighting" can be in a
            filter in any of these formats:

            Filter("type", "=", "indicator,sighting")
            Filter("type", "=", ["indicator", "sighting"])

        Args:
            query (list): list of filters to extract which ones are TAXII
                specific.

        Returns:
            A list of TAXII filters that meet the TAXII filtering parameters.

        """
        taxii_filters = []

        for filter_ in query:
            if filter_.property in TAXII_FILTERS and filter_.op == "=":
                taxii_filters.append(filter_)

        return taxii_filters
