# Libraries #
import numpy as np
import matplotlib.axes as ax
import matplotlib.pyplot as mpl

# mydata #
from functions import *
x, y = mydata(myID())

##########################
# Task 2: Plotting (15%) #
##########################

def plot(xValues, yValues, xLabel: str = "x", yLabel: str = "y", title: str = "y = f(x)",
         titleSize: int = 18, axisSize: int = 14, axisTickSize: int = 11, legendSize: int = 8.5,
         plotFormat: str = "*", zorder=0, linewidth=2, markersize=7):
    # I decided to abstract this into its own function as I saw in the task description that more plots will be created later
    # on. This takes several inputs, most of which have a default value and also a defined type.

    # This line creates a plot of the x values passed in against the y values, and applies the passed format as well. If one
    # wasn't provided then it will default to a scatter plot.
    mpl.plot(xValues, yValues, plotFormat, zorder=zorder, linewidth=linewidth, markersize=markersize)

    # This adds a title to the plot with a text size of titleSize.
    mpl.title(title, size=titleSize, pad=axisSize)

    # These add axes labels to the plot with text size of axisSize.
    mpl.xlabel(xLabel, size=axisSize)
    mpl.ylabel(yLabel, size=axisSize, rotation=0)

    # Change the limits of the axis.
    mpl.xlim(-2, 5)

    # This changes the size of the axis ticks to axisTickSize.
    mpl.tick_params(labelsize=axisTickSize)

    # Add a legend to the plot.
    mpl.legend(["Data points", "Cubic interpolation", "Root found at y=0"], loc="lower left", fontsize=legendSize)

# This line plots y against x and titles it appropriately.
plot(x, y, zorder=1)

#####################################
# Task 3: Cubic interpolation (35%) #
#####################################

# Reduced x and y down to the 2nd, 3rd, 4th and 5th data points.
reducedX, reducedY = x[1:5], y[1:5]

# Create a linear space for y - which will allow us to display the values inbetween the data points.
# Essential for graphing the cubic.
linX = np.linspace(reducedX.min(), reducedX.max(), 100)

# Map our linear space y values to x with the cubicfit function.
linY = cubicfit(reducedX, reducedY, linX)

# Plot the line using the linear space for y and then find the value of x for each on of those.
plot(linX, linY, plotFormat="r", zorder=0)

##############################
# Task 4: Root finding (45%) #
##############################

# Calculate an estimate for the root between x[2] and x[3]
xstar = findroot(x[2], x[3])

# Plot the root on the graph.
plot(xstar, 0, plotFormat="g*", zorder=2)

# Add the line y = 0 to the plot.
mpl.axhline(0, color="gray", alpha=0.5)

# Save the graph to yplot.png.
mpl.savefig("yplot.png")

# Show the graph.
mpl.show()