struct DSystemParameters
    data::Vector{Float64}

    lims::Tuple{Vararg{NTuple{2, Float64}}}
    name::String

    Δω::Float64

    DSystemParameters(
        data::Vector{Float64},

        lims::Tuple{Vararg{NTuple{2, Float64}}},
        name::String;

        Δω::Float64 = 0.0,
    ) = new(data, lims, name, Δω)
end

Base.vec(parameters::DSystemParameters) = [parameters.data...]

Base.iterate(parameters::DSystemParameters) = iterate(parameters.data)
Base.iterate(parameters::DSystemParameters, state) = iterate(parameters.data, state)

Base.getindex(parameters::DSystemParameters, i::Int) = parameters.data[i]
