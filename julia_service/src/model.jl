using Flux
using Statistics
using Random

# Ensure reproducibility
Random.seed!(42)

function train_and_predict(prices::Vector{Float64}, lookback::Int=5)
    
    # --- 1. PREPROCESSING ---
    # Normalize to [0, 1] range to help the Neural Net converge
    min_val = minimum(prices)
    max_val = maximum(prices)
    
    # Avoid division by zero if the market is flat
    if max_val == min_val
        return prices[end]
    end
    
    normalized_prices = (prices .- min_val) ./ (max_val - min_val)
    
    # Prepare X (features) and Y (target)
    X_data = []
    Y_data = []
    
    for i in 1:(length(normalized_prices) - lookback)
        push!(X_data, normalized_prices[i : i+lookback-1])
        push!(Y_data, normalized_prices[i+lookback])
    end
    
    # CRITICAL CONVERSION: Flux works best with Float32
    # X needs to be a Matrix (features x samples)
    X = Float32.(hcat(X_data...))
    Y = Float32.(reshape(Y_data, 1, :))
    
    # --- 2. DEFINE MODEL ---
    # Simple Multi-Layer Perceptron (MLP)
    model = Chain(
        Dense(lookback => 10, relu),
        Dense(10 => 5, relu),
        Dense(5 => 1)
    )
    
    # --- 3. TRAINING (New Explicit Syntax) ---
    
    # The loss function must now accept the MODEL (m) as an argument
    loss(m, x, y) = Flux.mse(m(x), y)
    
    # Configure optimizer with the model state
    opt_state = Flux.setup(Adam(0.01), model)
    
    # Explicit training loop
    data = [(X, Y)]
    for epoch in 1:50
        Flux.train!(loss, model, data, opt_state)
    end
    
    # --- 4. PREDICTION ---
    # Get the last window available to predict the future
    last_window = Float32.(normalized_prices[end-lookback+1:end])
    input_vector = reshape(last_window, :, 1)
    
    # Model returns a Float32 array with 1 element
    predicted_norm = model(input_vector)[1]
    
    # Denormalize back to real price
    predicted_price = (Float64(predicted_norm) * (max_val - min_val)) + min_val
    
    return predicted_price
end
