using Flux
using Statistics
using Random

# Ensure reproducibility
Random.seed!(42)

"""
    train_and_predict(prices, lookback)

Trains a Neural Network on the provided price sequence and returns:
1. The forecast for the next step.
2. The final training loss (MSE) to check convergence.
3. The fitted values (what the model learned from the past).
"""
function train_and_predict(prices::Vector{Float64}, lookback::Int=5)
    
    # --- 1. PREPROCESSING ---
    min_val = minimum(prices)
    max_val = maximum(prices)
    
    # Handle flat market edge case
    if max_val == min_val
        return (prices[end], 0.0, prices)
    end
    
    # Normalize data to [0, 1] for Neural Network stability
    normalized_prices = (prices .- min_val) ./ (max_val - min_val)
    
    X_data = []
    Y_data = []
    
    # Create Sliding Windows (Features X -> Target Y)
    # If lookback=5, we use prices [1..5] to predict [6], [2..6] to predict [7], etc.
    for i in 1:(length(normalized_prices) - lookback)
        push!(X_data, normalized_prices[i : i+lookback-1])
        push!(Y_data, normalized_prices[i+lookback])
    end
    
    # Convert to Float32 Matrices (Flux requirement)
    X = Float32.(hcat(X_data...))
    Y = Float32.(reshape(Y_data, 1, :))
    
    # --- 2. DEFINE MODEL ---
    # A simple Multi-Layer Perceptron
    model = Chain(
        Dense(lookback => 10, relu),
        Dense(10 => 5, relu),
        Dense(5 => 1)
    )
    
    # --- 3. TRAINING WITH METRICS ---
    # Loss function: Mean Squared Error
    loss(m, x, y) = Flux.mse(m(x), y)
    
    opt_state = Flux.setup(Adam(0.01), model)
    
    final_loss = 0.0
    data = [(X, Y)]
    
    # Train for 50 epochs
    for epoch in 1:50
        Flux.train!(loss, model, data, opt_state)
        
        # Capture the loss of the last epoch
        if epoch == 50
            final_loss = loss(model, X, Y)
        end
    end
    
    # --- 4. PREDICTION (THE FUTURE) ---
    # Use the very last window to predict the unknown next candle
    last_window = Float32.(normalized_prices[end-lookback+1:end])
    input_next = reshape(last_window, :, 1)
    
    pred_next_norm = model(input_next)[1]
    
    # Denormalize
    predicted_price = (Float64(pred_next_norm) * (max_val - min_val)) + min_val
    
    # --- 5. CURVE FITTING (THE PAST) ---
    # We run the whole training set (X) through the model to see how well it learned the pattern.
    # This helps visualize if the AI is "smart" or just guessing.
    fitted_norm = model(X)
    
    # Denormalize the fitted sequence
    fitted_vals = (vec(Float64.(fitted_norm)) .* (max_val - min_val)) .+ min_val
    
    # Return Tuple: (Forecast, Loss, Fitted Curve)
    return (predicted_price, Float64(final_loss), fitted_vals)
end
