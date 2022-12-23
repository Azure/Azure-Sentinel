import asyncio

from botocore.hooks import HierarchicalEmitter, logger


class AioHierarchicalEmitter(HierarchicalEmitter):
    async def _emit(self, event_name, kwargs, stop_on_response=False):
        responses = []
        # Invoke the event handlers from most specific
        # to least specific, each time stripping off a dot.
        handlers_to_call = self._lookup_cache.get(event_name)
        if handlers_to_call is None:
            handlers_to_call = self._handlers.prefix_search(event_name)
            self._lookup_cache[event_name] = handlers_to_call
        elif not handlers_to_call:
            # Short circuit and return an empty response is we have
            # no handlers to call.  This is the common case where
            # for the majority of signals, nothing is listening.
            return []
        kwargs['event_name'] = event_name
        responses = []
        for handler in handlers_to_call:
            logger.debug('Event %s: calling handler %s', event_name, handler)

            # Await the handler if its a coroutine.
            if asyncio.iscoroutinefunction(handler):
                response = await handler(**kwargs)
            else:
                response = handler(**kwargs)

            responses.append((handler, response))
            if stop_on_response and response is not None:
                return responses
        return responses

    async def emit_until_response(self, event_name, **kwargs):
        responses = await self._emit(event_name, kwargs, stop_on_response=True)
        if responses:
            return responses[-1]
        else:
            return None, None
