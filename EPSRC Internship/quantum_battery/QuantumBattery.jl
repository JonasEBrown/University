using SpecialFunctions

struct QBParameters
    k::Float64

    ω1::Float64
    ω2::Float64

    F::Float64
    γ::Float64

    QBParameters(
        parameters::DSystemParameters;
        lims::Tuple{Vararg{NTuple{2, Float64}}} = (
            (-6.0, 6.0), (-6.0, 6.0)
        ),

        name::String = "QuantumBattery",
        Δω::Float64 = parameters.Δω,
    ) = DSystemParameters(
        [parameters...],
        lims,
        name;
        Δω,
    )

    QBParameters(
        ;
        k::Float64 = 0.0,
        ω1::Float64 = 0.98,
        ω2::Float64 = 1.02,

        F::Float64 = 1.0,
        γ::Float64 = 0.0,

        lims::Tuple{Vararg{NTuple{2, Float64}}} = (
            (-6.0, 6.0), (-6.0, 6.0), (-6.0, 6.0), (-6.0, 6.0)
        ),

        name::String = "QuantumBattery",
    ) = DSystemParameters(
        [k, ω1, ω2, F, γ],
        lims,
        name;
        Δω = abs(ω1 - ω2),
    )
end

function QuantumBatteryUncoupled(
    ;
    parameters::DSystemParameters = QBParameters(
        ;
        lims = (
            (-6.0, 6.0), (-6.0, 6.0),
            (-6.0, 6.0), (-6.0, 6.0),
        )
    ),
    u0::SVector{4, Float64} = SVector(zeros(4)...),
    system_kw = (),
)
    ds = function
        (
            u,
            parameters, 
            t,
        )
        aR1, aC1, bR1, bC1 = u

        a1, b1 = aR1 + aC1*im, bR1 + bC1*im

        k, ω1, ω2, F, γ = parameters

        A, r, τ_Q = 1.0, 1.0, 10.0
        g = (A / erf(r)) * erf((r * t) / τ_Q)

        da1 = (-im*b1*g) + F - (γ/2)*a1
        db1 = -im*a1*g

        return SVector(
            real(da1),
            imag(da1),
            real(db1),
            imag(db1),
        )
    end

    return DSystem(
        ds,
        parameters,
        u0;
        system_kw...,
    )
end