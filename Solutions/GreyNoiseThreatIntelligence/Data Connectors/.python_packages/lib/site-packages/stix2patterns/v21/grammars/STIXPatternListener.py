# Generated from STIXPattern.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .STIXPatternParser import STIXPatternParser
else:
    from STIXPatternParser import STIXPatternParser

# This class defines a complete listener for a parse tree produced by STIXPatternParser.
class STIXPatternListener(ParseTreeListener):

    # Enter a parse tree produced by STIXPatternParser#pattern.
    def enterPattern(self, ctx:STIXPatternParser.PatternContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#pattern.
    def exitPattern(self, ctx:STIXPatternParser.PatternContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#observationExpressions.
    def enterObservationExpressions(self, ctx:STIXPatternParser.ObservationExpressionsContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#observationExpressions.
    def exitObservationExpressions(self, ctx:STIXPatternParser.ObservationExpressionsContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#observationExpressionOr.
    def enterObservationExpressionOr(self, ctx:STIXPatternParser.ObservationExpressionOrContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#observationExpressionOr.
    def exitObservationExpressionOr(self, ctx:STIXPatternParser.ObservationExpressionOrContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#observationExpressionAnd.
    def enterObservationExpressionAnd(self, ctx:STIXPatternParser.ObservationExpressionAndContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#observationExpressionAnd.
    def exitObservationExpressionAnd(self, ctx:STIXPatternParser.ObservationExpressionAndContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#observationExpressionRepeated.
    def enterObservationExpressionRepeated(self, ctx:STIXPatternParser.ObservationExpressionRepeatedContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#observationExpressionRepeated.
    def exitObservationExpressionRepeated(self, ctx:STIXPatternParser.ObservationExpressionRepeatedContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#observationExpressionSimple.
    def enterObservationExpressionSimple(self, ctx:STIXPatternParser.ObservationExpressionSimpleContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#observationExpressionSimple.
    def exitObservationExpressionSimple(self, ctx:STIXPatternParser.ObservationExpressionSimpleContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#observationExpressionCompound.
    def enterObservationExpressionCompound(self, ctx:STIXPatternParser.ObservationExpressionCompoundContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#observationExpressionCompound.
    def exitObservationExpressionCompound(self, ctx:STIXPatternParser.ObservationExpressionCompoundContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#observationExpressionWithin.
    def enterObservationExpressionWithin(self, ctx:STIXPatternParser.ObservationExpressionWithinContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#observationExpressionWithin.
    def exitObservationExpressionWithin(self, ctx:STIXPatternParser.ObservationExpressionWithinContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#observationExpressionStartStop.
    def enterObservationExpressionStartStop(self, ctx:STIXPatternParser.ObservationExpressionStartStopContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#observationExpressionStartStop.
    def exitObservationExpressionStartStop(self, ctx:STIXPatternParser.ObservationExpressionStartStopContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#comparisonExpression.
    def enterComparisonExpression(self, ctx:STIXPatternParser.ComparisonExpressionContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#comparisonExpression.
    def exitComparisonExpression(self, ctx:STIXPatternParser.ComparisonExpressionContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#comparisonExpressionAnd.
    def enterComparisonExpressionAnd(self, ctx:STIXPatternParser.ComparisonExpressionAndContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#comparisonExpressionAnd.
    def exitComparisonExpressionAnd(self, ctx:STIXPatternParser.ComparisonExpressionAndContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#propTestEqual.
    def enterPropTestEqual(self, ctx:STIXPatternParser.PropTestEqualContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#propTestEqual.
    def exitPropTestEqual(self, ctx:STIXPatternParser.PropTestEqualContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#propTestOrder.
    def enterPropTestOrder(self, ctx:STIXPatternParser.PropTestOrderContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#propTestOrder.
    def exitPropTestOrder(self, ctx:STIXPatternParser.PropTestOrderContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#propTestSet.
    def enterPropTestSet(self, ctx:STIXPatternParser.PropTestSetContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#propTestSet.
    def exitPropTestSet(self, ctx:STIXPatternParser.PropTestSetContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#propTestLike.
    def enterPropTestLike(self, ctx:STIXPatternParser.PropTestLikeContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#propTestLike.
    def exitPropTestLike(self, ctx:STIXPatternParser.PropTestLikeContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#propTestRegex.
    def enterPropTestRegex(self, ctx:STIXPatternParser.PropTestRegexContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#propTestRegex.
    def exitPropTestRegex(self, ctx:STIXPatternParser.PropTestRegexContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#propTestIsSubset.
    def enterPropTestIsSubset(self, ctx:STIXPatternParser.PropTestIsSubsetContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#propTestIsSubset.
    def exitPropTestIsSubset(self, ctx:STIXPatternParser.PropTestIsSubsetContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#propTestIsSuperset.
    def enterPropTestIsSuperset(self, ctx:STIXPatternParser.PropTestIsSupersetContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#propTestIsSuperset.
    def exitPropTestIsSuperset(self, ctx:STIXPatternParser.PropTestIsSupersetContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#propTestParen.
    def enterPropTestParen(self, ctx:STIXPatternParser.PropTestParenContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#propTestParen.
    def exitPropTestParen(self, ctx:STIXPatternParser.PropTestParenContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#propTestExists.
    def enterPropTestExists(self, ctx:STIXPatternParser.PropTestExistsContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#propTestExists.
    def exitPropTestExists(self, ctx:STIXPatternParser.PropTestExistsContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#startStopQualifier.
    def enterStartStopQualifier(self, ctx:STIXPatternParser.StartStopQualifierContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#startStopQualifier.
    def exitStartStopQualifier(self, ctx:STIXPatternParser.StartStopQualifierContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#withinQualifier.
    def enterWithinQualifier(self, ctx:STIXPatternParser.WithinQualifierContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#withinQualifier.
    def exitWithinQualifier(self, ctx:STIXPatternParser.WithinQualifierContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#repeatedQualifier.
    def enterRepeatedQualifier(self, ctx:STIXPatternParser.RepeatedQualifierContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#repeatedQualifier.
    def exitRepeatedQualifier(self, ctx:STIXPatternParser.RepeatedQualifierContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#objectPath.
    def enterObjectPath(self, ctx:STIXPatternParser.ObjectPathContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#objectPath.
    def exitObjectPath(self, ctx:STIXPatternParser.ObjectPathContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#objectType.
    def enterObjectType(self, ctx:STIXPatternParser.ObjectTypeContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#objectType.
    def exitObjectType(self, ctx:STIXPatternParser.ObjectTypeContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#firstPathComponent.
    def enterFirstPathComponent(self, ctx:STIXPatternParser.FirstPathComponentContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#firstPathComponent.
    def exitFirstPathComponent(self, ctx:STIXPatternParser.FirstPathComponentContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#indexPathStep.
    def enterIndexPathStep(self, ctx:STIXPatternParser.IndexPathStepContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#indexPathStep.
    def exitIndexPathStep(self, ctx:STIXPatternParser.IndexPathStepContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#pathStep.
    def enterPathStep(self, ctx:STIXPatternParser.PathStepContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#pathStep.
    def exitPathStep(self, ctx:STIXPatternParser.PathStepContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#keyPathStep.
    def enterKeyPathStep(self, ctx:STIXPatternParser.KeyPathStepContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#keyPathStep.
    def exitKeyPathStep(self, ctx:STIXPatternParser.KeyPathStepContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#setLiteral.
    def enterSetLiteral(self, ctx:STIXPatternParser.SetLiteralContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#setLiteral.
    def exitSetLiteral(self, ctx:STIXPatternParser.SetLiteralContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#primitiveLiteral.
    def enterPrimitiveLiteral(self, ctx:STIXPatternParser.PrimitiveLiteralContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#primitiveLiteral.
    def exitPrimitiveLiteral(self, ctx:STIXPatternParser.PrimitiveLiteralContext):
        pass


    # Enter a parse tree produced by STIXPatternParser#orderableLiteral.
    def enterOrderableLiteral(self, ctx:STIXPatternParser.OrderableLiteralContext):
        pass

    # Exit a parse tree produced by STIXPatternParser#orderableLiteral.
    def exitOrderableLiteral(self, ctx:STIXPatternParser.OrderableLiteralContext):
        pass



del STIXPatternParser