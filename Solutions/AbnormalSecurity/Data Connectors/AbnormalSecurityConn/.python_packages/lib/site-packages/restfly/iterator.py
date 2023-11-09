'''
Iterators
=========

.. autoclass:: APIIterator
    :members:
    :private-members:
'''
from typing import Any, Optional


class APIIterator:
    '''
    The API iterator provides a scalable way to work through result sets of any
    size.  The iterator will walk through each page of data, returning one
    record at a time.  If it reaches the end of a page of records, then it will
    request the next page of information and then continue to return records
    from the next page (and the next, and the next) until the counter reaches
    the total number of records that the API has reported.

    Note that this Iterator is used as a base model for all of the iterators,
    and while the mechanics of each iterator may vary, they should all behave
    to the user in a similar manner.

    Attributes:
        _api (restfly.session.APISession):
            The APISession object that will be used for querying for the
            data.
        count (int):
            The current number of records that have been returned
        max_items (int):
            The maximum number of items to return before stopping iteration.
        max_pages (int):
            The maximum number of pages to request before throwing stopping
            iteration.
        num_pages (int):
            The number of pages that have been requested.
        page (list):
            The current page of data being walked through.  pages will be
            cycled through as the iterator requests more information from the
            API.
        page_count (int): The number of record returned from the current page.
        total (int):
            The total number of records that exist for the current request.
    '''
    count = 0
    page_count = 0
    num_pages = 0
    max_pages = None
    max_items = None
    total = None
    page = []
    _api = None

    def __init__(self, api, **kw):
        '''
        Args:
            api (restfly.session.APISession):
                The APISession object to use for this iterator.
            **kw (dict):
                The various attributes to add/overload in the iterator.

        Example:
            >>> i = APIIterator(api, max_pages=1, max_items=100)
        '''
        self._api = api
        self.__dict__.update(kw)

    def _get_page(self) -> None:
        '''
        A method to be overloaded in order to instruct the iterator how to
        retrieve the next page of data.

        Example:
            >>> class ExampleIterator(APIIterator):
            ...    def _get_page(self):
            ...        self.total = 100
            ...        items = range(10)
            ...        self.page = [{'id': i + self._offset} for i in items]
            ...        self._offset += self._limit
        '''

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        '''
        Retrieves an item from the the current page based off of the key.

        Args:
            key (int): The index of the item to retrieve.
            default (obj): The returned object if the item does not exist.

        Examples:
            >>> a = APIIterator()
            >>> a.get(2)
            None
        '''
        try:
            return self.__getitem__(key)
        except IndexError:
            return default

    def __getitem__(self, key: str):
        return self.page[key]

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()  # noqa: PLE1102

    def next(self) -> Any:
        '''
        Ask for the next record
        '''
        # If there are no more records to return, then we should raise a
        # StopIteration exception to break the iterator out.
        if (
            (self.total and self.count + 1 > self.total)  # noqa: PLR0916
            or (self.max_items and self.count + 1 > self.max_items)
            or (self.max_pages and self.num_pages > self.max_pages)
        ):
            raise StopIteration()

        # If we have worked through the current page of records and we still
        # haven't hit to the total number of available records, then we should
        # query the next page of records.
        if (self.page_count >= len(self.page)
                and (not self.total or self.count + 1 <= self.total)):
            # If the number of pages requested reaches the total number of
            # pages that should be requested, then stop iteration.
            if self.max_pages and self.num_pages + 1 > self.max_pages:
                raise StopIteration()

            # Perform the _get_page call.
            self._get_page()
            self.page_count = 0
            self.num_pages += 1

            # If the length of the page is 0, then we don't have anything
            # further to do and should stop iteration.
            if len(self.page) == 0:
                raise StopIteration()

        # Get the relevant record, increment the counters, and return the
        # record.
        self.count += 1
        self.page_count += 1
        return self[self.page_count - 1]
