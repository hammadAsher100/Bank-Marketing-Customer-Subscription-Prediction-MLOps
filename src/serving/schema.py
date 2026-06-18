"""
src/serving/schema.py
─────────────────────────────────────────────────────────────
Pydantic schemas define karte hain:
  - PredictRequest  → client jo data bhejta hai
  - PredictResponse → FastAPI jo wapas bhejta hai
  - HealthResponse  → /health endpoint ka response

Pydantic kya karta hai?
  - Automatically validate karta hai incoming data
  - Type check karta hai (age int hai ya nahi, etc.)
  - Auto-generates OpenAPI docs (Swagger UI)
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST SCHEMA
# Bank Marketing dataset ke exact features
# ═══════════════════════════════════════════════════════════════════════════════
class PredictRequest(BaseModel):
    """
    Raw input features — same as bank-full.csv columns.
    FastAPI automatically validates types and ranges.
    """

    # ── Personal info ─────────────────────────────────────────────────────────
    age: int = Field(..., ge=18, le=100, description="Customer age (18-100)", example=35)

    job: Literal[
        "admin.", "blue-collar", "entrepreneur", "housemaid",
        "management", "retired", "self-employed", "services",
        "student", "technician", "unemployed", "unknown"
    ] = Field(..., description="Job type", example="management")

    marital: Literal["divorced", "married", "single"] = Field(
        ..., description="Marital status", example="married"
    )

    education: Literal["primary", "secondary", "tertiary", "unknown"] = Field(
        ..., description="Education level", example="tertiary"
    )

    default: Literal["yes", "no"] = Field(
        ..., description="Has credit in default?", example="no"
    )

    balance: int = Field(
        ..., description="Average yearly balance (euros)", example=1500
    )

    housing: Literal["yes", "no"] = Field(
        ..., description="Has housing loan?", example="yes"
    )

    loan: Literal["yes", "no"] = Field(
        ..., description="Has personal loan?", example="no"
    )

    # ── Last contact info ─────────────────────────────────────────────────────
    contact: Literal["cellular", "telephone", "unknown"] = Field(
        ..., description="Contact communication type", example="cellular"
    )

    day: int = Field(..., ge=1, le=31, description="Last contact day of month", example=15)

    month: Literal[
        "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec"
    ] = Field(..., description="Last contact month", example="may")

    duration: int = Field(
        ..., ge=1, description="Last contact duration (seconds, must be > 0)", example=300
    )

    # ── Campaign info ─────────────────────────────────────────────────────────
    campaign: int = Field(
        ..., ge=1, le=100, description="Number of contacts during this campaign", example=2
    )

    pdays: int = Field(
        ..., ge=-1, description="Days since last contact (-1 = never contacted)", example=-1
    )

    previous: int = Field(
        ..., ge=0, description="Number of contacts before this campaign", example=0
    )

    poutcome: Literal["failure", "other", "success", "unknown"] = Field(
        ..., description="Outcome of previous campaign", example="unknown"
    )

    # ── Optional: override model choice and threshold ─────────────────────────
    model_type: Literal["lgbm", "xgb"] = Field(
        default="lgbm", description="Which model to use for prediction"
    )

    threshold: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Decision threshold override (default: from params.yaml)"
    )

    @field_validator("duration")
    @classmethod
    def duration_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("duration must be > 0 (zero-duration calls are excluded)")
        return v

    model_config = {"json_schema_extra": {
        "example": {
            "age": 35, "job": "management", "marital": "married",
            "education": "tertiary", "default": "no", "balance": 1500,
            "housing": "yes", "loan": "no", "contact": "cellular",
            "day": 15, "month": "may", "duration": 300,
            "campaign": 2, "pdays": -1, "previous": 0, "poutcome": "unknown",
            "model_type": "lgbm", "threshold": None
        }
    }}


# ═══════════════════════════════════════════════════════════════════════════════
# RESPONSE SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════
class PredictResponse(BaseModel):
    """
    Prediction result returned by /predict endpoint.
    """
    prediction:     int   = Field(..., description="0 = No, 1 = Yes")
    probability:    float = Field(..., description="Probability of subscribing (class 1)")
    model_used:     str   = Field(..., description="Model that made the prediction")
    threshold_used: float = Field(..., description="Decision threshold applied")
    label:          str   = Field(..., description="Human readable result")
    message:        Optional[str] = Field(None, description="Optional warning or info message")

    model_config = {"json_schema_extra": {
        "example": {
            "prediction": 1,
            "probability": 0.7823,
            "model_used": "lgbm",
            "threshold_used": 0.5,
            "label": "Will Subscribe ✅"
        }
    }}


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════
class HealthResponse(BaseModel):
    status:       str  = Field(..., example="ok")
    lgbm_loaded:  bool = Field(..., description="LightGBM model available?")
    xgb_loaded:   bool = Field(..., description="XGBoost model available?")
    mlflow_db:    bool = Field(..., description="MLflow tracking DB found?")


# ═══════════════════════════════════════════════════════════════════════════════
# BATCH PREDICT SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════
class BatchPredictRequest(BaseModel):
    """For predicting multiple customers at once."""
    records:    list[PredictRequest]
    model_type: Literal["lgbm", "xgb"] = "lgbm"
    threshold:  Optional[float] = None

class BatchPredictResponse(BaseModel):
    results:       list[PredictResponse]
    total_records: int
    subscribers:   int
    non_subscribers: int