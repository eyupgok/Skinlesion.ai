from pydantic import BaseModel
from typing import List
from app.models.prediction import Prediction, PredictionResult # Assuming Prediction model is defined here
import uuid

# Schema for request body when uploading an image
class ImageUploadRequest(BaseModel):
    # FastAPI will handle the file upload separately using UploadFile
    # This schema is more for potential additional metadata if needed with the upload
    pass 

# Schema for the response after a prediction is made
class PredictionResponse(BaseModel):
    id: uuid.UUID
    filename: str
    predictions: List[PredictionResult]
    # created_at: datetime # You might want to include this

    class Config:
        # In Pydantic V2, orm_mode is replaced by from_attributes = True
        # from_attributes = True
        orm_mode = True 