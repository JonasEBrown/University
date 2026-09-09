from typing import Callable, Any, Protocol, runtime_checkable # Define necessary type aliases and protocols.

import os # Import necessary standard and third-party libraries.
import colorsys
import sympy as sp
import numpy as np
from fractions import Fraction
import matplotlib.pyplot as plt

type number = int | float # Define custom type aliases.
type NPArray = np.ndarray[tuple[Any, ...], np.dtype[np.float64]]
type FunctionArgument = NPArray | number | np.float64 | sp.Expr
type FunctionReturn = FunctionArgument | sp.core.add.Add
type ColorValue = tuple[float, float, float, float]
type CMapFunc = Callable[[int], ColorValue]

@runtime_checkable # Allows runtime checking of this protocol.
class MathFunc(Protocol):
    """
        A protocol for mathematical functions.
    """
    def __call__(self, *args: FunctionArgument) -> FunctionReturn:
        """Call the mathematical function with number arguments and return a number."""
        ...