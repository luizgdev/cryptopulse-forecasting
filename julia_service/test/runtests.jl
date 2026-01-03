using Test
using Statistics
using Flux

# Import the logic file
include("../src/model.jl")

@testset "Julia Backend Tests" begin

    @testset "Neural Network Logic" begin
        # 1. Sanity Check
        dummy_prices = collect(1.0:10.0) 
        
        (prediction, loss_val, fitted) = train_and_predict(dummy_prices, 3)
        
        # Testes on prediction
        @test prediction isa Float64
        @test !isnan(prediction)
        @test prediction > 0
        
        # Testes on new metrics
        @test loss_val isa Float64
        @test loss_val >= 0
        @test length(fitted) > 0
    end

    @testset "Edge Cases" begin
        # 2. Flat Market Scenario
        flat_prices = fill(100.0, 20)
        
        (prediction, loss_val, fitted) = train_and_predict(flat_prices, 5)
        
        @test prediction ≈ 100.0 atol=0.5
        
        @test loss_val < 0.1
    end

end
