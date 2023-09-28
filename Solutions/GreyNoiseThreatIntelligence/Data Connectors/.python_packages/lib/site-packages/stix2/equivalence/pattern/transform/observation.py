"""
Transformation utilities for STIX pattern observation expressions.
"""
import functools
import itertools

from stix2.equivalence.pattern.compare import iter_in, iter_lex_cmp
from stix2.equivalence.pattern.compare.observation import (
    observation_expression_cmp,
)
from stix2.equivalence.pattern.transform import (
    ChainTransformer, SettleTransformer, Transformer,
)
from stix2.equivalence.pattern.transform.comparison import (
    SpecialValueCanonicalization,
)
from stix2.equivalence.pattern.transform.comparison import \
    AbsorptionTransformer as CAbsorptionTransformer
from stix2.equivalence.pattern.transform.comparison import \
    DNFTransformer as CDNFTransformer
from stix2.equivalence.pattern.transform.comparison import \
    FlattenTransformer as CFlattenTransformer
from stix2.equivalence.pattern.transform.comparison import \
    OrderDedupeTransformer as COrderDedupeTransformer
from stix2.patterns import (
    AndObservationExpression, FollowedByObservationExpression,
    ObservationExpression, OrObservationExpression, ParentheticalExpression,
    QualifiedObservationExpression, _CompoundObservationExpression,
)


def _dupe_ast(ast):
    """
    Create a duplicate of the given AST.  The AST root must be an observation
    expression of some kind (AND/OR/qualified, etc).

    Note: the observation expression "leaves", i.e. simple square-bracket
    observation expressions are currently not duplicated.  I don't think it's
    necessary as of this writing.  But revisit this if/when necessary.

    Args:
        ast: The AST to duplicate

    Returns:
        The duplicate AST
    """
    if isinstance(ast, AndObservationExpression):
        result = AndObservationExpression([
            _dupe_ast(child) for child in ast.operands
        ])

    elif isinstance(ast, OrObservationExpression):
        result = OrObservationExpression([
            _dupe_ast(child) for child in ast.operands
        ])

    elif isinstance(ast, FollowedByObservationExpression):
        result = FollowedByObservationExpression([
            _dupe_ast(child) for child in ast.operands
        ])

    elif isinstance(ast, QualifiedObservationExpression):
        # Don't need to dupe the qualifier object at this point
        result = QualifiedObservationExpression(
            _dupe_ast(ast.observation_expression), ast.qualifier,
        )

    elif isinstance(ast, ObservationExpression):
        result = ast

    else:
        raise TypeError("Can't duplicate " + type(ast).__name__)

    return result


class ObservationExpressionTransformer(Transformer):
    """
    Transformer base class with special support for transforming observation
    expressions.  The transform method implemented here performs a bottom-up
    in-place transformation, with support for some observation
    expression-specific callbacks.  It recurses down as far as the "leaf node"
    observation expressions; it does not go inside of them, to the individual
    components of a comparison expression.

    Specifically, subclasses can implement methods:
        "transform_or" for OR nodes
        "transform_and" for AND nodes
        "transform_followedby" for FOLLOWEDBY nodes
        "transform_qualified" for qualified nodes (all qualifier types)
        "transform_observation" for "leaf" observation expression nodes
        "transform_default" for all types of nodes

    "transform_default" is a fallback, if a type-specific callback is not
    found.  The default implementation does nothing to the AST.  The
    type-specific callbacks are preferred over the default, if both exist.

    In all cases, the callbacks are called with an AST for a subtree rooted at
    the appropriate node type, where the AST's children have already been
    transformed.  They must return the same thing as the base transform()
    method: a 2-tuple with the transformed AST and a boolean for change
    detection.  See doc for the superclass' method.

    This process currently silently drops parenthetical nodes.
    """

    # Determines how AST node types map to callback method names
    _DISPATCH_NAME_MAP = {
        ObservationExpression: "observation",
        AndObservationExpression: "and",
        OrObservationExpression: "or",
        FollowedByObservationExpression: "followedby",
        QualifiedObservationExpression: "qualified",
    }

    def transform(self, ast):

        changed = False
        if isinstance(ast, ObservationExpression):
            # A "leaf node" for observation expressions.  We don't recurse into
            # these.
            result, this_changed = self.__dispatch_transform(ast)
            if this_changed:
                changed = True

        elif isinstance(ast, _CompoundObservationExpression):
            for i, operand in enumerate(ast.operands):
                result, this_changed = self.transform(operand)
                if this_changed:
                    ast.operands[i] = result
                    changed = True

            result, this_changed = self.__dispatch_transform(ast)
            if this_changed:
                changed = True

        elif isinstance(ast, QualifiedObservationExpression):
            # I don't think we need to process/transform the qualifier by
            # itself, do we?
            result, this_changed = self.transform(ast.observation_expression)
            if this_changed:
                ast.observation_expression = result
                changed = True

            result, this_changed = self.__dispatch_transform(ast)
            if this_changed:
                changed = True

        elif isinstance(ast, ParentheticalExpression):
            result, _ = self.transform(ast.expression)
            # Dropping a node is a change, right?
            changed = True

        else:
            raise TypeError(
                "Not an observation expression: {}: {}".format(
                    type(ast).__name__, str(ast),
                ),
            )

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

        dispatch_name = self._DISPATCH_NAME_MAP.get(type(ast))
        if dispatch_name:
            meth_name = "transform_" + dispatch_name
            meth = getattr(self, meth_name, self.transform_default)
        else:
            meth = self.transform_default

        return meth(ast)

    def transform_default(self, ast):
        return ast, False


