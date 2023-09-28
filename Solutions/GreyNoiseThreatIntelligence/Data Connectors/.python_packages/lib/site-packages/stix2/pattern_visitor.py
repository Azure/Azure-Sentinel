"""STIX2 classes and methods to generate AST from patterns"""

import importlib
import inspect

from stix2patterns.exceptions import ParseException
from stix2patterns.grammars.STIXPatternParser import TerminalNode
from stix2patterns.v20.grammars.STIXPatternParser import \
    STIXPatternParser as STIXPatternParser20
from stix2patterns.v20.grammars.STIXPatternVisitor import \
    STIXPatternVisitor as STIXPatternVisitor20
from stix2patterns.v20.pattern import Pattern as Pattern20
from stix2patterns.v21.grammars.STIXPatternParser import \
    STIXPatternParser as STIXPatternParser21
from stix2patterns.v21.grammars.STIXPatternVisitor import \
    STIXPatternVisitor as STIXPatternVisitor21
from stix2patterns.v21.pattern import Pattern as Pattern21

from .patterns import *
from .patterns import _BooleanExpression
from .version import DEFAULT_VERSION

# flake8: noqa F405


def collapse_lists(lists):
    result = []
    for c in lists:
        if isinstance(c, list):
            result.extend(c)
        else:
            result.append(c)
    return result


def remove_terminal_nodes(parse_tree_nodes):
    values = []
    for x in parse_tree_nodes:
        if not isinstance(x, TerminalNode):
            values.append(x)
    return values


_TIMESTAMP_RE = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?Z')


def check_for_valid_timetamp_syntax(timestamp_string):
    return _TIMESTAMP_RE.match(timestamp_string)


def same_boolean_operator(current_op, op_token):
    return current_op == op_token.getText()


