function predator_prey_model(
    ;
    u0 = SVector(0.0, 0.0),
    r = 2,
    δ = 2.2,
    c = 0.19,
    μ = 0.03,
    υ = 0.003,
    α = 800,
    β = 1.5,
    χ = 0.004,
    diffeq = (
        ;
        abstol = 1e-6,
        reltol = 1e-6
    )
)
    p = [r, δ, c, μ, υ, α, β, χ]

    function dynamic_rule(u, p, t)
        N, P = u
        r, δ, c, μ, υ, α, β, χ = p

        s = (α * N * P) / (β + N)

        dN = (r * N * (1 - ((c / r) * N)) * ((N - μ) / (N + υ))) - s
        dP = (χ * s) - (δ * P)

        return SVector(dN, dP)
    end

    return CoupledODEs(dynamic_rule, u0, p; diffeq = diffeq)
end

function predator_prey_ics(
    ;
    density = 100,
)
    Ng = range(0, 15; length = density) .+ 0.01
    Pg = range(0, 30e-3; length = density) .+ 1e-6
    return [SVector(N, P) for P in Pg for N in Ng]
end

function parameter_curve(
    θ_values;
    a = 1.2,
    b = -0.5,
    c = 1.5,
    d = -0.5,
)
    f(θ) = SVector(
        a + (b * cos(θ)),
        c + (d * sin(θ))
    )

    return stack(
        f.(θ_values);
        dims = 1
    )
end