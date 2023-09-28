import collections


class InspectionException(Exception):
    """Represents a error that occurred during inspection."""
    pass


_PatternData = collections.namedtuple("pattern_data",
                                      "comparisons observation_ops qualifiers")


# For representing a "star" array index step in an object path
INDEX_STAR = object()


def _string_literal_to_string(string_literal_token):
    """Converts the StringLiteral token to a plain string: get text content,
    removes quote characters, and unescapes it.

    :param string_literal_token: The string literal
    :return:
    """
    token_text = string_literal_token.getText()
    return token_text[1:-1].replace(u"\\'", u"'"). \
        replace(u"\\\\", u"\\")
