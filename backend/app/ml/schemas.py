from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class OverduePredictionRequest(BaseModel):
    priority: str = Field(..., description="Task priority: LOW, MEDIUM, HIGH, CRITICAL")
    category_id: int = Field(..., description="Category ID")
    user_id: int = Field(..., description="Assigned User ID")
    estimated_hours: float = Field(..., ge=0, description="Estimated hours")
    deadline: Optional[datetime] = Field(None, description="Task deadline timestamp")


class OverduePredictionResponse(BaseModel):
    late_probability: float = Field(..., description="Predicted late completion probability (0.0 to 1.0)")
    risk_level: str = Field(..., description="Risk Level: LOW, MEDIUM, or HIGH")
    model_version: str = Field(..., description="Trained model version")
    explanation: str = Field("Predicted late-completion risk based on historical task patterns.", description="Non-guarantee explanation notice")


class CompletionTimePredictionRequest(BaseModel):
    priority: str = Field(..., description="Task priority: LOW, MEDIUM, HIGH, CRITICAL")
    category_id: int = Field(..., description="Category ID")
    user_id: int = Field(..., description="Assigned User ID")
    estimated_hours: float = Field(..., ge=0, description="Estimated hours")


class CompletionTimePredictionResponse(BaseModel):
    predicted_completion_days: float = Field(..., description="Predicted completion duration in days")
    model_version: str = Field(..., description="Trained model version")
    explanation: str = Field("Predicted task duration based on historical completion trends.", description="Non-guarantee explanation notice")


class ModelInfoResponse(BaseModel):
    classification_model: Dict[str, Any]
    regression_model: Dict[str, Any]
    dataset_summary: Dict[str, Any]


class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float


class FeatureImportanceResponse(BaseModel):
    classification_importance: List[FeatureImportanceItem]
    regression_importance: List[FeatureImportanceItem]
