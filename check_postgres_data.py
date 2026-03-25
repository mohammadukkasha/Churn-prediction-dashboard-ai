import pandas as pd
from app.database import engine

# Query the tables directly from Postgres to confirm
print("--- FETCHING CUSTOMERS FROM POSTGRES ---")
customers = pd.read_sql("SELECT * FROM customers", engine)
print(customers)

print("\n--- FETCHING PREDICTIONS FROM POSTGRES ---")
predictions = pd.read_sql("SELECT * FROM predictions", engine)
print(predictions)

print("\n--- RECENT HISTORY (JOINED) ---")
history = pd.read_sql("""
    SELECT c.id, c.gender, c.monthlycharges, p.prediction, p.probability 
    FROM customers c 
    JOIN predictions p ON c.id = p.customer_id
    ORDER BY c.created_at DESC
""", engine)
print(history)
