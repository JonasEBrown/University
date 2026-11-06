PLOT_SIZE = (450, 300)
PLOT_PADDING = 20

function plot_trajectory(
    system,
    u0;
    three_d = false,
    tr_parameters = (),
    colors = COLORS,
    title = "",
    kwargs...
)
    tr, _ = system_trajectory(system, u0; tr_parameters...)

    fig = Figure(
        ;
        size = PLOT_SIZE,
        backgroundcolor = :white,
    )

    axis = three_d ? Axis3(
        fig[1, 1];
        title = title,
        kwargs...
    ) : Axis(
        fig[1, 1];
        title = title,
        kwargs...
    )

    lines!(axis, tr; color = colors[1])

    return fig, axis 
end

function plot_trajectories(
    system,
    u0s;
    parameters = Dict{Int, Vector}(),
    titles = nothing,
    kwargs...
)
    if isempty(parameters)
        current = current_parameters(system)
        parameters = Dict(
            idx => [param]
            for (idx, param) in enumerate(current)
        )
    end

    parameter_count = length(first(parameters)[2])

    figs, axes = [], []
    for u0 in u0s
        for idx in 1:parameter_count
            for (key, params) in parameters
                set_parameter!(
                    system,
                    key,
                    params[idx]
                )
            end

            fig, axis = plot_trajectory(
                system,
                u0;
                title = !isnothing(titles) ? titles[idx] : "",
                kwargs...
            )

            push!(figs, fig)
            push!(axes, axis)
        end
    end

    return figs, axes
end

function plot_timeseries(
    x::AbstractVector,
    t::AbstractVector;
    title = "Timeseries",
    ylabel = "Value",
    Δt = 0.05,
    limits = (0.0, length(x) * Δt),
    colors = COLORS,
)
    min_range, max_range = (
        round(
            Int, 
            max(
                limits[1] / Δt,
                1.0
            )
        ),
        round(Int, limits[2] / Δt)
    )
    variable = x[min_range:max_range]
    t_values = t[min_range:max_range]

    fig = Figure(
        ;
        size = PLOT_SIZE,
        backgroundcolor = :white,
    )

    axis = Axis(
        fig[1, 1];
        title = title,
        xlabel = "Time",
        ylabel = ylabel,
        xticks = limits[1]:(abs(limits[2] - limits[1]) / 10):limits[2],
    )

    lines!(axis, t_values, variable; color = colors[1])

    return fig, axis 
end

function plot_x_z_mean_against_b_values(
    system,
    u0,
    b_values;
    tr_parameters = (),
    colors = COLORS,
)
    fig = Figure(
        ;
        size = PLOT_SIZE,
        backgroundcolor = :white,
    )

    min_b_value, max_b_value = first(b_values), last(b_values)
    ticks = 5

    axis = Axis(
        fig[1, 1];
        xlabel = "b",
        ylabel = "Mean Values",
        xticks = min_b_value:(abs(max_b_value - min_b_value) / ticks):max_b_value,
        yticks = 0:0.1:1.0,
    )
    
    for b in b_values
        set_parameter!(system, 2, b)

        tr, _ = system_trajectory(system, u0; tr_parameters...)
        x_mean, z_mean = mean(tr[:, 1]), mean(tr[:, 3])

        scatter!(
            axis,
            [b, b],
            [x_mean, z_mean],
            color = colors[1:2],
            label = ["Mean x", "Mean z"],
        )
    end

    Legend(fig[1, 2], axis; title = "Mean Values", merge = true, unique = true)

    return fig, axis 
end

function plot_poincare_section(
    A::StateSpaceSet,
    index::Integer,
    value::Real;
    colors = COLORS,
)
    intersections = psos1(A, index, value)

    fig = Figure(
        ;
        size = figure_size(1, 2),
        backgroundcolor = :white,
    )

    left_axis = Axis3(
        fig[1, 1];
        title = "Trajectory",
        xlabel = "x",
        ylabel = "y",
        zlabel = "z",
    )

    right_axis = Axis(
        fig[1, 2];
        title = "Poincaré Section",
        xlabel = "x",
        ylabel = "y",
    )

    lines!(left_axis, A; color = colors[1])

    scatter!(
        left_axis,
        intersections[:, 1],
        intersections[:, 2],
        intersections[:, 3],
        color = colors[2],
        label = "Poincaré section",
    )

    scatter!(
        right_axis,
        intersections[:, 1],
        intersections[:, 2],
        color = colors[2],
        label = "Poincaré section",
    )

    return fig, [left_axis, right_axis]
end

