using JLD2
using StaticArrays

struct DSystemAttractor{ U <: SVector }
    u0::U
    trajectory::StateSpaceSet
    times::StepRangeLen
    Δt::Float64
    dims::Int

    function DSystemAttractor(
        sys::DSystem,
        u0::U;
        t::Float64 = 1000.0,
        Δt::Float64 = 0.1,
        kw...
    ) where { U <: SVector }
        tr, times = trajectory(
            sys.sys,
            t,
            u0;
            Δt,
            kw...
        )

        return new{U}(
            u0,
            tr,
            times,
            Δt,
            length(tr[1])
        )
    end

    # DSystemAttractor(
    #     u0::SVector,
    #     trajectory::StateSpaceSet,
    #     times::StepRangeLen,
    #     Δt::Float64,
    #     dims::Int,
    # ) = new{typeof(u0)}(
    #     u0,
    #     trajectory,
    #     times,
    #     Δt,
    #     dims
    # )
end

# Base.convert(
#     ::Type{DSystemAttractor}, 
#     old::JLD2.ReconstructedMutable{:DSystemAttractor, (:u0, :trajectory, :times, :Δt, :dims), Tuple{Any, Any, Any, Float64, Int64}}
# ) = DSystemAttractor(
#     SVector{old.dims}(old.u0),
#     old.trajectory,
#     old.times,
#     old.Δt,
#     old.dims,
# )

struct DSystemAttractors
    attractors::Vector{<:DSystemAttractor}
    parameters::Vector
    fs::Union{Dict, Nothing}

    function DSystemAttractors(
        sys::DSystem,
        attractors::Vector{<:DSystemAttractor}
    )
        parameters = current_parameters(sys.sys)

        return new(
            attractors,
            parameters,
            nothing,
        )
    end

    function DSystemAttractors(
        sys::DSystem;
        n_tesselation::Int = 50,
        n_initial_conditions::Int = 1000,
        recurrences_kw = (),
        trajectory_kw = (
            t = 1000.0,
            Δt = 0.01,
        ),
    )
        grid = Tuple(
            range(low, high; length=n_tesselation)
            for (low, high) in sys.parameters.lims
        )

        mapper = attractors_via_recurrences(
            sys,
            grid;
            recurrences_kw = recurrences_kw,
        )

        # Old Attractors.jl code.

        # sampler, _ = statespace_sampler(grid)
        # fs = basins_fractions(mapper, sampler; N = n_initial_conditions)

        sampler = RandomICsSampler(
            n_initial_conditions,
            grid
        )
        fs = basins_fractions(mapper, sampler)

        attractors = extract_attractors(mapper)

        dsystem_attractors = map(
            attractor -> DSystemAttractor(
                sys,
                attractor[end];
                trajectory_kw...,
            ),
            values(attractors)
        )

        parameters = current_parameters(sys.sys)

        return new(
            dsystem_attractors,
            parameters,
            fs,
        )
    end
end

function save_dsystem_attractors(
    dsystem::DSystemAttractors,
    filename::String = ""
)
    JLD2.save(
        filename,
        Dict(
            "dsystem" => dsystem,
        )
    )
end

function load_dsystem_attractors(filename::String)::DSystemAttractors
    data = JLD2.load(filename)
    return data["dsystem"]
end

function classify_trajectory(
    trajectory::StateSpaceSet
)::Symbol
    columns = eachcol(trajectory)

    is_fixed = maximum(std.(columns)) < 1e-1

    amplitudes = get_amplitude.(columns)

    is_fixed_and_osc = is_fixed_and_oscillatory(amplitudes)

    return is_fixed ? :fixed_point : Symbol(
        classify_attractor(is_fixed_and_osc),
        Symbol(
            "_",
            is_fixed_and_osc ? 
                abs(maximum(amplitudes) - large_cycle_amplitude) < 2e-1 ? :large : :small
            : join(
                classify_limit_cycles(amplitudes, large_cycle_amplitude),
                "_"
            )
        )
    )
