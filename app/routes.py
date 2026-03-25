from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.database import get_db
from app.models import Customer, Prediction
from app.schemas import CustomerCreate, CustomerUpdate, CustomerOut, DashboardOut
from app.ml.predict import predict_churn

router = APIRouter()


def run_prediction(c: Customer, db: Session):
    """Run ML prediction and upsert the Prediction row."""
    # Ensure all field names passed to ML match what it expects internally
    r = predict_churn(
        gender=c.gender,
        SeniorCitizen=c.seniorcitizen,
        Partner=c.partner,
        Dependents=c.dependents,
        tenure=c.tenure,
        PhoneService=c.phoneservice,
        MultipleLines=c.multiplelines,
        InternetService=c.internetservice,
        OnlineSecurity=c.onlinesecurity,
        OnlineBackup=c.onlinebackup,
        DeviceProtection=c.deviceprotection,
        TechSupport=c.techsupport,
        StreamingTV=c.streamingtv,
        StreamingMovies=c.streamingmovies,
        Contract=c.contract,
        PaperlessBilling=c.paperlessbilling,
        PaymentMethod=c.paymentmethod,
        MonthlyCharges=c.monthlycharges,
        TotalCharges=c.totalcharges
    )

    p = db.query(Prediction).filter(Prediction.customer_id == c.id).first()

    if p:
        p.prediction  = r["prediction"]
        p.probability = r["probability"]
        p.timestamp   = datetime.utcnow()
    else:
        p = Prediction(
            customer_id=c.id,
            prediction=r["prediction"],
            probability=r["probability"],
            timestamp=datetime.utcnow(),
        )
        db.add(p)

    db.commit()


# ── CREATE ──────────────────────────────────────────────────────────────────
@router.post("/customers", response_model=CustomerOut, status_code=201)
def add(body: CustomerCreate, db: Session = Depends(get_db)):
    c = Customer(**body.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)

    run_prediction(c, db)
    db.refresh(c)

    return CustomerOut.from_orm_with_latest(c)


# ── UPDATE ──────────────────────────────────────────────────────────────────
@router.put("/customers/{id}", response_model=CustomerOut)
def update(id: int, body: CustomerUpdate, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == id).first()

    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")

    for k, v in body.model_dump(exclude_none=True).items():
        setattr(c, k, v)

    c.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(c)

    run_prediction(c, db)
    db.refresh(c)

    return CustomerOut.from_orm_with_latest(c)


# ── READ ALL ─────────────────────────────────────────────────────────────────
@router.get("/customers", response_model=list[CustomerOut])
def get_all(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return [CustomerOut.from_orm_with_latest(c) for c in customers]


# ── READ ONE ─────────────────────────────────────────────────────────────────
@router.get("/customers/{id}", response_model=CustomerOut)
def get_one(id: int, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == id).first()

    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")

    return CustomerOut.from_orm_with_latest(c)


# ── DASHBOARD ────────────────────────────────────────────────────────────────
@router.get("/dashboard", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db)):
    total     = db.query(Customer).count()
    churn     = db.query(Prediction).filter(Prediction.prediction == "Yes").count()
    non_churn = db.query(Prediction).filter(Prediction.prediction == "No").count()

    avg_charges = db.query(func.avg(Customer.monthlycharges)).scalar() or 0.0

    return {
        "total_customers":    total,
        "churn_count":        churn,
        "non_churn_count":    non_churn,
        "churn_percentage":   round((churn / total * 100), 2) if total else 0.0,
        "avg_monthly_charges": round(float(avg_charges), 2),
        "high_risk_customers": db.query(Prediction)
                                  .filter(Prediction.probability > 0.7)
                                  .count(),
    }