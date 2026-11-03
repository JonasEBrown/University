# General maths functions.
span(A::Union{<:Vector, <:Tuple}) = maximum(A) - minimum(A)

# General distance functions.
centeroid_distance(A::StateSpaceSet, B::StateSpaceSet) = norm(mean(A) - mean(B))
euclidean_distance(trs::AbstractVector...) = norm(
    sum(
        [
            mean(tr[:, 1]),
            span(tr[:, 1]),
        ] * (
            idx == 1 ? 1 : -1
        )
        for (idx, tr) in enumerate(trs)
    )
)

# Trajectory shorthand.
system_trajectory(system, u0; t = 1000.0, Δt = 0.05, kwargs...) = trajectory(
    system,
    t,
    u0;
    Δt = Δt,
    kwargs...
)

# Simulate trajectory given initial conditions and save to file.
function evolve_ics(
    ds,
    ics;
    filepath = nothing,
    T = 1000.0,
    Dt = 0.05,
    kwargs...
)
    trs = map(
        ic -> system_trajectory(
            ds,
            ic;
            t = T,
            Δt = Dt,
            kwargs...
        )[1],
        ics
    )

    if !isnothing(filepath)
        JLD2.save(
            filepath,
            Dict(
                "trajectories" => trs,
            )
        )
    end

    return trs
end

# Retreive trajectory data from file.
load_trajectories(
    path::Union{String, Nothing}
) = !isnothing(path) && isfile(path) ? get(JLD2.load(path), "trajectories", nothing) : nothing

# Convert 1D vector to square matrix.
function flat_vector_to_matrix(
    vec::AbstractVector
)
    d = isqrt(length(vec))
    mat = Matrix{Int}(undef, d, d)

    for (idx, value) in enumerate(vec)
        row = div(idx - 1, d) + 1
        column = mod1(idx, d)
        mat[column, row] = value
    end

    return mat
end

# Check if a range is cyclic.
is_cyclic_parameter_sweep(parameters; tolerance = 1e-8) = all(
    abs(
        first(parameter_values) - last(parameter_values)
    ) <= tolerance
    for parameter_values in parameters
)

# Size figure.
figure_size(rows::Int, cols::Int; plot_size = PLOT_SIZE, padding = PLOT_PADDING) = (
    (plot_size[1] * cols) + (padding * (cols - 1)),
    (plot_size[2] * rows) + (padding * (rows - 1)),
)

# Generate axes matrix.
axes_grid!(
    fig::Figure,
    rows::Int,
    cols::Int;
    xlabels = fill("", cols * rows),
    ylabels = fill("", cols * rows),
    titles = fill("", cols * rows),
) = reshape(
    [
        Axis(
            fig[row, col];
            xlabel = xlabels[((col - 1) * rows) + row],
            ylabel = ylabels[((col - 1) * rows) + row],
            title = titles[((col - 1) * rows) + row],
        )
        for col in 1:cols
        for row in 1:rows
    ],
    rows,
    cols,
)

function axes_grid(
    rows::Int,
    cols::Int;
    xlabels = fill("", cols * rows),
    ylabels = fill("", cols * rows),
    titles = fill("", cols * rows),
    size = nothing,
    plot_title = nothing,
    plot_size = PLOT_SIZE,
    padding = PLOT_PADDING,
    kwargs...
)
    if isnothing(size)
        size = figure_size(
            rows, cols;
            plot_size = plot_size,
            padding = padding,
        )
    end
    if !isnothing(plot_title)
        size = size .+ (
            0,
            padding * (
                length(
                    split(plot_title, "\n")
                ) + 1
            )
        )
    end
    fig = Figure(
        ;
        size = size,
        kwargs...,
    )
    !isnothing(plot_title) && Label(
        fig[0, 1:cols],
        plot_title,
        fontsize = 22,
        font = :bold,
    )
    return fig, axes_grid!(
        fig,
        rows,
        cols;
        xlabels = xlabels,
        ylabels = ylabels,
        titles = titles,
    )
end

# Check for fixed point using std.
is_fixed_point_attractor(tr::StateSpaceSet; tolerance = 1e-3) = maximum(std(tr[end - 100:end])) <= tolerance

# Ellipse.
pi_range = range(0, 2pi; length = 314)
ellipse(x0, y0, rx, ry) = (
    x0 .+ rx .* cos.(pi_range),
    y0 .+ ry .* sin.(pi_range),
)

# Period finding.
function get_period(trajectory::StateSpaceSet; Δt = 1.0)
    return [
        mean(
            diff(
                [
                    idx
                    for (idx, point) in enumerate(axis[2:end - 1])
                        if axis[idx] < point > axis[idx + 2]
                ]
            )
        ) * Δt
        for axis in eachcol(trajectory)
    ]
end