class STIXPatternVisitorForSTIX2():
    classes = {}

    def get_class(self, class_name):
        if class_name in STIXPatternVisitorForSTIX2.classes:
            return STIXPatternVisitorForSTIX2.classes[class_name]
        else:
            return None

    def instantiate(self, klass_name, *args):
        klass_to_instantiate = None
        if self.module_suffix:
            klass_to_instantiate = self.get_class(klass_name + "For" + self.module_suffix)
        if not klass_to_instantiate:
            # use the classes in python_stix2
            klass_to_instantiate = globals()[klass_name]
        return klass_to_instantiate(*args)

    # Visit a parse tree produced by STIXPatternParser#pattern.
    def visitPattern(self, ctx):
        children = self.visitChildren(ctx)
        return children[0]

    # Visit a parse tree produced by STIXPatternParser#observationExpressions.
    def visitObservationExpressions(self, ctx):
        children = self.visitChildren(ctx)
        if len(children) == 1:
            return children[0]
        else:
            return FollowedByObservationExpression([children[0], children[2]])

    # Visit a parse tree produced by STIXPatternParser#observationExpressionOr.
    def visitObservationExpressionOr(self, ctx):
        children = self.visitChildren(ctx)
        if len(children) == 1:
            return children[0]
        else:
            return self.instantiate("OrObservationExpression", [children[0], children[2]])

    # Visit a parse tree produced by STIXPatternParser#observationExpressionAnd.
    def visitObservationExpressionAnd(self, ctx):
        children = self.visitChildren(ctx)
        if len(children) == 1:
            return children[0]
        else:
            return self.instantiate("AndObservationExpression", [children[0], children[2]])

    # Visit a parse tree produced by STIXPatternParser#observationExpressionRepeated.
    def visitObservationExpressionRepeated(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("QualifiedObservationExpression", children[0], children[1])

    # Visit a parse tree produced by STIXPatternParser#observationExpressionSimple.
    def visitObservationExpressionSimple(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("ObservationExpression", children[1])

    # Visit a parse tree produced by STIXPatternParser#observationExpressionCompound.
    def visitObservationExpressionCompound(self, ctx):
        children = self.visitChildren(ctx)
        if isinstance(children[0], TerminalNode) and children[0].symbol.type == self.parser_class.LPAREN:
            return self.instantiate("ParentheticalExpression", children[1])
        else:
            return self.instantiate("ObservationExpression", children[0])

    # Visit a parse tree produced by STIXPatternParser#observationExpressionWithin.
    def visitObservationExpressionWithin(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("QualifiedObservationExpression", children[0], children[1])

    # Visit a parse tree produced by STIXPatternParser#observationExpressionStartStop.
    def visitObservationExpressionStartStop(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("QualifiedObservationExpression", children[0], children[1])

    # Visit a parse tree produced by STIXPatternParser#comparisonExpression.
    def visitComparisonExpression(self, ctx):
        children = self.visitChildren(ctx)
        if len(children) == 1:
            return children[0]
        else:
            if isinstance(children[0], _BooleanExpression) and same_boolean_operator(children[0].operator, children[1]):
                children[0].operands.append(children[2])
                return children[0]
            else:
                return self.instantiate("OrBooleanExpression", [children[0], children[2]])

    # Visit a parse tree produced by STIXPatternParser#comparisonExpressionAnd.
    def visitComparisonExpressionAnd(self, ctx):
        # TODO: NOT
        children = self.visitChildren(ctx)
        if len(children) == 1:
            return children[0]
        else:
            if isinstance(children[0], _BooleanExpression):
                children[0].operands.append(children[2])
                return children[0]
            else:
                return self.instantiate("AndBooleanExpression", [children[0], children[2]])

    # Visit a parse tree produced by STIXPatternParser#propTestEqual.
    def visitPropTestEqual(self, ctx):
        children = self.visitChildren(ctx)
        operator = children[1].symbol.type
        negated = operator != self.parser_class.EQ
        return self.instantiate(
            "EqualityComparisonExpression", children[0], children[3 if len(children) > 3 else 2],
            negated,
        )

    # Visit a parse tree produced by STIXPatternParser#propTestOrder.
    def visitPropTestOrder(self, ctx):
        children = self.visitChildren(ctx)
        operator = children[1].symbol.type
        if operator == self.parser_class.GT:
            return self.instantiate(
                "GreaterThanComparisonExpression", children[0],
                children[3 if len(children) > 3 else 2], False,
            )
        elif operator == self.parser_class.LT:
            return self.instantiate(
                "LessThanComparisonExpression", children[0],
                children[3 if len(children) > 3 else 2], False,
            )
        elif operator == self.parser_class.GE:
            return self.instantiate(
                "GreaterThanEqualComparisonExpression", children[0],
                children[3 if len(children) > 3 else 2], False,
            )
        elif operator == self.parser_class.LE:
            return self.instantiate(
                "LessThanEqualComparisonExpression", children[0],
                children[3 if len(children) > 3 else 2], False,
            )

    # Visit a parse tree produced by STIXPatternParser#propTestSet.
    def visitPropTestSet(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("InComparisonExpression", children[0], children[3 if len(children) > 3 else 2], False)

    # Visit a parse tree produced by STIXPatternParser#propTestLike.
    def visitPropTestLike(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("LikeComparisonExpression", children[0], children[3 if len(children) > 3 else 2], False)

    # Visit a parse tree produced by STIXPatternParser#propTestRegex.
    def visitPropTestRegex(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate(
            "MatchesComparisonExpression", children[0], children[3 if len(children) > 3 else 2],
            False,
        )

    # Visit a parse tree produced by STIXPatternParser#propTestIsSubset.
    def visitPropTestIsSubset(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("IsSubsetComparisonExpression", children[0], children[3 if len(children) > 3 else 2])

    # Visit a parse tree produced by STIXPatternParser#propTestIsSuperset.
    def visitPropTestIsSuperset(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("IsSupersetComparisonExpression", children[0], children[3 if len(children) > 3 else 2])

    # Visit a parse tree produced by STIXPatternParser#propTestParen.
    def visitPropTestParen(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("ParentheticalExpression", children[1])

    # Visit a parse tree produced by STIXPatternParser#startStopQualifier.
    def visitStartStopQualifier(self, ctx):
        children = self.visitChildren(ctx)
        # 2.0 parser will accept any string, need to make sure it is a full STIX timestamp
        if isinstance(children[1], StringConstant):
            if not check_for_valid_timetamp_syntax(children[1].value):
                raise (ValueError("Start time is not a legal timestamp"))
        if isinstance(children[3], StringConstant):
            if not check_for_valid_timetamp_syntax(children[3].value):
                raise (ValueError("Stop time is not a legal timestamp"))

        return StartStopQualifier(children[1], children[3])

    # Visit a parse tree produced by STIXPatternParser#withinQualifier.
    def visitWithinQualifier(self, ctx):
        children = self.visitChildren(ctx)
        return WithinQualifier(children[1])

    # Visit a parse tree produced by STIXPatternParser#repeatedQualifier.
    def visitRepeatedQualifier(self, ctx):
        children = self.visitChildren(ctx)
        return RepeatQualifier(children[1])

    # Visit a parse tree produced by STIXPatternParser#objectPath.
    def visitObjectPath(self, ctx):
        children = self.visitChildren(ctx)
        flat_list = collapse_lists(children[2:])
        property_path = []
        i = 0
        while i < len(flat_list):
            current = flat_list[i]
            if i == len(flat_list)-1:
                property_path.append(current)
                break
            next = flat_list[i+1]
            if isinstance(next, TerminalNode):
                property_path.append(self.instantiate("ListObjectPathComponent", current.property_name, next.getText()))
                i += 2
            elif isinstance(next, IntegerConstant):
                property_path.append(
                    self.instantiate(
                        "ListObjectPathComponent",
                        current.property_name if isinstance(current, BasicObjectPathComponent) else str(current),
                        next.value,
                    ),
                )
                i += 2
            else:
                property_path.append(current)
                i += 1
        return self.instantiate("ObjectPath", children[0].getText(), property_path)

    # Visit a parse tree produced by STIXPatternParser#objectType.
    def visitObjectType(self, ctx):
        children = self.visitChildren(ctx)
        return children[0]

    # Visit a parse tree produced by STIXPatternParser#firstPathComponent.
    def visitFirstPathComponent(self, ctx):
        children = self.visitChildren(ctx)
        first_component = children[0]
        # hack for when the first component isn't a TerminalNode (see issue #438)
        if isinstance(first_component, TerminalNode):
            step = first_component.getText()
        else:
            step = str(first_component)
        # if step.endswith("_ref"):
        #     return stix2.ReferenceObjectPathComponent(step)
        # else:
        return self.instantiate("BasicObjectPathComponent", step, False)

    # Visit a parse tree produced by STIXPatternParser#indexPathStep.
    def visitIndexPathStep(self, ctx):
        children = self.visitChildren(ctx)
        return children[1]

    # Visit a parse tree produced by STIXPatternParser#pathStep.
    def visitPathStep(self, ctx):
        return collapse_lists(self.visitChildren(ctx))

    # Visit a parse tree produced by STIXPatternParser#keyPathStep.
    def visitKeyPathStep(self, ctx):
        children = self.visitChildren(ctx)
        if isinstance(children[1], StringConstant):
            # special case for hashes and quoted steps
            return children[1]
        else:
            return self.instantiate("BasicObjectPathComponent", children[1].getText(), True)

    # Visit a parse tree produced by STIXPatternParser#setLiteral.
    def visitSetLiteral(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("ListConstant", remove_terminal_nodes(children))

    # Visit a parse tree produced by STIXPatternParser#primitiveLiteral.
    def visitPrimitiveLiteral(self, ctx):
        children = self.visitChildren(ctx)
        return children[0]

    # Visit a parse tree produced by STIXPatternParser#orderableLiteral.
    def visitOrderableLiteral(self, ctx):
        children = self.visitChildren(ctx)
        return children[0]

    def visitTerminal(self, node):
        if node.symbol.type == self.parser_class.IntPosLiteral or node.symbol.type == self.parser_class.IntNegLiteral:
            return IntegerConstant(node.getText())
        elif node.symbol.type == self.parser_class.FloatPosLiteral or node.symbol.type == self.parser_class.FloatNegLiteral:
            return FloatConstant(node.getText())
        elif node.symbol.type == self.parser_class.HexLiteral:
            return HexConstant(node.getText(), from_parse_tree=True)
        elif node.symbol.type == self.parser_class.BinaryLiteral:
            return BinaryConstant(node.getText(), from_parse_tree=True)
        elif node.symbol.type == self.parser_class.StringLiteral:
            if node.getText()[0] == "'" and node.getText()[-1] == "'":
                return StringConstant(node.getText()[1:-1], from_parse_tree=True)
            else:
                raise ParseException("The pattern does not start and end with a single quote")
        elif node.symbol.type == self.parser_class.BoolLiteral:
            return BooleanConstant(node.getText())
        elif node.symbol.type == self.parser_class.TimestampLiteral:
            value = node.getText()
            # STIX 2.1 uses a special timestamp literal syntax
            if value.startswith("t"):
                value = value[2:-1]
            return TimestampConstant(value)
        else:
            return node

    def aggregateResult(self, aggregate, nextResult):
        if aggregate:
            aggregate.append(nextResult)
        elif nextResult:
            aggregate = [nextResult]
        return aggregate

# This class defines a complete generic visitor for a parse tree produced by STIXPatternParser.
class STIXPatternVisitorForSTIX21(STIXPatternVisitorForSTIX2, STIXPatternVisitor21):
    classes = {}

    def __init__(self, module_suffix, module_name):
        if module_suffix and module_name:
            self.module_suffix = module_suffix
            if not STIXPatternVisitorForSTIX2.classes:
                module = importlib.import_module(module_name)
                for k, c in inspect.getmembers(module, inspect.isclass):
                    STIXPatternVisitorForSTIX2.classes[k] = c
        else:
            self.module_suffix = None
        self.parser_class = STIXPatternParser21
        super(STIXPatternVisitor21, self).__init__()


class STIXPatternVisitorForSTIX20(STIXPatternVisitorForSTIX2, STIXPatternVisitor20):
    classes = {}

    def __init__(self, module_suffix, module_name):
        if module_suffix and module_name:
            self.module_suffix = module_suffix
            if not STIXPatternVisitorForSTIX2.classes:
                module = importlib.import_module(module_name)
                for k, c in inspect.getmembers(module, inspect.isclass):
                    STIXPatternVisitorForSTIX2.classes[k] = c
        else:
            self.module_suffix = None
        self.parser_class = STIXPatternParser20
        super(STIXPatternVisitor20, self).__init__()


def create_pattern_object(pattern, module_suffix="", module_name="", version=DEFAULT_VERSION):
    """
    Create a STIX pattern AST from a pattern string.
    """

    if version == "2.1":
        pattern_class = Pattern21
        visitor_class = STIXPatternVisitorForSTIX21
    else:
        pattern_class = Pattern20
        visitor_class = STIXPatternVisitorForSTIX20

    pattern_obj = pattern_class(pattern)
    builder = visitor_class(module_suffix, module_name)
    return pattern_obj.visit(builder)
