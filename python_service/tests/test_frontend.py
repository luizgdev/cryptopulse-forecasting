import pytest
import requests
import sys
import os

# Add the 'src' directory to the system path to allow importing 'app.py'
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

# Import the function we want to test
from app import get_julia_calculations

def test_julia_integration_success(requests_mock):
    """
    Test if the Python app correctly parses a valid JSON response from Julia.
    """
    
    # The fake URL we want to intercept
    # Note: We use the service name 'julia-backend' as defined in Docker
    fake_url = "http://julia-backend:8080/process"
    
    # Mock response: This is what Julia WOULD return
    mock_response = {
        "sma_values": [100.0, 101.0, 102.0],
        "forecast_price": 103.5,
        "message": "Success"
    }
    
    # Configure the mock
    requests_mock.post(fake_url, json=mock_response, status_code=200)
    
    # Force the environment variable for the test context
    os.environ["JULIA_URL"] = "http://julia-backend:8080"
    
    # Execute the function
    dummy_prices = [10.0, 11.0, 12.0]
    result = get_julia_calculations(dummy_prices, 5)
    
    # Assertions
    assert result["forecast_price"] == 103.5
    assert len(result["sma_values"]) == 3
    assert result["message"] == "Success"

def test_julia_connection_fail(requests_mock):
    """
    Test if the Python app handles a server crash gracefully (no crash).
    """
    
    fake_url = "http://julia-backend:8080/process"
    
    # Simulate a 500 Internal Server Error
    requests_mock.post(fake_url, text="Internal Server Error", status_code=500)
    
    os.environ["JULIA_URL"] = "http://julia-backend:8080"
    
    dummy_prices = [10.0, 11.0]
    result = get_julia_calculations(dummy_prices, 5)
    
    # It should return an empty dict, not raise an Exception
    assert result == {}
