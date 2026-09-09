import numpy as np
import matplotlib.pyplot as plt

f = lambda x: np.sin(np.pow(x, 3)) # f(x) = dx/dt.
fp = lambda x: (3.0 * np.pow(x, 2)) * np.cos(np.pow(x, 3)) # f'(x).

g = lambda a, b, dt: b - a - (dt * f(b)) # g(x_n, x_n+1) = Implicit method g(x_{n+1}) = 0.
gp = lambda a, b, dt: 1.0 - (dt * fp(b)) # g'(x_n, x_n+1).

def newtonRaphson(xn, dt, tolerance=1e-10, iterations=50):
    z = xn
    for i in range(iterations):
        z_new = z - g(xn, z, dt) / gp(xn, z, dt)
        if abs(z_new - z) < tolerance: return z_new
        z = z_new
    raise RuntimeError(f"Newton-Raphson did not converge to a value within {iterations} iterations")

def backwardEuler(initialX, t_max, dt, tolerance=1e-10, iterations=50):
    N = int(t_max / dt)
    x = np.zeros(N + 1)
    x[0] = initialX
    for n in range(N):
        x[n + 1] = newtonRaphson(x[n], dt, tolerance, iterations)
    return x

def plot(x, t_max, dt, title): # Plot x against time.
    size_t = max(t_max, 18) # Set minimum plot size.
    plt.figure(figsize=(size_t / 3, (size_t + 5) * 9 / 48)) # Size the plot so x-axis isn't squished and adjust height to 16:9 ratio.
    plt.plot(x, label="x") # Plot x-values.
    total_ticks = int(t_max + 1) # Total ticks is actual +1 as starts at 0.
    plt.xticks( # Show the x-axis in seconds not dt.
        np.arange(0, total_ticks / dt, 1 / dt),
        range(0, total_ticks, 1),
    )
    plt.xlabel("Time (t)") # Label x axis.
    plt.ylabel("x(t)") # Label y axis.
    plt.title(title) # Title plot.
    plt.legend() # Add legend.
    plt.grid(True) # Show gridlines.
    plt.show() # Display plot.

# Initial condition x_0 and t_max (with precision dt).

x_0 = 1.0
t_max = 5.0
dt = 0.1

# Solve with Backward-Euler.

x = backwardEuler(x_0, t_max, dt)

# Plot results.

plot(x, t_max, dt, "Backward-Euler and Newton-Raphson")