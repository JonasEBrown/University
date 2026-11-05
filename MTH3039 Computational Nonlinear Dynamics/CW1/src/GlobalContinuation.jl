function match_attractors(
    old_attractors,
    new_attractors,
    old_ids;
    match_tolerance = Inf,
    distance_function = centeroid_distance,
    next_id = nothing,
)
    used_old, used_new = Set{Int}(), Set{Int}()
    matches = Tuple{Int, Int}[]

    new_ids = zeros(Int, length(new_attractors))

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

    for (distance, o, n) in distances
        if distance <= match_tolerance && (
                !(o in used_old) &&
                !(n in used_new)
            )
            new_ids[n] = old_ids[o]
            
            push!(used_old, o)
            push!(used_new, n)
            push!(matches, (o, n))         
        end
    end

    if isnothing(next_id)
        next_id = isempty(old_ids) ? 1 : (maximum(old_ids) + 1)
    end

    for n in eachindex(new_ids)
        if !(n in used_new)
            new_ids[n] = next_id
            next_id += 1
        end
    end

    return new_ids, next_id, matches
end

function global_continuation(
    system,
    ics,
    parameters::AbstractDict{Int};

    ic_samples = 1000,

    grouping_radius = 1,
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

    ids = Vector{Vector{Int}}(undef, continuation_count)

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

    max_attractors = maximum(length.(global_attractors))

    measurements = [
        [
            i <= length(global_attractors[idx]) ? measurement_collector(
                global_attractors[idx][i],
                global_fractions[idx][i];
            ) : missing
            for i in 1:max_attractors
        ]
        for idx in eachindex(global_attractors)
    ]
    max_measurements = length(first(first(measurements))) + 1

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
            distance_function = distance_function,
            next_id = next_id,
        )

        ids[idx] = copy(new_ids)

        for i in eachindex(current_attractors)
            id = new_ids[i]

            pushfirst!(measurements[idx][i], first_param_range[idx])

            if !haskey(tracked, id)
                tracked[id] = [
                    Vector{Union{Missing, Any}}(missing, continuation_count)
                    for _ in 1:max_measurements
                ]
            end

            for (j, value) in enumerate(measurements[idx][i])
                tracked[id][j][idx] = value
            end

            history[id] = (
                attractor = current_attractors[i],
                last = idx,
            )
        end
    end

    if (track_vanishing_attractors
        && is_cyclic_parameter_sweep(parameters_vectorised)
        && length(global_attractors) > 1)
        _, _, wrap_matches = match_attractors(
            global_attractors[end],
            global_attractors[1],
            ids[end];
            distance_function = distance_function,
            next_id = next_id,
        )

        for (old, new) in wrap_matches
            first_id, last_id = ids[1][new], ids[end][old]
            if last_id != first_id
                for i in eachindex(tracked[first_id])
                    for j in eachindex(tracked[first_id][i])
                        if ismissing(tracked[first_id][i][j])
                            tracked[first_id][i][j] = tracked[last_id][i][j]
                        end
                    end
                end

                delete!(tracked, last_id)
            end
        end
    end

    return tracked
end