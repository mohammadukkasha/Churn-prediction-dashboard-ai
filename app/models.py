from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = {"extend_existing": True}

    id             = Column(Integer, primary_key=True, index=True)
    gender         = Column(String, nullable=False)
    seniorcitizen  = Column(Integer, nullable=False, default=0)
    partner        = Column(String, default="No")
    dependents     = Column(String, default="No")
    tenure         = Column(Integer, nullable=False, default=0)
    phoneservice   = Column(String, default="No")
    multiplelines  = Column(String, default="No phone service")
    internetservice = Column(String, default="No")
    onlinesecurity = Column(String, default="No internet service")
    onlinebackup   = Column(String, default="No internet service")
    deviceprotection = Column(String, default="No internet service")
    techsupport    = Column(String, default="No internet service")
    streamingtv    = Column(String, default="No internet service")
    streamingmovies = Column(String, default="No internet service")
    contract       = Column(String, nullable=False, default="Month-to-month")
    paperlessbilling = Column(String, default="No")
    paymentmethod  = Column(String, default="Electronic check")
    monthlycharges = Column(Float, nullable=False, default=0.0)
    totalcharges   = Column(Float, default=0.0)

    created_at     = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at     = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship with Prediction (one-to-one via back_populates)
    predictions = relationship("Prediction", back_populates="customer",
                               cascade="all, delete-orphan")


class Prediction(Base):
    __tablename__ = "predictions"
    __table_args__ = {"extend_existing": True}

    id          = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    prediction  = Column(String, nullable=False)          # "Yes" / "No"
    probability = Column(Float,  nullable=False)
    timestamp   = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Link back to customer
    customer = relationship("Customer", back_populates="predictions")