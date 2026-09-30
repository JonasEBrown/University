using GLMakie
using CairoMakie
using StaticArrays
using MakieForProjects
using DynamicalSystems

GLMakie.activate!()

struct DSystem{F <: Function, U <: SVector}

    ds::F
    parameters::DSystemParameters
    u0::U

    diffeq

    sys::CoupledODEs
    sys_uncoupled::Union{DSystem, Nothing}

    function DSystem(
        ds::F,
        parameters::DSystemParameters,
        u0::U;

        sys_uncoupled::Union{DSystem, Nothing} = nothing,
        
        diffeq = (
            abstol = 1e-6,
            reltol = 1e-6,
        )
    ) where {F <: Function, U <: SVector}
        return new{F, U}(
            ds, parameters, u0, diffeq, 
            CoupledODEs(
                ds,
                u0,
                vec(parameters);
                diffeq = diffeq,
            ),
            sys_uncoupled
        )
    end
end

function attractors_via_recurrences(
    sys::DSystem,
    grid;
    recurrences_kw = (
        ;
        Δt = 2π/25,
        consecutive_recurrences = 8000,
        attractor_locate_steps = 4000,
        consecutive_lost_steps = 400,
        consecutive_attractor_steps = 40,
        store_once_per_cell = false,
        stop_at_Δt = true,
    ),
)
    mapper = AttractorsViaRecurrences(
        sys.sys,
        grid;
        recurrences_kw...,
    )

    return mapper
end

function system_heatmap(
    sys::DSystem;
    n_tesselation::Int = 75,
    # n_initial_conditions::Int = 1000,
    recurrences_kw = (
        ;
        # consecutive_recurrences = 4000,
        # attractor_locate_steps = 2000,
        # consecutive_lost_steps = 300,
        # consecutive_attractor_steps = 30,
    ),
    last_attractors = nothing,
)
    ugrid = wgrid = range(sys.parameters.lims[1]...; length = n_tesselation)
    subgrid =  (ugrid, wgrid)
    subics = ics_from_grid(subgrid)
    allics = [SVector(u..., u...) for u in subics]

    mapper = attractors_via_recurrences(
        sys,
        (subgrid..., subgrid...);
        recurrences_kw = recurrences_kw
    )

    # Old Attractors.jl code.

    # fs, labels = basins_fractions(mapper, allics; N = n_initial_conditions)

    sampler = PrescribedICs(allics)

    fs, labels = basins_fractions_labels(mapper, sampler)

    basins = reshape(labels, length(ugrid), length(wgrid))

    attractors = extract_attractors(mapper)

    if !isnothing(last_attractors)
        distance(A, B) = abs(maximum(A[:, 1]) - maximum(B[:, 1]))
        matcher = MatchBySSSetDistance(; distance)
        rmap = matching_map(attractors, last_attractors, matcher)

        replace!(basins, rmap...)
        swap_dict_keys!(attractors, rmap)
    end

    fig = heatmap_basins_attractors(
        subgrid,
        basins,
        attractors;
        colors = COLORS,
    )

    return fig, attractors
end

function interactive_dsystem(
    sys::DSystem,
    u0s::Vector{<:AbstractVector{Float64}};
    idxs::Vector{Int} = [2, 4],
    kwargs...
)
    parameter_sliders = Dict(1 => 0.0:0.001:0.5)
    parameter_names = Dict(1 => "k")

    fig, dsobs = interactive_trajectory_timeseries(
        sys.sys,
        idxs,
        u0s;
        idxs = idxs,
        lims = sys.parameters.lims[1:length(idxs)],
        parameter_sliders = parameter_sliders,
        parameter_names = parameter_names,
        Δt = 0.05,
        add_controls = true,
        # figure = (
        #     ;
        #     size = (1800, 1200),
        # ),
        plotkwargs = (
            ;
            linestyle = :solid,
        ),
        linekwargs = (
            ;
            linestyle = :solid,
        ),
        kwargs...
    )

    controls = fig[2, 1]
    bottom_row = controls[2, 1]

    button = Button(bottom_row[1, 4], label = "save")

    on(button.clicks) do _
        save("timeseries.png", fig)
    end

    display(fig)

    return fig, dsobs
end