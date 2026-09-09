from case_study import *


class BoundaryValueProblem:
    """
        Class to solve a boundary value problem of the form d²y/dx² = f(x) with given boundary conditions.
    """
    # Mapping from NumPy functions to SymPy functions.
    numpy_to_sympy = {
        np.sin: sp.sin,
        np.cos: sp.cos,
        np.tan: sp.tan,
        np.exp: sp.exp,
        np.log: sp.log,
        np.sqrt: sp.sqrt,
        np.abs: sp.Abs
    }

    @staticmethod
    def convert_numpy_to_sympy(np_func: Callable[..., Any], var='x') -> sp.Expr:
        """
            Convert a NumPy function to a SymPy expression.

            Args:
                np_func (Callable[..., Any]): The NumPy function to convert.
                var (str): The variable name to use in the SymPy expression.

            Returns:
                A SymPy expression corresponding to the NumPy function.
        """
        x = sp.symbols(var) # Define the variable.
        # Get the corresponding SymPy function if defined in our map.
        sp_func = BoundaryValueProblem.numpy_to_sympy.get(np_func)
        if sp_func is None: # If not found:
            return np_func # Return the original NumPy function.
        return sp_func(x) # Return the SymPy expression.

    def __init__(self, d2ydx2: MathFunc, domain: list[number], initialConditions: list[list[number]]):
        """
            Initialise the BoundaryValueProblem instance.
            Taking any second derivative function and boundary conditions to find a solution.
            Again, specific to the Boundary-value matrix problem in the case study, but can
            be used to solve other problems of similar nature.

            Args:
                d2ydx2 (MathFunc): The second derivative function d²y/dx² = f(x).
                domain (list[number]): The domain of the problem.
                initialConditions (list[list[number]]): The boundary conditions in order [[x1, y], [x2, y'], [x3, y'']].
        """
        self._d2ydx2 = Function(d2ydx2, symbols='x') # Wrap second derivative function.
        self._domain = domain # Store the domain.
        self._initialConditions = initialConditions # Store the boundary conditions.

        self.trueSolution = None # Placeholder for the true solution.
        self.findTrueSolution() # Find the true solution symbolically.

        self.numericalSolution = None # Placeholder for the numerical solution.
        self.error = 0 # Placeholder for the error.
        self.order = 0 # Placeholder for the order of accuracy.

    def findTrueSolution(self):
        """
            Find the true solution symbolically using SymPy.

            This method integrates the second derivative function twice and applies the boundary conditions
            to solve for the constants of integration.
        """
        x = sp.symbols('x') # Define the variable.
        C1, C2 = sp.symbols('C1 C2') # Define constants of integration.

        sym_d2ydx2 = self.convert_numpy_to_sympy(self._d2ydx2.func) # Convert the second derivative function to SymPy.
        sym_dydx = sp.integrate(sym_d2ydx2, x) + C1 # First integration + constant C1.
        sym_y = sp.integrate(sym_dydx, x) + C2 # Second integration + constant C2.

        functions = [ # List of functions to apply boundary conditions to.
            sym_y,
            sym_dydx,
            sym_d2ydx2,
        ]
        equations = [ # Create equations based on boundary conditions.
            sp.Eq(
                functions[index].subs(x, condition[0]), # Substitute x with boundary condition x-value.
                condition[1] # Set equal to boundary condition y-value.
            ) for index, condition in enumerate(self._initialConditions) # Iterate over each of the boundary conditions.
        ]
        solutions = sp.solve(equations, (C1, C2)) # Solve for constants C1 and C2.
        sym_y = sym_y.subs(solutions) # Substitute constants back into the y solution to obtain the true solution.
        self.trueSolution = Function(sp.lambdify(x, sym_y, "numpy"), symbols='x') # Wrap the true solution as a Function.

    def solveNumerically(self, N: int = 51) -> NPArray:
        """
            Solve the boundary value problem numerically using finite difference method.

            Args:
                N (int): The number of grid points.

            Returns:
                NPArray: The numerical solution array.
        """
        deltaX = self._domain[1] / (N - 1) # Calculate grid spacing Δx.
        x = np.linspace(*self._domain, N) # Create x values in domain with grid spacing.

        f = (deltaX**2) * self._d2ydx2(x) # Evaluate f(x) scaled by Δx².
        T = np.zeros((N, N)) # Initialise the tridiagonal matrix T.
        # Fill in the tridiagonal matrix T with finite difference coefficients (1, -2, 1)
        for index in range(1, (N - 1)):
            T[index, (index - 1)] = 1 # Lower diagonal y_{i - 1}.
            T[index, index] = -2 # Main diagonal y_{i}.
            T[index, (index + 1)] = 1 # Upper diagonal y_{i + 1}.

        # Apply Neumann boundary conditions to T: y'(0) = 0 implies y_0 - y_1 = 0.
        T[0, 0] = 1 # => y_0 coefficient (1).
        T[0, 1] = -1 # => y_1 coefficient (-1).

        # Apply Dirichlet boundary conditions to T: y(2π) = 0 implies y_{N - 1} = 0.
        T[-1, -1] = 1 # Set last row to enforce y_{N - 1} = 0.
        f[-1] = 0 # Set the last entry of f to 0 as y_{N - 1} = 0.

        self.numericalSolution = np.linalg.solve(T, f) # Solve the linear system T * y = f for y.
        # Calculate the mean absolute error between the numerical solution and true solution if available.
        self.error = np.mean(np.abs(self.numericalSolution - self.trueSolution(x))) if self.trueSolution is not None else 0
        return self.numericalSolution # Return the numerical solution.

    def plot(self, N: int = 51, out: str | None = None, margin: float = 1.1):
        """
            Plot the numerical and true solutions of the boundary value problem.

            Args:
                N (int): The number of grid points for the numerical solution.
                out (str | None): The output directory to save the plot. If None, the plot is not saved.
                margin (float): Margin factor for y-axis limits.
        """
        self.solveNumerically(N) # Solve numerically to get the solution with a given N.

        figure, axis = plt.subplots(1) # Create a new figure and axis for plotting.

        trueX = np.linspace(*self._domain, 100) # Generate x values for true solution plot.
        self.trueSolution.plot( # Plot the true solution.
            x=trueX, # The x values for true solution.
            axis=axis, # Axis to plot on.
            label="True solution", # Label for the true solution.
            color="blue", # Colour of the true solution.
        )
        # Generate x values for numerical solution plot (same as used in numerical solution).
        numericalX = np.linspace(*self._domain, len(self.numericalSolution))
        axis.plot( # Plot the numerical solution as red circles.
            numericalX, self.numericalSolution, # x and y values from numerical solution.
            "ro", # Red circles for numerical solution points.
            label="Numerical solution", # Label for the numerical solution.
        )

        axis.set_xlabel("x") # Label x-axis.
        axis.set_ylabel("y") # Label y-axis.

        true_solutions = self.trueSolution(trueX) # Evaluate true solution for y-limits calculation.
        # Determine y-limits for better visualisation with a margin adjustment.
        y_min = min(np.nanmin(self.numericalSolution), np.nanmin(true_solutions)) * margin
        y_max = max(np.nanmax(self.numericalSolution), np.nanmax(true_solutions)) * margin

        axis.set_xlim(*self._domain) # Set x-limits to the domain.
        axis.set_ylim(y_min, y_max) # Set y-limits based on calculated min and max.

        axis.set_title(f"Boundary Value Problem with $N = {N}$") # Set plot title.
        axis.legend() # Show legend.

        figure.show() # Display the plot.
        # Check if output directory is provided and exists, then save the figure.
        if type(out) is str and os.path.exists(out):
            figure.savefig(os.path.join(out, f"boundary-value-problem-N-{N}"))

    def loglog(self, minN: int = 4, maxN: int = 100, out: str | None = None):
        """
            Plot the error of numerical solutions with different N values against their
            Δx on a log-log scale to determine the order of accuracy.

            Args:
                minN (int): The minimum number of grid points to consider.
                maxN (int): The maximum number of grid points to consider.
                out (str | None): The output directory to save the plot. If None, the plot is not saved.
        """
        errors = [] # List to store errors for different N values.
        for N in range(minN, maxN + 1): # Iterate over N values from minN to maxN.
            self.solveNumerically(N) # Solve numerically for the current N.
            errors.append(self.error) # Append the calculated error to the list.
        errors = np.array(errors) # Convert errors list to a NumPy array for processing.

        figure, axis = plt.subplots(1) # Create a new figure and axis for plotting.

        N = np.linspace(minN, maxN, (maxN - minN)) # Generate N values for x-axis.
        deltaX = self._domain[1] / (N - 1) # Calculate corresponding Δx values.
        # Perform linear fit on log-log data to find the order of accuracy - from the slop of the polyfit.
        self.order, _ = np.polyfit(np.log(deltaX), np.log(errors), 1)

        axis.scatter( # Plot the error vs Δx on a log-log scale.
            deltaX, errors, # x and y values.
            label="Error", # Label for the error points.
        )

        axis.set_xlabel("$\\Delta x$") # Label x-axis.
        axis.set_ylabel("Error") # Label y-axis.

        axis.set_xscale("log") # Set x-axis to logarithmic scale.
        axis.set_yscale("log") # Set y-axis to logarithmic scale.

        axis.set_title("Boundary Value Problem: Error vs $\\Delta x$") # Set plot title.
        axis.legend() # Show legend.

        figure.show() # Display the plot.
        # Check if output directory is provided and exists, then save the figure.
        if type(out) is str and os.path.exists(out):
            figure.savefig(os.path.join(out, "boundary-value-problem-loglog"))
