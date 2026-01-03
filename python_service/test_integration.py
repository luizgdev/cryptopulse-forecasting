import requests

JULIA_URL = "http://localhost:8080"

try:
    # 1. Health test
    health = requests.get(f"{JULIA_URL}/health").json()
    print(f"Julia says: {health}")

    # 2. Prediction test
    payload = {"current_price": 50000.0}
    prediction = requests.post(f"{JULIA_URL}/predict", json=payload).json()
    print(f"Prediction: {prediction}")

except Exception as e:
    print(f"Conection error with Julia: {e}")
