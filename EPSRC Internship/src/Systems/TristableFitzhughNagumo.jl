struct TFNParameters
    k::Float64

    ω1::Float64
    ω2::Float64

    α::Float64
    β::Float64
    e::Float64

    d::Float64
    c::Float64
    I::Float64
    ε::Float64

    a0::Float64
    a1::Float64
    a2::Float64
    a3::Float64
    a4::Float64

    TFNParameters(
        parameters::DSystemParameters;
        lims::Tuple{Vararg{NTuple{2, Float64}}} = (
            (-3.0, 3.0), (-3.0, 3.0)
        ),
        name::String = "TristableFitzhughNagumo",
        Δω::Float64 = parameters.Δω,
    ) = DSystemParameters(
        [parameters...],
        lims,
        name;
        Δω,
    )
    
    TFNParameters(
        ;
        k::Float64 = 0.0,
        ω1::Float64 = 0.98,
        ω2::Float64 = 1.02,

        α::Float64 = 1.0,
        β::Float64 = 1.0,
        e::Float64 = 1.0,

        d::Float64 = 5.0,
        c::Float64 = 100.0,
        I::Float64 = 0.0,
        ε::Float64 = 0.01,

        a0::Float64 = -1.0,
        a1::Float64 = 2.7778,
        a2::Float64 = 2.3333,
        a3::Float64 = 0.7619,
        a4::Float64 = 0.0847,

        lims::Tuple{Vararg{NTuple{2, Float64}}} = (
            (-3.0, 3.0), (-3.0, 3.0), (-3.0, 3.0), (-3.0, 3.0)
        ),

        name::String = "TristableFitzhughNagumo"
    ) = DSystemParameters(
        [k, ω1, ω2, α, β, e, d, c, I, ε, a0, a1, a2, a3, a4],
        lims,
        name;
        Δω = abs(ω1 - ω2),
    )
end

function TristableFitzhughNagumoUncoupled(
    ;
    parameters::DSystemParameters = TFNParameters(),
    u0::SVector{2, Float64} = SVector(zeros(2)...),
    system_kw = (),
)
    ds = function
        (
            u,
            parameters, 
            t,
        )
        v1, w1 = u

        k, ω1, ω2, α, β, e, d, c, I, ε, a0, a1, a2, a3, a4 = parameters

        dv1 = a0*v1 + a1*v1^3 - a2*v1^5 + a3*v1^7 - a4*v1^9 - α*w1 + I
        dw1 = ε*(β + c*v1 + d*v1^2 - e*w1)

        return SVector(dv1, dw1)
    end

    return DSystem(ds, parameters, u0; system_kw...)
end

function TristableFitzhughNagumoCoupled(
    ;
    parameters::DSystemParameters = TFNParameters(),
    u0::SVector{4, Float64} = SVector(zeros(4)...),
    system_kw = (),
)
    ds = function
        (
            u,
            parameters, 
            t,
        )
        v1, w1, v2, w2 = u

        k, ω1, ω2, α, β, e, d, c, I, ε, a0, a1, a2, a3, a4 = parameters

        dv1 = ω1*(a0*v1 + a1*v1^3 - a2*v1^5 + a3*v1^7 - a4*v1^9 - α*w1 + I + k*(v2 - v1))
        dw1 = ω1*(ε*(β + c*v1 + d*v1^2 - e*w1))

        dv2 = ω2*(a0*v2 + a1*v2^3 - a2*v2^5 + a3*v2^7 - a4*v2^9 - α*w2 + I + k*(v1 - v2))
        dw2 = ω2*(ε*(β + c*v2 + d*v2^2 - e*w2))

        return SVector(dv1, dw1, dv2, dw2)
    end

    sys_uncoupled = TristableFitzhughNagumoUncoupled(
        ;
        parameters = TFNParameters(parameters),
        u0 = SVector{2}(u0[[1,2]]),
        system_kw = system_kw,
    )

    return DSystem(ds, parameters, u0; sys_uncoupled = sys_uncoupled, system_kw...)
end

function TristableFitzhughNagumoWUCoupled(
    ;
    parameters::DSystemParameters = TFNParameters(
        ;
        name = "TristableFitzhughNagumo_W_U",
    ),
    u0::SVector{4, Float64} = SVector(zeros(4)...),
    system_kw = (),
)
    if parameters.name != "TristableFitzhughNagumo_W_U"
        parameters = TFNParameters(
            parameters;
            lims = parameters.lims,
            name = "TristableFitzhughNagumo_W_U",
        )
    end

    ds = function
        (
            u,
            parameters, 
            t,
        )
        v1, w1, v2, w2 = u

        k, ω1, ω2, α, β, e, d, c, I, ε, a0, a1, a2, a3, a4 = parameters

        dv1 = ω1*(a0*v1 + a1*v1^3 - a2*v1^5 + a3*v1^7 - a4*v1^9 - α*w1 + I)
        dw1 = ω1*(ε*(β + c*v1 + d*v1^2 - e*w1) + k*(v2 - v1))

        dv2 = ω2*(a0*v2 + a1*v2^3 - a2*v2^5 + a3*v2^7 - a4*v2^9 - α*w2 + I)
        dw2 = ω2*(ε*(β + c*v2 + d*v2^2 - e*w2) + k*(v2 - v1))

        return SVector(dv1, dw1, dv2, dw2)
    end

    sys_uncoupled = TristableFitzhughNagumoUncoupled(
        ;
        parameters = TFNParameters(parameters),
        u0 = SVector{2}(u0[[1,2]]),
        system_kw = system_kw,
    )

    return DSystem(ds, parameters, u0; sys_uncoupled = sys_uncoupled, system_kw...)
end