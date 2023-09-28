"""
Comparison utilities for STIX pattern observation expressions.
"""
from stix2.equivalence.pattern.compare import generic_cmp, iter_lex_cmp
from stix2.equivalence.pattern.compare.comparison import (
    comparison_expression_cmp, generic_constant_cmp,
)
from stix2.patterns import (
    AndObservationExpression, FollowedByObservationExpression,
    ObservationExpression, OrObservationExpression,
    QualifiedObservationExpression, RepeatQualifier, StartStopQualifier,
    WithinQualifier, _CompoundObservationExpression,
)

_OBSERVATION_EXPRESSION_TYPE_ORDER = (
    ObservationExpression, AndObservationExpression, OrObservationExpression,
    FollowedByObservationExpression, QualifiedObservationExpression,
)


_QUALIFIER_TYPE_ORDER = (
    RepeatQualifier, WithinQualifier, StartStopQualifier,
)


def repeats_cmp(qual1, qual2):
    """
    Compare REPEATS qualifiers.  This orders by repeat count.
    """
    return generic_constant_cmp(qual1.times_to_repeat, qual2.times_to_repeat)


def within_cmp(qual1, qual2):
    """
    Compare WITHIN qualifiers.  This orders by number of seconds.
    """
    return generic_constant_cmp(
        qual1.number_of_seconds, qual2.number_of_seconds,
    )


def startstop_cmp(qual1, qual2):
    """
    Compare START/STOP qualifiers.  This lexicographically orders by start time,
    then stop time.
    """
    return iter_lex_cmp(
        (qual1.start_time, qual1.stop_time),
        (qual2.start_time, qual2.stop_time),
        generic_constant_cmp,
    )


_QUALIFIER_COMPARATORS = {
    RepeatQualifier: repeats_cmp,
    WithinQualifier: within_cmp,
    StartStopQualifier: startstop_cmp,
}


def observation_expression_cmp(expr1, expr2):
    """
    Compare two observation expression ASTs.  This is sensitive to the order of
    the expressions' sub-components.  To achieve an order-insensitive
    comparison, the sub-component ASTs must be ordered first.

    Args:
        expr1: The first observation expression
        expr2: The second observation expression

    Returns:
        <0, 0, or >0 depending on whether the first arg is less, equal or
        greater than the second
    """
    type1 = type(expr1)
    type2 = type(expr2)

    type1_idx = _OBSERVATION_EXPRESSION_TYPE_ORDER.index(type1)
    type2_idx = _OBSERVATION_EXPRESSION_TYPE_ORDER.index(type2)

    if type1_idx != type2_idx:
        result = generic_cmp(type1_idx, type2_idx)

    # else, both exprs are of same type.

    # If they're simple, use contained comparison expression order
    elif type1 is ObservationExpression:
        result = comparison_expression_cmp(
            expr1.operand, expr2.operand,
        )

    elif isinstance(expr1, _CompoundObservationExpression):
        # Both compound, and of same type (and/or/followedby): sort according
        # to contents.
        result = iter_lex_cmp(
            expr1.operands, expr2.operands, observation_expression_cmp,
        )

    else:  # QualifiedObservationExpression
        # Both qualified.  Check qualifiers first; if they are the same,
        # use order of the qualified expressions.
        qual1_type = type(expr1.qualifier)
        qual2_type = type(expr2.qualifier)

        qual1_type_idx = _QUALIFIER_TYPE_ORDER.index(qual1_type)
        qual2_type_idx = _QUALIFIER_TYPE_ORDER.index(qual2_type)

        result = generic_cmp(qual1_type_idx, qual2_type_idx)

        if result == 0:
            # Same qualifier type; compare qualifier details
            qual_cmp = _QUALIFIER_COMPARATORS.get(qual1_type)
            if qual_cmp:
                result = qual_cmp(expr1.qualifier, expr2.qualifier)
            else:
                raise TypeError(
                    "Can't compare qualifier type: " + qual1_type.__name__,
                )

        if result == 0:
            # Same qualifier type and details; use qualified expression order
            result = observation_expression_cmp(
                expr1.observation_expression, expr2.observation_expression,
            )

    return result
