from ...my_types import *

from .function import Function


class LambdaMathFunc(Function):
    """
    A mathematical function wrapper for lambda expressions.
    """
    def __init__(self, func: Callable[..., number]):
        """
            Initialise the LambdaMathFunc with a callable.

            Args:
                func (Callable[..., number]): A function that takes numerical inputs and returns a numerical output.
        """
        super().__init__(func) # Initialise the base Function class with the provided callable.