using CairoMakie
using MakieForProjects

function plot_attractors_timeseries(
    sys::DSystem,
    dsystem::DSystemAttractors;
    t::Float64 = 100.0,
    max_plots_per_page::Int = 3,
    organise_by_systems::Bool = false,
)
    k = dsystem.parameters[1]

    figs = []
    attractors = dsystem.attractors

    attractor_count = length(attractors)
    page_count = cld(attractor_count, max_plots_per_page)

    sys_size = Int(ceil(sqrt(attractors[1].dims)))

    time = 1:attractors[1].Δt:t

    for i in 1:page_count
        start_point = (((i - 1) * max_plots_per_page) + 1)
        end_point = min((i * max_plots_per_page), attractor_count)

        rows, cols = (end_point - start_point + 1), organise_by_systems ? div(attractors[1].dims, 2) : sys_size

        fig, axs = axesgrid(
            rows,
            cols;
            xlabels = "t",
            sharex = true,
            ylabels = "u",
            size = (900, 600),
            backgroundcolor = :white,
        )

        for row in 1:rows
            for col in 1:cols
                axs[row, col].ylabel = organise_by_systems ? "sys$(col)" : "dim$(col)"
            end
        end

        for (idx, attractor::DSystemAttractor) in enumerate(attractors[start_point:end_point])
            for tr_idx in 1:attractor.dims
                col = organise_by_systems ? Int(ceil(tr_idx / sys_size)) : Int(mod1(tr_idx, cols))
                lines!(
                    axs[idx, col],
                    time,
                    attractor.trajectory[:, tr_idx][1:length(time)];
                    linestyle = :solid,
                )
            end
        end

        figuretitle!(
            fig,
            "$(sys.parameters.name) timeseries for k = $(k) (attractors $(start_point)-$(end_point))";
            fontsize = 24,
            font = :bold,
        )

        # label_axes!(
        #     axs;
        #     valign = :top,
        #     halign = :right,
        #     pad = 4,
        #     transpose = false,
        #     labels = [
        #         "Δω = $(round(sys.parameters.Δω, digits=3))"
        #         for ax in axs
        #     ],
        #     add_box = false,
        #     fontsize = 20,
        # )

        push!(figs, (fig, axs))
    end

    return figs
end

function plot_system_timeseries(
    sys::DSystem;
    t::Float64 = 1000.0,
    max_plots_per_page::Int = 3,
    k::Union{Float64, Nothing} = nothing,
    u0s::Vector{<:SVector} = [SVector(y, y) for y in [0.1, 1.0, 1.5]],
    organise_by_systems::Bool = false,
    dsystem_attractors_kw = (),
)
    if !isnothing(k)
        set_parameter!(sys.sys, 1, k)
    end

    dsytem_attractors = DSystemAttractors(
        sys,
        u0s .|> (
            u0 -> DSystemAttractor(
                sys,
                u0;
                t = t,
                dsystem_attractors_kw...
            )
        )
    )

    return plot_attractors_timeseries(
        sys,
        dsytem_attractors;
        t = t,
        max_plots_per_page = max_plots_per_page,
        organise_by_systems = organise_by_systems,
    )
end

function plot_analysis_timeseries(
    sys::DSystem,
    dsystem::DSystemAttractors,
    analysis::Vector{AttractorAnalysis},
    classifications::Vector{Symbol};
    t::Float64 = 1000.0,
    max_plots_per_page::Int = 3,
    organise_by_systems::Bool = false,
)
    figs = plot_attractors_timeseries(
        sys,
        dsystem;
        t = t,
        max_plots_per_page = max_plots_per_page,
        organise_by_systems = organise_by_systems,
    )
    
    attractor_count = length(analysis)
    page_count = cld(attractor_count, max_plots_per_page)

    for i in 1:page_count
        start_point = (((i - 1) * max_plots_per_page) + 1)
        end_point = min((i * max_plots_per_page), attractor_count)

        for idx in eachindex(start_point:end_point)
            figs[i][2][idx, 1].title = string(classifications[idx + ((i - 1) * max_plots_per_page)])
        end
    end

    return figs
end