"""
Comparison utilities for STIX pattern comparison expressions.
"""
import base64
import functools

from stix2.equivalence.pattern.compare import generic_cmp, iter_lex_cmp
from stix2.patterns import (
    AndBooleanExpression, BinaryConstant, BooleanConstant, FloatConstant,
    HexConstant, IntegerConstant, ListConstant, ListObjectPathComponent,
    OrBooleanExpression, StringConstant, TimestampConstant,
    _ComparisonExpression,
)

_COMPARISON_OP_ORDER = (
    "=", "!=", "<>", "<", "<=", ">", ">=",
    "IN", "LIKE", "MATCHES", "ISSUBSET", "ISSUPERSET",
)


_CONSTANT_TYPE_ORDER = (
    # ints/floats come first, but have special handling since the types are
    # treated equally as a generic "number" type.  So they aren't in this list.
    # See constant_cmp().
    StringConstant, BooleanConstant,
    TimestampConstant, HexConstant, BinaryConstant, ListConstant,
)


def generic_constant_cmp(const1, const2):
    """
    Generic comparator for most _Constant instances.  They must have a "value"
    attribute whose value supports the builtin comparison operators.

    Args:
        const1: The first _Constant instance
        const2: The second _Constant instance

    Returns:
        <0, 0, or >0 depending on whether the first arg is less, equal or
        greater than the second
    """
    return generic_cmp(const1.value, const2.value)


def bool_cmp(value1, value2):
    """
    Compare two boolean constants.

    Args:
        value1: The first BooleanConstant instance
        value2: The second BooleanConstant instance

    Returns:
        <0, 0, or >0 depending on whether the first arg is less, equal or
        greater than the second
    """

    # unwrap from _Constant instances
    value1 = value1.value
    value2 = value2.value

    if (value1 and value2) or (not value1 and not value2):
        result = 0

    # Let's say... True < False?
    elif value1:
        result = -1

    else:
        result = 1

    return result


def hex_cmp(value1, value2):
    """
    Compare two STIX "hex" values.  This decodes to bytes and compares that.
    It does *not* do a string compare on the hex representations.

    Args:
        value1: The first HexConstant
        value2: The second HexConstant

    Returns:
        <0, 0, or >0 depending on whether the first arg is less, equal or
        greater than the second
    """
    bytes1 = bytes.fromhex(value1.value)
    bytes2 = bytes.fromhex(value2.value)

    return generic_cmp(bytes1, bytes2)


def bin_cmp(value1, value2):
    """
    Compare two STIX "binary" values.  This decodes to bytes and compares that.
    It does *not* do a string compare on the base64 representations.

    Args:
        value1: The first BinaryConstant
        value2: The second BinaryConstant

    Returns:
        <0, 0, or >0 depending on whether the first arg is less, equal or
        greater than the second
    """
    bytes1 = base64.standard_b64decode(value1.value)
    bytes2 = base64.standard_b64decode(value2.value)

    return generic_cmp(bytes1, bytes2)


def list_cmp(value1, value2):
    """
    Compare lists order-insensitively.

    Args:
        value1: The first ListConstant
        value2: The second ListConstant

    Returns:
        <0, 0, or >0 depending on whether the first arg is less, equal or
        greater than the second
    """

    # Achieve order-independence by sorting the lists first.
    sorted_value1 = sorted(
        value1.value, key=functools.cmp_to_key(constant_cmp),
    )

    sorted_value2 = sorted(
        value2.value, key=functools.cmp_to_key(constant_cmp),
    )

    result = iter_lex_cmp(sorted_value1, sorted_value2, constant_cmp)

    return result


_CONSTANT_COMPARATORS = {
    # We have special handling for ints/floats, so no entries for those AST
    # classes here.  See constant_cmp().
    StringConstant: generic_constant_cmp,
    BooleanConstant: bool_cmp,
    TimestampConstant: generic_constant_cmp,
    HexConstant: hex_cmp,
    BinaryConstant: bin_cmp,
    ListConstant: list_cmp,
}


def object_path_component_cmp(comp1, comp2):
    """
    Compare a string/int to another string/int; this induces an ordering over
    all strings and ints.  It is used to perform a lexicographical sort on
    object paths.

    Ints and strings compare as usual to each other; ints compare less than
    strings.

    Args:
        comp1: An object path component (string or int)
        comp2: An object path component (string or int)

    Returns:
        <0, 0, or >0 depending on whether the first arg is less, equal or
        greater than the second
    """

    # both ints or both strings: use builtin comparison operators
    if (isinstance(comp1, int) and isinstance(comp2, int)) \
            or (isinstance(comp1, str) and isinstance(comp2, str)):
        result = generic_cmp(comp1, comp2)

    # one is int, one is string.  Let's say ints come before strings.
    elif isinstance(comp1, int):
        result = -1

    else:
        result = 1

    return result


def object_path_to_raw_values(path):
    """
    Converts the given ObjectPath instance to a list of strings and ints.
    All property names become strings, regardless of whether they're *_ref
    properties; "*" index steps become that string; and numeric index steps
    become integers.

    Args:
        path: An ObjectPath instance

    Returns:
        A generator iterator over the values
    """

    for comp in path.property_path:
        if isinstance(comp, ListObjectPathComponent):
            yield comp.property_name

            if comp.index == "*" or isinstance(comp.index, int):
                yield comp.index
            else:
                # in case the index is a stringified int; convert to an actual
                # int
                yield int(comp.index)

        else:
            yield comp.property_name


