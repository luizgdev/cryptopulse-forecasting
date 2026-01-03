using Oxygen
using HTTP
using JSON
using TimeSeries
using Statistics
using Dates

# Include our new AI model file
include("model.jl")

# --- HELPER (SMA) ---
function calculate_sma(prices::Vector{Float64}, period::Int)
    dates = Date(2023,1,1):Day(1):(Date(2023,1,1) + Day(length(prices)-1))
    ta = TimeArray(dates, prices, [:close])
    sma_ta = moving(mean, ta, period)
    return values(sma_ta)
end

# --- ROUTES ---

@get "/health" function(req::HTTP.Request)
    return json(Dict("status" => "ready", "engine" => "Julia Flux + TimeSeries"))
end

@post "/process" function(req::HTTP.Request)
    try
        data = json(req)
        prices = convert(Vector{Float64}, data["prices"])
        period = get(data, "period", 5)
        
        # 1. Classical Algo: Calculate SMA
        sma_values = calculate_sma(prices, period)
        
        # 2. AI Algo: Predict NEXT price using Flux
        # We only run this if we have enough data
        forecast = 0.0
        if length(prices) > 10
            forecast = train_and_predict(prices, 5) # Lookback of 5
        end
        
        return json(Dict(
            "sma_values" => sma_values,
            "forecast_price" => forecast,
            "message" => "Processed with Flux.jl"
        ))
        
    catch e
        @error "Error processing" exception=(e, catch_backtrace())
        return HTTP.Response(500, ["Content-Type" => "application/json"], body=JSON.json(Dict("error" => string(e))))
    end
end

serve(host="0.0.0.0", port=8080)
