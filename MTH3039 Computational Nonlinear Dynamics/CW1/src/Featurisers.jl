predator_prey_featurizer(A::StateSpaceSet) = SVector(
    mean(A[:, 1]),
    std(A[:, 2]),
)

function h_improved_featurizer(
    A::StateSpaceSet
)
    x, v = A[:, 1], A[:, 2]
    return SVector(
        mean(x),
        std(x),
        mean(v),
        std(v),
        minimum(x),
        maximum(x),
        minimum(v),
        maximum(v),
        h(A),
    )
end

task_3_measurement_feature_collector(_, attractor, fraction) = [
    fraction,
    maximum(attractor[:, 1]),
    maximum(attractor[:, 2]),
    std(attractor[:, 1]),
]

task_3_6_measurement_feature_collector(_, attractor, fraction) = [
    fraction,
    mean(attractor[:, 1]),
    span(attractor[:, 1]),
    h(attractor),
]