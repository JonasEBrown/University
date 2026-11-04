find_basin(
    source_ic,
    basins;
) = basins[argmin(norm(source_ic - ic) for ic in ics)]

function minimum_critical_shock(
    source_ic,
    ics,
    basins;
    metric = mymetric,
)
    source_basin = find_basin(source_ic, basins)
    return ics[
        argmin(
            [
                basins[idx] == source_basin ? Inf : metric(source_ic, ic)
                for (idx, ic) in enumerate(ics)
            ]
        )
    ] - source_ic
end

function find_metric_switch_interval(
    metric_generator,
    source_ic,
    ics,
    basins,
    weights::AbstractDict{Int},
)
    max_length = maximum(length.(values(weights)))

    idx = 1
    previous_params = previous_dominated = missing

    while idx <= max_length
        params = [
            typeof(weights[k]) <: AbstractVector ? weights[k][idx] : weights[k]
            for k in sort(collect(keys(weights)))
        ]

        if any(==(0), params)
            idx += 1
            continue
        end

        contributions = minimum_critical_shock(
            source_ic,
            ics,
            basins;
            metric = metric_generator(params...),
        ) ./ params

        dominated = [
            all(contribution .> contributions[1:end .!= i])
            for (i, contribution) in enumerate(contributions)
        ]

        if !ismissing(previous_dominated) && all(dominated .!= previous_dominated)
            return (previous_params, params)
        end

        previous_params = params
        previous_dominated = dominated

        idx += 1
    end

    return nothing
end

limit_cycle_minimum_critical_shock(
    system,
    cycle_attractor,
    ics,
    basins;
    samples = 50,
    metric = mymetric,
    Δt = 0.05,
) = Dict(
    position => minimum_critical_shock(
        position,
        ics,
        basins;
        metric = metric,
    )
    for position in sample_limit_cycle(
        system,
        cycle_attractor,
        samples;
        Δt = Δt,
    )
)

function minimum_critical_shock_averages(
    mcs;
    metric = mymetric,
)
    mcs_vectorised = values(mcs)

    average_mcs_vector = mean(mcs_vectorised)
    average_mcs_vector_magnitude, average_mcs_vector_direction = magnitude_and_direction(
        average_mcs_vector;
        metric = metric,
    )

    average_magnitudes, average_directions = mean(
        reduce(
            vcat,
            [
                magnitude_and_direction(
                    mcs_value;
                    metric = metric,
                )
                for mcs_value in mcs_vectorised
            ]'
        ), 
        dims = 1,
    )

    return (
        average_mcs_vector_magnitude,
        average_mcs_vector_direction
    ),
    (
        average_magnitudes,
        average_directions
    )
end

function limit_cycle_susceptibility(
    mcs;
    metric = mymetric,
)
    magnitudes = Dict(
        key => magnitude_and_direction(
            mcs[key];
            metric = metric,
        )[1]
        for key in collect(keys(mcs))
    )
    max_magnitude = maximum(collect(values(magnitudes)))
    return Dict(key => magnitude / max_magnitude  for (key, magnitude) in magnitudes)
end

function basin_transferable_fraction(
    source_basins,
    new_basins,
    attractor;
)
    total_ics = length(source_basins)
    source_basin = find_basin(attractor[end], basins)
    return count(
        idx -> (source_basins[idx] != new_basins[idx]
                && source_basins[idx] == source_basin),
        1:total_ics
    ) / total_ics
end