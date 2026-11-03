struct PredPreyParameters
    δ::Float64
    r::Float64
    c::Float64
    μ::Float64
    υ::Float64
    α::Float64
    β::Float64
    χ::Float64

    PredPreyParameters(
        parameters::PredPreyParameters;
        lims::Tuple{Vararg{NTuple{2, Float64}}} = (
            (0.0, 15.0), (0.0, 0.05)
        ),
        name::String = "PredPreyModel",
    ) = PredPreyParameters(
        [parameters...],
        lims,
        name;
    )

    PredPreyParameters(
        ;
        r::Float64 = 2.0,
        δ::Float64 = 2.2,
        c::Float64 = 0.19,
        μ::Float64 = 0.03,
        υ::Float64 = 0.003,
        α::Float64 = 800.0,
        β::Float64 = 1.5,
        χ::Float64 = 0.004,

        lims::Tuple{Vararg{NTuple{2, Float64}}} = (
            (0.0, 15.0), (0.0, 0.05), (0.0, 15.0), (0.0, 0.05),
        ),

        name::String = "PredPreyModel",
    ) = DSystemParameters(
        [r, δ, c, μ, υ, α, β, χ],
        lims,
        name;
    )
end

function PredPreyModelUncoupled(
    ;
    parameters::DSystemParameters = PredPreyParameters(
        ;
        lims = (
            (0.0, 15.0), (0.0, 0.05)
        )
    ),
    u0::SVector{2, Float64} = SVector(zeros(2)...),
    system_kw = (),
)
    ds = function
        (
            u,
            parameters, 
            t,
        )
        N, P = u
        r, δ, c, μ, υ, α, β, χ = parameters

        s = (α * N * P) / (β + N)

        dN = (r * N * (1 - ((c / r) * N)) * ((N - μ) / (N + υ))) - s
        dP = (χ * s) - (δ * P)

        return SVector(dN, dP)
    end

    return DSystem(ds, parameters, u0; system_kw...)
end