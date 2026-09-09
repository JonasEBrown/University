using CairoMakie
using ColorSchemes
using Makie.Colors
using ProgressMeter
using MakieForProjects

DEFAULT_SYNCHRONISED_COUNT_COLOURS = COLORS

function default_synchronised_count_colour(
    count::Int;
    colours = DEFAULT_SYNCHRONISED_COUNT_COLOURS
)
    return colours[clamp(count + 1, 1, length(colours))]
end

function get_synchronous_attractor_count(
    analysis::Vector{AttractorAnalysis}
)
    return count(
        a -> a.is_synchronous,
        analysis
    )
end

function convert_analysis_to_plot_colour(
    analysis::Vector{AttractorAnalysis};
    count_colour_function::Function = default_synchronised_count_colour,
    colours = DEFAULT_SYNCHRONISED_COUNT_COLOURS,
)
    synchronous_count = get_synchronous_attractor_count(analysis)
    return count_colour_function(synchronous_count; colours = colours)
end

function get_data(
    sys::DSystem,
    k::Float64,
    filename::String;
    dsystem_attractors_kw = (),
    large_amplitude::Union{Float64, Nothing} = nothing,
)
    dsystem_attractors = analysis = classifications = nothing

    if isfile(filename)
        dsystem_attractors, analysis, classifications = load_attractor_analysis(filename)
    end

    if isnothing(dsystem_attractors)
        set_parameter!(sys.sys, 1, k)

        dsystem_attractors = DSystemAttractors(
            sys;
            dsystem_attractors_kw...
        )

        save_attractor_analysis(dsystem_attractors, analysis, classifications, filename)
    end

    if isnothing(analysis) || isnothing(classifications)
        analysis, classifications = analyse_dsystem_attractors(dsystem_attractors; large_amplitude = large_amplitude)

        save_attractor_analysis(dsystem_attractors, analysis, classifications, filename)
    end   

    return dsystem_attractors, analysis, classifications
end

function plot_system_attractor_count(
    fig::Figure,
    ax::Axis,
    sys::DSystem,
    standard_attractor_count::Int;
    k_values::StepRangeLen = 0.005:0.001:0.2,
    path::String = "attractors",
    dsystem_attractors_kw = (),
    colours = DEFAULT_SYNCHRONISED_COUNT_COLOURS,
    large_amplitude::Union{Float64, Nothing} = nothing,
)
    if !isdir(path)
        mkpath(path)
    end

    @showprogress for k in k_values
        filename_attractors = "$(path)/k_$(k)_attractors.jld2"

        dsystem_attractors, analysis, classifications = get_data(
            sys,
            k,
            filename_attractors;
            dsystem_attractors_kw = dsystem_attractors_kw,
            large_amplitude = large_amplitude,
        )

        point_colour = convert_analysis_to_plot_colour(analysis; colours = colours)

        fixed_points = map(
            attractor -> attractor.is_fixed,
            analysis
        )

        attractor_count = count(!, fixed_points) + Int(any(fixed_points))

        scatter!(
            ax, k,
            attractor_count;
            color = point_colour,
            marker = :circle
        )
    end

    hlines!(ax, [standard_attractor_count], 0:last(k_values))

    min_k, max_k = minimum(k_values), maximum(k_values)
    max_attractors = standard_attractor_count^2

    x_tick_count = 10
    x_tick_step = abs(max_k - min_k) / x_tick_count

    ax.xticks = min_k:x_tick_step:max_k
    ax.yticks = 0:1:max_attractors

    ax.limits = ((maximum([(min_k - x_tick_step), 0]), (max_k + x_tick_step)), (0, max_attractors + 1))
end

attractor_count_label_func(i, standard_attractor_count = 3) = "$(i < standard_attractor_count + 1 ? i - 1 : "$(i - 1)+") synchronised"

