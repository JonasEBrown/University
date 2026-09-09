# Libraries #
import numpy as np

# myID #

def myID():
     return 0

# mydata #

def mydata(studentID):
    # Generate a series of 6 data points, dependent on the
    # input argument studentID

    # DO NOT MODIFY THIS CODE
    # otherwise your coursework functions might not
    # work correctly when tested

    # This code is deliberately obscure - you are not
    # expected to understand it or even look at it!

    assert studentID < 1e9, "studentID exceeds maximum allowed"

    studentID += int(1e8)
    tmp = str(studentID)

    T = []
    for k in tmp:
        T.append(float(k))
    T = np.array(T)
    xoff = sum(T)/17 % 2 - 1
    x = np.linspace(0, 5, 6)
    x += 0.01 * x * x + xoff
    yoff = 0.1 + 0.5 * sum(T**2)/13
    kperm = [7, 5, 8, 4, 6, 1]
    p = [2, 3, 5, 4, 6, 1] + T[7]
    y = abs(T[kperm] - yoff) * (-1)**p

    return x, y

#####################################
# Task 3: Cubic interpolation (35%) #
#####################################

def mul(*args):
    # I decided to make this a function as it is normally not included in Python,
    # and it would be much easier if it was an option to use.

    # Set result to 1 so that it can be multiplied by any number.
    result = 1

    for arg in args:
        # Loop through any arguments passed in.

        # Multiply result by arg and store it back in result.
        result *= arg

    # Return the result.
    return result


class Cubic:
    """
    I thought that abstracting the code into a class would make it much easier to work with
    and also much nicer to look at.
    """

    def __init__(self, xValues, yValues):
        # Basic setup of the class.

        # Store the parameters as variables inside the class.
        self.xValues = xValues
        self.yValues = yValues

    def legrange(self, _x, i: int):
        # Create a function for calculating the Legrange coefficient (I guess it's called).

        """
            You may well look at the below code and think to yourself "WHAT the bloody hell is this??",
            and you would be correct in judging it like that. However, once I've explained it, I hope that
            you won't judge it too hard anymore :).
            Okay, so...
                - "mul" is the function that I made up above,
                - "for j in range(len(self.xValues))" loops through values 0 to n, where n is the number of x values.
                - "if j != i" excludes the value i from the loop (where j == i).
                - "(_x - self.xValues[j]) /
                                (self.xValues[i] - self.xValues[j])" is essentially our (x_hat - x_j) divided by
                                                                     (x_i - x_j) - which is our Legrange formula.
                - "*[ ...CODE ]" - the square brackets [] define a for loop, following the same format as
                                 [(2 * i) for i in range(1, 4)] which would produce a list of [2, 4, 6, 8].
                                 In addition, adding an if statement:
                                 [(2 * i) for i in range(1, 5) if (i != 3)] would give [2, 4, 8, 10].
                                     Finally, the "*" unpacks the list returns into the function mul.
        """
        # LaTeX: \[l_{i}(x) = \prod_{j=0, j\neq i}^{n} \frac{(x - x_{j})}{(x_{i} - x_{j})} \]
        return mul(*[
            (
                    (_x - self.xValues[j]) /
                    (self.xValues[i] - self.xValues[j])
            ) for j in range(len(self.xValues)) if j != i
        ])

    def yhat(self, xhat):
        # Function returns the value of the Legrange polynomial at xhat.

        """
            Returns the value of the polynomial p(x) where x = xhat.
            Essentially, it is doing this:
                p(xhat) = (y_0 * l_0(xhat)) + ... + (y_n * l_n(xhat)) where n is the number of y values.
        """
        # LaTeX: \[p(x)=\sum_{i=0}^{n} y_{i}l_{i}(x)\]
        return sum([(_y * self.legrange(xhat, i)) for i, _y in enumerate(self.yValues)])


def cubicfit(_x, _y, xhat):
    # Define a function cubicfit as told.

    # Return the value of the cubic at xhat.
    return Cubic(_x, _y).yhat(xhat)

##############################
# Task 4: Root finding (45%) #
##############################

def regulaFalsi(func, xl, xr):
    # Abstracted the function to make the code more readable.

    # Get the values of xl and xr on the curve.
    fl, fr = func(xl), func(xr)

    # Return the result of the regula falsi method.
    # LaTeX: \[\frac{x_{l}f(x_{r}) - x_{r}f(x_{l})}{f(x_{r}) - f(x_{l})}\]
    return (
        ((xl * fr) - (xr * fl)) /
            (fr - fl)
    )

def findroot(xl, xr):
    # findroot function called by the marker.

    # Get the x, y values from mydata.
    #xValues, yValues = mydata(myID())
    xValues, yValues = [-0.52941176, 0.48058824, 1.51058824, 2.56058824, 3.63058824, 4.72058824], [7.25384615, -7.25384615, -2.25384615, 7.25384615, 2.25384615, -7.25384615]

    # Create a Cubic class using the data given, between the ranges specified in Task 3.
    cubic = Cubic(xValues[1:5], yValues[1:5])

    # Initialise xstar and fstar as 1.
    xstar = fstar = 1

    # Repeat while the estimate for the root is greater than 1e-5.
    while abs(fstar) > 1e-5:

        # Use the regula falsi function from above to calculate the next x.
        xstar = regulaFalsi(cubic.yhat, xl, xr)

        # Calculate the value of y at xstar.
        fstar= cubic.yhat(xstar)

        # Check if fstar is on the left.
        if fstar <= 0:
            # If it is set xr to xstar.
            xr = xstar
        else:
            # Else set xl to xstar.
            xl = xstar

    # Return our estimate, xstar.
    return xstar

