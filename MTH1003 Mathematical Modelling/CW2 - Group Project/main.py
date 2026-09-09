import numpy as np
import matplotlib.pyplot as plt

# Constants
g = 10  # m/s^2
m = 10**3  # kg
a, b, d = 100, 100, 100  # given parameters
G = 21  # Replace with your group number
c = 50 + (10 * G) / 6  # dependent on group number

V0 = 1


# Potential function and derivatives
def V(s):
    return -V0 * ((s / a) ** 2) * (((s / b) ** 2) - 1) * (((s / c) ** 2) - 1) * np.exp(-2 * (((s / d) ** 2) - 1))


def dV_ds(s):
    h = 1e-5  # small step for numerical differentiation
    return (V(s + h) - V(s - h)) / (2 * h)


def d2V_ds2(s):
    h = 1e-5
    return (V(s + h) - 2 * V(s) + V(s - h)) / (h ** 2)


s_values = np.linspace(-500, 500, 1000)
F_values = -dV_ds(s_values)


# Plot the graph of V against displacement
def plot_graph():
    plt.plot(s_values, F_values, label='F(s)')
    plt.axhline(0, color='black', linestyle='--')
    plt.xlabel('s (m)')
    plt.ylabel('F(s)')
    plt.title('Force F(s) vs. Position s')
    plt.legend()
    plt.grid()
    plt.show()


# Finding equilibrium positions
def find_equilibria():
    # Root-finding using simple numerical approach
    equilibria = []
    for i in range(len(s_values) - 1):
        if F_values[i] * F_values[i + 1] < 0:  # Sign change indicates root
            root = (s_values[i] + s_values[i + 1]) / 2
            equilibria.append(round(root, 3))

    return np.unique(equilibria)


# Stability and oscillation frequency
def analyse_stability(equilibria):
    stable = []
    unstable = []
    frequencies = {}

    for s_eq in equilibria:
        second_derivative = d2V_ds2(s_eq)
        if second_derivative > 0:
            stable.append(s_eq)
            omega = np.sqrt(second_derivative / m)
            frequencies[s_eq] = omega
        else:
            unstable.append(s_eq)

    return stable, unstable, frequencies


# Running the analysis
V0 = 600  # Example value for V0, can be adjusted
plot_graph()
equilibria = find_equilibria()
stable, unstable, frequencies = analyse_stability(equilibria)

print("Equilibrium positions:", equilibria)
print("Stable positions:", stable)
print("Unstable positions:", unstable)
print("Frequencies of oscillation at stable points:", frequencies)
