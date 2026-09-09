# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

# Number of points
nx = 10000
dx = (2 * np.pi) / (nx - 1)

# Grid points
x = np.linspace(0, 2 * np.pi, nx)

# Fine grid for plotting true solution
dxs = (2 * np.pi) / 100
x_t = np.linspace(0, 2 * np.pi, int((2 * np.pi) / dxs) + 1)

# Right-hand side (f_i)
b = (dx**2) * np.cos(x)

# Initialize matrix A
A = np.zeros((nx, nx))

# Fill interior points
for i in range(1, nx - 1):
    A[i, i - 1] = 1
    A[i, i] = -2
    A[i, i + 1] = 1

# Neumann BC at x=0: y'(0) ≈ (y1 - y0)/dx = 0 → y1 = y0
A[0, 0] = 1
A[0, 1] = -1

# Dirichlet BC at x=2π: y(nx-1) = 0
A[-1, -1] = 1
b[-1] = 0

# Solve Ay = b
y = np.linalg.solve(A, b)

# True solution on same grid
y_true = -np.cos(x) + 1

# Compute average error
error = np.mean(np.abs(y - y_true))
print(f"Average error for nx={nx}: {error:.6f}")

# Plot results
plt.figure()
plt.plot(x, y, label='Numerical')
plt.plot(x_t, -np.cos(x_t) + 1, 'r.', label='True solution')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Numerical vs True Solution')
plt.legend()
plt.grid(True)
plt.show()
