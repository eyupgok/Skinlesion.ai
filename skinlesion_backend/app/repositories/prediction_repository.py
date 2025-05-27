# This file will contain the logic for interacting with the database (MongoDB)
# for Prediction data. It will implement the Repository Pattern.

from pymongo import MongoClient
from app.core.config import settings
from app.models.prediction import PredictionInDB, PredictionCreate, PredictionResult
from typing import List, Optional
import uuid

class PredictionRepository:
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db["predictions"]

    def save_prediction(self, prediction_data: PredictionCreate, results: List[PredictionResult]) -> PredictionInDB:
        """Saves a new prediction to the database."""
        db_prediction = PredictionInDB(
            filename=prediction_data.filename,
            prediction_results=results
        )
        # Convert UUID to string for MongoDB if it's not automatically handled
        # or store as Binary subtype 4 if preferred for native UUID support in MongoDB
        prediction_dict = db_prediction.model_dump(exclude_none=True)
        prediction_dict["_id"] = db_prediction.id # Use the Pydantic generated UUID as _id
        prediction_dict["id"] = str(db_prediction.id) # Also store string version for easier querying if needed
        
        inserted = self.collection.insert_one(prediction_dict)
        # created_prediction = self.collection.find_one({"_id": inserted.inserted_id})
        # return PredictionInDB(**created_prediction) if created_prediction else None
        return db_prediction # Return the Pydantic model instance

    def get_prediction_by_id(self, prediction_id: uuid.UUID) -> Optional[PredictionInDB]:
        """Retrieves a prediction by its ID."""
        # MongoDB stores _id often as ObjectId if not specified, or can be UUID
        # If you store id as UUID, query like this. If as string, convert prediction_id to str.
        prediction_data = self.collection.find_one({"_id": prediction_id})
        if prediction_data:
            return PredictionInDB(**prediction_data)
        return None

    def get_all_predictions(self, skip: int = 0, limit: int = 100) -> List[PredictionInDB]:
        """Retrieves all predictions with pagination."""
        predictions_cursor = self.collection.find().skip(skip).limit(limit)
        return [PredictionInDB(**pred) for pred in predictions_cursor]

    # Add other methods as needed, e.g., update, delete, query by user, etc. 