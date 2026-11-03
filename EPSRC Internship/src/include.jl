# import Pkg

# Pkg.gc()
# Pkg.instantiate()
# Pkg.precompile()

# Pkg.add([
#     "FFTW",
#     "JLD2",
#     "Makie",
#     "LsqFit",
#     "GLMakie",
#     "CairoMakie",
#     "ChaosTools",
#     "Statistics",
#     "ColorSchemes",
#     "StaticArrays",
#     "ProgressMeter",
#     "LinearAlgebra",
#     "DynamicalSystems",
# ])

# Pkg.add(url="https://github.com/Datseris/MakieForProjects.jl")

ENV["BGCOLOR"] = :white
ENV["LINESTYLE"] = :solid

include("DSystem/DSystemParameters.jl")
include("DSystem/DSystem.jl")
include("DSystem/DSystemAttractors.jl")

include("Systems/VanDerPol.jl")
include("Systems/TristableFitzhughNagumo.jl")

include("Analysis/AttractorAnalysis.jl")
include("Analysis/AnalysisPlotting.jl")
include("Analysis/TimeseriesPlots.jl")