function plot_system_attractor_count(
    sys::DSystem;
    k_values::StepRangeLen = 0.005:0.001:0.1,
    path::String = "attractors",
    dsystem_attractors_kw = (),
    colours = DEFAULT_SYNCHRONISED_COUNT_COLOURS,
    labels::Union{Vector{String}, Nothing} = nothing,
)
    uncoupled_dsystem_attractors, uncoupled_classifications = get_uncoupled_system_classifications(
        sys;
        dsystem_attractors_kw = dsystem_attractors_kw,
    )

    large_amplitude = get_large_limit_cycle_amplitude(uncoupled_dsystem_attractors)

    standard_attractor_count = length(uncoupled_classifications)

    colours = colours[1:standard_attractor_count + 1]

    fig = Figure(size=(900, 600); backgroundcolor = :white)
    ax = Axis(
        fig[1,1],
        xlabel = "k",
        ylabel = "Number of attractors",
        title = "Number of attractors for each k value - $(sys.parameters.name) Δω = $(round(sys.parameters.Δω, digits=3))",
    )

    axislegend(
        ax,
        [
            scatter!(
                ax, [NaN], [NaN];
                color = colour,
                label = attractor_count_label_func(i, standard_attractor_count),
                marker = :circle,
            ) 
            for (i, colour) in enumerate(colours)
        ],
        [attractor_count_label_func(i, standard_attractor_count) for i in eachindex(colours)],
    )

    if !isnothing(labels)
        label_axes!(
            axs;
            valign = :top,
            halign = :right,
            pad = 4,
            transpose = false,
            labels = labels,
            add_box = false,
            fontsize = 20,
        )
    end

    plot_system_attractor_count(
        fig,
        ax,
        sys,
        standard_attractor_count;
        k_values = k_values,
        path = path,
        dsystem_attractors_kw = dsystem_attractors_kw,
        colours = colours,
        large_amplitude = large_amplitude,
    )

    return fig
end

function compare_system_attractor_counts(
    systems::Vector{<:DSystem};
    k_values::StepRangeLen = 0.005:0.001:0.2,
    paths::Vector{String} = ["attractors"],
    dsystem_attractors_kw = (),
    colours = DEFAULT_SYNCHRONISED_COUNT_COLOURS,
    ylabels::Union{Vector{String}, Nothing} = nothing,
    labels::Union{Vector{String}, Nothing} = nothing,
)
    first_sys = first(systems)
    system_count = length(systems)

    uncoupled_dsystem_attractors, uncoupled_classifications = get_uncoupled_system_classifications(
        first_sys;
        dsystem_attractors_kw = dsystem_attractors_kw,
    )

    large_amplitude = get_large_limit_cycle_amplitude(uncoupled_dsystem_attractors)

    standard_attractor_count = length(uncoupled_classifications)

    colours = colours[1:standard_attractor_count + 1]

    fig, axs = axesgrid(
        system_count,
        1;
        xlabels = "k",
        sharex = true,
        ylabels = "Attractor count",
        size = ((length(k_values) * 5) + 200, system_count * 300),
        backgroundcolor = :white,
    )

    Legend(
        fig[Int(ceil(system_count / 2)), 2],
        [
            scatter!(
                axs[1], [NaN], [NaN];
                color = colour,
                label = attractor_count_label_func(i, standard_attractor_count),
                marker = :circle,
            ) 
            for (i, colour) in enumerate(colours)
        ],
        [attractor_count_label_func(i, standard_attractor_count) for i in eachindex(colours)],
    )

    if !isnothing(labels)
        label_axes!(
            axs;
            valign = :top,
            halign = :right,
            pad = 4,
            transpose = false,
            labels = labels,
            add_box = false,
            fontsize = 20,
        )
    end

    for (idx, sys) in enumerate(systems)
        plot_system_attractor_count(
            fig,
            axs[idx],
            sys,
            standard_attractor_count;
            k_values = k_values,
            path = paths[idx],
            dsystem_attractors_kw = dsystem_attractors_kw,
            colours = colours,
            large_amplitude = large_amplitude,
        )

        if !isnothing(ylabels)
            axs[idx].ylabel = ylabels[idx]
        end
    end

    figuretitle!(
        fig,
        "Attractor count against k for systems";
        fontsize = 24,
        font = :bold,
    )

    return fig
end