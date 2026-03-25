from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import router



app = FastAPI(
    title="Churn Prediction API",
    version="1.0"
)

# 🔥 CORS (frontend ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # production mein specific domain dena
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 Routes
app.include_router(router, prefix="/api", tags=["Customers"])

# 🔥 Health check
@app.get("/")
def root():
    return {
        "status": "running",
        "docs": "/docs"
    }