from ...my_types import *


class Function:
    """
    A wrapper for mathematical functions to facilitate plotting and string representation.
    """
    LIMIT = 1e16 # Threshold to avoid overflow in numerical evaluations.

    def __init__(self, func: MathFunc, symbols: str = 'x'):
        """
            Creates a Function instance wrapping a given mathematical function.

            Args:
                func (MathFunc): The mathematical function to wrap.
                symbols (str): The variable symbols used in the function for string representation.
        """
        match type(func).__name__:
            case "callable" | "ufunc" | "function":     # Check if func is a built-in function or user-defined function,
                self.func = func                        # then directly use the callable.
            case _:                                     # Else assume it's already a Function instance
                self.func = func.func                   # and use the underlying function.
        self._symbols = symbols # Store symbols for string representation.

    def _efunc(self, *args: FunctionArgument) -> FunctionReturn:
        """
            Safely evaluates the wrapped function with overflow handling.
            Handles large values by returning NaN for inputs that would cause overflow
            and returns symbolic expressions as is.

            Args:
                *args (FunctionArgument): Input values for the function.

            Returns:
                FunctionReturn: The evaluated result.
        """

        try:
            value = self.func(*args) # Evaluate the function with given args.
             # Check if the result is a symbolic expression or is an sympy function (like cos, sin, etc).
            if type(value) is sp.core.add.Add or str(type(value)) in sp.functions.__all__:
                return value # Return symbolic expressions as is.
            # Handle numerical results with overflow check.
            return np.where((value <= -self.LIMIT) | (value >= self.LIMIT), np.nan, value)
        except ValueError as e: # Catch ValueErrors during evaluation.
            return np.nan # Return NaN for any evaluation errors.

    def plot(self, x: NPArray, axis: plt.Axes, **kwargs: Any) -> Function:
        """
            Plots the function on a given matplotlib axis using given x values.

            Args:
                x (NPArray): The x values for plotting.
                axis (plt.Axes): The matplotlib axis to plot on.
                **kwargs (Any): Additional keyword arguments passed to matplotlib.

            Returns:
                Function: The current Function instance for method chaining.
        """
        y_values = self._efunc(x) # Evaluate the function at given x values.

        axis.set_xlim(np.nanmin(x), np.nanmax(x)) # Set x-axis limits based on mininum and maximum x values.
        y_min, y_max = axis.get_ylim() # Get current y-axis limits.
        # Update y-axis limits based on evaluated y values, ensuring NaNs are ignored and that when new lines
        # are added, the y-limits expand to accommodate them.
        y_min, y_max = min(y_min, np.nanmin(y_values)), max(y_max, np.nanmax(y_values))
        axis.set_ylim(y_min, y_max) # Set updated y-axis limits.

        axis.plot(x, y_values, **kwargs) # Plot the function on the axis with additional kwargs.

        return self # Return self for method chaining.

    def title(self, axis: plt.Axes) -> Function:
        """
            Sets the title of the plot axis to the LaTeX representation of the function.
            Only implemented for method chaining.

            Args:
                axis (plt.Axes): The matplotlib axis to set the title on.

            Returns:
                Function: The current Function instance for method chaining.
        """
        axis.set_title(f"$g(x) = {self.func}$") # Set the title with LaTeX formatted function.
        return self # Return self for method chaining.

    @staticmethod
    def convert_exponents_to_rational(expr: sp.Expr) -> sp.Expr:
        """
            Recursively converts all floating-point exponents in a sympy expression to rational numbers,
            so they can be represented in LaTeX as fractions instead of decimal points.

            Args:
                expr (sp.Expr): The sympy expression to convert.

            Returns:
                sp.Expr: The modified sympy expression with rational exponents.
        """
        if expr.is_Pow: # Check if the expression is a power.
            base, exp = expr.args # Get base and exponent.
             # If exponent is a float, convert it to a rational number.
            if exp.is_Float:
                frac = Fraction(float(exp)).limit_denominator(1000) # Limit denominator to avoid overly complex fractions.
                # Return the base raised to the rational exponent.
                return base ** sp.Rational(frac.numerator, frac.denominator)
            else:
                # Else recursively convert exponents in the base and exponent.
                return expr.func(base, Function.convert_exponents_to_rational(exp))
        elif expr.args: # If the expression has arguments (like in sums, products, etc).
             # Recursively convert exponents in all arguments.
            return expr.func(
                *(Function.convert_exponents_to_rational(arg) for arg in expr.args)
            )
        else: # Else return as is.
            return expr

    @staticmethod
    def convert_to_str(func: MathFunc, symbols: str = 'x') -> str:
        """
            Converts a mathematical function to its LaTeX string representation,
            ensuring all exponents are represented as rational numbers.

            Args:
                func (MathFunc): The mathematical function to convert.
                symbols (str): The variable symbols used in the function.
                
            Returns:
                str: The LaTeX string representation of the function.
        """
        # Create a sympy expression by applying the function to sympy symbols.
        # Then convert any floating-point exponents to rational numbers.
        expr_rational = Function.convert_exponents_to_rational(
            func(
                sp.symbols(symbols)
            )
        )
        # Finally, convert the expression to LaTeX format without root notation.
        return sp.latex(expr_rational, root_notation=False)

    def __str__(self) -> str:
        """
            Returns the LaTeX string representation of the wrapped function.

            Returns:
                str: The LaTeX string representation.
        """
        return Function.convert_to_str(self.func, self._symbols)

    def __call__(self, *args: FunctionArgument) -> FunctionReturn:
        """
            Allows the Function instance to be called like a regular function,
            evaluating the wrapped function with overflow handling.

            Args:
                *args (FunctionArgument): Input values for the function.

            Returns:
                FunctionReturn: The evaluated result.
        """
        return self._efunc(*args) # Evaluate the function with overflow handling.