function plot_histogram(
    data::AbstractVector;
    colors = COLORS,
)
    fig = Figure(
        ;
        size = PLOT_SIZE,
        backgroundcolor = :white,
    )

    return fig, hist(
        fig[1, 1],
        data;
        color = colors[1],
    )
end

function plot_simple_grouping(
    features,
    r;
    colors = COLORS,
    kwargs...
)
    groups, _ = simple_grouping(features, r)

    fig = Figure(
        ;
        size = PLOT_SIZE
    )

    axis = Axis(
        fig[1, 1];
        kwargs...
        
    )

    for (idx, feature) in enumerate(features)
        scatter!(
            axis,
            [feature[1]],
            [feature[2]];
            color = colors[groups[idx]],
        )
    end

    return fig, axis 
end

function plot_basins_of_attraction_heatmap!(
    axis,
    ics,
    basins;
    attractors = nothing,
    fractions = nothing,
    colors = COLORS,
    sckwargs = (
        ;
        strokewidth = 0.5,
        strokecolor = :white,
    )
)
    x = sort(unique(ic[1] for ic in ics))
    y = sort(unique(ic[2] for ic in ics))

    grid = (x, y)

    attractors = isnothing(attractors) ? Dict(
        basin => SVector(-Inf, -Inf)
        for basin in unique(basins)
    ) : attractors

    heatmap!(
        axis,
        grid...,
        basins;
        colormap = colors,
        colorrange = (1, length(colors)),
    )
    for (idx, attractor) in attractors
        scatter!(
            axis,
            attractor;
            color = colors[idx],
            label = isnothing(fractions)
                        ? "$(idx)" : "$(round(fractions[idx], digits=2))",
            sckwargs...,
        )
    end
end

function plot_basins_of_attraction_heatmaps(
    ics,
    basins;
    titles = nothing,
    attractors = nothing,
    fractions = nothing,
    colors = COLORS,
    xlabel = "x",
    ylabel = "y",
    kwargs...
)
    plots = length(basins)
    cols = Int(ceil(sqrt(plots)))
    rows = Int(ceil(plots / cols))

    fig, axes = axes_grid(
        rows, cols;
        titles = titles,
        xlabels = [xlabel for _ in 1:plots],
        ylabels = [ylabel for _ in 1:plots],
    )

    [
        plot_basins_of_attraction_heatmap!(
            axes[idx],
            ics,
            basins_value;
            attractors = isnothing(attractors) ? nothing : attractors[idx],
            fractions = isnothing(fractions) ? nothing : fractions[idx],
            colors = colors,
        )
        for (idx, basins_value) in enumerate(basins)
    ]

    return fig, axes
end

function plot_basins_of_attraction_heatmaps(
    ics,
    data::Dict;
    titles = nothing,
    colors = COLORS,
    xlabel = "x",
    ylabel = "y",
    kwargs...
)
    plots = length(data)
    cols = Int(ceil(sqrt(plots)))
    rows = Int(ceil(plots / cols))

    fig, axes = axes_grid(
        rows, cols;
        titles = titles,
        xlabels = [xlabel for _ in 1:plots],
        ylabels = [ylabel for _ in 1:plots],
    )

    [
        plot_basins_of_attraction_heatmap!(
            axes[idx],
            ics,
            value[1];
            attractors = value[2],
            fractions = value[3],
            colors = colors,
            kwargs...
        )
        for (idx, (_, value)) in enumerate(data)
    ]

    return fig, axes
end

plot_basins_of_attraction_heatmap(
    ics,
    basins;
    attractors = nothing,
    fractions = nothing,
    colors = COLORS,
    kwargs...
) = plot_basins_of_attraction_heatmaps(
    ics,
    [basins];
    attractors = isnothing(attractors) ? nothing : [attractors],
    fractions = isnothing(fractions) ? nothing : [fractions],
    colors = colors,
    kwargs...
)

function plot_basins_and_attractors_split(
    ics,
    basins,
    attractors;
    colors = COLORS,
    xlabel = "x",
    ylabel = "y",
    kwargs...
)
    fig, axes = axes_grid(
        1, 2;
        titles = ["BoA of system", "Attractors of system"],
        xlabels = [xlabel, xlabel],
        ylabels = [ylabel, ylabel],
    )

    plot_basins_of_attraction_heatmap!(
        axes[1, 1],
        ics,
        basins;
        attractors = Dict(
            basin => SVector(-Inf, -Inf)
            for basin in unique(basins)
        ),
        colors = colors,
        kwargs...
    )

    for (basin, attractor) in attractors
        scatter!(
            axes[1, 2],
            attractor;
            color = colors[basin],
        )
    end
    
    return fig, axes
end

