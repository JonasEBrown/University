from case_study import *


class NewtonRaphson2D:
    """
        Class to perform the Newton-Raphson method in 2D.
    """
    def __init__(self, f: MathFunc, g: MathFunc, symbols: str = 'x y'):
        """
            Initialise the NewtonRaphson2D instance with functions and symbols.
            Specifically set up for the question provided in the case study, but
            other function definitions for the stationary points can be used.

            Args:
                f (MathFunc): The first function.
                g (MathFunc): The second function.
                symbols (str): The symbols used in the functions.
        """
        self._f = Function(f, symbols=symbols) # Wrap the first function.
        self._g = Function(g, symbols=symbols) # Wrap the second function.
        # Define the vector function F, a combination of f and g.
        self._F = lambda x, y: np.array(
            [
                [self._f(x, y)],
                [self._g(x, y)],
            ]
        )

        self._symbols = sp.symbols(symbols) # Define symbolic variables.

        sym_f: sp.core.add.Add = self._f(*self._symbols) # Symbolic representation of f.
        sym_g: sp.core.add.Add = self._g(*self._symbols) # Symbolic representation of g.

        self._dfdx = sp.lambdify(self._symbols, sym_f.diff(self._symbols[0])) # Partial derivative of f with respect to x.
        self._dfdy = sp.lambdify(self._symbols, sym_f.diff(self._symbols[1])) # Partial derivative of f with respect to y.

        self._dgdx = sp.lambdify(self._symbols, sym_g.diff(self._symbols[0])) # Partial derivative of g with respect to x.
        self._dgdy = sp.lambdify(self._symbols, sym_g.diff(self._symbols[1])) # Partial derivative of g with respect to y.
        # Define the Jacobian matrix as a function.
        self._jacobian = lambda x, y: np.array(
            [
                [self._dfdx(x, y), self._dfdy(x, y)],
                [self._dgdx(x, y), self._dgdy(x, y)],
            ]
        )

        self.x_values = [] # List to store the x values during iterations.
        self.root = None # To store the found root after iterations.
        self.verification = None # To store the verification of the root.
        self.eigenvalues = None # To store the eigenvalues of the Hessian at the root.
        self.nature = None # To store the nature of the stationary point.

    def _step(self, x: NPArray) -> NPArray:
        """
            Perform a single step of the 2D Newton-Raphson method.

            Args:
                x (NPArray): The current point in 2D space.

            Returns:
                NPArray: The updated point after one step.
        """
        x1, x2 = x[0][0], x[1][0] # Extract x and y components.
        return x - (np.linalg.inv(self._jacobian(x1, x2)) @ self._F(x1, x2)) # x_new = x - J_inv * F

    def iterate(self, x_0: NPArray, iterations: int = 10):
        """
            Perform multiple iterations of the Newton-Raphson method.

            Args:
                x_0 (NPArray): The initial guess for the root.
                iterations (int): The number of iterations to perform.
        """
        self.x_values = [x_0] # Initialise the list with the initial guess.
        # Perform the specified number of iterations using the previous result to calculate the next.
        [self.x_values.append(self._step(self.x_values[-1])) for _ in range(iterations)]
        self.root = self.x_values[-1][::, 0] # Store the final result as the root.

    def analysis(self):
        """
            Analysis of the root found by the Newton-Raphson method, including:
                - Verification of the root,
                - Eigenvalues of the Hessian,
                - and nature of the stationary point.

            Raises:
                ValueError: If iterations have not been run yet.
        """
        if self.root is []: # Check if iterations have been performed.
            raise ValueError("Need to run iterations first.") # Raise error if not.
        # Verify the root by evaluating F at the root.
        self.verification = self._F(self.root[0], self.root[1])[::,0]
        # Calculate the Hessian matrix at the root and its eigenvalues.
        hessian = self._jacobian(self.root[0], self.root[1])
        self.eigenvalues = np.linalg.eigvals(hessian) # Compute eigenvalues.
        # Determine the nature of the stationary point based on eigenvalues.
        self.nature = "local " + ("maximum" if self.eigenvalues[0] < 0 else "minimum") if np.sign(self.eigenvalues[0]) == np.sign(self.eigenvalues[1]) else "saddle point"
