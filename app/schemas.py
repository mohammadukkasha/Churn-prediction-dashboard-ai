from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CustomerCreate(BaseModel):
    gender: str
    seniorcitizen: int
    partner: str = "No"
    dependents: str = "No"
    tenure: int
    phoneservice: str = "No"
    multiplelines: str = "No phone service"
    internetservice: str = "No"
    onlinesecurity: str = "No internet service"
    onlinebackup: str = "No internet service"
    deviceprotection: str = "No internet service"
    techsupport: str = "No internet service"
    streamingtv: str = "No internet service"
    streamingmovies: str = "No internet service"
    contract: str = "Month-to-month"
    paperlessbilling: str = "No"
    paymentmethod: str = "Electronic check"
    monthlycharges: float
    totalcharges: float = 0.0


class CustomerUpdate(BaseModel):
    gender: Optional[str] = None
    seniorcitizen: Optional[int] = None
    partner: Optional[str] = None
    dependents: Optional[str] = None
    tenure: Optional[int] = None
    phoneservice: Optional[str] = None
    multiplelines: Optional[str] = None
    internetservice: Optional[str] = None
    onlinesecurity: Optional[str] = None
    onlinebackup: Optional[str] = None
    deviceprotection: Optional[str] = None
    techsupport: Optional[str] = None
    streamingtv: Optional[str] = None
    streamingmovies: Optional[str] = None
    contract: Optional[str] = None
    paperlessbilling: Optional[str] = None
    paymentmethod: Optional[str] = None
    monthlycharges: Optional[float] = None
    totalcharges: Optional[float] = None


class PredictionOut(BaseModel):
    prediction: str
    probability: float
    timestamp: datetime

    model_config = {"from_attributes": True}


class CustomerOut(BaseModel):
    id: int
    gender: str
    seniorcitizen: int
    partner: str
    dependents: str
    tenure: int
    phoneservice: str
    multiplelines: str
    internetservice: str
    onlinesecurity: str
    onlinebackup: str
    deviceprotection: str
    techsupport: str
    streamingtv: str
    streamingmovies: str
    contract: str
    paperlessbilling: str
    paymentmethod: str
    monthlycharges: float
    totalcharges: float
    created_at: datetime
    updated_at: datetime
    # The Customer model has a list 'predictions'; expose the latest one
    prediction: Optional[PredictionOut] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_latest(cls, customer):
        """Build response using the latest prediction from the relationship list."""
        data = {
            "id": customer.id,
            "gender": customer.gender,
            "seniorcitizen": customer.seniorcitizen,
            "partner": customer.partner,
            "dependents": customer.dependents,
            "tenure": customer.tenure,
            "phoneservice": customer.phoneservice,
            "multiplelines": customer.multiplelines,
            "internetservice": customer.internetservice,
            "onlinesecurity": customer.onlinesecurity,
            "onlinebackup": customer.onlinebackup,
            "deviceprotection": customer.deviceprotection,
            "techsupport": customer.techsupport,
            "streamingtv": customer.streamingtv,
            "streamingmovies": customer.streamingmovies,
            "contract": customer.contract,
            "paperlessbilling": customer.paperlessbilling,
            "paymentmethod": customer.paymentmethod,
            "monthlycharges": customer.monthlycharges,
            "totalcharges": customer.totalcharges,
            "created_at": customer.created_at,
            "updated_at": customer.updated_at,
            "prediction": None,
        }
        if customer.predictions:
            latest = sorted(customer.predictions, key=lambda p: p.timestamp)[-1]
            data["prediction"] = PredictionOut.model_validate(latest)
        return cls(**data)


class DashboardOut(BaseModel):
    total_customers: int
    churn_count: int
    non_churn_count: int
    churn_percentage: float
    avg_monthly_charges: float
    high_risk_customers: int