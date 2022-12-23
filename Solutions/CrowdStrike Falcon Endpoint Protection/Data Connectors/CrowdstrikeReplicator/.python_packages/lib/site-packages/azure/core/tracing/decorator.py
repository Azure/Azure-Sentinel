# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
"""The decorator to apply if you want the given function traced."""

import functools

from typing import Callable, Any, TypeVar, overload
from typing_extensions import ParamSpec
from .common import change_context, get_function_and_class_name
from . import SpanKind as _SpanKind
from ..settings import settings


P = ParamSpec("P")
T = TypeVar("T")


@overload
def distributed_trace(__func: Callable[P, T]) -> Callable[P, T]:
    pass


@overload
def distributed_trace(  # pylint:disable=function-redefined
    **kwargs: Any,  # pylint:disable=unused-argument
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    pass


def distributed_trace(  # pylint:disable=function-redefined
    __func: Callable[P, T] = None, **kwargs: Any
):
    """Decorator to apply to function to get traced automatically.

    Span will use the func name or "name_of_span".

    :param callable func: A function to decorate
    :keyword name_of_span: The span name to replace func name if necessary
    :paramtype name_of_span: str
    :keyword kind: The kind of the span. INTERNAL by default.
    :paramtype kind: ~azure.core.tracing.SpanKind
    """
    name_of_span = kwargs.pop("name_of_span", None)
    tracing_attributes = kwargs.pop("tracing_attributes", {})
    kind = kwargs.pop("kind", _SpanKind.INTERNAL)

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper_use_tracer(*args: Any, **kwargs: Any) -> T:
            merge_span = kwargs.pop("merge_span", False)
            passed_in_parent = kwargs.pop("parent_span", None)

            span_impl_type = settings.tracing_implementation()
            if span_impl_type is None:
                return func(*args, **kwargs)

            # Merge span is parameter is set, but only if no explicit parent are passed
            if merge_span and not passed_in_parent:
                return func(*args, **kwargs)

            with change_context(passed_in_parent):
                name = name_of_span or get_function_and_class_name(func, *args)
                with span_impl_type(name=name, kind=kind) as span:
                    for key, value in tracing_attributes.items():
                        span.add_attribute(key, value)
                    return func(*args, **kwargs)

        return wrapper_use_tracer

    return decorator if __func is None else decorator(__func)
