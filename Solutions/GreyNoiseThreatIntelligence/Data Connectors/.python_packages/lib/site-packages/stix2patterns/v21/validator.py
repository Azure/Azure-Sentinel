"""
Validates a user entered pattern against STIXPattern grammar.
"""

import enum

from antlr4 import CommonTokenStream, ParseTreeWalker

from . import object_validator
from ..exceptions import STIXPatternErrorListener
from .grammars.STIXPatternLexer import STIXPatternLexer
from .grammars.STIXPatternListener import STIXPatternListener
from .grammars.STIXPatternParser import STIXPatternParser
from .inspector import InspectionListener

QualType = enum.Enum("QualType", "WITHIN REPEATS STARTSTOP")


class DuplicateQualifierTypeError(Exception):
    """
    Instances represent finding multiple qualifiers of the same type directly
    applied to an observation expression (i.e. not on some parenthesized group
    of which the observation expression is a member).
    """
    def __init__(self, qual_type):
        """
        Initialize this exception instance.

        :param qual_type: The qualifier type which was found to be duplicated.
            Must be a member of the QualType enum.
        """
        message = "Duplicate qualifier type encountered: " + qual_type.name

        super(DuplicateQualifierTypeError, self).__init__(message)

        self.qual_type = qual_type


class ValidationListener(STIXPatternListener):
    """
    Does some pattern validation via a parse tree traversal.
    """
    def __init__(self):
        self.__qual_types = None

    def __check_qualifier_type(self, qual_type):
        if self.__qual_types is not None:
            if qual_type in self.__qual_types:
                raise DuplicateQualifierTypeError(qual_type)
            else:
                self.__qual_types.add(qual_type)

    def exitObservationExpressionSimple(self, ctx):
        self.__qual_types = set()

    def exitObservationExpressionCompound(self, ctx):
        self.__qual_types = None

    def exitObservationExpressionWithin(self, ctx):
        self.__check_qualifier_type(QualType.WITHIN)

    def exitObservationExpressionRepeated(self, ctx):
        self.__check_qualifier_type(QualType.REPEATS)

    def exitObservationExpressionStartStop(self, ctx):
        self.__check_qualifier_type(QualType.STARTSTOP)


def run_validator(pattern):
    """
    Validates a pattern against the STIX Pattern grammar.  Error messages are
    returned in a list.  The test passed if the returned list is empty.
    """
    parseErrListener = STIXPatternErrorListener()

    lexer = STIXPatternLexer(pattern)
    # it always adds a console listener by default... remove it.
    lexer.removeErrorListeners()

    stream = CommonTokenStream(lexer)

    parser = STIXPatternParser(stream)

    # it always adds a console listener by default... remove it.
    parser.removeErrorListeners()
    parser.addErrorListener(parseErrListener)

    # To improve error messages, replace "<INVALID>" in the literal
    # names with symbolic names.  This is a hack, but seemed like
    # the simplest workaround.
    for i, lit_name in enumerate(parser.literalNames):
        if lit_name == u"<INVALID>":
            parser.literalNames[i] = parser.symbolicNames[i]

    tree = parser.pattern()

    # validate observed objects
    if len(parseErrListener.err_strings) == 0:
        inspection_listener = InspectionListener()
        ParseTreeWalker.DEFAULT.walk(inspection_listener, tree)
        patt_data = inspection_listener.pattern_data()

        # check objects
        obj_validator_results = object_validator.verify_object(patt_data)
        if obj_validator_results:
            parseErrListener.err_strings.extend(obj_validator_results)

        # check qualifiers
        try:
            ParseTreeWalker.DEFAULT.walk(ValidationListener(), tree)
        except DuplicateQualifierTypeError as e:
            parseErrListener.err_strings.insert(0, "FAIL: " + e.args[0])

    return parseErrListener.err_strings
