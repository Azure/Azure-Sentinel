from .models import DurableEntityContext
from .models.entities import OperationResult, EntityState
from datetime import datetime
from typing import Callable, Any, List, Dict


class InternalEntityException(Exception):
    """Framework-internal Exception class (for internal use only)."""

    pass


class Entity:
    """Durable Entity Class.

    Responsible for executing the user-defined entity function.
    """

    def __init__(self, entity_func: Callable[[DurableEntityContext], None]):
        """Create a new entity for the user-defined entity.

        Responsible for executing the user-defined entity function

        Parameters
        ----------
        entity_func: Callable[[DurableEntityContext], Generator[Any, Any, Any]]
            The user defined entity function
        """
        self.fn: Callable[[DurableEntityContext], None] = entity_func

    def handle(self, context: DurableEntityContext, batch: List[Dict[str, Any]]) -> str:
        """Handle the execution of the user-defined entity function.

        Loops over the batch, which serves to specify inputs to the entity,
        and collects results and generates a final state, which are returned.

        Parameters
        ----------
        context: DurableEntityContext
            The entity context of the entity, which the user interacts with as their Durable API

        Returns
        -------
        str
            A JSON-formatted string representing the output state, results, and exceptions for the
            entity execution.
        """
        response = EntityState(results=[], signals=[])
        for operation_data in batch:
            result: Any = None
            is_error: bool = False
            start_time: datetime = datetime.now()

            try:
                # populate context
                operation = operation_data["name"]
                if operation is None:
                    message = "Durable Functions Internal Error:"\
                        "Entity operation was missing a name field"
                    raise InternalEntityException(message)
                context._operation = operation
                context._input = operation_data["input"]
                self.fn(context)
                result = context._result

            except InternalEntityException as e:
                raise e

            except Exception as e:
                is_error = True
                result = str(e)

            duration: int = self._elapsed_milliseconds_since(start_time)
            operation_result = OperationResult(
                is_error=is_error,
                duration=duration,
                result=result
            )
            response.results.append(operation_result)

        response.state = context._state
        response.entity_exists = context._exists
        return response.to_json_string()

    @classmethod
    def create(cls, fn: Callable[[DurableEntityContext], None]) -> Callable[[Any], str]:
        """Create an instance of the entity class.

        Parameters
        ----------
            fn (Callable[[DurableEntityContext], None]): [description]

        Returns
        -------
        Callable[[Any], str]
            Handle function of the newly created entity client
        """
        def handle(context) -> str:
            # It is not clear when the context JSON would be found
            # inside a "body"-key, but this pattern matches the
            # orchestrator implementation, so we keep it for safety.
            context_body = getattr(context, "body", None)
            if context_body is None:
                context_body = context
            ctx, batch = DurableEntityContext.from_json(context_body)
            return Entity(fn).handle(ctx, batch)
        return handle

    def _elapsed_milliseconds_since(self, start_time: datetime) -> int:
        """Calculate the elapsed time, in milliseconds, from the start_time to the present.

        Parameters
        ----------
        start_time: datetime
            The timestamp of when the entity began processing a batched request.

        Returns
        -------
        int
            The time, in millseconds, from start_time to now
        """
        end_time = datetime.now()
        time_diff = end_time - start_time
        elapsed_time = int(time_diff.total_seconds() * 1000)
        return elapsed_time
