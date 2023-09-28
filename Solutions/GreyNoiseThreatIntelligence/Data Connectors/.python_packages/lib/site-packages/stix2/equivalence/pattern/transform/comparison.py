"""
Transformation utilities for STIX pattern comparison expressions.
"""
import functools
import itertools

from stix2.equivalence.pattern.compare import iter_in, iter_lex_cmp
from stix2.equivalence.pattern.compare.comparison import (
    comparison_expression_cmp,
)
from stix2.equivalence.pattern.transform import Transformer
from stix2.equivalence.pattern.transform.specials import (
    ipv4_addr, ipv6_addr, windows_reg_key,
)
from stix2.patterns import (
    AndBooleanExpression, OrBooleanExpression, ParentheticalExpression,
    _BooleanExpression, _ComparisonExpression,
)


def _dupe_ast(ast):
    """
    Create a duplicate of the given AST.

    Note:
        The comparison expression "leaves", i.e. simple <path> <op> <value>
        comparisons are currently not duplicated.  I don't think it's necessary
        as of this writing; they are never changed.  But revisit this if/when
        necessary.

    Args:
        ast: The AST to duplicate

    Returns:
        The duplicate AST
    """
    if isinstance(ast, AndBooleanExpression):
        result = AndBooleanExpression([
            _dupe_ast(operand) for operand in ast.operands
        ])

    elif isinstance(ast, OrBooleanExpression):
        result = OrBooleanExpression([
            _dupe_ast(operand) for operand in ast.operands
        ])

    elif isinstance(ast, _ComparisonExpression):
        # Change this to create a dupe, if we ever need to change simple
        # comparison expressions as part of normalization.
        result = ast

    else:
        raise TypeError("Can't duplicate " + type(ast).__name__)

    return result


class ComparisonExpressionTransformer(Transformer):
    """
    Transformer base class with special support for transforming comparison
    expressions.  The transform method implemented here performs a bottom-up
    in-place transformation, with support for some comparison
    expression-specific callbacks.

    Specifically, subclasses can implement methods:
        "transform_or" for OR nodes
        "transform_and" for AND nodes
        "transform_comparison" for plain comparison nodes (<prop> <op> <value>)
        "transform_default" for both types of nodes

    "transform_default" is a fallback, if a type-specific callback is not
    found.  The default implementation does nothing to the AST.  The
    type-specific callbacks are preferred over the default, if both exist.

    In all cases, the callbacks are called with an AST for a subtree rooted at
    the appropriate node type, where the subtree's children have already been
    transformed.  They must return the same thing as the base transform()
    method: a 2-tuple with the transformed AST and a boolean for change
    detection.  See doc for the superclass' method.

    This process currently silently drops parenthetical nodes.
    """

    def transform(self, ast):
        if isinstance(ast, _BooleanExpression):
            changed = False
            for i, operand in enumerate(ast.operands):
                operand_result, this_changed = self.transform(operand)
                if this_changed:
                    changed = True

                ast.operands[i] = operand_result

            result, this_changed = self.__dispatch_transform(ast)
            if this_changed:
                changed = True

        elif isinstance(ast, _ComparisonExpression):
            result, changed = self.__dispatch_transform(ast)

        elif isinstance(ast, ParentheticalExpression):
            # Drop these
            result, changed = self.transform(ast.expression)

        else:
            raise TypeError("Not a comparison expression: " + str(ast))

        return result, changed

    def __dispatch_transform(self, ast):
        """
        Invoke a transformer callback method based on the given ast root node
        type.

        Args:
            ast: The AST

        Returns:
            The callback's result
        """

        if isinstance(ast, AndBooleanExpression):
            meth = getattr(self, "transform_and", self.transform_default)

        elif isinstance(ast, OrBooleanExpression):
            meth = getattr(self, "transform_or", self.transform_default)

        elif isinstance(ast, _ComparisonExpression):
            meth = getattr(
                self, "transform_comparison", self.transform_default,
            )

        else:
            meth = self.transform_default

        return meth(ast)

    def transform_default(self, ast):
        """
        Override to handle transforming AST nodes which don't have a more
        specific method implemented.
        """
        return ast, False


class OrderDedupeTransformer(
    ComparisonExpressionTransformer,
):
    """
    Order the children of all nodes in the AST.  Because the deduping algorithm
    is based on sorted data, this transformation also does deduping.

    E.g.:
        A and A => A
        A or A => A
    """

    def __transform(self, ast):
        """
        Sort/dedupe children.  AND and OR can be treated identically.

        Args:
            ast: The comparison expression AST

        Returns:
            The same AST node, but with sorted children
        """
        sorted_children = sorted(
            ast.operands, key=functools.cmp_to_key(comparison_expression_cmp),
        )

        deduped_children = [
            # Apparently when using a key function, groupby()'s "keys" are the
            # key wrappers, not actual sequence values.  Obviously we don't
            # need key wrappers in our ASTs!
            k.obj for k, _ in itertools.groupby(
                sorted_children, key=functools.cmp_to_key(
                    comparison_expression_cmp,
                ),
            )
        ]

        changed = iter_lex_cmp(
            ast.operands, deduped_children, comparison_expression_cmp,
        ) != 0

        ast.operands = deduped_children

        return ast, changed

    def transform_or(self, ast):
        return self.__transform(ast)

    def transform_and(self, ast):
        return self.__transform(ast)


