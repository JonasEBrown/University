using FFTW
using ChaosTools
using Statistics
using LinearAlgebra

function is_fixed_point_attractor(
    attractor::DSystemAttractor;
    tolerance::Float64 = 1e-1
)
    tr = attractor.trajectory
    stds = std.(eachcol(tr))

    return maximum(stds) < tolerance
end

function estimate_attractor_periods(
    attractor::DSystemAttractor
)
    tr = attractor.trajectory

    return [
        ChaosTools.estimate_period(tr, :periodogram)
        for tr in eachcol(tr)
    ]
end

function estimate_phase_difference(
    x::Vector,
    y::Vector,
)
    N = length(x)

    x_norm = x .- mean(x) # Normalise x and y.
    y_norm = y .- mean(y)

    # Pad x and y.
    x_padded = vcat(x_norm, zeros(N))
    y_padded = vcat(y_norm, zeros(N))

    # Compute cross-correlation.
    cross_correlation = real(
        ifft(
            fft(x_padded) .* conj(
                fft(y_padded)
            )
        )
    )

    cross_correlation = vcat(
        cross_correlation[1:N],
        cross_correlation[
            (2N):-1:(N+2)
        ]
    )

    lag = argmax(cross_correlation) - 1

    if lag > (N / 2)
        lag -= N
    end

    return 2π * lag / N
end

function estimate_attractor_phase_differences(
    attractor::DSystemAttractor
)
    tr = attractor.trajectory

    phase_differences = Float64[]

    for i in 1:attractor.dims
        for j in 1:attractor.dims
            xi = [state[i] for state in tr]
            xj = [state[j] for state in tr]

            push!(
                phase_differences,
                estimate_phase_difference(xi, xj)
            )
        end
    end

    return phase_differences
end

function get_amplitude(
    x::Vector
)
    return maximum(x) - minimum(x)
end

function get_attractor_amplitudes(
    attractor::DSystemAttractor;
)
    tr = attractor.trajectory
    step = Int(round(sqrt(attractor.dims)))

    return [get_amplitude(getindex.(tr, d)) for d in 1:step:attractor.dims]
end

function get_period_differences(
    periods::Vector{Float64};
)
    D = length(periods)
    step = Int(round(sqrt(D)))

    X = reshape(
        periods,
        step,
        :
    )

    results = []
    n_nodes = size(X, 2)

    for i in 1:step
        ref = X[i, 1]

        push!(
            results, 
            [
                abs(ref - X[i, j])
                for j in 2:n_nodes
            ]
        )
    end

    return results
end

function classify_limit_cycles(
    amplitudes::Vector{Float64},
    large_amplitude::Float64;
    tolerance::Float64 = 2e-1
)
    D = length(amplitudes)
    step = Int(round(sqrt(D)))

    new_amplitudes = [amplitudes[i] for i in 1:step:D]

    return [
        abs(amplitude - large_amplitude) < tolerance ? :large : :small
        for amplitude in new_amplitudes
    ]
end

function is_fixed_and_oscillatory(
    amplitudes::Vector{Float64};
    tolerance::Float64 = 1e-1
)
    D = length(amplitudes)
    step = Int(round(sqrt(D)))

    new_amplitudes = [amplitudes[i] for i in 1:step:D]

    fixed_and_oscillatory = [
        amplitude > tolerance * 2
        for amplitude in new_amplitudes
    ]

    return !all(
        fixed_and_oscillatory
    )
end

# function is_synchronised(
#     periods::Vector{Float64};
#     tolerance::Float64 = 1e-3
# )
#     period_differences = get_period_differences(periods)

#     synchronised = [
#         period_differences[j][i] < tolerance
#         for i in eachindex(period_differences[1]), j in eachindex(period_differences)
#     ]

#     return all(synchronised)
# end

function is_synchronised(
    phase_differences::Vector{Float64};
    tolerance::Float64 = 1e-3
)
    return all(
        abs.(phase_differences) .< tolerance
    )
end

function classify_attractor(
    is_fixed_and_osc::Bool,
    # is_synchronous::Bool
)
    # return Symbol(
    #     is_fixed_and_osc ? :fixed_point_and_oscillatory : :oscillatory,
    #     !is_fixed_and_osc ? Symbol(
    #         "_",
    #         is_synchronous ? :sychronised : :non_synchronised
    #     ) : ""
    # )

    return is_fixed_and_osc ? :fixed_point_and_oscillatory : :oscillatory
end

abstract type AttractorClassification end

struct AttractorAnalysis
    attractor::DSystemAttractor

    is_fixed::Bool
    amplitudes::Vector{Float64}
    periods::Vector{Float64}
    phase_differences::Vector{Float64}

    classification::Symbol

    is_synchronous::Bool
    is_fixed_and_osc::Bool

    function AttractorAnalysis(
        attractor::DSystemAttractor,
    )
        is_fixed = is_fixed_point_attractor(attractor)

        amplitudes = get_attractor_amplitudes(attractor)
        periods = estimate_attractor_periods(attractor)
        phase_differences = estimate_attractor_phase_differences(attractor)

        is_fixed_and_osc = is_fixed ? false : is_fixed_and_oscillatory(amplitudes)
        is_synchronous = is_fixed ? false : (is_fixed_and_osc ? false : is_synchronised(phase_differences))

        classification = is_fixed ? :fixed_point : classify_attractor(is_fixed_and_osc)

        return new(
            attractor,
            is_fixed,
            amplitudes,
            periods,
            phase_differences,
            classification,
            is_synchronous,
            is_fixed_and_osc,
        )
    end

    # AttractorAnalysis(
    #     attractor,
    #     is_fixed,
    #     amplitudes,
    #     periods,
    #     phase_differences,
    #     classification,
    #     is_synchronous,
    #     is_fixed_and_osc,
    # ) = new(
    #     attractor,
    #     is_fixed,
    #     amplitudes,
    #     periods,
    #     phase_differences,
    #     classification,
    #     is_synchronous,
    #     is_fixed_and_osc,
    # )
end

# function Base.convert(
#     ::Type{AttractorAnalysis},
#     old::JLD2.ReconstructedMutable{:DSystemAttractor, (:u0, :trajectory, :times, :Δt, :dims), Tuple{Any, Any, Any, Float64, Int64}}
# )
#     return AttractorAnalysis(
#         convert(DSystemAttractor, old.attractor),
#         old.is_fixed,
#         old.amplitudes,
#         old.periods,
#         old.phase_differences,
#         old.classification,
#         old.is_synchronous,
#         old.is_fixed_and_osc,
#     )
# end

function save_attractor_analysis(
    dsystem::DSystemAttractors,
    analysis::Union{Vector{AttractorAnalysis}, Nothing},
    classifications::Union{Vector{Symbol}, Nothing},
    filename::String
)
    JLD2.save(
        filename,
        Dict(
            "dsystem" => dsystem,
            "analysis" => analysis,
            "classifications" => classifications,
        )
    )
end

function load_attractor_analysis(
    filename::String
)::Tuple{DSystemAttractors, Union{Vector{AttractorAnalysis}, Nothing}, Union{Vector{Symbol}, Nothing}}
    data = JLD2.load(filename)
    return get(data, "dsystem", nothing), get(data, "analysis", nothing), get(data, "classifications", nothing)
end
