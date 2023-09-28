"""
Generic AST transformation classes.

.. autosummary::
   :toctree: transform

   comparison
   observation
   specials

|
"""


class Transformer:
    """
    Base class for AST transformers.
    """
    def transform(self, ast):
        """
        Transform the given AST and return the resulting AST.

        :param ast: The AST to transform
        :return: A 2-tuple: the transformed AST and a boolean indicating whether
            the transformation actually changed anything.  The change detection
            is useful in situations where a transformation needs to be repeated
            until the AST stops changing.
        """
        raise NotImplementedError("transform")


class ChainTransformer(Transformer):
    """
    A composite transformer which consists of a sequence of sub-transformers.
    Applying this transformer applies all sub-transformers in sequence, as
    a group.
    """
    def __init__(self, *transformers):
        self.__transformers = transformers

    def transform(self, ast):
        changed = False
        for transformer in self.__transformers:
            ast, this_changed = transformer.transform(ast)
            if this_changed:
                changed = True

        return ast, changed


class SettleTransformer(Transformer):
    """
    A transformer that repeatedly performs a transformation until that
    transformation no longer changes the AST.  I.e. the AST has "settled".
    """
    def __init__(self, transform):
        self.__transformer = transform

    def transform(self, ast):
        changed = False
        ast, this_changed = self.__transformer.transform(ast)
        while this_changed:
            changed = True
            ast, this_changed = self.__transformer.transform(ast)

        return ast, changed
