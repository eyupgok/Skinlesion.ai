from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SkinLesionAI Backend"
    API_V1_STR: str = "/api/v1"
    
    # Database settings (MongoDB example)
    MONGODB_URL: Optional[str] = "mongodb://localhost:27017"
    DATABASE_NAME: str = "skinlesion_db"
    
    # AI Model path
    AI_MODEL_PATH: str = "app/ai_model/assets/skin_lesion_model.h5"

    class Config:
        case_sensitive = True
        env_file = ".env" # Load from .env file if it exists

settings = Settings() 