end

function analyse_dsystem_attractors(
    dsystem_attractors::DSystemAttractors;
    large_amplitude::Union{Float64, Nothing} = nothing,
)
    analysis = AttractorAnalysis.(dsystem_attractors.attractors)
    large_amplitude = isnothing(large_amplitude) ? get_large_limit_cycle_amplitude(dsystem_attractors) : large_amplitude

    amplitudes = analysis .|> (a -> a.is_fixed ? 0.0 : maximum(a.amplitudes))

    limit_cycle_classification = amplitudes .|> (a -> abs(a - large_amplitude) < 0.1 ? :large : :small)

    classifications = [
        Symbol(
            a.classification,
            !a.is_fixed ? Symbol(
                "_",
                a.is_fixed_and_osc ? limit_cycle_classification[idx] : join(
                    classify_limit_cycles(a.amplitudes, large_amplitude),
                    "_"
                )
            ) : ""
        )
        for (idx, a::AttractorAnalysis) in enumerate(analysis)
    ]

    return analysis, classifications
end

classification_comparison_function(a, b, y, z) = (a == y && b == z) || (a == z && b == y)

function get_uncoupled_system_classifications(
    sys::DSystem;
    dsystem_attractors_kw = (),
)
    set_parameter!(sys.sys_uncoupled.sys, 1, 0.0)

    dsystem_attractors = DSystemAttractors(
        sys.sys_uncoupled;
        dsystem_attractors_kw...,
    )

    _, classifications = analyse_dsystem_attractors(dsystem_attractors)

    return dsystem_attractors, classifications
end

function find_all_attractor_classification_combinations(
    sys::DSystem,
    dsystem_attractors_kw = (),
)::Tuple{Vector{Symbol}, Vector{Any}}
    dsystem_attractors, classifications = get_uncoupled_system_classifications(
        sys;
        dsystem_attractors_kw = dsystem_attractors_kw,
    )

    attractor_combinations = []

    for (idx, classification) in enumerate(classifications)
        for (idx2, classification_2) in enumerate(classifications)
            new_classification = classification
            if classification_comparison_function(classification, classification_2, :fixed_point, :oscillatory_small_small)
                new_classification = :fixed_point_and_oscillatory_small
            elseif classification_comparison_function(classification, classification_2, :fixed_point, :oscillatory_large_large)
                new_classification = :fixed_point_and_oscillatory_large
            elseif classification_comparison_function(classification, classification_2, :oscillatory_small_small, :oscillatory_large_large)
                new_classification = classification == :oscillatory_small_small ? :oscillatory_small_large : :oscillatory_large_small
            elseif classification_comparison_function(classification, classification_2, :oscillatory_large_large, :oscillatory_small_small)
                new_classification = classification == :oscillatory_large_large ? :oscillatory_large_small : :oscillatory_small_large
            end
            push!(
                attractor_combinations,
                (
                    new_classification,
                    [
                        dsystem_attractors.attractors[idx].trajectory[:][end]...,
                        dsystem_attractors.attractors[idx2].trajectory[:][end]...
                    ]
                )
            )
        end
    end

    return classifications, attractor_combinations
end

function get_large_limit_cycle_amplitude(
    dsystem_attractors::DSystemAttractors
)
    return maximum(
        dsystem_attractors.attractors .|> (
                attractor -> is_fixed_point_attractor(attractor) ? 0.0 : maximum(
                    get_attractor_amplitudes(attractor)
                )
            )
        )
end

function classify_initial_condition(
    sys::DSystem,
    dsystem_attractors::DSystemAttractors,
    initial_condition::Vector{Float64},
)::Tuple{Symbol, StateSpaceSet, StepRangeLen}
    k = current_parameters(sys.sys)[1]

    set_parameter!(sys.sys, 1, k)

    set_state!(sys.sys, initial_condition)

    X, t = trajectory(sys.sys, 1000.0)

    return classify_trajectory(
        X[end-100:end]
    ), X, t
