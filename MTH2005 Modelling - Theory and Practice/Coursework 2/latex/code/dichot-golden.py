import numpy as np
import matplotlib.pyplot as plt
import time

golden_ratio = (np.sqrt(5) - 1) / 2 # Define the golden ratio

# User-defined function
fdich = lambda x: np.exp(-x + np.pi) + np.pow(x, 2)

# Initial values
a = 0.0
b = 6.0
niter = 40
tolerance = 1e-4

# Plot analytic function
x = np.linspace(a, b, int(1/0.01))  # about 100 steps across interval
y = fdich(x)

plt.figure(figsize=(8, 5))
plt.plot(x, y, label="Analytic solution")
plt.grid(True)

colors = plt.cm.tab20(np.linspace(0, 1, niter))
legend_entries = ["Analytic solution"]

def golden_section_search(a, b, tol=1e-4): # Define the golden-search algorithm
    start_time = time.time()
    c = b - golden_ratio * (b - a)  # Set c to the left bracket offset by the difference multiplied by the golden ratio.
    d = a + golden_ratio * (b - a)  # Set d to right bracket ""
    fc, fd = fdich(c), fdich(d)
    totalFunctionCalls = 2
    functionCalls = [0, totalFunctionCalls]
    err = np.abs(b - a) / 2
    errors = []
    while err > tol: # Check if the difference between the two brackets is less than the tolerance.                                                     "".
        if fc < fd: # If f(c) < f(d) then set the right bracket to d.
            b, d, fd = d, c, fc
            # Choose new interval [a, d].
            # Point d now becomes c.
            # Reuse f(c).
            c = b - golden_ratio * (b - a) # Calculate new point c.
            fc = fdich(c) # Find f(c).
        else: # Else set the left bracket to c. Can change fdich(c) < fdich(d) to fdich(c) > fdich(d) for maximum.
            a, c, fc = c, d, fd
            # Choose new interval [c, b].
            # Point c now becomes d.
            # Reuse f(d).
            d = a + golden_ratio * (b - a) # Calculate new point d.
            fd = fdich(d) # Find f(d).
        totalFunctionCalls += 1
        err = np.abs(b - a) / 2
        errors.append(err)
        functionCalls.append(totalFunctionCalls)
    end_time = time.time()
    total_time = end_time - start_time
    return total_time, (b + a) / 2, errors, functionCalls # When the brackets are within a tolerance of each other return the midpoint of the two.

def iteration(a, b, tol=1e-4):
    iter_count = 0
    err = abs(b - a) / 2
    eps = tol / 2
    totalFunctionCalls = 0

    print(" iter, a, b, err")
    start_time = time.time()

    errors = [err]
    functionCalls = [totalFunctionCalls]

    while err > tol:
        x1 = a + 0.5 * (b - a) - eps
        x2 = a + 0.5 * (b - a) + eps

        u = fdich(x1)
        v = fdich(x2)

        midpoint = (a + b) / 2
        fmid = fdich(midpoint)

        totalFunctionCalls += 3
        functionCalls.append(totalFunctionCalls)

        # Plot midpoint marker
        plt.plot(
            midpoint,
            fmid,
            marker="x",
            markersize=10,
            linewidth=2,
            # color=colors[iter_count]
        )
        legend_entries.append(f"Iter {iter_count + 1}")

        if u > v:
            a = x1
        elif u < v:
            b = x2
        else:
            print("help")

        err = abs(b - a) / 2

        errors.append(err)
        print(iter_count, a, b, err)
        iter_count += 1

    end_time = time.time()
    total_time = end_time-start_time

    plt.title("Plot of $f(x) = e^{-(x-\pi)}+x^{2}$")
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.legend(legend_entries, loc="best")
    plt.show()

    return total_time, errors, functionCalls

def plot_errors(errors, title):
    plt.figure(figsize=(8, 5))
    x = np.linspace(0, len(errors), len(errors))
    plt.plot(x, np.log10(errors), marker="x")
    plt.xticks(range(0, len(errors) + 1))
    plt.xlabel("Iteration")
    plt.ylabel("log10(errors)")
    plt.title(title)
    plt.show()

def plot_function_calls(function_calls, title):
    plt.figure(figsize=(8, 5))
    x = np.linspace(0, len(function_calls), len(function_calls))
    plt.plot(x, function_calls, marker="x")
    plt.xticks(range(0, len(function_calls) + 1))
    plt.xlabel("Iteration")
    plt.ylabel("Function calls")
    plt.title(title)
    plt.show()

    slope, intercept = np.polyfit(x, function_calls, 1)
    return {
        'slope': slope,
        'intercept': intercept,
    }

dichotomous_time, dichotomous_errors, dichotomous_function_calls = iteration(a, b, tolerance)
golden_time, xmin, golden_errors, golden_function_calls = golden_section_search(a, b)

plot_errors(dichotomous_errors, "Dichotomous method error")
plot_errors(golden_errors, "Golden-Section method error")

dichotomous_analysis = plot_function_calls(dichotomous_function_calls, "Dichotomous function calls")
golden_analysis = plot_function_calls(golden_function_calls, "Golden-Section function calls")

print(f'xmin = {xmin:0.4f}')
print(f'Dichotomous: time = {dichotomous_time:0.4f}, slope = {dichotomous_analysis['slope']:0.4f}')
print(f'Golden: time = {golden_time:0.4f}, slope = {golden_analysis['slope']:0.4f}')