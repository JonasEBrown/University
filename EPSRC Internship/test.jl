include("src/include.jl")

sys = TristableFitzhughNagumoCoupled()

interactive_dsystem(
    sys,
    [
        SVector(y, 0, y, 0)
        for y in [0.1, 1.3, 2.0]
    ];
)