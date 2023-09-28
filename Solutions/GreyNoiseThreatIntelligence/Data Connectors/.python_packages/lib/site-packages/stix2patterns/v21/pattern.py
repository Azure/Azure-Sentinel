import antlr4
import six

from ..exceptions import ParseException, ParserErrorListener
from .grammars.STIXPatternLexer import STIXPatternLexer
from .grammars.STIXPatternParser import STIXPatternParser
from .inspector import InspectionListener


class Pattern(object):
    """
    Represents a pattern in a "compiled" form, for more efficient reuse.
    """
    def __init__(self, pattern_str):
        """
        Compile a pattern.

        :param pattern_str: The pattern to compile
        :raises ParseException: If there is a parse error
        """
        self.__parse_tree = self.__do_parse(pattern_str)

    def inspect(self):
        """
        Inspect a pattern.  This gives information regarding the sorts of
        operations, content, etc in use in the pattern.

        :return: Pattern information
        """

        inspector = InspectionListener()
        self.walk(inspector)

        return inspector.pattern_data()

    def walk(self, listener):
        """Walk the parse tree, using the given listener.  The listener
        should be a
        stix2patterns.grammars.STIXPatternListener.STIXPatternListener (or
        subclass) instance."""
        antlr4.ParseTreeWalker.DEFAULT.walk(listener, self.__parse_tree)

    def visit(self, visitor):
        """
        Walk the parse tree using the given visitor.

        :param visitor: A visitor object (STIXPatternVisitor instance)
        :return: The visitor's return value
        """
        return visitor.visit(self.__parse_tree)

    def __do_parse(self, pattern_str):
        """
        Parses the given pattern and returns the antlr parse tree.

        :param pattern_str: The STIX pattern
        :return: The parse tree
        :raises ParseException: If there is a parse error
        """
        in_ = antlr4.InputStream(pattern_str)
        lexer = STIXPatternLexer(in_)
        lexer.removeErrorListeners()  # remove the default "console" listener
        token_stream = antlr4.CommonTokenStream(lexer)

        parser = STIXPatternParser(token_stream)
        parser.removeErrorListeners()  # remove the default "console" listener
        error_listener = ParserErrorListener()
        parser.addErrorListener(error_listener)

        # I found no public API for this...
        # The default error handler tries to keep parsing, and I don't
        # think that's appropriate here.  (These error handlers are only for
        # handling the built-in RecognitionException errors.)
        parser._errHandler = antlr4.BailErrorStrategy()

        # To improve error messages, replace "<INVALID>" in the literal
        # names with symbolic names.  This is a hack, but seemed like
        # the simplest workaround.
        for i, lit_name in enumerate(parser.literalNames):
            if lit_name == u"<INVALID>":
                parser.literalNames[i] = parser.symbolicNames[i]

        # parser.setTrace(True)

        try:
            tree = parser.pattern()
            # print(tree.toStringTree(recog=parser))

            return tree
        except antlr4.error.Errors.ParseCancellationException as e:
            # The cancellation exception wraps the real RecognitionException
            # which caused the parser to bail.
            real_exc = e.args[0]

            # I want to bail when the first error is hit.  But I also want
            # a decent error message.  When an error is encountered in
            # Parser.match(), the BailErrorStrategy produces the
            # ParseCancellationException.  It is not a subclass of
            # RecognitionException, so none of the 'except' clauses which would
            # normally report an error are invoked.
            #
            # Error message creation is buried in the ErrorStrategy, and I can
            # (ab)use the API to get a message: register an error listener with
            # the parser, force an error report, then get the message out of the
            # listener.  Error listener registration is above; now we force its
            # invocation.  Wish this could be cleaner...
            parser._errHandler.reportError(parser, real_exc)

            # should probably chain exceptions if we can...
            # Should I report the cancellation or recognition exception as the
            # cause...?
            six.raise_from(ParseException(error_listener.error_message),
                           real_exc)