end

function display_actual_classifications(
    axs::Matrix{Axis},
    sys::DSystem,
    dsystem_attractors::DSystemAttractors,
    attractors_in_4D::Vector{Any};
    save_plots::Bool = false,
    path::Union{String, Nothing} = nothing,
)
    k = current_parameters(sys.sys)[1]

    actual_classifications = []

    for (expected_classification, initial_condition) in attractors_in_4D
        actual_classification, X, t = classify_initial_condition(
            sys,
            dsystem_attractors,
            initial_condition
        )

        empty!(axs[1, 1])
        empty!(axs[2, 1])

        lines!(
            axs[1, 1],
            t, X[:, 1];
            linestyle = :solid,
        )

        lines!(
            axs[2, 1],
            t, X[:, 3];
            linestyle = :solid,
        )

        classification_matches = expected_classification == actual_classification

        push!(actual_classifications, [expected_classification, actual_classification])

        title.text[] = "$(classification_matches ? "Expected" : "Missing") attractor for k = $(k)"

        classification_label.text[] = classification_matches ? rich(
            "Got expected classification ",
            rich("$(expected_classification)", font = :bold),
        ) : rich(
            "Expected ",
            rich("$(expected_classification)", font = :bold),
            " but got ",
            rich("$(actual_classification)", font = :bold)
        )

        if save_plots
            i = 0
            filepath = nothing
            while isnothing(filepath) || isfile(filename)
                filename = "k_$(k)_$(classification_matches ? "expected" : "missing")_attractor_$(expected_classification)$(i == 0 ? "" : "_$(i)")"
                filepath = isnothing(path) ? filename : join(
                    [path, filename],
                    "/"
                )
                i += 1
            end

            CairoMakie.save("$(filepath).png", fig)
        end

        wait(continue_flag)
    end

    return actual_classifications
end

function plot_system_trajectories(
    sys::DSystem;
    t::Float64 = 1000.0,
    k::Union{Float64, Nothing} = nothing,
    u0s::Vector{<:SVector} = [SVector(y, y) for y in [0.1, 1.0, 1.5]],
    dsystem_attractors_kw = (),
)
    if !isnothing(k)
        set_parameter!(sys.sys, 1, k)
    end

    dsystem_attractors = DSystemAttractors(
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

    attractors = dsystem_attractors.attractors
    sys_size = Int(ceil(sqrt(attractors[1].dims)))
    cols = div(attractors[1].dims, 2)

    fig, axs = axesgrid(
        1,
        cols;
        xlabels = "dim1",
        sharex = true,
        ylabels = "dim2",
        size = (600 * cols, 600),
        backgroundcolor = :white,
    )

    min_tr, max_tr = Inf, -Inf

    for attractor in dsystem_attractors.attractors
        trs = [attractor.trajectory[:, idx] for idx in 1:attractor.dims]
        for tr_idx in 1:sys_size:length(trs)
            col = Int(ceil(tr_idx / sys_size))
            lines!(
                axs[1, col],
                [trs[tr_idx + idx - 1] for idx in 1:sys_size]...;
                linestyle = :solid,
                label = "$(trs[tr_idx][1])"
            )
        end
        new_min, new_max = minimum(minimum.(trs)), maximum(maximum.(trs))
        min_tr, max_tr = min_tr > new_min ? new_min : min_tr, max_tr < new_max ? new_max : max_tr
    end

    diff = abs(max_tr - min_tr)

    min_tr += sign(min_tr) * 0.1*diff 
    max_tr += sign(max_tr) * 0.1*diff

    for idx in 1:cols
        axislegend(axs[1, idx])

        axs[1, idx].limits = Tuple(
            (min_tr, max_tr)
            for dim in 1:sys_size
        )
    end

    return fig
end