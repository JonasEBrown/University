# Import needed modules #

import math
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable

# Constant values #

# Squirrels.
INITIAL_RED_SQUIRREL_POPULATION: float = 0.5
INITIAL_GREY_SQUIRREL_POPULATION: float = 0.116

# Time step.
T0_THRESHOLD: float = 0.001
DEFAULT_DELTA_TIME_STEP: float = 0.003125
DEFAULT_SIMULATION_LENGTH: int = 6
DEFAULT_SQUIRREL_POPULATION_CONSTRAINTS: Tuple[float, float] = (0, 10)

# Essential maths function #

clamp: Callable[[float, float, float], float] = (lambda x, minimum, maximum: max(minimum, min(x, maximum)))

# Set up our model #

class SquirrelCompetitionModel:

    def __init__(self,
                 initialRedSquirrelPopulation: float = INITIAL_RED_SQUIRREL_POPULATION,
                 initialGreySquirrelPopulation: float = INITIAL_GREY_SQUIRREL_POPULATION,
                 deltaTimeStep: float = DEFAULT_DELTA_TIME_STEP,
                 simulationLength: int = DEFAULT_SIMULATION_LENGTH,
                 t0Threshold: float = INITIAL_RED_SQUIRREL_POPULATION,
                 squirrelPopulationConstraints: Tuple[float, float] = DEFAULT_SQUIRREL_POPULATION_CONSTRAINTS):
        """
        Initialises the model with default constant parameters.

        :param initialRedSquirrelPopulation: Initial red squirrel population.
        :param initialGreySquirrelPopulation: Initial grey squirrel population.
        :param deltaTimeStep: Time step size.
        :param simulationLength: Simulation length.
        :param t0Threshold: Threshold for finding the minimum time step.
        :param squirrelPopulationConstraints: Constrains the squirrel population between a minimum and maximum value.
        """

        self.initialRedSquirrelPopulation: float = initialRedSquirrelPopulation
        self.initialGreySquirrelPopulation: float = initialGreySquirrelPopulation
        self.deltaTimeStep: float = deltaTimeStep
        self.simulationLength: int = simulationLength
        self.t0Threshold: float = t0Threshold
        self.squirrelPopulationConstraints: Tuple[float, float] = squirrelPopulationConstraints

        # Aliases #

        self.rDot = self.redSquirrelFunctionDerivative
        self.gDot = self.greySquirrelFunctionDerivative
        self.const = self.findNewConstantC

    @staticmethod
    def redSquirrelFunctionDerivative(redSquirrels: float, greySquirrels: float) -> float:
        """
        Computes the rate of change of the red squirrel population.

        :param redSquirrels: Current red squirrel population.
        :param greySquirrels: Current grey squirrel population.
        :return: New value of red squirrel population.
        """

        return redSquirrels * (1 - greySquirrels)

    @staticmethod
    def greySquirrelFunctionDerivative(redSquirrels: float, greySquirrels: float) -> float:
        """
        Computes the rate of change of the grey squirrel population.

        :param redSquirrels: Current red squirrel population.
        :param greySquirrels: Current grey squirrel population.
        :return: New value of grey squirrel population.
        """

        return greySquirrels * (2 - redSquirrels)

    @staticmethod
    def findNewConstantC(redSquirrels: float, greySquirrels: float) -> float:
        """
        Computes the constant C.

        :param redSquirrels: Current red squirrel population.
        :param greySquirrels: Current grey squirrel population.
        :return: New value of C.
        """

        # I found a few issues with the exponential function in python so here are some safety checks:
        greySquirrels = 1e-10 if (abs(greySquirrels) < 1e-10) else greySquirrels
        redSquirrels = min(redSquirrels, 1e5)
        exponential_value = clamp((greySquirrels - redSquirrels), -700, 700)

        return ((redSquirrels ** 2) * (math.exp(exponential_value))) / greySquirrels

    def timeStep(self,
                 initialRedSquirrels: float | None = None,
                 initialGreySquirrels: float | None = None,
                 deltaTimeStep: float | None = None,
                 simulationLength: int | None = None,
                 forward: bool = True,
                 squirrelPopulationConstraints: Tuple[float, float] | None = None) -> Tuple[List[float], List[float], List[float], List[float]]:

        """
        Performs time stepping using Euler's method.

        :param initialRedSquirrels: Initial red squirrel population.
        :param initialGreySquirrels: Initial grey squirrel population.
        :param deltaTimeStep: Time step size.
        :param simulationLength: Simulation length.
        :param forward: If true steps forward, else backward.
        :param squirrelPopulationConstraints: Constrains the squirrel population between a minimum and maximum value.
        :return: New values for red and grey squirrel population, constants, and time.
        """

        # Convert boolean to +/- 1 to determine direction of step.
        direction = (1 if forward else -1)

        # Check parameters.

        initialRedSquirrels = initialRedSquirrels if (initialRedSquirrels is not None) else self.initialRedSquirrelPopulation
        initialGreySquirrels = initialGreySquirrels if (initialGreySquirrels is not None) else self.initialGreySquirrelPopulation
        deltaTimeStep = deltaTimeStep if (deltaTimeStep is not None) else self.deltaTimeStep
        simulationLength = simulationLength if (simulationLength is not None) else self.simulationLength
        squirrelPopulationConstraints = squirrelPopulationConstraints if (squirrelPopulationConstraints is not None) else self.squirrelPopulationConstraints

        # Initialise lists with values passed to the function.

        red: List[float] = [initialRedSquirrels]
        grey: List[float] = [initialGreySquirrels]
        time: List[float] = [0]
        constants: List[float] = [self.const(
            initialRedSquirrels,
            initialGreySquirrels
        )] # Initialise the constants list using the "const" function defined above, passing
           # the initial values given.
        subintervals: int = int(simulationLength / deltaTimeStep)

        for x in range(subintervals):
            # Loop for each subinterval.

            red.append(
                clamp(red[x] + (self.rDot(red[x], grey[x]) * deltaTimeStep * direction), *squirrelPopulationConstraints)
            )  # Calculate the next red value.
            grey.append(
                clamp(grey[x] + (self.gDot(red[x], grey[x]) * deltaTimeStep * direction), *squirrelPopulationConstraints)
            )  # Calculate the next grey value.
            time.append(time[x] + (deltaTimeStep * direction))
            constants.append(self.const(red[-1], grey[-1]))
            # Calculate the constant for the new values.

        return red, grey, time, constants

    def findMinimumDeltaTime(self, threshold: float | None = None) -> float:
        """
        Computes the smallest value of time step, such that the relative change in C is less than the threshold given.

        :param threshold: Minimum value of time step.
        :return: Smallest value of time step.
        """

        # Initialise variables.
        deltaTime: float = 0.1
        constants: List[float] = []

        # Check parameters.
        threshold = threshold if (threshold is not None) else self.t0Threshold

        while (
            (deltaTime == 0.1) or
            (abs(
                ((constants[-1] - constants[0]) / constants[0])
            ) < threshold)
        ):  # Repeat until the relative change in C is less than the threshold given,
            # or at least once.
            red, grey, time, constants = self.timeStep(deltaTimeStep=deltaTime)
                # Get the latest values from the step function.
            deltaTime /= 2
                # Divide deltaTime by 2.

        return deltaTime

    @staticmethod
    def formatPlot(xLabel: str | None = None,
                   yLabel: str | None = None,
                   title: str | None = None) -> None:
        """
        Formats plot figure.

        :param xLabel: X-axis label.
        :param yLabel: Y-axis label.
        :param title: Title of plot.
        """

        plt.xlabel(xLabel)
        plt.ylabel(yLabel)
        plt.title(title)
        plt.legend()
        plt.grid()

    def plotRedAndGreyOverTime(self) -> None:
        """
        Plots r, g, and C against time.
        """

        red, grey, time, constants = self.timeStep()

        plt.plot(time, grey, color="grey", label="Grey Squirrels (g)")
        plt.plot(time, red, color="red", label="Red Squirrels (r)")
        plt.plot(time, constants, color="blue", linestyle="dashed", label="Conserved Quantity (C)")

        self.formatPlot("Time", "Population", "Red & Grey Squirrel Populations Over Time")

        plt.show()

    def plotRedAndGreyPlane(self, deltaTimeStep: float | None = None) -> None:
        """
        Plots the r and g values in the rg plane, visualising the relation between grey and red squirrels
        """

        deltaTimeStep = deltaTimeStep if (deltaTimeStep is not None) else self.deltaTimeStep

        red0, grey0, time0, constants0 = self.timeStep()
        red1, grey1, time1, constants1 = self.timeStep(deltaTimeStep=deltaTimeStep)

        plt.plot(red0, grey0, label="Timestep t0", color="navy")
        plt.plot(red1, grey1, label=f'Timestep {deltaTimeStep}', color="darkcyan")
        plt.scatter([0, 2], [0, 1], marker='x', label="Equilibrium points", color="black")
        plt.plot([1, 3], [1 + math.sqrt(2) / 2, 1 - math.sqrt(2) / 2], "red", linestyle="dotted",
                 label="Unstable Manifold")
        plt.plot([1, 3], [1 - math.sqrt(2) / 2, 1 + math.sqrt(2) / 2], "green", linestyle="dotted",
                 label="Stable Manifold")

        self.formatPlot("Red Squirrels (r)", "Grey Squirrels (g)", "Plane of Squirrel Competition Model")

        plt.show()

    def plotStableAndUnstableManifolds(self,
                                       deltaTimeStep: float | None = None,
                                       simulationLength: int | None = None) -> None:
        """
        Plots estimates of the stable and unstable manifolds.
        """

        deltaTimeStep = deltaTimeStep if (deltaTimeStep is not None) else self.deltaTimeStep
        simulationLength = simulationLength if (simulationLength is not None) else self.simulationLength

        redForward, greyForward, _, _ = self.timeStep(
            initialRedSquirrels=(1 + deltaTimeStep),
            initialGreySquirrels=(1 - deltaTimeStep),
            deltaTimeStep=deltaTimeStep,
            simulationLength=simulationLength
        )
        redBackward, greyBackward, _, _ = self.timeStep(
            initialRedSquirrels=(1 - deltaTimeStep),
            initialGreySquirrels=(1 + deltaTimeStep),
            deltaTimeStep=deltaTimeStep,
            simulationLength=simulationLength,
            forward=False
        )

        plt.plot(redForward, greyForward, label="Unstable Manifold (Forward)", color="red")
        plt.plot(redBackward, greyBackward, label="Stable Manifold (Backward)", color="green")
        plt.scatter([0, 2], [0, 1], marker='x', label="Equilibrium Points", color="black")

        self.formatPlot("Red Squirrels (r)", "Grey Squirrels (g)", "Stable and Unstable Manifolds")

        plt.show()

# Create & run the model.

model = SquirrelCompetitionModel()

model.plotRedAndGreyOverTime()
model.plotRedAndGreyPlane(deltaTimeStep=0.1)
model.plotStableAndUnstableManifolds()