class FlattenTransformer(ObservationExpressionTransformer):
    """
    Flatten an observation expression AST.  E.g.:

        A and (B and C) => A and B and C
        A or (B or C) => A or B or C
        A followedby (B followedby C) => A followedby B followedby C
        (A) => A
    """

    def __transform(self, ast):

        changed = False

        if len(ast.operands) == 1:
            # Replace an AND/OR/FOLLOWEDBY with one child, with the child
            # itself.
            result = ast.operands[0]
            changed = True

        else:
            flat_children = []
            for operand in ast.operands:
                if isinstance(operand, _CompoundObservationExpression) \
                        and ast.operator == operand.operator:
                    flat_children.extend(operand.operands)
                    changed = True
                else:
                    flat_children.append(operand)

            ast.operands = flat_children
            result = ast

        return result, changed

    def transform_and(self, ast):
        return self.__transform(ast)

    def transform_or(self, ast):
        return self.__transform(ast)

    def transform_followedby(self, ast):
        return self.__transform(ast)


class OrderDedupeTransformer(
    ObservationExpressionTransformer,
):
    """
    Order AND/OR expressions, and dedupe ORs.  E.g.:

        A or A => A
        B or A => A or B
        B and A => A and B
    """

    def __transform(self, ast):
        sorted_children = sorted(
            ast.operands, key=functools.cmp_to_key(observation_expression_cmp),
        )

        # Deduping only applies to ORs
        if ast.operator == "OR":
            deduped_children = [
                key.obj for key, _ in itertools.groupby(
                    sorted_children, key=functools.cmp_to_key(
                        observation_expression_cmp,
                    ),
                )
            ]
        else:
            deduped_children = sorted_children

        changed = iter_lex_cmp(
            ast.operands, deduped_children, observation_expression_cmp,
        ) != 0

        ast.operands = deduped_children

        return ast, changed

    def transform_and(self, ast):
        return self.__transform(ast)

    def transform_or(self, ast):
        return self.__transform(ast)


