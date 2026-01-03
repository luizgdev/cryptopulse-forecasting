import pytest
import sys
import os

# Add the 'src' directory to the system path to allow importing modules from it
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

# Import the entire 'app' module to access its global variables
import app 
from app import get_julia_calculations

def test_julia_integration_success(requests_mock):
    """
    Test if the Python app correctly parses a valid JSON response from Julia.
    """
    
    # 1. Define the mock URL we want to use
    test_url = "http://julia-backend:8080"
    
    # 2. CRITICAL FIX: Overwrite the GLOBAL variable inside the imported app module
    # This ensures the function uses this URL instead of the default 'localhost' loaded at import time.
    app.JULIA_URL = test_url
    
    # The full endpoint that will be called
    fake_endpoint = f"{test_url}/process"
    
    # Mock response: This is what Julia WOULD return (including new metrics)
    mock_response = {
        "sma_values": [100.0, 101.0, 102.0],
        "forecast_price": 103.5,
        "training_loss": 0.015,
        "fitted_data": [100.1, 101.2],
        "message": "Success"
    }
    
    # Configure the mock to intercept the POST request
    requests_mock.post(fake_endpoint, json=mock_response, status_code=200)
    
    # Execute the function
    dummy_prices = [10.0, 11.0, 12.0]
    result = get_julia_calculations(dummy_prices, 5)
    
    # Assertions
    assert result["forecast_price"] == 103.5
    assert len(result["sma_values"]) == 3
    assert result["training_loss"] == 0.015

def test_julia_connection_fail(requests_mock):
    """
    Test if the app handles a connection failure gracefully (returns empty dict).
    """
    test_url = "http://julia-backend:8080"
    app.JULIA_URL = test_url
    fake_endpoint = f"{test_url}/process"
    
    # Simulate a 500 Internal Server Error
    requests_mock.post(fake_endpoint, text="Internal Server Error", status_code=500)
    
    dummy_prices = [10.0, 11.0]
    result = get_julia_calculations(dummy_prices, 5)
    
    # Should return an empty dictionary, not raise an Exception
    assert result == {}
