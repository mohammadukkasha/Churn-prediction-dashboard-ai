import requests

BASE_URL = "http://localhost:8000/api"

SAMPLE_CUSTOMER = {
    "gender": "Female",
    "seniorcitizen": 1,
    "partner": "Yes",
    "dependents": "No",
    "tenure": 24,
    "phoneservice": "Yes",
    "multiplelines": "Yes",
    "internetservice": "Fiber optic",
    "onlinesecurity": "No",
    "onlinebackup": "Yes",
    "deviceprotection": "Yes",
    "techsupport": "No",
    "streamingtv": "Yes",
    "streamingmovies": "Yes",
    "contract": "One year",
    "paperlessbilling": "Yes",
    "paymentmethod": "Credit card (automatic)",
    "monthlycharges": 104.8,
    "totalcharges": 2427.35
}

print("Adding test customer...")
response = requests.post(f"{BASE_URL}/customers", json=SAMPLE_CUSTOMER)

if response.status_code == 201:
    data = response.json()
    print("Success! Customer created with ID:", data["id"])
    print("Prediction Result:", data["prediction"])
else:
    print("Failed to add customer:", response.status_code, response.text)

print("\nFetching all customers (history check)...")
history = requests.get(f"{BASE_URL}/customers").json()
print(f"Total entries in history: {len(history)}")
for entry in history:
    print(f"ID: {entry['id']} | Prediction: {entry['prediction']['prediction']} (Prob: {entry['prediction']['probability']})")