class AbsorptionTransformer(
    ObservationExpressionTransformer,
):
    """
    Applies boolean "absorption" rules for observation expressions, for AST
    simplification:

        A or (A and B) = A
        A or (A followedby B) = A
        A or (B followedby A) = A

    Other variants do not hold for observation expressions.
    """

    def __is_contained_and(self, exprs_containee, exprs_container):
        """
        Determine whether the "containee" expressions are contained in the
        "container" expressions, with AND semantics (order-independent but need
        distinct bindings).  For example (with containee on left and container
        on right):

            (A and A and B) or (A and B and C)

        In the above, all of the lhs vars have a counterpart in the rhs, but
        there are two A's on the left and only one on the right.  Therefore,
        the right does not "contain" the left.  You would need two A's on the
        right.

        Args:
            exprs_containee: The expressions we want to check for containment
            exprs_container: The expressions acting as the "container"

        Returns:
            True if the containee is contained in the container; False if not
        """

        # make our own list we are free to manipulate without affecting the
        # function args.
        container = list(exprs_container)

        result = True
        for ee in exprs_containee:
            for i, er in enumerate(container):
                if observation_expression_cmp(ee, er) == 0:
                    # Found a match in the container; delete it so we never try
                    # to match a container expr to two different containee
                    # expressions.
                    del container[i]
                    break
            else:
                result = False
                break

        return result

    def __is_contained_followedby(self, exprs_containee, exprs_container):
        """
        Determine whether the "containee" expressions are contained in the
        "container" expressions, with FOLLOWEDBY semantics (order-sensitive and
        need distinct bindings).  For example (with containee on left and
        container on right):

            (A followedby B) or (B followedby A)

        In the above, all of the lhs vars have a counterpart in the rhs, but
        the vars on the right are not in the same order.  Therefore, the right
        does not "contain" the left.  The container vars don't have to be
        contiguous though.  E.g. in:

            (A followedby B) or (D followedby A followedby C followedby B)

        in the container (rhs), B follows A, so it "contains" the lhs even
        though there is other stuff mixed in.

        Args:
            exprs_containee: The expressions we want to check for containment
            exprs_container: The expressions acting as the "container"

        Returns:
            True if the containee is contained in the container; False if not
        """

        ee_iter = iter(exprs_containee)
        er_iter = iter(exprs_container)

        result = True
        while True:
            ee = next(ee_iter, None)
            if not ee:
                break

            while True:
                er = next(er_iter, None)
                if er:
                    if observation_expression_cmp(ee, er) == 0:
                        break
                else:
                    break

            if not er:
                result = False
                break

        return result

    def transform_or(self, ast):
        changed = False
        to_delete = set()
        for i, child1 in enumerate(ast.operands):
            if i in to_delete:
                continue

            # The simplification doesn't work across qualifiers
            if isinstance(child1, QualifiedObservationExpression):
                continue

            for j, child2 in enumerate(ast.operands):
                if i == j or j in to_delete:
                    continue

                if isinstance(
                    child2, (
                        AndObservationExpression,
                        FollowedByObservationExpression,
                    ),
                ):
                    # The simple check: is child1 contained in child2?
                    if iter_in(
                        child1, child2.operands, observation_expression_cmp,
                    ):
                        to_delete.add(j)

                    # A more complicated check: does child1 occur in child2
                    # in a "flattened" form?
                    elif type(child1) is type(child2):
                        if isinstance(child1, AndObservationExpression):
                            can_simplify = self.__is_contained_and(
                                child1.operands, child2.operands,
                            )
                        else:  # child1 and 2 are followedby nodes
                            can_simplify = self.__is_contained_followedby(
                                child1.operands, child2.operands,
                            )

                        if can_simplify:
                            to_delete.add(j)

        if to_delete:
            changed = True

            for i in reversed(sorted(to_delete)):
                del ast.operands[i]

        return ast, changed


class DNFTransformer(ObservationExpressionTransformer):
    """
    Transform an observation expression to DNF.  This will distribute AND and
    FOLLOWEDBY over OR:

        A and (B or C) => (A and B) or (A and C)
        A followedby (B or C) => (A followedby B) or (A followedby C)
        (A or B) followedby C => (A followedby C) or (B followedby C)
    """

    def __transform(self, ast):

        # If no OR children, nothing to do
        if any(
            isinstance(child, OrObservationExpression)
            for child in ast.operands
        ):
            # When we distribute FOLLOWEDBY over OR, it is important to
            # preserve the original FOLLOWEDBY order!  We don't need to do that
            # for AND, but we do it anyway because it doesn't hurt, and we can
            # use the same code for both.
            iterables = []
            for child in ast.operands:
                if isinstance(child, OrObservationExpression):
                    iterables.append(child.operands)
                else:
                    iterables.append((child,))

            root_type = type(ast)  # will be AST class for AND or FOLLOWEDBY
            distributed_children = [
                root_type([
                    _dupe_ast(sub_ast) for sub_ast in itertools.chain(
                        prod_seq,
                    )
                ])
                for prod_seq in itertools.product(*iterables)
            ]

            # Need to recursively continue to distribute AND/FOLLOWEDBY over OR
            # in any of our new sub-expressions which need it.
            distributed_children = [
                self.transform(child)[0] for child in distributed_children
            ]

            result = OrObservationExpression(distributed_children)
            changed = True

        else:
            result = ast
            changed = False

        return result, changed

    def transform_and(self, ast):
        return self.__transform(ast)

    def transform_followedby(self, ast):
        return self.__transform(ast)


class NormalizeComparisonExpressionsTransformer(
    ObservationExpressionTransformer,
):
    """
    Normalize all comparison expressions.
    """
    def __init__(self):
        comp_flatten = CFlattenTransformer()
        comp_order = COrderDedupeTransformer()
        comp_absorb = CAbsorptionTransformer()
        simplify = ChainTransformer(comp_flatten, comp_order, comp_absorb)
        settle_simplify = SettleTransformer(simplify)

        comp_special = SpecialValueCanonicalization()
        comp_dnf = CDNFTransformer()
        self.__comp_normalize = ChainTransformer(
            comp_special, settle_simplify, comp_dnf, settle_simplify,
        )

    def transform_observation(self, ast):
        comp_expr = ast.operand
        norm_comp_expr, changed = self.__comp_normalize.transform(comp_expr)
        ast.operand = norm_comp_expr

        return ast, changed
