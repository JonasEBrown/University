# import Pkg

# Pkg.add([
#     "JLD2",
#     "CairoMakie",
#     "DynamicalSystems",
# ])

using JLD2
using CairoMakie
using Statistics
using LinearAlgebra
using DynamicalSystems

# Constants.

COLORS = [
    "#7143E0",
    "#191E44",
    "#0A9A84",
    "#AF9327",
    "#900C37",
    "#6C768C"
]

# Utilities.

include("Utils.jl")

# Systems.

include("systems/Rossler.jl")
include("systems/PredatorPrey.jl")
include("systems/DuffingOscillator.jl")

# Individual modules.

include("FGBase.jl")
include("DBSCAN.jl")
include("Featurisers.jl")
include("GlobalContinuation.jl")
include("MinimumCriticalShock.jl")

# Plotting methods.

include("Plotting.jl")