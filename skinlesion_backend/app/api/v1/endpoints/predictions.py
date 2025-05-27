from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from typing import List, Optional
from app.services.prediction_service import PredictionService
from app.repositories.prediction_repository import PredictionRepository # For dependency
from app.api.v1 import schemas # Import the schemas module
from app.models.prediction import PredictionInDB # For response model

router = APIRouter()

# Dependency to get repository (could be more sophisticated with a DI container)
def get_prediction_repository():
    return PredictionRepository()

# Dependency to get service
def get_prediction_service(
    repo: PredictionRepository = Depends(get_prediction_repository)
) -> PredictionService:
    return PredictionService(repository=repo)

@router.post("/predict", response_model=schemas.PredictionResponse)
async def create_prediction(
    file: UploadFile = File(...),
    service: PredictionService = Depends(get_prediction_service)
):
    """
    Receives an image, performs a prediction, and stores the result.
    Returns the prediction details.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    try:
        prediction_db = await service.process_prediction(file)
        return schemas.PredictionResponse(
            id=prediction_db.id,
            filename=prediction_db.filename,
            predictions=prediction_db.prediction_results
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re: # e.g., AI model loading/prediction error
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail="An unexpected error occurred during prediction.")

@router.get("/predictions/{prediction_id}", response_model=schemas.PredictionResponse)
def read_prediction(
    prediction_id: str,
    service: PredictionService = Depends(get_prediction_service)
):
    """Retrieves a specific prediction by its ID."""
    db_prediction = service.get_prediction(prediction_id)
    if db_prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return schemas.PredictionResponse(
        id=db_prediction.id,
        filename=db_prediction.filename,
        predictions=db_prediction.prediction_results
    )

@router.get("/predictions", response_model=List[schemas.PredictionResponse])
def read_predictions(
    skip: int = 0,
    limit: int = Query(default=10, le=100), # Max 100 items per page
    service: PredictionService = Depends(get_prediction_service)
):
    """Retrieves a list of all predictions with pagination."""
    predictions_db = service.get_all_predictions(skip=skip, limit=limit)
    return [
        schemas.PredictionResponse(
            id=pred.id, 
            filename=pred.filename, 
            predictions=pred.prediction_results
        ) for pred in predictions_db
    ] 