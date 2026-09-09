import numpy as np
import matplotlib.pyplot as plt

a, b, c = 1, -1.5, 0.2

def F(t, X):
    x, y, z = X # Deconstruct X into components.
    return np.array( # Construct a nparray with new values from system (dx/dt, dy/dt, dz/dt).
        [
            (-a * np.pow(x, 3)) + (3 * b * y * np.pow(z, 4)),
            (a * np.pow(x, 3)) - (b * y * np.pow(z, 2)),
            (-b * y * np.pow(z, 2)) + (c * np.sin(x)),
        ]
    )

def rungeKutta2Step(t, X, dt): # Runge-Kutta 2
    k1 = F(t, X)
    k2 = F(t + dt, X + (k1 * dt))
    return X + ((k1 + k2) * dt * 0.5) # New value of X.

def rungeKutta4Step(t, X, dt): # Runge-Kutta 4
    k1 = F(t, X)
    k2 = F(t + (dt * 0.5), X + (k1 * dt * 0.5))
    k3 = F(t + (dt * 0.5), X + (k2 * dt * 0.5))
    k4 = F(t + dt,   X + (k3 * dt))
    return X + ((k1 + (k2 * 0.5) + (k3 * 0.5) + k4) * dt / 6) # New value of X.

def integrate(rungeKuttaMethod, initial_conditions, t_max, dt): # Function to integrate to time t_max with dt and initial conditions
    steps = int(t_max / dt) # Total steps in integration.
    X = np.zeros((steps + 1, 3)) # Initialise nparray with columns of all zeros.
    X[0] = initial_conditions # Set initial conditions.
    for t in range(1, steps): # Iterate through each delta step.
        X[t] = rungeKuttaMethod(t, X[t - 1], dt) # Set each t value to the Runge-Kutta returned value for the last X value.
    return X # Return each step of X.

def plot(X, t_max, dt, title): # Plot X against time.
    size_t = max(t_max, 18)  # Set minimum plot size.
    plt.figure(figsize=(size_t / 3, (size_t + 5) * 9 / 48)) # Size the plot so x-axis isn't squished and adjust height to 16:9 ratio.
    plt.plot(X[:, 0], label="x") # Plot x-values.
    plt.plot(X[:, 1], label="y") # Plot y-values.
    plt.plot(X[:, 2], label="z") # Plot z-values.
    total_ticks = int(t_max + 1) # Total ticks is actual +1 as starts at 0.
    plt.xticks( # Show the x-axis in seconds not dt.
        np.arange(0, total_ticks / dt, 1 / dt),
        range(0, total_ticks, 1),
    )
    plt.xlabel("Time (t)") # Label x-axis.
    plt.ylabel("Value") # Label y-axis.
    plt.title(title) # Title plot.
    plt.legend() # Add legend.
    plt.grid(True) # Show gridlines.
    plt.show() # Display plot.

# Initial conditions & total time to integrate for (along with precision dt).

initial_conditions = [1.0, 0.0, 0.5]
t_max = 20.0
dt = 0.01

# Integrate.

X_RungeKutta2 = integrate(rungeKutta2Step, initial_conditions, t_max, dt)
X_RungeKutta4 = integrate(rungeKutta4Step, initial_conditions, t_max, dt)

# Plot results.

plot(X_RungeKutta2, t_max, dt, "Runge-Kutta 2 Solution")
plot(X_RungeKutta4, t_max, dt, "Runge-Kutta 4 Solution")
