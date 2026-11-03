function rössler_model(
    ;
    u0 = SVector(0.0, 0.0, 0.0),
    a = 0.2,
    b = 0.0,
    c = 5.7,
    diffeq = (
        ;
        abstol = 1e-6,
        reltol = 1e-6
    ),
)
    p = [a, b, c]

    function dynamic_rule(u, p, t)
        x, y, z = u
        a, b, c = p

        dx = -y - z
        dy = x + (a * y)
        dz = b + (z * (x - c))

        return SVector(dx, dy, dz)
    end

    return CoupledODEs(dynamic_rule, u0, p; diffeq = diffeq)
end