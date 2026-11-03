function minimum_critical_shock(
    source_ic,
    ics,
    basins;
    metric = mymetric,
)
    source_basin = basins[argmin(norm(source_ic - ic) for ic in ics)]
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

function limit_cycle_minimum_critical_shock(
    system,
    cycle_attractor,
    ics,
    basins;
    samples = 50,
    metric = mymetric,
    Δt = 0.05,
)
    period = get_period(cycle_attractor; Δt = Δt)[1]
    sampling_time = period / samples
    
    limit_cycle_mcs = Dict()
    set_state!(system, cycle_attractor[end])

    for _ in 1:samples
        state = current_state(system)
        limit_cycle_mcs[state] = minimum_critical_shock(
            state,
            ics,
            basins;
            metric = metric,
        )
        step!(system, sampling_time)
    end

    return limit_cycle_mcs
end