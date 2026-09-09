include("../src/include.jl")
include("QuantumBattery.jl")

sys = QuantumBatteryUncoupled(
    ;
)

k_values = [0.0]
u0s = [SVector(y, y, y, y) for y in [0.0]]

for k in k_values
    figs = plot_system_timeseries(
        sys;
        k = k,
        u0s = u0s,
        t = 100.0,
    )

    [display(fig) for (fig, axs) in figs]

    # [save("k_0.05_ghost_la_sync.png", fig) for (fig, axs) in figs]
end