class FlattenTransformer(ComparisonExpressionTransformer):
    """
    Flatten all nodes of the AST.  E.g.:

        A and (B and C) => A and B and C
        A or (B or C) => A or B or C
        (A) => A
    """

    def __transform(self, ast):
        """
        Flatten children.  AND and OR can be treated mostly identically.  The
        little difference is that we can absorb AND children if we're an AND
        ourselves; and OR for OR.

        Args:
            ast: The comparison expression AST

        Returns:
            The same AST node, but with flattened children
        """

        changed = False
        if len(ast.operands) == 1:
            # Replace an AND/OR with one child, with the child itself.
            ast = ast.operands[0]
            changed = True

        else:
            flat_operands = []
            for operand in ast.operands:
                if isinstance(operand, _BooleanExpression) \
                        and ast.operator == operand.operator:
                    flat_operands.extend(operand.operands)
                    changed = True

                else:
                    flat_operands.append(operand)

            ast.operands = flat_operands

        return ast, changed

    def transform_or(self, ast):
        return self.__transform(ast)

    def transform_and(self, ast):
        return self.__transform(ast)


class AbsorptionTransformer(
    ComparisonExpressionTransformer,
):
    """
    Applies boolean "absorption" rules for AST simplification.  E.g.:

        A and (A or B) = A
        A or (A and B) = A
    """

    def __transform(self, ast):

        changed = False
        secondary_op = "AND" if ast.operator == "OR" else "OR"

        to_delete = set()

        # Check i (child1) against j to see if we can delete j.
        for i, child1 in enumerate(ast.operands):
            if i in to_delete:
                continue

            for j, child2 in enumerate(ast.operands):
                if i == j or j in to_delete:
                    continue

                # We're checking if child1 is contained in child2, so
                # child2 has to be a compound object, not just a simple
                # comparison expression.  We also require the right operator
                # for child2: "AND" if ast is "OR" and vice versa.
                if not isinstance(child2, _BooleanExpression) \
                        or child2.operator != secondary_op:
                    continue

                # The simple check: is child1 contained in child2?
                if iter_in(
                    child1, child2.operands, comparison_expression_cmp,
                ):
                    to_delete.add(j)

                # A more complicated check: does child1 occur in child2
                # in a "flattened" form?
                elif child1.operator == child2.operator:
                    if all(
                        iter_in(
                            child1_operand, child2.operands,
                            comparison_expression_cmp,
                        )
                        for child1_operand in child1.operands
                    ):
                        to_delete.add(j)

        if to_delete:
            changed = True

            for i in reversed(sorted(to_delete)):
                del ast.operands[i]

        return ast, changed

    def transform_or(self, ast):
        return self.__transform(ast)

    def transform_and(self, ast):
        return self.__transform(ast)


class DNFTransformer(ComparisonExpressionTransformer):
    """
    Convert a comparison expression AST to DNF.  E.g.:

        A and (B or C) => (A and B) or (A and C)
    """
    def transform_and(self, ast):
        or_children = []
        other_children = []
        changed = False

        # Sort AND children into two piles: the ORs and everything else
        for child in ast.operands:
            if isinstance(child, _BooleanExpression) and child.operator == "OR":
                # Need a list of operand lists, so we can compute the
                # product below.
                or_children.append(child.operands)
            else:
                other_children.append(child)

        if or_children:
            distributed_children = [
                AndBooleanExpression([
                    # Make dupes: distribution implies adding repetition, and
                    # we should ensure each repetition is independent of the
                    # others.
                    _dupe_ast(sub_ast) for sub_ast in itertools.chain(
                        other_children, prod_seq,
                    )
                ])
                for prod_seq in itertools.product(*or_children)
            ]

            # Need to recursively continue to distribute AND over OR in
            # any of our new sub-expressions which need it.  This causes
            # more downward recursion in the midst of this bottom-up transform.
            # It's not good for performance.  I wonder if a top-down
            # transformation algorithm would make more sense in this phase?
            # But then we'd be using two different algorithms for the same
            # thing...  Maybe this transform should be completely top-down
            # (no bottom-up component at all)?
            distributed_children = [
                self.transform(child)[0] for child in distributed_children
            ]

            result = OrBooleanExpression(distributed_children)
            changed = True

        else:
            # No AND-over-OR; nothing to do
            result = ast

        return result, changed


class SpecialValueCanonicalization(ComparisonExpressionTransformer):
    """
    Try to find particular leaf-node comparison expressions whose rhs (i.e. the
    constant) can be canonicalized.  This is an idiosyncratic transformation
    based on some ideas people had for context-sensitive semantic equivalence
    in constant values.
    """
    def transform_comparison(self, ast):
        if ast.lhs.object_type_name == "windows-registry-key":
            windows_reg_key(ast)

        elif ast.lhs.object_type_name == "ipv4-addr":
            ipv4_addr(ast)

        elif ast.lhs.object_type_name == "ipv6-addr":
            ipv6_addr(ast)

        # Hard-code False here since this particular canonicalization is never
        # worth doing more than once.  I think it's okay to pretend nothing has
        # changed.
        return ast, False
