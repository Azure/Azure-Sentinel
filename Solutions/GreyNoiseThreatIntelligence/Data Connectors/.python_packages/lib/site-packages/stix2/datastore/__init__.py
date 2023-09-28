"""
Python STIX2 DataStore API.

.. autosummary::
   :toctree: datastore

   filesystem
   filters
   memory
   taxii

|
"""

from abc import ABCMeta, abstractmethod
import uuid

from stix2.datastore.filters import Filter, FilterSet
from stix2.utils import deduplicate


def make_id():
    return str(uuid.uuid4())


class DataSourceError(Exception):
    """General DataSource error instance, used primarily for wrapping
    lower level errors

    Args:
        message (str): error message
        root_exception (Exception): Exception instance of root exception
            in the case that DataSourceError is wrapping a lower level or
            other exception
    """
    def __init__(self, message, root_exception=None):
        self.message = message
        self.root_exception = root_exception

    def __str__(self):
        if self.root_exception:
            return "{} \"{}\"".format(self.message, self.root_exception)
        else:
            return self.message


class DataStoreMixin(object):
    """Provides mechanisms for storing and retrieving STIX data. The specific
    behavior can be customized by subclasses.

    Args:
        source (DataSource): An existing DataSource to use
            as this DataStore's DataSource component
        sink (DataSink): An existing DataSink to use
            as this DataStore's DataSink component

    Attributes:
        id (str): A unique UUIDv4 to identify this DataStore.
        source (DataSource): An object that implements DataSource class.
        sink (DataSink): An object that implements DataSink class.

    """
    def __init__(self, source=None, sink=None):
        super(DataStoreMixin, self).__init__()
        self.id = make_id()
        self.source = source
        self.sink = sink

    def get(self, *args, **kwargs):
        """Retrieve the most recent version of a single STIX object by ID.

        Translate get() call to the appropriate DataSource call.

        Args:
            stix_id (str): the id of the STIX object to retrieve.

        Returns:
            stix_obj: the single most recent version of the STIX
                object specified by the "id".

        """
        try:
            return self.source.get(*args, **kwargs)
        except AttributeError:
            msg = "%s has no data source to query"
            raise AttributeError(msg % self.__class__.__name__)

    def all_versions(self, *args, **kwargs):
        """Retrieve all versions of a single STIX object by ID.

        Translate all_versions() call to the appropriate DataSource call.

        Args:
            stix_id (str): the id of the STIX object to retrieve.

        Returns:
            list: All versions of the specified STIX object.

        """
        try:
            return self.source.all_versions(*args, **kwargs)
        except AttributeError:
            msg = "%s has no data source to query"
            raise AttributeError(msg % self.__class__.__name__)

    def query(self, *args, **kwargs):
        """Retrieve STIX objects matching a set of filters.

        Translate query() call to the appropriate DataSource call.

        Args:
            query (list): a list of filters (which collectively are the query)
                to conduct search on.

        Returns:
            list: The STIX objects matching the query.

        """
        try:
            return self.source.query(*args, **kwargs)
        except AttributeError:
            msg = "%s has no data source to query"
            raise AttributeError(msg % self.__class__.__name__)

    def creator_of(self, *args, **kwargs):
        """Retrieve the Identity refered to by the object's `created_by_ref`.

        Translate creator_of() call to the appropriate DataSource call.

        Args:
            obj: The STIX object whose `created_by_ref` property will be looked
                up.

        Returns:
            The STIX object's creator, or None, if the object contains no
            `created_by_ref` property or the object's creator cannot be found.

        """
        try:
            return self.source.creator_of(*args, **kwargs)
        except AttributeError:
            msg = "%s has no data source to query"
            raise AttributeError(msg % self.__class__.__name__)

    def relationships(self, *args, **kwargs):
        """Retrieve Relationships involving the given STIX object.

        Translate relationships() call to the appropriate DataSource call.

        Only one of `source_only` and `target_only` may be `True`.

        Args:
            obj (STIX object OR dict OR str): The STIX object (or its ID) whose
                relationships will be looked up.
            relationship_type (str): Only retrieve Relationships of this type.
                If None, all relationships will be returned, regardless of type.
            source_only (bool): Only retrieve Relationships for which this
                object is the source_ref. Default: False.
            target_only (bool): Only retrieve Relationships for which this
                object is the target_ref. Default: False.

        Returns:
            list: The Relationship objects involving the given STIX object.

        """
        try:
            return self.source.relationships(*args, **kwargs)
        except AttributeError:
            msg = "%s has no data source to query"
            raise AttributeError(msg % self.__class__.__name__)

    def related_to(self, *args, **kwargs):
        """Retrieve STIX Objects that have a Relationship involving the given
        STIX object.

        Translate related_to() call to the appropriate DataSource call.

        Only one of `source_only` and `target_only` may be `True`.

        Args:
            obj (STIX object OR dict OR str): The STIX object (or its ID) whose
                related objects will be looked up.
            relationship_type (str): Only retrieve objects related by this
                Relationships type. If None, all related objects will be
                returned, regardless of type.
            source_only (bool): Only examine Relationships for which this
                object is the source_ref. Default: False.
            target_only (bool): Only examine Relationships for which this
                object is the target_ref. Default: False.
            filters (list): list of additional filters the related objects must
                match.

        Returns:
            list: The STIX objects related to the given STIX object.

        """
        try:
            return self.source.related_to(*args, **kwargs)
        except AttributeError:
            msg = "%s has no data source to query"
            raise AttributeError(msg % self.__class__.__name__)

    def add(self, *args, **kwargs):
        """Method for storing STIX objects.

        Defines custom behavior before storing STIX objects using the
        appropriate method call on the associated DataSink.

        Args:
            stix_objs (list): a list of STIX objects

        """
        try:
            return self.sink.add(*args, **kwargs)
        except AttributeError:
            msg = "%s has no data sink to put objects in"
            raise AttributeError(msg % self.__class__.__name__)


