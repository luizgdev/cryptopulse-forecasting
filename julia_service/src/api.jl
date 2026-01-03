using Oxygen
using HTTP
using JSON
using TimeSeries
using Statistics
using Dates

# Include the logic file
include("model.jl")

# --- HELPER: SMA Calculation ---
function calculate_sma(prices::Vector{Float64}, period::Int)
    # Generate dummy dates for TimeSeries.jl compatibility
    dates = Date(2023,1,1):Day(1):(Date(2023,1,1) + Day(length(prices)-1))
    ta = TimeArray(dates, prices, [:close])
    sma_ta = moving(mean, ta, period)
    return values(sma_ta)
end

# --- ROUTES ---

@get "/health" function(req::HTTP.Request)
    return json(Dict("status" => "online", "engine" => "Julia Flux 0.14+"))
end

@post "/process" function(req::HTTP.Request)
    try
        data = json(req)
        
        # Safe extraction of parameters
        prices = convert(Vector{Float64}, data["prices"])
        period = get(data, "period", 5)
        
        # 1. Classical Algo: SMA
        sma_values = calculate_sma(prices, period)
        
        # 2. AI Algo: Flux Neural Network
        forecast = 0.0
        training_loss = 0.0
        fitted_data = []

        # Only train if we have enough data points (more than 10)
        if length(prices) > 10
            # Unpack the Tuple from the model
            (forecast, training_loss, fitted_vals) = train_and_predict(prices, 5)
            fitted_data = fitted_vals
        end
        
        # 3. Build Response
        return json(Dict(
            "sma_values" => sma_values,
            "forecast_price" => forecast,
            "training_loss" => training_loss, # Metric: How well it learned
            "fitted_data" => fitted_data,     # Visual: The learned curve
            "message" => "Processed successfully"
        ))
        
    catch e
        @error "Error processing request" exception=(e, catch_backtrace())
        return HTTP.Response(500, ["Content-Type" => "application/json"], body=JSON.json(Dict("error" => string(e))))
    end
end

# Start Server on 0.0.0.0 to be accessible via Docker
serve(host="0.0.0.0", port=8080)
