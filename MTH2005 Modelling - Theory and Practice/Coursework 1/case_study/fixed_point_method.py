from case_study import *


class FixedPointMethod:
    """
        Class to represent the Fixed Point Method for finding roots of equations.
    """

    def __init__(self, func: MathFunc, identities: list[MathFunc]):
        """
            Initialise the Fixed Point Method with a function and its identity functions.

            Args:
                func (MathFunc): The function for which to find the fixed point.
                identities (list[MathFunc]): A list of identity functions g(x) such that x = g(x).
        """
        self.func = Function(func) # Wrap the main function.
        self.root = None # To store the computed root.
        self.error = 0 # To store the error estimate.
        self._iterables = [IterationFunction(identity) for identity in identities] # Wrap identity functions.

    def plot(self, x: NPArray, x_0: number, iterations: int = 10, percentile: int = 20, out: str | None = None):
        """
            Plot the Fixed Point Method iterations and functions.

            Args:
                x (NPArray): The range of x values to plot.
                x_0 (number): The initial guess for the fixed point.
                iterations (int): The number of iterations to perform.
                percentile (int): The percentile for y-axis limits.
                out (str | None): The output directory to save plots, if any.    
        """
        lines = len(self._iterables) + 1 # Number of lines to plot (function + iterations).
        segments = (lines * 2) - 1 # Number of color segments needed.

        figures = [plt.subplots(1) for _ in range(lines)] # Create subplots.
        all_functions_axis = figures[0][1] # Axis to display all functions.

        # Create a colormap for plotting.
        cmap = CMap(
            cmap="Paired", # Use the "Paired" colormap from matplotlib for matching function and iteration points.
            segments=segments, # Number of segments for distinct colors.
        ).darken_desaturate(
            factor=0.9
        ) # Darken and desaturate the colormap for better visibility.
        # Plot the main function f(x).
        self.func.plot(
            x=x, # X values to plot.
            axis=all_functions_axis, # Plot on the combined functions axis.
            # Use the last color for the main function since it will always
            # be an odd colour (so we won't have weird overlap).
            color=cmap(segments - 1),
            label=f"$f(x) = {self.func}$", # Label for the function plot.
        )
        all_functions_axis.set_title("$f(x)$ and $g(x)$ identity functions") # Title for the combined plot.
        all_functions_axis.set_xlabel("$x$") # X-axis label.
        all_functions_axis.set_ylabel("$y$") # Y-axis label.
        # Iterate over identity functions.
        for index, identity in enumerate(self._iterables):
            identity.iterate( # Perform iterations for each identity function.
                x_0=x_0, # Initial guess.
                iterations=iterations, # Number of iterations.
                axis=figures[index + 1][1], # Axis for the specific identity function plot.
                color=cmap((2 * index) + 1), # Colour of iteration points.
                markersize=4, # Size of iteration markers.
                lw=2, # Line width for iteration lines.
                zorder=10, # Z-order for layering.
            ).plot( # Plot the identity function on the general plot.
                x=x, # X values to plot.
                axis=all_functions_axis, # Plot on the combined functions axis.
                color=cmap(index * 2), # Colour for the identity function.
                label=f"$g(x) = {identity.func}$", # Label for the identity function plot.
            ).plot( # Plot on its own axis.
                x=x, # X values to plot.
                axis=figures[index + 1][1], # Axis for the specific identity function plot.
                color=cmap(index * 2), # Colour for the identity function.
                label=f"$g(x) = {identity.func}$", # Label for the identity function plot.
            ).title( # Set the title for the identity function plot.
                axis=figures[index + 1][1], # Axis for the specific identity function plot.
            )
        # Average the last x values from all the converging identity functions to estimate the root.
        self.root = float(np.nanmean([
            identity.x_values[-1]
            for identity in self._iterables
        ]))
        # Calculate the error as the absolute difference between the last two estimates.
        self.error = abs(self.func(self.root) - self.func(float(np.nanmean([
            identity.x_values[-2]
            for identity in self._iterables
        ]))))
        # Iterate over each figure.
        for index, (figure, axis) in enumerate(figures):
            if index != 0: # Skip the combined functions plot.
                axis.plot( # Plot the initial guess point.
                    x_0, x_0, # Initial guess point.
                    color="black", # Colour for the initial guess point.
                    marker='o', # Marker style.
                    markersize=5, # Marker size.
                    zorder=11, # Z-order for layering.
                    label=f"$x_{0} = {x_0}$", # Label for the initial guess point.
                )

                axis.set_xlabel("Iteration") # X-axis label.
                axis.set_ylabel("$y$") # Y-axis label.
            # Plot the computed root on all plots.
            axis.plot(
                self.root, self.root, # The root position.
                color="red", # Colour for the root point.
                marker='o', # Marker style.
                markersize=5, # Marker size.
                zorder=11, # Z-order for layering.
                label=f"$x_{{*}} = {self.root:0.4f}$" # Label for the root point.
            )
            # Plot the line y = x.
            axis.plot(
                x, x, # y = x line.
                color="black", # Colour for the line.
                lw=1, # Line width.
                label="$y = x$", # Label for the line.
            )
            # Get all y-data from the lines in the plot.
            all_y = np.concatenate([line.get_ydata() for line in axis.get_lines()])
            all_y = all_y[np.isfinite(all_y)] # Filter out non-finite values.
            # Determine y-axis limits based on percentiles.
            y_min, y_max = np.percentile(np.vstack(all_y), [percentile, 100 - percentile])
            axis.set_xlim(x.min(), x.max()) # Set x-axis limits.
            axis.set_ylim(y_min.min(), max(y_max.max(), x_0 + 1)) # Set y-axis limits.
            axis.locator_params(axis='x', nbins=iterations) # Set number of x-axis bins.

            handles, labels = axis.get_legend_handles_labels() # Get legend handles and labels.
            unique = dict(zip(labels, handles)) # Remove duplicate labels.
            axis.legend(unique.values(), unique.keys()) # Set the legend.

            figure.show() # Display the figure.
            # Check if output directory is specified.
            if type(out) is str and os.path.exists(out):
                figure.savefig( # Save the figure to the specified output directory.
                    os.path.join(out, "fixed-point-" + ("all-functions" if index == 0 else f"g{index}"))
                )