function plot_global_continuation(
    continuation;
    x_values = nothing,
    xlabel = "parameter",
    ylabels = [
        "BoA fraction",
        "Maximum N",
        "Maximum P",
        "Standard deviation of N",
    ],
    plot_title = "Global continuation",
    titles = [
        "Basins of Attraction",
        "Maximum prey population",
        "Maximum predator population",
        "Prey population variability",
    ],
    colors = COLORS,
)
    plots = length(titles)
    cols = Int(ceil(sqrt(plots)))
    rows = Int(ceil(plots / cols))

    fig, axes = axes_grid(
        rows, cols;
        xlabels = fill(xlabel, cols * rows),
        ylabels = ylabels,
        titles = titles,
        plot_title = plot_title,
    )

    for (attractor, measurements) in continuation
        x_vals = isnothing(x_values) ? measurements[1] : x_values

        for (idx, axis) in enumerate(axes)
            scatter!(
                axis,
                x_vals,
                measurements[idx + 1];
                color = colors[attractor]
            )
        end
    end
    
    min_measurements, max_measurements = [
        minimum(
            [
                minimum(filter(!ismissing, continuation[key][idx]))
                for key in collect(keys(continuation))
            ]
        )
        for idx in eachindex(first(continuation)[2])
    ], [
        maximum(
            [
                maximum(filter(!ismissing, continuation[key][idx]))
                for key in collect(keys(continuation))
            ]
        )
        for idx in eachindex(first(continuation)[2])
    ]

    tick_count = 5

    x_min, x_maxis = isnothing(x_values) ? min_measurements[1] : minimum(x_values), isnothing(x_values) ? max_measurements[1] : maximum(x_values)
    x_step = abs(x_maxis - x_min) / tick_count
    x_step = x_step == 0 ? 1 : x_step
    x_ticks = round.(
        x_min:x_step:x_maxis,
        digits=2,
    )

    for (idx, axis) in enumerate(axes)
        axis.xticks[] = x_ticks

        y_step = abs(max_measurements[idx + 1] - min_measurements[idx + 1]) / tick_count
        y_step = y_step == 0 ? 1 : y_step

        axis.yticks[] = round.(
            min_measurements[idx + 1]:y_step:max_measurements[idx + 1],
            digits=2,
        )
    end

    return fig, axes
end

function plot_minimum_critical_shock!(
    axis,
    position,
    mcs;
    show_radius = false,
    color = "#900C37",
    circle_kwargs = (
        ;
        linewidth = 2,
    ),
    arrow_kwargs = (
        ;
        tailwidth = 2,
        tipwidth = 12,
    ),
    kwargs...,
)
    viewpoint_width, viewport_height = width(axis.scene.viewport[]), height(axis.scene.viewport[])

    xlim = axis.xaxis.attributes.limits[]
    ylim = axis.yaxis.attributes.limits[]
    ratio = span(ylim) / span(xlim)

    if show_radius
        ellipse_x = maximum(abs.(mcs))

        lines!(
            axis,
            ellipse(
                position...,
                ellipse_x,
                ellipse_x * ratio * (viewpoint_width / viewport_height),
            )...;
            color = color,
            circle_kwargs...,
        )
    end

    arrows2d!(
        axis,
        position,
        mcs;
        color = color,
        arrow_kwargs...,
    )

    xlims!(axis, xlim)
    ylims!(axis, ylim)
end

function plot_minimum_critical_shock(
    mcs,
    ics,
    basins;
    attractors,
    fractions,
    show_radius = false,
    xlabel = "x",
    ylabel = "y",
    sckwargs = (
        strokewidth = 0.5,
        strokecolor = :white,
    ),
    kwargs...
)
    fig, axes = plot_basins_of_attraction_heatmap(
        ics,
        basins;
        attractors = attractors,
        fractions = fractions,
        xlabel = xlabel,
        ylabel = ylabel,
        sckwargs = sckwargs,
        kwargs...,
    )
    axis = axes[1]

    for (source_ic, shock) in mcs
        plot_minimum_critical_shock!(
            axis,
            source_ic,
            shock;
            show_radius = show_radius,
        )
    end

    return fig, axis
end

function plot_limit_cycle_susceptibility(
    susceptibilities;
    scaling = 15 / 0.05,
    xlabel = "Phase (radians)",
    ylabel = "Susceptibility",
)
    fig = Figure(
        ;
        size = PLOT_SIZE,
    )

    axis = Axis(
        fig[1, 1];
        xlabel = xlabel,
        ylabel = ylabel,
    )

    x = StateSpaceSet(collect(keys(susceptibilities)))
    phases = naive_phases(x, scaling)

    y = collect(values(susceptibilities))

    scatter!(
        axis,
        phases,
        y;
    )

    return fig, axis
end