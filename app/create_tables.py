# create_tables.py
from app.database import Base, engine
from app.models import Customer, Prediction

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

print("Tables are synced successfully!")