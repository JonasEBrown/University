from ...my_types import *

from .function import Function


class IterationFunction(Function):
    """
        Class for performing and visualising iterations of a mathematical function.
        Inherits from the Function class.
    """
    def __init__(self, func: MathFunc):
        """
            Initialises the IterationFunction with a given mathematical function.

            Args:
                func (MathFunc): The mathematical function to be iterated.
        """
        super().__init__(func)
        self.x_values = [] # List to store x values during iterations.

    def iterate(self, x_0: number, iterations: int, axis: plt.Axes, arrow_size: int = 17, **kwargs: Any) -> IterationFunction:
        """
            Performs iterations of the function starting from an initial value and visualises the process on a given plot axis.

            Args:
                x_0 (number): The initial value to start the iterations. 
                iterations (int): The number of iterations to perform.
                axis (plt.Axes): The matplotlib axis on which to plot the iterations.
                arrow_size (int, optional): The size of the arrows used in the plot. Defaults to 17.
                **kwargs (Any): Additional keyword arguments for plotting passed to matplotlib.

            Returns:
                IterationFunction: The instance of the IterationFunction after performing iterations for method chaining.
        """
        self.x_values = [float(x_0)] # Reset x_values with the initial value.
        # Perform iterations and store the results using the previous result to find the next.
        [self.x_values.append(self._efunc(self.x_values[-1])) for i in range(1, iterations)]
        # Plot the iterations on the provided axis with arrows to show direction.
        for index, x_value in enumerate(self.x_values):
            # Check if the next x value exists and both current and next values are finite.
            if index < len(self.x_values) - 1 and np.isfinite(self.x_values[index + 1]) and np.isfinite(x_value):
                x_next = self.x_values[index + 1] # Get the next x value.
                midpoint = (x_next + x_value) / 2 # Calculate the midpoint of the current and next x value.
                half_distance = (x_next - x_value) / 2 # Half the distance between current and next x value.
                delta: number = 0.001 * np.sign(half_distance) # Small delta in the direction of the next point to offset arrows for visibility.

                axis.plot([x_value, x_value], [x_value, x_next], **kwargs) # Vertical line from (x_value, x_value) to (x_value, x_next).
                axis.plot([x_value, x_next], [x_next, x_next], marker='o', **kwargs) # Horizontal line from (x_value, x_next) to (x_next, x_next).
                # Only draw arrows if the distance is significant enough.
                if abs(half_distance) > 0.05:
                    # Draw arrow for vertical segment.
                    axis.annotate(
                        '', # No text for the annotation.
                        xy=(x_value, midpoint + delta), # Arrow head position.
                        xytext=(x_value, midpoint), # Arrow tail position.
                        arrowprops=dict( # Arrow properties.
                            arrowstyle="-|>", # Arrow style.
                            color=kwargs["color"], # Colour from kwargs.
                            lw=0, # Line width.
                            shrinkA=0, # No shrinking at the start.
                            shrinkB=0, # No shrinking at the end.
                            mutation_scale=arrow_size, # Size of the arrow head.
                        ),
                    )
                    # Limit the arrow length for horizontal segment if it exceeds the iteration limit
                    # so that the arrow always displays in the middle of the visible part of the line.
                    if abs(midpoint) > iterations:
                        midpoint = (iterations + x_value) / 2 # Adjust midpoint.
                    # Draw arrow for horizontal segment.
                    axis.annotate(
                        '', # No text for the annotation.
                        xy=(midpoint + delta, x_next), # Arrow head position.
                        xytext=(midpoint, x_next), # Arrow tail position.
                        arrowprops=dict( # Arrow properties.
                            arrowstyle="-|>", # Arrow style.
                            color=kwargs["color"], # Colour from kwargs.
                            lw=0, # Line width.
                            shrinkA=0, # No shrinking at the start.
                            shrinkB=0, # No shrinking at the end.
                            mutation_scale=arrow_size, # Size of the arrow head.
                        ),
                    )
        return self # Return self for method chaining.