def object_path_cmp(path1, path2):
    """
    Compare two object paths.

    Args:
        path1: The first ObjectPath instance
        path2: The second ObjectPath instance

    Returns:
        <0, 0, or >0 depending on whether the first arg is less, equal or
        greater than the second
    """
    if path1.object_type_name < path2.object_type_name:
        result = -1

    elif path1.object_type_name > path2.object_type_name:
        result = 1

    else:
        # I always thought of key and index path steps as separate.  The AST
        # lumps indices in with the previous key as a single path component.
        # The following splits the path components into individual comparable
        # values again.  Maybe I should not do this...
        path_vals1 = object_path_to_raw_values(path1)
        path_vals2 = object_path_to_raw_values(path2)
        result = iter_lex_cmp(
            path_vals1, path_vals2, object_path_component_cmp,
        )

    return result


def comparison_operator_cmp(op1, op2):
    """
    Compare two comparison operators.

    Args:
        op1: The first comparison operator (a string)
        op2: The second comparison operator (a string)

    Returns:
        <0, 0, or >0 depending on whether the first arg is less, equal or
        greater than the second
    """
    op1_idx = _COMPARISON_OP_ORDER.index(op1)
    op2_idx = _COMPARISON_OP_ORDER.index(op2)

    result = generic_cmp(op1_idx, op2_idx)

    return result


def constant_cmp(value1, value2):
    """
    Compare two constants.

    Args:
        value1: The first _Constant instance
        value2: The second _Constant instance

    Returns:
        <0, 0, or >0 depending on whether the first arg is less, equal or
        greater than the second
    """

    # Special handling for ints/floats: treat them generically as numbers,
    # ordered before all other types.
    if isinstance(value1, (IntegerConstant, FloatConstant)) \
            and isinstance(value2, (IntegerConstant, FloatConstant)):
        result = generic_constant_cmp(value1, value2)

    elif isinstance(value1, (IntegerConstant, FloatConstant)):
        result = -1

    elif isinstance(value2, (IntegerConstant, FloatConstant)):
        result = 1

    else:

        type1 = type(value1)
        type2 = type(value2)

        type1_idx = _CONSTANT_TYPE_ORDER.index(type1)
        type2_idx = _CONSTANT_TYPE_ORDER.index(type2)

        result = generic_cmp(type1_idx, type2_idx)
        if result == 0:
            # Types are the same; must compare values
            cmp_func = _CONSTANT_COMPARATORS.get(type1)
            if not cmp_func:
                raise TypeError("Don't know how to compare " + type1.__name__)

            result = cmp_func(value1, value2)

    return result


def simple_comparison_expression_cmp(expr1, expr2):
    """
    Compare "simple" comparison expressions: those which aren't AND/OR
    combinations, just <path> <op> <value> comparisons.

    Args:
        expr1: first _ComparisonExpression instance
        expr2: second _ComparisonExpression instance

    Returns:
        <0, 0, or >0 depending on whether the first arg is less, equal or
        greater than the second
    """

    result = object_path_cmp(expr1.lhs, expr2.lhs)

    if result == 0:
        result = comparison_operator_cmp(expr1.operator, expr2.operator)

    if result == 0:
        # _ComparisonExpression's have a "negated" attribute.  Umm...
        # non-negated < negated?
        if not expr1.negated and expr2.negated:
            result = -1
        elif expr1.negated and not expr2.negated:
            result = 1

    if result == 0:
        result = constant_cmp(expr1.rhs, expr2.rhs)

    return result


def comparison_expression_cmp(expr1, expr2):
    """
    Compare two comparison expressions.  This is sensitive to the order of the
    expressions' sub-components.  To achieve an order-insensitive comparison,
    the sub-component ASTs must be ordered first.

    Args:
        expr1: The first comparison expression
        expr2: The second comparison expression

    Returns:
        <0, 0, or >0 depending on whether the first arg is less, equal or
        greater than the second
    """
    if isinstance(expr1, _ComparisonExpression) \
            and isinstance(expr2, _ComparisonExpression):
        result = simple_comparison_expression_cmp(expr1, expr2)

    # One is simple, one is compound.  Let's say... simple ones come first?
    elif isinstance(expr1, _ComparisonExpression):
        result = -1

    elif isinstance(expr2, _ComparisonExpression):
        result = 1

    # Both are compound: AND's before OR's?
    elif isinstance(expr1, AndBooleanExpression) \
            and isinstance(expr2, OrBooleanExpression):
        result = -1

    elif isinstance(expr1, OrBooleanExpression) \
            and isinstance(expr2, AndBooleanExpression):
        result = 1

    else:
        # Both compound, same boolean operator: sort according to contents.
        # This will order according to recursive invocations of this comparator,
        # on sub-expressions.
        result = iter_lex_cmp(
            expr1.operands, expr2.operands, comparison_expression_cmp,
        )

    return result
