import sys

from case_study import *

"""
This script demonstrates the usage of various numerical methods
from the case_study module. It can perform fixed-point iteration,
2D Newton-Raphson method, solve boundary value problems,
and condense modules into a single file based on user input.
"""

# Check if this script is being run directly.
if __name__ == "__main__":
    # Get the argument from command line or prompt the user for input.
    arg = sys.argv[1] if len(sys.argv) > 1 else input(
        """Please type "fixed-point", "2d-nr", "boundary", or "condense": """)
    match arg:  # match-case statement to handle different cases based on the input argument.
        case "fixed-point":  # Fixed Point Method case.
            x_0: number = 6  # Initial guess.
            iterations: int = 10  # Number of iterations.

            f: MathFunc = LambdaMathFunc(lambda x: ((x + 5) ** (1 / 3)) - x + 3)  # Function definition.
            g_1: MathFunc = LambdaMathFunc(lambda x: ((x + 5) ** (1 / 3)) + 3)  # First identity function.
            g_2: MathFunc = LambdaMathFunc(lambda x: ((x - 3) ** 3) - 5)  # Second identity function.

            x = np.linspace(0, iterations, 100)  # x values for plotting.
            # Initialise Fixed Point Method.
            method = FixedPointMethod(
                func=f,  # Function to find root of.
                identities=[g_1, g_2],  # Identity functions.
            )

            method.plot(  # Plot the results.
                x=x,  # x values.
                x_0=x_0,  # Initial guess.
                out=sys.argv[2] if len(sys.argv) > 2 else None,  # Output file if provided.
            )

            print(f"Root: {method.root:0.4f}")  # Print the root found.
            print(f"Error: {method.error:0.4f}")  # Print the error.
        case "2d-nr":  # 2D Newton-Raphson Method case.
            f: MathFunc = LambdaMathFunc(lambda x, y: (9 * x ** 2) + (4 * x) + (2 * y) - 6)  # Function definition.
            g: MathFunc = LambdaMathFunc(
                lambda x, y: (6 * y ** 2) + (2 * x) + (4 * y) - 6)  # Second function definition.
            # Initial guess as a NumPy array.
            x_0: NPArray = np.array([
                [-5],
                [-1],
            ])
            # Initialise 2D Newton-Raphson Method.
            newton = NewtonRaphson2D(
                f=f,  # First function.
                g=g,  # Second function.
                symbols='x y',  # Variable symbols.
            )

            newton.iterate(  # Perform iterations.
                x_0=x_0,  # Initial guess.
                iterations=10  # Number of iterations.
            )

            newton.analysis()  # Analyse the results.

            print(f"Root: {newton.root}")  # Print the root found.
            print(f"Root verification: {newton.verification}")  # Print verification of the root.
            print(f"Hessian eigenvalues: {newton.eigenvalues}")  # Print Hessian eigenvalues.
            print(f"Stationary point nature: {newton.nature}")  # Print nature of stationary point.
        case "boundary":  # Boundary Value Problem case.
            domain = [0, 2 * np.pi]  # Define the domain.
            # Initialise Boundary Value Problem.
            boundary = BoundaryValueProblem(
                d2ydx2=LambdaMathFunc(np.cos),  # Second derivative function.
                domain=domain,  # Domain of the problem.
                initialConditions=[  # Initial conditions.
                    [2 * np.pi, 0],  # y(2π) = 0.
                    [0, 0],  # y'(0) = 0.
                ],
            )
            boundary.plot(  # Plot the solution for N = 51.
                N=51,  # Number of points.
                out=sys.argv[2] if len(sys.argv) > 2 else None  # Output file if provided.
            )
            boundary.loglog(  # Log-log plot for convergence analysis.
                minN=4,  # Minimum number of points.
                maxN=100,  # Maximum number of points.
                out=sys.argv[2] if len(sys.argv) > 2 else None  # Output file if provided.
            )

            print(f"Order: {boundary.order:0.2f}")  # Print the order of convergence.
        case "condense":  # Condense module case.
            output_file = sys.argv[3] if len(sys.argv) > 3 else "."  # Check for output file argument.
            # Ensure the output file has a .py extension.
            output_file = os.path.join(output_file, "output.py") if not output_file.endswith(".py") else output_file
            condense_module_to_file(  # Condense module to file.
                sys.argv[2] if len(sys.argv) > 2 else None,  # Module name from command line argument.
                output_file,  # Output file path.
            )
        case _:  # Default case for unknown input.
            raise ValueError("Unknown input")  # Raise an error for unknown input.