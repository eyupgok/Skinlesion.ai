# This file contains the business logic for predictions.

from fastapi import UploadFile
from app.repositories.prediction_repository import PredictionRepository
from app.models.prediction import PredictionCreate, PredictionInDB, PredictionResult
from app.ai_model.loader import AIModel # Assuming your AI model loader is here
from typing import List, Optional
import shutil # For saving uploaded file temporarily (optional)
import os # For file operations (optional)

# TEMP_UPLOAD_DIR = "temp_uploads"
# os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

class PredictionService:
    def __init__(self, repository: PredictionRepository):
        self.repository = repository
        self.ai_model = AIModel() # Or inject AIModel instance if preferred

    async def process_prediction(self, file: UploadFile) -> PredictionInDB:
        """Processes the uploaded image, gets a prediction, and saves the result."""
        if not file.filename:
            raise ValueError("File has no filename")
        
        # 1. (Optional) Save the uploaded file temporarily if your model needs a file path
        # or process it in memory if possible.
        # file_location = os.path.join(TEMP_UPLOAD_DIR, file.filename)
        # with open(file_location, "wb+") as file_object:
        #     shutil.copyfileobj(file.file, file_object)
        
        # For in-memory processing:
        image_bytes = await file.read()
        await file.close() # Ensure the file is closed

        # 2. Get prediction from AI model
        # Ensure AIModel.predict can handle image_bytes or a file_path
        try:
            raw_predictions = self.ai_model.predict(image_bytes)
        except Exception as e:
            # Potentially clean up temp file if created
            # if os.path.exists(file_location):
            #     os.remove(file_location)
            print(f"Error during AI model prediction: {e}")
            raise # Re-raise the exception to be handled by the endpoint
        
        # 3. Convert raw predictions to PredictionResult schema
        # This depends on the output format of your AIModel.predict method
        # Assuming it returns a list of dicts like: [{"label": "melanoma", "confidence": 0.75}, ...]
        prediction_results = [PredictionResult(**p) for p in raw_predictions]

        # 4. Create prediction data entry
        prediction_data = PredictionCreate(filename=file.filename)

        # 5. Save to database via repository
        saved_prediction = self.repository.save_prediction(
            prediction_data=prediction_data, 
            results=prediction_results
        )
        
        # 6. (Optional) Clean up the temporary file if you saved it
        # if os.path.exists(file_location):
        #     os.remove(file_location)
            
        return saved_prediction

    def get_prediction(self, prediction_id: str) -> Optional[PredictionInDB]:
        """Retrieves a specific prediction by its ID."""
        # Convert string ID to UUID if your repository expects UUID
        import uuid
        try:
            pred_uuid = uuid.UUID(prediction_id)
        except ValueError:
            return None # Invalid UUID format
        return self.repository.get_prediction_by_id(pred_uuid)

    def get_all_predictions(self, skip: int = 0, limit: int = 100) -> List[PredictionInDB]:
        """Retrieves all predictions with pagination."""
        return self.repository.get_all_predictions(skip=skip, limit=limit) 