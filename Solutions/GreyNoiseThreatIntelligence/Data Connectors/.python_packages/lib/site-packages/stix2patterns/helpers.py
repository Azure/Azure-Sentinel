import six


def brackets_check(pattern):
    """
    Check whether the pattern is missing square brackets, in a way which does
    not require the usual parsing.  This is a light hack to provide an improved
    error message in this particular case.

    :param pattern: A STIX pattern string
    :return: True if the pattern had its brackets; False if not
    """
    if isinstance(pattern, six.string_types):

        # There can be an arbitrary number of open parens first... skip over
        # those
        for c in pattern:
            if c != "(" and not c.isspace():
                break

        if c == "[":
            result = True
        else:
            result = False

    else:
        result = False

    return result
