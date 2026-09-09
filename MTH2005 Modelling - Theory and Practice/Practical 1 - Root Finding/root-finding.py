"""
    Practical answer written from scratch.
"""

import os
import PIL.Image
import numpy as np
import imageio.v2 as imageio
import matplotlib.pyplot as plt

from typing import Callable, Annotated, List

type number = int | float

# Define an Error for our program.

class RootFindingError(Exception):
    """
        Essentially this is just for cleanliness. So we have errors that look like:

        Traceback (most recent call last):
        File "f:\\University\\Year 2\\MTH2005 Modelling - Theory and Practice\\Practical 1 - Root Finding\\scratch.py", line 36, in <module>
            ).findRoot()
            ~~~~~~~~^^
        File "f:\\University\\Year 2\\MTH2005 Modelling - Theory and Practice\\Practical 1 - Root Finding\\scratch.py", line 17, in findRoot
            raise RootFindingError(f"No root between {self._bracket[0]} and {self._bracket[1]}!")

        RootFindingError: There is no root in [2, 4].
    """

    def __init__(self, message: str = ""):
        """
            Basically, inherit all the properties from the Exception class in Python, but change the message.
        """

        super().__init__(message)

# Define a class to generalise root finding.

class RootFinder:

    """
        This class is simply here to demonstrate the reuability of code.
        For other methods, such as Newton-Raphson, this class doesn't need to be updated.
        
        There are a few functions that are NOT defined here specifically but are required for the RootFinder class to work:
        (most are fairly self-explanitory from the naming, but I will explain each below)

            - hasRoot:
                -> Returns True or False depending on if there is a root in the interval provided to the class.

            - errorEvaluation:
                -> Returns the error of the current value of x.

            - step:
                -> Runs one "step" of the method.
    """

    def __init__(self, func: Callable[[number], number], interval: Annotated[List[number], 2], errorTolerance: number = 1e-6):
        """
            Initialise the class with required variables and check for the correct required functions.
        """

        self._func = func
        self._originalInterval = interval.copy()
        self._errorTolerance = errorTolerance

        if self.hasRoot is None:
            raise RootFindingError(f"There is no hasRoot function defined! It is required to run the program.")
        
        if self.errorEvaluation is None:
            raise RootFindingError(f"There is no errorEvaluation function defined! It is required to run the program.")
        
        if self.step is None:
            raise RootFindingError(f"There is no step function defined! It is required to run the program.")

    def findRoot(self, debug: bool = False) -> number | None:
        """
            This is a generic function built so that any root finding method could be used with it.
            This is because they all follow the same pattern logically:
                - Has a root?
                    - Yes -> Repeat stepping our method until the error is below a tolerance level.
                    - No -> Don't do anything.
        """

        self._interval = self._originalInterval.copy()

        if not(self.hasRoot()):
            raise RootFindingError(f"There is no root in [{self._originalInterval[0]}, {self._originalInterval[1]}].")
        
        if debug:
            self._debug = []

        while self.errorEvaluation() > self._errorTolerance:
            self.step()
            if debug:
                self._debug.append([self._interval.copy(), self._root, self.errorEvaluation()])
        return self._root
    
    def output(self):
        """
            Simply outputs whether there is a root or not and where it was found.
        """

        if not(self.hasRoot()) or (self._root is None):
            raise RootFindingError(f"There is no root in [{self._originalInterval[0]}, {self._originalInterval[1]}].")
        print(f"The root x={self._root:0.4f} was found in [{self._originalInterval[0]}, {self._originalInterval[1]}].")

    def conclude(self) -> number:
        """
            An ease of use function to orchestrate finding the root, outputting the result, and then return the solution.
        """

        self.findRoot()
        self.output()
        return self._root
    
    def visualise(self, gif_path: str | None = None):
        if not(self.hasRoot()) or (self._root is None):
            raise RootFindingError(f"There is no root in [{self._originalInterval[0]}, {self._originalInterval[1]}].")
         
        # Create graphs to plot on.

        figure, axis = plt.subplots(figsize=(8,5))
        x_values = np.linspace(self._originalInterval[0] - 1, self._originalInterval[1] + 1)
        y_values = self._func(x_values)
        y_min, y_max = min(y_values), max(y_values)
        y_range = y_max - y_min
        y_min -= 0.1 * y_range
        y_max += 0.1 * y_range

        def plot_figure():
            axis.plot(x_values, y_values, color="blue", linewidth=1)
            axis.axhline(0, color="black", linewidth=1)
            axis.set_xlabel("x")
            axis.set_ylabel("f(x)")
            axis.set_title(f"{self.__class__.__name__} - Root Finding Visualisation")
            axis.set_xlim(self._originalInterval[0]-1, self._originalInterval[1]+1)
            axis.set_ylim(y_min, y_max)


        self.findRoot(debug=True)
        frames = []

        for index, debugInfo in enumerate(self._debug):
            if ((index < 1) or (abs(debugInfo[2] - self._debug[index - 1][2]) > 5e-3)):
                axis.clear()
                plot_figure()
                axis.plot(
                    [*debugInfo[0]],
                    [self._func(debugInfo[0][0]), self._func(debugInfo[0][1])],
                    'o', color="green", alpha=0.8, markersize=8, label="Interval")
                axis.plot(
                    debugInfo[1],
                    self._func(debugInfo[1]),
                    'X', color="red", alpha=0.8, markersize=10, label="Midpoint")
                axis.axvline(
                    debugInfo[1], color="gray", linestyle="--", alpha=0.4)
                axis.text(
                    0.02, 0.95, f"Iteration {index + 1}", transform=axis.transAxes,
                    fontsize=10, bbox=dict(facecolor="white", alpha=0.7, edgecolor="gray"))
                frame_path = f"frame_{index}.png"
                figure.savefig(frame_path)
                frames.append(imageio.imread(frame_path))

        pil_frames = [PIL.Image.fromarray(frame) for frame in frames]
        pil_frames[0].save(
            gif_path,
            save_all=True,
            append_images=pil_frames[1:],
            duration=500,
            loop=0
        )
        [os.remove(f"frame_{index}.png") for index in range(len(frames))]
        plt.close(figure)
    
# Define our bisection method for root finding.    

class BisectionMethod(RootFinder):

    """
        Our bisection method class.

        All public functions are required by the parent RootFinder class.
        All private functions (prefixed with an _) are internal only functions.
    """

    def errorEvaluation(self) -> number:
        return abs(self._interval[0] - self._interval[1])

    def hasRoot(self) -> bool:
        return self._func(self._interval[0]) * self._func(self._interval[1]) <= 0
    
    def _bisect(self) -> number:
        """
            Uses a bisection to calculate the mid-point value between the ends of the current interval.
        """

        return sum(self._interval) / 2
    
    def _IVT(self, bisect: number) -> int:
        """
            The Intermediate Value Theorem (IVT):
                If the left side of the interval, a, multiplied by the new bisection value, c
                is less than 0 then the new right hand side of the interval should be c.
                    Let I = [a, b]
                    Let c = (a + b) / 2
                    If a * c < 0 then I = [a, c]
                    Otherwise I = [c, b]
        """

        return 1 if ((self._func(self._interval[0]) * self._func(bisect)) < 0) else 0

    def step(self):
        bisect: number = self._bisect()
        ivt = self._IVT(bisect)
        self._interval[ivt] = bisect
        self._root = bisect

    


if __name__ == "__main__":
    method = BisectionMethod(
        lambda x: (x**3) - (2 * x**2) - 3,
        [2, 4]
    )
    root = method.conclude()
    method.visualise("bisection-method.gif")

