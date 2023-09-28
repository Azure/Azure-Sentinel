"""
Some generic comparison utility functions.

.. autosummary::
   :toctree: compare

   comparison
   observation

|
"""


def generic_cmp(value1, value2):
    """
    Generic comparator of values which uses the builtin '<' and '>' operators.
    Assumes the values can be compared that way.

    Args:
        value1: The first value
        value2: The second value

    Returns:
        -1, 0, or 1 depending on whether value1 is less, equal, or greater
        than value2
    """

    return -1 if value1 < value2 else 1 if value1 > value2 else 0


def iter_lex_cmp(seq1, seq2, cmp):
    """
    Generic lexicographical compare function, which works on two iterables and
    a comparator function.

    Args:
        seq1: The first iterable
        seq2: The second iterable
        cmp: a two-arg callable comparator for values iterated over.  It
            must behave analogously to this function, returning <0, 0, or >0 to
            express the ordering of the two values.

    Returns:
        <0 if seq1 < seq2; >0 if seq1 > seq2; 0 if they're equal
    """

    it1 = iter(seq1)
    it2 = iter(seq2)

    it1_exhausted = it2_exhausted = False
    while True:
        try:
            val1 = next(it1)
        except StopIteration:
            it1_exhausted = True

        try:
            val2 = next(it2)
        except StopIteration:
            it2_exhausted = True

        # same length, all elements equal
        if it1_exhausted and it2_exhausted:
            result = 0
            break

        # one is a prefix of the other; the shorter one is less
        elif it1_exhausted:
            result = -1
            break

        elif it2_exhausted:
            result = 1
            break

        # neither is exhausted; check values
        else:
            val_cmp = cmp(val1, val2)

            if val_cmp != 0:
                result = val_cmp
                break

    return result


def iter_in(value, seq, cmp):
    """
    A function behaving like the "in" Python operator, but which works with a
    a comparator function.  This function checks whether the given value is
    contained in the given iterable.

    Args:
        value: A value
        seq: An iterable
        cmp: A 2-arg comparator function which must return 0 if the args
            are equal

    Returns:
        True if the value is found in the iterable, False if it is not
    """
    result = False
    for seq_val in seq:
        if cmp(value, seq_val) == 0:
            result = True
            break

    return result
