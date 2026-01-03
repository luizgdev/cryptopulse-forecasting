using Test
using Statistics
using Flux

# Import the logic file directly (bypass the HTTP server)
# We assume the file is located at ../src/model.jl relative to this test file
include("../src/model.jl")

@testset "Julia Backend Tests" begin

    @testset "Neural Network Logic" begin
        # 1. Sanity Check: Does the model run without errors?
        # Create a dummy array of prices: [1.0, 2.0, ..., 10.0]
        dummy_prices = collect(1.0:10.0) 
        
        # Run the training and prediction function
        prediction = train_and_predict(dummy_prices, 3)
        
        # Assertions
        @test prediction isa Float64       # Result must be a number
        @test !isnan(prediction)           # Result cannot be NaN
        @test prediction > 0               # Price cannot be negative
    end

    @testset "Edge Cases" begin
        # 2. Flat Market Scenario
        # If the price is stable at 100.0, the prediction should be close to 100.0
        flat_prices = fill(100.0, 20)
        prediction = train_and_predict(flat_prices, 5)
        
        # We use 'approx' (≈) because Neural Nets are stochastic
        @test prediction ≈ 100.0 atol=0.5
    end

end
