# Generated from STIXPattern.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .STIXPatternParser import STIXPatternParser
else:
    from STIXPatternParser import STIXPatternParser

# This class defines a complete generic visitor for a parse tree produced by STIXPatternParser.

class STIXPatternVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by STIXPatternParser#pattern.
    def visitPattern(self, ctx:STIXPatternParser.PatternContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#observationExpressions.
    def visitObservationExpressions(self, ctx:STIXPatternParser.ObservationExpressionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#observationExpressionOr.
    def visitObservationExpressionOr(self, ctx:STIXPatternParser.ObservationExpressionOrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#observationExpressionAnd.
    def visitObservationExpressionAnd(self, ctx:STIXPatternParser.ObservationExpressionAndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#observationExpressionRepeated.
    def visitObservationExpressionRepeated(self, ctx:STIXPatternParser.ObservationExpressionRepeatedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#observationExpressionSimple.
    def visitObservationExpressionSimple(self, ctx:STIXPatternParser.ObservationExpressionSimpleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#observationExpressionCompound.
    def visitObservationExpressionCompound(self, ctx:STIXPatternParser.ObservationExpressionCompoundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#observationExpressionWithin.
    def visitObservationExpressionWithin(self, ctx:STIXPatternParser.ObservationExpressionWithinContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#observationExpressionStartStop.
    def visitObservationExpressionStartStop(self, ctx:STIXPatternParser.ObservationExpressionStartStopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#comparisonExpression.
    def visitComparisonExpression(self, ctx:STIXPatternParser.ComparisonExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#comparisonExpressionAnd.
    def visitComparisonExpressionAnd(self, ctx:STIXPatternParser.ComparisonExpressionAndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#propTestEqual.
    def visitPropTestEqual(self, ctx:STIXPatternParser.PropTestEqualContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#propTestOrder.
    def visitPropTestOrder(self, ctx:STIXPatternParser.PropTestOrderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#propTestSet.
    def visitPropTestSet(self, ctx:STIXPatternParser.PropTestSetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#propTestLike.
    def visitPropTestLike(self, ctx:STIXPatternParser.PropTestLikeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#propTestRegex.
    def visitPropTestRegex(self, ctx:STIXPatternParser.PropTestRegexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#propTestIsSubset.
    def visitPropTestIsSubset(self, ctx:STIXPatternParser.PropTestIsSubsetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#propTestIsSuperset.
    def visitPropTestIsSuperset(self, ctx:STIXPatternParser.PropTestIsSupersetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#propTestParen.
    def visitPropTestParen(self, ctx:STIXPatternParser.PropTestParenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#startStopQualifier.
    def visitStartStopQualifier(self, ctx:STIXPatternParser.StartStopQualifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#withinQualifier.
    def visitWithinQualifier(self, ctx:STIXPatternParser.WithinQualifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#repeatedQualifier.
    def visitRepeatedQualifier(self, ctx:STIXPatternParser.RepeatedQualifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#objectPath.
    def visitObjectPath(self, ctx:STIXPatternParser.ObjectPathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#objectType.
    def visitObjectType(self, ctx:STIXPatternParser.ObjectTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#firstPathComponent.
    def visitFirstPathComponent(self, ctx:STIXPatternParser.FirstPathComponentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#indexPathStep.
    def visitIndexPathStep(self, ctx:STIXPatternParser.IndexPathStepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#pathStep.
    def visitPathStep(self, ctx:STIXPatternParser.PathStepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#keyPathStep.
    def visitKeyPathStep(self, ctx:STIXPatternParser.KeyPathStepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#setLiteral.
    def visitSetLiteral(self, ctx:STIXPatternParser.SetLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#primitiveLiteral.
    def visitPrimitiveLiteral(self, ctx:STIXPatternParser.PrimitiveLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#orderableLiteral.
    def visitOrderableLiteral(self, ctx:STIXPatternParser.OrderableLiteralContext):
        return self.visitChildren(ctx)



del STIXPatternParser