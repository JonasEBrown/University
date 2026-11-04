include("src/include.jl")

# A - trajectory.
# index - axis index of trajectory to check for intersections.
# value - value of axis at which the hyperplane is situated.
function psos1(
    A::StateSpaceSet,
    index::Integer,
    value::Real,
)
    out = Matrix(undef, 0, size(first(A), 1)) # Create an empty matrix to store the intercetions.
    for (k, point) in enumerate(A[1:end - 1]) # Iterate through the trajectory points, excluding the last point.
        a, b = point[index], A[k + 1, index] # Get the values of the specified axis for the current and next trajectory points.
        if a < value <= b # Check if the hyperplane is crossed between the current and next points.
            t = (value - a) / (b - a) # Calculate the interpolation factor to find the intersection point.
            intersection = point + t * (A[k + 1] - point) # Calculate the intersection point using linear interpolation.
            intersection = [i == index ? value : axis for (i, axis) in enumerate(intersection)] # Fix floating point errors.
            out = vcat(out, collect(intersection)') # Append the intersection point to the output.
        end
    end
    return out
end

# Same as pso1, but now logs t as well as the intersection point and gives return times.
function psos2(
    A::StateSpaceSet,
    tvec::AbstractVector,
    index::Integer,
    value::Real,
)
    out = Matrix(undef, 0, size(first(A), 1))
    last_t = 0
    return_times = []
    for (k, point) in enumerate(A[1:end - 1])
        a, b = point[index], A[k + 1, index]
        if a < value <= b
            t = (value - a) / (b - a)
            intersection = point .+ t .* (A[k + 1] .- point)
            intersection = [i == index ? value : axis for (i, axis) in enumerate(intersection)]
            out = vcat(out, collect(intersection)')
            new_t = tvec[k] .+ t .* (tvec[k + 1] .- tvec[k])
            push!(return_times, abs(new_t - last_t))
            last_t = new_t
        end
    end
    return out, return_times
end

function simple_grouping(features, r)
    group_idx = 1
    groups = Int[group_idx]
    centers = Vector{Float64}[first(features)]
    for feature in features[2:end]
        distances = norm.(centers .- Ref(feature))
        min_distance = minimum(distances)
        if min_distance < r
            center_idx = findfirst(==(min_distance), distances)
            push!(groups, center_idx)
        else
            group_idx += 1
            push!(groups, group_idx)
            push!(centers, feature)
        end
    end
    return groups, centers
end

fg1(
    ds,
    featurizer,
    r,
    ics;
    Ttr = 400,
    T = 40,
    Dt = 0.2,
    kwargs...
) = fg_base(
    ds,
    featurizer,
    r,
    ics;
    Ttr = Ttr,
    T = T,
    Dt = Dt,
    kwargs...
)

fg2(
    ds,
    featurizer,
    r,
    ics;
    Ttr = 400,
    T = 40,
    Dt = 0.2,
    kwargs...
) = fg_base(
    ds,
    featurizer,
    r,
    ics;
    Ttr = Ttr,
    T = T,
    Dt = Dt,
    return_fractions = true,
    kwargs...
)

function random_r_sim(
    ds,
    m,
    n,
    metric;
    u0 = [5.0, 0.01],
    r_values = [1.6, 2.55],
)
    trues = 0
    r_values = [r_values..., r_values[1]]

    for _ in 1:m
        set_state!(ds, u0)
        set_parameter!(ds, 1, r_values[1])
        step!(ds, randomtime())

        for _ in 1:n
            for r in r_values[2:end]
                set_parameter!(ds, 1, r)
                step!(ds, randomtime())
            end
        end

        trues += Int(metric([0, 0], current_state(ds)) < 1e-6)
    end
    
    return trues / m
end

# Brief-defined functions.

h(
    X::StateSpaceSet
) = length(
    unique(
        [
            round.(p; digits = 1)
            for p in X
        ]
    )
) / length(X)

function provided_featurizer(X)
    x = X[:, 1]
    xmean = mean(x)
    xspan = maximum(x) - minimum(x)
    h = length(unique([round.(p; digits = 1) for p in X])) / length(X)
    return SVector(xmean, xspan, 2h)
end

function generate_metric(Nweight, Pweight)
    function metric(u, v)
        sqrt( ((u[1] - v[1])/Nweight)^2 + ((u[2] - v[2])/Pweight)^2 )
    end
    return metric
end
mymetric = generate_metric(15, 0.03)

function naive_phases(X::StateSpaceSet, scaling)
    center = mean(X)
    xs = X[:, 1] .- center[1]
    ys = X[:, 2] .- center[2]
    return atan.(scaling .* ys, xs)
end

randomtime() = 13*(2 + rand())