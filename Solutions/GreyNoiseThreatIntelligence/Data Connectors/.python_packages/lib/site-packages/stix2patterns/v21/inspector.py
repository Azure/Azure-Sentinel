from ..inspector import INDEX_STAR, _PatternData, _string_literal_to_string
from .grammars.STIXPatternListener import STIXPatternListener


class InspectionListener(STIXPatternListener):
    """This listener collects info about a pattern and puts it
    in a python structure.  It is intended to assist apps which wish to
    look "inside" a pattern and know what's in there.
    """

    def __init__(self):
        self.__comparison_data = {}
        self.__qualifiers = set()
        self.__observation_ops = set()
        self.__obj_type = None
        self.__obj_path = None

    def pattern_data(self):
        return _PatternData(self.__comparison_data, self.__observation_ops,
                            self.__qualifiers)

    def __add_prop_tuple(self, obj_type, obj_path, op, value):
        if obj_type not in self.__comparison_data:
            self.__comparison_data[obj_type] = []

        self.__comparison_data[obj_type].append((obj_path, op, value))

    def exitObservationExpressions(self, ctx):
        if ctx.FOLLOWEDBY():
            self.__observation_ops.add(u"FOLLOWEDBY")

    def exitObservationExpressionOr(self, ctx):
        if ctx.OR():
            self.__observation_ops.add(u"OR")

    def exitObservationExpressionAnd(self, ctx):
        if ctx.AND():
            self.__observation_ops.add(u"AND")

    def exitStartStopQualifier(self, ctx):
        self.__qualifiers.add(
            u"START {0} STOP {1}".format(
                ctx.TimestampLiteral(0), ctx.TimestampLiteral(1)
            )
        )

    def exitWithinQualifier(self, ctx):
        self.__qualifiers.add(
            u"WITHIN {0} SECONDS".format(
                ctx.IntPosLiteral() or ctx.FloatPosLiteral()
            )
        )

    def exitRepeatedQualifier(self, ctx):
        self.__qualifiers.add(
            u"REPEATS {0} TIMES".format(
                ctx.IntPosLiteral()
            )
        )

    def exitPropTestEqual(self, ctx):
        op_tok = ctx.EQ() or ctx.NEQ()
        op_str = u"NOT " if ctx.NOT() else u""
        op_str += op_tok.getText()

        value = ctx.primitiveLiteral().getText()

        self.__add_prop_tuple(self.__obj_type, self.__obj_path, op_str,
                              value)

    def exitPropTestOrder(self, ctx):
        op_tok = ctx.GT() or ctx.LT() or ctx.GE() or ctx.LE()
        op_str = u"NOT " if ctx.NOT() else u""
        op_str += op_tok.getText()

        value = ctx.orderableLiteral().getText()

        self.__add_prop_tuple(self.__obj_type, self.__obj_path, op_str,
                              value)

    def exitPropTestSet(self, ctx):
        op_str = u"NOT " if ctx.NOT() else u""
        op_str += u"IN"

        value = ctx.setLiteral().getText()

        self.__add_prop_tuple(self.__obj_type, self.__obj_path, op_str,
                              value)

    def exitPropTestLike(self, ctx):
        op_str = u"NOT " if ctx.NOT() else u""
        op_str += u"LIKE"

        value = ctx.StringLiteral().getText()

        self.__add_prop_tuple(self.__obj_type, self.__obj_path, op_str,
                              value)

    def exitPropTestRegex(self, ctx):
        op_str = u"NOT " if ctx.NOT() else u""
        op_str += u"MATCHES"

        value = ctx.StringLiteral().getText()

        self.__add_prop_tuple(self.__obj_type, self.__obj_path, op_str,
                              value)

    def exitPropTestIsSubset(self, ctx):
        op_str = u"NOT " if ctx.NOT() else u""
        op_str += u"ISSUBSET"

        value = ctx.StringLiteral().getText()

        self.__add_prop_tuple(self.__obj_type, self.__obj_path, op_str,
                              value)

    def exitPropTestIsSuperset(self, ctx):
        op_str = u"NOT " if ctx.NOT() else u""
        op_str += u"ISSUPERSET"

        value = ctx.StringLiteral().getText()

        self.__add_prop_tuple(self.__obj_type, self.__obj_path, op_str,
                              value)

    def exitObjectType(self, ctx):
        self.__obj_type = ctx.getText()

    def exitFirstPathComponent(self, ctx):
        if ctx.StringLiteral():
            path_component = _string_literal_to_string(ctx.StringLiteral())
        else:
            path_component = ctx.getText()

        self.__obj_path = [path_component]

    def exitKeyPathStep(self, ctx):
        if ctx.IdentifierWithoutHyphen():
            path_component = ctx.IdentifierWithoutHyphen().getText()
        else:  # A StringLiteral
            path_component = _string_literal_to_string(ctx.StringLiteral())

        self.__obj_path.append(path_component)

    def exitIndexPathStep(self, ctx):
        if ctx.ASTERISK():
            self.__obj_path.append(INDEX_STAR)
        else:
            self.__obj_path.append(int(ctx.IntPosLiteral().getText()))
