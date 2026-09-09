struct LVParameters
    k::Float64

    ω1::Float64
    ω2::Float64

    a::Float64
    b::Float64
    c::Float64
    d::Float64

    LVParameters(
        parameters::DSystemParameters;
        lims::Tuple{Vararg{NTuple{2, Float64}}} = (
            (-6.0, 6.0), (-6.0, 6.0)
        ),

        name::String = "LotkaVolterra",
        Δω::Float64 = parameters.Δω,
    ) = DSystemParameters(
        [parameters...],
        lims,
        name;
        Δω,
    )

    LVParameters(
        ;
        k::Float64 = 0.0,
        ω1::Float64 = 0.98,
        ω2::Float64 = 1.02,

        a::Float64 = 1.0,
        b::Float64 = 1.0,
        c::Float64 = 2.0,
        d::Float64 = 1.0,

        h::Float64 = 0.5,

        lims::Tuple{Vararg{NTuple{2, Float64}}} = (
            (-6.0, 6.0), (-6.0, 6.0), (-6.0, 6.0), (-6.0, 6.0)
        ),

        name::String = "LotkaVolterra",
    ) = DSystemParameters(
        [k, ω1, ω2, a, b, c, d, h],
        lims,
        name;
        Δω = abs(ω1 - ω2),
    )
end

function LotkaVolterraUncoupled(
    ;
    parameters::DSystemParameters = LVParameters(
        ;
        lims = (
            (-6.0, 6.0), (-6.0, 6.0),
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

        k, ω1, ω2, a, b, c, d, h = parameters

        dx1 = x1 * (a - b*y1)
        dy1 = y1 * (-c + d*x1)

        return SVector(dx1, dy1)
    end

    return DSystem(
        ds,
        parameters,
        u0;
        system_kw...,
    )
end

function LotkaVolterraCoupled(
    ;
    parameters::DSystemParameters = LVParameters(
        ;
        lims = (
            (-6.0, 6.0), (-6.0, 6.0), (-6.0, 6.0), (-6.0, 6.0),
        )
    ),
    u0::SVector{4, Float64} = SVector(zeros(4)...),
    system_kw...,
)
    ds = function
        (
            u,
            parameters, 
            t,
        )
        x1, y1, x2, y2 = u

        k, ω1, ω2, a, b, c, d, h = parameters

        dx1 = ω1*(x1 * (a - b*y1) + k*(x2 - x1))
        dy1 = ω1*(y1 * (-c + d*x1))

        dx2 = ω2*(x2 * (a - b*y2) + k*(x1 - x2) + h)
        dy2 = ω2*(y2 * (-c + d*x2))

        return SVector(dx1, dy1, dx2, dy2)
    end

    sys_uncoupled = LotkaVolterraUncoupled(
        ;
        parameters = LVParameters(parameters),
        u0 = SVector{2}(u0[[1,2]]),
        system_kw = system_kw,
    )

    return DSystem(
        ds,
        parameters,
        u0;
        sys_uncoupled = sys_uncoupled,
        system_kw...
    )
end