class DataSink(metaclass=ABCMeta):
    """An implementer will create a concrete subclass from
    this class for the specific DataSink.

    Attributes:
        id (str): A unique UUIDv4 to identify this DataSink.

    """
    def __init__(self):
        super(DataSink, self).__init__()
        self.id = make_id()

    @abstractmethod
    def add(self, stix_objs):
        """Method for storing STIX objects.

        Implement: Specific data sink API calls, processing,
        functionality required for adding data to the sink

        Args:
            stix_objs (list): a list of STIX objects (where each object is a
                STIX object)

        """


class DataSource(metaclass=ABCMeta):
    """An implementer will create a concrete subclass from
    this class for the specific DataSource.

    Attributes:
        id (str): A unique UUIDv4 to identify this DataSource.
        filters (FilterSet): A collection of filters attached to this DataSource.

    """
    def __init__(self):
        super(DataSource, self).__init__()
        self.id = make_id()
        self.filters = FilterSet()

    @abstractmethod
    def get(self, stix_id):
        """
        Implement: Specific data source API calls, processing,
        functionality required for retrieving data from the data source

        Args:
            stix_id (str): the id of the STIX 2.0 object to retrieve. Should
                return a single object, the most recent version of the object
                specified by the "id".

        Returns:
            stix_obj: The STIX object.

        """

    @abstractmethod
    def all_versions(self, stix_id):
        """
        Implement: Similar to get() except returns list of all object versions
        of the specified "id". In addition, implement the specific data
        source API calls, processing, functionality required for retrieving
        data from the data source.

        Args:
            stix_id (str): The id of the STIX 2.0 object to retrieve. Should
                return a list of objects, all the versions of the object
                specified by the "id".

        Returns:
            list: All versions of the specified STIX object.

        """

    @abstractmethod
    def query(self, query=None):
        """
        Implement: The specific data source API calls, processing,
        functionality required for retrieving query from the data source

        Args:
            query (list): a list of filters (which collectively are the query)
                to conduct search on.

        Returns:
            list: The STIX objects that matched the query.

        """

    def creator_of(self, obj):
        """Retrieve the Identity referred to by the object's `created_by_ref`.

        Args:
            obj: The STIX object whose `created_by_ref` property will be looked
                up.

        Returns:
            The STIX object's creator, or None, if the object contains no
            `created_by_ref` property or the object's creator cannot be found.

        """
        creator_id = obj.get('created_by_ref', '')
        if creator_id:
            return self.get(creator_id)
        else:
            return None

    def relationships(self, obj, relationship_type=None, source_only=False, target_only=False):
        """Retrieve Relationships involving the given STIX object.

        Only one of `source_only` and `target_only` may be `True`.

        Args:
            obj (STIX object OR dict OR str): The STIX object (or its ID) whose
                relationships will be looked up.
            relationship_type (str): Only retrieve Relationships of this type.
                If None, all relationships will be returned, regardless of type.
            source_only (bool): Only retrieve Relationships for which this
                object is the source_ref. Default: False.
            target_only (bool): Only retrieve Relationships for which this
                object is the target_ref. Default: False.

        Returns:
            list: The Relationship objects involving the given STIX object.

        """
        results = []
        filters = [Filter('type', '=', 'relationship')]

        try:
            obj_id = obj['id']
        except KeyError:
            raise ValueError("STIX object has no 'id' property")
        except TypeError:
            # Assume `obj` is an ID string
            obj_id = obj

        if relationship_type:
            filters.append(Filter('relationship_type', '=', relationship_type))

        if source_only and target_only:
            raise ValueError("Search either source only or target only, but not both")

        if not target_only:
            results.extend(self.query(filters + [Filter('source_ref', '=', obj_id)]))
        if not source_only:
            results.extend(self.query(filters + [Filter('target_ref', '=', obj_id)]))

        return results

    def related_to(self, obj, relationship_type=None, source_only=False, target_only=False, filters=None):
        """Retrieve STIX Objects that have a Relationship involving the given
        STIX object.

        Only one of `source_only` and `target_only` may be `True`.

        Args:
            obj (STIX object OR dict OR str): The STIX object (or its ID) whose
                related objects will be looked up.
            relationship_type (str): Only retrieve objects related by this
                Relationships type. If None, all related objects will be
                returned, regardless of type.
            source_only (bool): Only examine Relationships for which this
                object is the source_ref. Default: False.
            target_only (bool): Only examine Relationships for which this
                object is the target_ref. Default: False.
            filters (list): list of additional filters the related objects must
                match.

        Returns:
            list: The STIX objects related to the given STIX object.

        """
        results = []
        rels = self.relationships(obj, relationship_type, source_only, target_only)

        try:
            obj_id = obj['id']
        except TypeError:
            # Assume `obj` is an ID string
            obj_id = obj

        # Get all unique ids from the relationships except that of the object
        ids = set()
        for r in rels:
            ids.update((r.source_ref, r.target_ref))
        ids.discard(obj_id)

        # Assemble filters
        filter_list = FilterSet(filters)

        for i in ids:
            results.extend(self.query([f for f in filter_list] + [Filter('id', '=', i)]))

        return results


