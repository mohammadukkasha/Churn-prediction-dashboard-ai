import requests

BASE_URL = "http://localhost:8000/api"

print("--- TESTING CUSTOMER UPDATE (PUT) ---")
# 1. Fetch current customer
res = requests.get(f"{BASE_URL}/customers")
if res.status_code != 200:
    print("Cannot fetch customers:", res.text)
    exit()

customer_list = res.json()
if not customer_list:
    print("No customers to update.")
    exit()

cust = customer_list[0]
cid = cust["id"]
old_tenure = cust["tenure"]
old_prob = cust["prediction"]["probability"]

print(f"Customer ID: {cid} | Old Tenure: {old_tenure} | Old Prob: {old_prob}")

# 2. Update tenure
new_tenure = old_tenure + 50
print(f"Updating tenure to {new_tenure}...")

update_res = requests.put(f"{BASE_URL}/customers/{cid}", json={"tenure": new_tenure})

if update_res.status_code == 200:
    data = update_res.json()
    new_prob = data["prediction"]["probability"]
    print(f"Update Success! New Tenure: {data['tenure']} | New Prob: {new_prob}")
    if old_prob != new_prob:
        print("Cool: Prediction was updated based on new data.")
    else:
        print("Note: Prediction probability remained the same (or model didn't change its output).")
else:
    print("Update failed:", update_res.status_code, update_res.text)
