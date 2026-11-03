function duffing_oscillator_model(
    ;
    u0 = SVector(0.0, 0.0),
    δ = 0.1,
    f = 0.45,
    ω = 2.15,
    diffeq = (
        ;
        abstol = 1e-6,
        reltol = 1e-6
    )
)
    p = [δ, f, ω]

    function dynamic_rule(u, p, t)
        x, v = u
        δ, f, ω = p

        dx = v
        dv = x - x^3 - (δ*v) + (f * cos(ω*t))

        return SVector(dx, dv)
    end

    return CoupledODEs(dynamic_rule, u0, p; diffeq = diffeq)
end

duffing_oscillator_ics(
    ;
    x_v_range = -2.5:0.05:2.5
) = [SVector(x, v) for v in x_v_range for x in x_v_range]