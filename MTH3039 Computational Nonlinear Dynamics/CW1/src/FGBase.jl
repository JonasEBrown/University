function fg_base(
    ds,
    featurizer,
    r,
    ics;
    filepath = nothing,
    grouper = simple_grouping,
    return_fractions = false,
    kwargs...
)
    trajectories = load_trajectories(filepath)

    if isnothing(trajectories)
        trajectories = evolve_ics(
            ds,
            ics;
            filepath = filepath,
            kwargs...
        )
    end

    features = featurizer.(trajectories)

    basins, centers = grouper(features, r)

    attractors = Dict{Int, StateSpaceSet}(
        idx => trajectories[findfirst(==(center), features)]
        for (idx, center) in enumerate(centers)
    )

    if !return_fractions
        return flat_vector_to_matrix(basins), attractors
    end

    total_basins = count(>(0), basins)
    fractions = Dict{Int, Float64}(
        idx => count(==(basin), basins) / total_basins
        for (idx, basin) in enumerate(unique(basins))
    )

    return flat_vector_to_matrix(basins), attractors, fractions
end