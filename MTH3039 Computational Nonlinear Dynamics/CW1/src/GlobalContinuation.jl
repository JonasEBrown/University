function match_attractors(
    old_attractors,
    new_attractors,
    old_basins;
    match_tolerance = Inf,
    distance_function = centeroid_distance,
    next_id = nothing,
)
    used_old, used_new = Set{Int}(), Set{Int}()
    matches = Tuple{Int, Int}[]

    new_basins = zeros(Int, length(new_attractors))

    distances = sort!(
        [
            (
                distance_function(old, new),
                o,
                n,
            )
            for (o, old) in old_attractors
            for (n, new) in new_attractors
        ];
        by = first
    )

    if !isempty(distances)
        distance, o, n = first(distances)
        total_distances = length(distances)
        
        idx = 1
        while distance <= match_tolerance
            if (
                    !(o in used_old) &&
                    !(n in used_new)
                )
                new_basins[n] = old_basins[o]
                
                push!(used_old, o)
                push!(used_new, n)
                push!(matches, (o, n))
            end
            idx += 1
            idx > total_distances && break
            distance, o, n = distances[idx]
        end
    end

    if isnothing(next_id)
        next_id = isempty(old_basins) ? 1 : (maximum(old_basins) + 1)
    end

    for n in eachindex(new_basins)
        if !(n in used_new)
            new_basins[n] = next_id
            next_id += 1
        end
    end

    return new_basins, next_id, matches
end

function global_continuation(
    system,
    ics,
    parameters::AbstractDict{Int};

    ic_samples = 1000,

    grouping_radius = 1,
    match_tolerance = Inf,

    path = nothing,
    
    featurizer = predator_prey_featurizer,
    grouper = simple_grouping,
    distance_function = centeroid_distance,
    measurement_collector = task_3_measurement_feature_collector,
    
    track_vanishing_attractors = false,

    Ttr = 400,
    T = 40,
    Δt = 0.05,
    kwargs...,
)        
    tracked = Dict{Int, Vector{Union{Missing, Any}}}()
    history = Dict{Int, NamedTuple{
        (:attractor, :last),
        Tuple{<:StateSpaceSet, Int}
    }}()

    next_id = 1
    global_attractors, global_fractions = Dict{Int, StateSpaceSet}[], Dict{Int, Float64}[]
    
    parameters_vectorised = [parameters[k] for k in sort(collect(keys(parameters)))]
    first_param_range = first(parameters_vectorised)
    continuation_count = length(first_param_range)

    total_ics = length(ics)

    for idx in 1:continuation_count
        filepath = "$(isnothing(path) ? "" : "$(path)/")trajectories_$(idx).jld2"

        for (key, params) in parameters
            set_parameter!(
                system,
                key,
                params[idx]
            )
        end

        ics_copy = copy(ics)
        sampled_ics = [
            splice!(
                ics_copy,
                Int(
                    ceil(
                        (total_ics - i + 1) * rand()
                    )
                )
            )
            for i in 1:ic_samples
        ]

        _, attractors, fractions = fg2(
            system,
            featurizer,
            grouping_radius,
            sampled_ics;
            filepath = filepath,
            Ttr = Ttr,
            T = T,
            Dt = Δt,
            grouper = grouper,
            return_basins_matrix = false,
            kwargs...,
        )

        push!(global_attractors, attractors)
        push!(global_fractions, fractions)
    end

    for (idx, current_attractors) in enumerate(global_attractors)
        possible_ids = sort!(
            [
                id for (id, value) in history
                if track_vanishing_attractors 
                    || (idx - value.last == 1)
            ]
        )

        old_attractors = Dict(
            i => history[id].attractor
            for (i, id) in enumerate(possible_ids)
        )

        new_ids, next_id, _ = match_attractors(
            old_attractors,
            current_attractors,
            possible_ids;
            match_tolerance = match_tolerance,
            distance_function = distance_function,
            next_id = next_id,
        )

        for i in eachindex(current_attractors)
            id = new_ids[i]

            measurements = [
                first_param_range[idx];
                measurement_collector(
                    current_attractors[i],
                    global_fractions[idx][i],
                )
            ]

            if !haskey(tracked, id)
                tracked[id] = [
                    Vector{Union{Missing, Any}}(missing, continuation_count)
                    for _ in eachindex(measurements)
                ]
            end

            for (j, value) in enumerate(measurements)
                tracked[id][j][idx] = value
            end

            history[id] = (
                attractor = current_attractors[i],
                last = idx,
            )
        end
    end

    return tracked
end