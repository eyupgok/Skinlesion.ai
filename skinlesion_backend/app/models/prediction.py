from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class PredictionBase(BaseModel):
    filename: str
    # Add other relevant metadata if needed, e.g., image_size, content_type

class PredictionCreate(PredictionBase):
    pass # No additional fields needed for creation from base

class PredictionResult(BaseModel):
    label: str
    confidence: float

class Prediction(PredictionBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    prediction_results: List[PredictionResult]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True # For compatibility with ORMs, though we're using NoSQL directly
        # In Pydantic V2, orm_mode is replaced by from_attributes = True
        # from_attributes = True

class PredictionInDB(Prediction):
    # Could add fields that are only in DB, if any
    pass 