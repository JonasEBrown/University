struct VDPParameters
    k::Float64

    ω1::Float64
    ω2::Float64

    α::Float64
    β::Float64
    μ::Float64
    d::Float64

    VDPParameters(
        parameters::DSystemParameters;
        lims::Tuple{Vararg{NTuple{2, Float64}}} = (
            (-10.0, 10.0), (-10.0, 10.0)
        ),
        name::String = "VanDerPol",
        Δω::Float64 = parameters.Δω,
    ) = DSystemParameters(
        [parameters...],
        lims,
        name;
        Δω,
    )

    VDPParameters(
        ;
        k::Float64 = 0.0,
        ω1::Float64 = 0.98,
        ω2::Float64 = 1.02,

        α::Float64 = 0.114,
        β::Float64 = 0.003,
        μ::Float64 = 0.6,
        d::Float64 = -0.1,

        ϵ = 1.0,

        lims::Tuple{Vararg{NTuple{2, Float64}}} = (
            (-10.0, 10.0), (-10.0, 10.0), (-10.0, 10.0), (-10.0, 10.0)
        ),

        name::String = "VanDerPol",
    ) = DSystemParameters(
        [k, ω1, ω2, α, β, μ, d, ϵ],
        lims,
        name;
        Δω = abs(ω1 - ω2),
    )
end

function VanDerPolUncoupled(
    ;
    parameters::DSystemParameters = VDPParameters(
        ;
        lims = (
            (-10.0, 10.0), (-10.0, 10.0)
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
        x1, y1 = u

        k, ω1, ω2, α, β, μ, d, ϵ = parameters

        dx1 = y1*ϵ
        dy1 = μ*y1*ϵ*(1 - x1^2 + α*(x1^4) - β*(x1^6)) - x1 - d*(y1 - x1)

        return SVector(dx1, dy1)
    end

    return DSystem(ds, parameters, u0; system_kw...)
end

function VanDerPolCoupled(
    ;
    parameters::DSystemParameters = VDPParameters(
        ;
        lims = (
            (-10.0, 10.0), (-10.0, 10.0), (-10.0, 10.0), (-10.0, 10.0),
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
        x1, y1, x2, y2 = u

        k, ω1, ω2, α, β, μ, d, ϵ = parameters

        dx1 = ω1*ϵ*(y1 + k*(x2 - x1))
        dy1 = ω1*ϵ*(μ*y1*(1 - x1^2 + α*(x1^4) - β*(x1^6)) - x1 - d*(y1 - x1))

        dx2 = ω2*ϵ*(y2 + k*(x1 - x2))
        dy2 = ω2*ϵ*(μ*y2*(1 - x2^2 + α*(x2^4) - β*(x2^6)) - x2 - d*(y2 - x2))

        return SVector(dx1, dy1, dx2, dy2)
    end

    sys_uncoupled = VanDerPolUncoupled(
        ;
        parameters = VDPParameters(parameters),
        u0 = SVector{2}(u0[[1,2]]),
        system_kw = system_kw,
    )

    return DSystem(ds, parameters, u0; sys_uncoupled = sys_uncoupled, system_kw...)
end