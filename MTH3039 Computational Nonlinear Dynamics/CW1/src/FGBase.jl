function fg_base(
    ds,
    featurizer,
    grouping_radius,
    ics;
    filepath = nothing,
    grouper = simple_grouping,
    return_fractions = false,
    return_basins_matrix = true,
    kwargs...,
)
    trajectories = get_trajectories(
        filepath,
        ds,
        ics;
        kwargs...,
    )

    features = featurizer.(trajectories)

    basins, centers = grouper(features, grouping_radius)

    attractors = Dict{Int, StateSpaceSet}(
        idx => trajectories[findfirst(==(center), features)]
        for (idx, center) in enumerate(centers)
    )

    basins = return_basins_matrix ? flat_vector_to_matrix(basins) : basins

    if !return_fractions
        return basins, attractors
    end

    total_basins = count(>(0), basins)
    fractions = Dict{Int, Float64}(
        basin => count(==(basin), basins) / total_basins
        for basin in keys(attractors)
    )

    return basins, attractors, fractions
end

fg2(
    filepath,
    featurizer,
    r;
    kwargs...
) = fg_base(
    nothing,
    featurizer,
    r,
    nothing;
    filepath = filepath,
    kwargs...,
)