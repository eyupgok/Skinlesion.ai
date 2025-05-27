from fastapi import FastAPI
from app.api.v1.endpoints import predictions
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# API v1 routers
app.include_router(predictions.router, prefix=settings.API_V1_STR, tags=["predictions"])

@app.get("/")
async def root():
    return {"message": "Welcome to SkinLesionAI API"}

# Placeholder for startup and shutdown events if needed later
# @app.on_event("startup")
# async def startup_event():
#     # Load AI model, connect to DB etc.
#     pass

# @app.on_event("shutdown")
# async def shutdown_event():
#     # Clean up resources
#     pass 