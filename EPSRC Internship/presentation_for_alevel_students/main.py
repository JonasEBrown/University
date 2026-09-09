import math
import matplotlib.pyplot as plt

CONST_R = 1
CONST_G = 2

def rDot(r, g):
    return r*(CONST_R - g)

def gDot(r, g):
    return g*(CONST_G - r)

def diffuse(xs, exclude, k):
    return k*(sum(xs) - ((len(xs) - 1) * xs[exclude]))

def timeStep(r_values, g_values, k, deltaTime = 1e-1):
    dr_values = [rDot(r, g_values[idx]) + diffuse(r_values, idx, k) for idx, r in enumerate(r_values)]
    dg_values = [gDot(r_values[idx], g) for idx, g in enumerate(g_values)]

    new_r = [r + (dr_values[idx] * deltaTime) for idx, r in enumerate(r_values)]
    new_g = [g + (dg_values[idx] * deltaTime) for idx, g in enumerate(g_values)]

    return new_r, new_g

u0s = [
    [0.5, 0.5],
    [0.116, 0.116],
]

k_values = [0, 5e-2, 5e-1, 1]
runLength = 10
dt = 1e-5

for k in k_values:
    r, g = u0s
    r_values, g_values = [], []
    t_values = []

    for t in range(int(runLength / dt)):
        r, g = timeStep(r, g, k, deltaTime=dt)
        r_values.append(r)
        g_values.append(g)
        t_values.append(t * dt)

    r_values = [[r_values[idx][dim] for idx in range(len(r_values))] for dim in range(len(r_values[0]))]
    g_values = [[g_values[idx][dim] for idx in range(len(g_values))] for dim in range(len(g_values[0]))]

    for idx, r in enumerate(r_values):
        plt.plot(t_values, r)
        plt.plot(t_values, g_values[idx])

    plt.show()