class CompositeDataSource(DataSource):
    """Controller for all the attached DataSources.

    A user can have a single CompositeDataSource as an interface
    to a set of DataSources. When an API call is made to the
    CompositeDataSource, it is delegated to each of the (real)
    DataSources that are attached to it.

    DataSources can be attached to CompositeDataSource for a variety
    of reasons, e.g. common filters, organization, less API calls.

    Attributes:

        data_sources (list): A dictionary of DataSource objects; to be
            controlled and used by the Data Source Controller object.

    """
    def __init__(self):
        """Create a new STIX Data Source.

        Args:

        """
        super(CompositeDataSource, self).__init__()
        self.data_sources = []

    def get(self, stix_id, _composite_filters=None):
        """Retrieve STIX object by STIX ID

        Federated retrieve method, iterates through all DataSources
        defined in the "data_sources" parameter. Each data source has a
        specific API retrieve-like function and associated parameters. This
        function does a federated retrieval and consolidation of the data
        returned from all the STIX data sources.

        A composite data source will pass its attached filters to
        each configured data source, pushing filtering to them to handle.

        Args:
            stix_id (str): the id of the STIX object to retrieve.
            _composite_filters (FilterSet): a collection of filters passed from a
                CompositeDataSource (i.e. if this CompositeDataSource is attached
                to another parent CompositeDataSource), not user supplied.

        Returns:
            stix_obj: The STIX object to be returned.

        """
        if not self.has_data_sources():
            raise AttributeError("CompositeDataSource has no data sources")

        all_data = []
        all_filters = FilterSet()

        all_filters.add(self.filters)

        if _composite_filters:
            all_filters.add(_composite_filters)

        # for every configured Data Source, call its retrieve handler
        for ds in self.data_sources:
            data = ds.get(stix_id=stix_id, _composite_filters=all_filters)
            if data:
                all_data.append(data)

        # Search for latest version
        stix_obj = latest_ver = None
        for obj in all_data:
            ver = obj.get("modified") or obj.get("created")

            if stix_obj is None or ver is None or ver > latest_ver:
                stix_obj = obj
                latest_ver = ver

        return stix_obj

    def all_versions(self, stix_id, _composite_filters=None):
        """Retrieve all versions of a STIX object by STIX ID.

        Federated all_versions retrieve method - iterates through all
        DataSources defined in "data_sources".

        A composite data source will pass its attached filters to
        each configured data source, pushing filtering to them to handle.

        Args:
            stix_id (str): id of the STIX objects to retrieve.
            _composite_filters (FilterSet): a collection of filters passed from a
                CompositeDataSource (i.e. if this CompositeDataSource is
                attached to a parent CompositeDataSource), not user supplied.

        Returns:
            list: The STIX objects that have the specified id.

        """
        if not self.has_data_sources():
            raise AttributeError("CompositeDataSource has no data sources")

        all_data = []
        all_filters = FilterSet()

        all_filters.add(self.filters)

        if _composite_filters:
            all_filters.add(_composite_filters)

        # retrieve STIX objects from all configured data sources
        for ds in self.data_sources:
            data = ds.all_versions(stix_id=stix_id, _composite_filters=all_filters)
            all_data.extend(data)

        # remove exact duplicates (where duplicates are STIX 2.0 objects
        # with the same 'id' and 'modified' values)
        if len(all_data) > 0:
            all_data = deduplicate(all_data)

        return all_data

    def query(self, query=None, _composite_filters=None):
        """Retrieve STIX objects that match a query.

        Federate the query to all DataSources attached to the
        Composite Data Source.

        Args:
            query (list): list of filters to search on.
            _composite_filters (FilterSet): a collection of filters passed from a
                CompositeDataSource (i.e. if this CompositeDataSource is
                attached to a parent CompositeDataSource), not user supplied.

        Returns:
            list: The STIX objects to be returned.

        """
        if not self.has_data_sources():
            raise AttributeError("CompositeDataSource has no data sources")

        if not query:
            # don't mess with the query (i.e. deduplicate, as that's done
            # within the specific DataSources that are called)
            query = []

        all_data = []
        all_filters = FilterSet()

        all_filters.add(self.filters)

        if _composite_filters:
            all_filters.add(_composite_filters)

        # federate query to all attached data sources,
        # pass composite filters to id
        for ds in self.data_sources:
            data = ds.query(query=query, _composite_filters=all_filters)
            all_data.extend(data)

        # remove exact duplicates (where duplicates are STIX 2.0
        # objects with the same 'id' and 'modified' values)
        if len(all_data) > 0:
            all_data = deduplicate(all_data)

        return all_data

    def relationships(self, *args, **kwargs):
        """Retrieve Relationships involving the given STIX object.

        Only one of `source_only` and `target_only` may be `True`.

        Federated relationships retrieve method - iterates through all
        DataSources defined in "data_sources".

        Args:
            obj (STIX object OR dict OR str): The STIX object (or its ID) whose
                relationships will be looked up.
            relationship_type (str): Only retrieve Relationships of this type.
                If None, all relationships will be returned, regardless of type.
            source_only (bool): Only retrieve Relationships for which this
                object is the source_ref. Default: False.
            target_only (bool): Only retrieve Relationships for which this
                object is the target_ref. Default: False.

        Returns:
            list: The Relationship objects involving the given STIX object.

        """
        if not self.has_data_sources():
            raise AttributeError("CompositeDataSource has no data sources")

        results = []
        for ds in self.data_sources:
            results.extend(ds.relationships(*args, **kwargs))

        # remove exact duplicates (where duplicates are STIX 2.0
        # objects with the same 'id' and 'modified' values)
        if len(results) > 0:
            results = deduplicate(results)

        return results

    def related_to(self, *args, **kwargs):
        """Retrieve STIX Objects that have a Relationship involving the given
        STIX object.

        Only one of `source_only` and `target_only` may be `True`.

        Federated related objects method - iterates through all
        DataSources defined in "data_sources".

        Args:
            obj (STIX object OR dict OR str): The STIX object (or its ID) whose
                related objects will be looked up.
            relationship_type (str): Only retrieve objects related by this
                Relationships type. If None, all related objects will be
                returned, regardless of type.
            source_only (bool): Only examine Relationships for which this
                object is the source_ref. Default: False.
            target_only (bool): Only examine Relationships for which this
                object is the target_ref. Default: False.
            filters (list): list of additional filters the related objects must
                match.

        Returns:
            list: The STIX objects related to the given STIX object.

        """
        if not self.has_data_sources():
            raise AttributeError("CompositeDataSource has no data sources")

        results = []
        for ds in self.data_sources:
            results.extend(ds.related_to(*args, **kwargs))

        # remove exact duplicates (where duplicates are STIX 2.0
        # objects with the same 'id' and 'modified' values)
        if len(results) > 0:
            results = deduplicate(results)

        return results

    def add_data_source(self, data_source):
        """Attach a DataSource to CompositeDataSource instance

        Args:
            data_source (DataSource): a stix2.DataSource to attach
                to the CompositeDataSource

        """
        if issubclass(data_source.__class__, DataSource):
            if data_source.id not in [ds_.id for ds_ in self.data_sources]:
                # check DataSource not already attached CompositeDataSource
                self.data_sources.append(data_source)
        else:
            raise TypeError("DataSource (to be added) is not of type stix2.DataSource. DataSource type is '%s'" % type(data_source))

        return

    def add_data_sources(self, data_sources):
        """Attach list of DataSources to CompositeDataSource instance

        Args:
            data_sources (list): stix2.DataSources to attach to
                CompositeDataSource
        """
        for ds in data_sources:
            self.add_data_source(ds)
        return

    def remove_data_source(self, data_source_id):
        """Remove DataSource from the CompositeDataSource instance

        Args:
            data_source_id (str): DataSource IDs.

        """
        def _match(ds_id, candidate_ds_id):
            return ds_id == candidate_ds_id

        self.data_sources[:] = [ds for ds in self.data_sources if not _match(ds.id, data_source_id)]

        return

    def remove_data_sources(self, data_source_ids):
        """Remove DataSources from the CompositeDataSource instance

        Args:
            data_source_ids (list): DataSource IDs

        """
        for ds_id in data_source_ids:
            self.remove_data_source(ds_id)
        return

    def has_data_sources(self):
        return len(self.data_sources)

    def get_all_data_sources(self):
        return self.data_sources
