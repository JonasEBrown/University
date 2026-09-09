import numpy as np
import matplotlib.pyplot as plt
import time

# User-defined function
def fdich(x):
    return np.abs(np.sin(x)) # example placeholder

# Initial values
iter_count = 0
niter = 40
a = 1.2
b = 4.1

tolerance = 1e-4
eps = tolerance / 2

err = abs(b - a) / 2

# Plot analytic function
x = np.linspace(a, b, int(1/0.01))  # about 100 steps across interval
y = fdich(x)

plt.figure(figsize=(8, 5))
plt.plot(x, y, label="Analytic solution")
plt.grid(True)

colors = plt.cm.tab20(np.linspace(0, 1, niter))
legend_entries = ["Analytic solution"]

print(" iter, a, b, err")
start_time = time.time()

# 39 3.1315926535881586 3.151592653590778 0.010000000001309628

while err > 1e-3:
    x1 = a + 0.5 * (b - a) - eps
    x2 = a + 0.5 * (b - a) + eps

    u = fdich(x1)
    v = fdich(x2)

    midpoint = (a + b) / 2
    fmid = fdich(midpoint)

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

    print(iter_count, a, b, err)
    iter_count += 1

end_time = time.time()
print(f'execution time = {end_time-start_time}')
plt.legend(legend_entries, loc="best")
plt.show()
