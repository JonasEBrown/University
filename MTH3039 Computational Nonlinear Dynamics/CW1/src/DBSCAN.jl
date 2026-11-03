# Psuedocode sourced from Wikipedia (https://en.wikipedia.org/wiki/DBSCAN).

# DBSCAN(DB, distFunc, eps, minPts) {
#     C := 0                                                  /* Cluster counter */
#     for each point P in database DB {
#         if label(P) ≠ undefined then continue               /* Previously processed in inner loop */
#         Neighbors N := RangeQuery(DB, distFunc, P, eps)     /* Find neighbors */
#         if |N| < minPts then {                              /* Density check */
#             label(P) := Noise                               /* Label as Noise */
#             continue
#         }
#         C := C + 1                                          /* Next cluster label */
#         label(P) := C                                       /* Label initial point */
#         SeedSet S := N \ {P}                                /* Neighbors to expand */
#         for each point Q in S {                             /* Process every seed point Q */
#             if label(Q) = Noise then label(Q) := C          /* Change Noise to border point */
#             if label(Q) ≠ undefined then continue           /* Previously processed (e.g., border point) */
#             label(Q) := C                                   /* Label neighbor */
#             Neighbors N := RangeQuery(DB, distFunc, Q, eps) /* Find neighbors */
#             if |N| ≥ minPts then {                          /* Density check (if Q is a core point) */
#                 S := S ∪ N                                  /* Add new neighbors to seed set */
#             }
#         }
#     }
# }

function dbscan_grouping(
    features,
    r;
    min_points = 2,
)
    n = length(features)

    # Initialisations.
    cluster = 0
    labels = zeros(Int, n)
    visited_features = falses(n)

    # Create a cache for neighbours.
    neighbours_cached = Vector{Union{Vector{Int}, Missing}}(missing, n)

    # Search for neighbours of a feature within a threshold r and cache results.
    function neighbours(idx)
        if ismissing(neighbours_cached[idx])
            neighbours_cached[idx] = [
                j for j in 1:n
                if norm(features[idx] - features[j]) <= r # Find neighbours within threshold r.
            ]
        end
        return neighbours_cached[idx]
    end

    for idx in 1:n
        visited_features[idx] && continue # Skip if the feature has already been visited.
        visited_features[idx] = true # Mark the feature as visited.

        feature_neighbours = neighbours(idx)

        # Not enough neighbours to form a cluster, assign as noise.
        if length(feature_neighbours) < min_points
            labels[idx] = -1
            continue
        end

        # Create a new cluster and assign current label.
        cluster += 1
        labels[idx] = cluster

        # Initialise a queue with feature's neighbours and a set to track visited features.
        queue = copy(feature_neighbours)
        visited = Set(queue)

        # Repeat until all valid neighbours are labelled.
        head = 1
        while head <= length(queue)
            current = queue[head] # Get the next neighbour from the queue.
            head += 1

            # If the neighbour has not been visited.
            if !visited_features[current]
                visited_features[current] = true # Mark the neighbour as visited.

                current_neighbours = neighbours(current) # Get the neighbours of the current neighbour.

                # If the neighbour itself has enough neighbours to form a cluster,
                # add its neighbours to the queue and enforce set behaviour.
                if length(current_neighbours) >= min_points
                    for neighbour in current_neighbours
                        if !(neighbour in visited)
                            push!(queue, neighbour)
                            push!(visited, neighbour)
                        end
                    end
                end
            end

            # If the neighbour is unlabelled, assign it to the current cluster.
            if labels[current] <= 0
                labels[current] = cluster
            end
        end
    end

    # Find first entry for each label and use it as a the center of the cluster.
    centers = [
        features[findfirst(==(c), labels)]
        for c in 1:cluster
    ]

    return labels, centers
end