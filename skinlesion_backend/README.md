# SkinLesionAI Backend

This project is a FastAPI backend for the SkinLesionAI application. It allows users to upload images of skin lesions, get predictions from an AI model, and store/retrieve prediction results.

## Project Structure

The project follows a layered architecture:

- `app/main.py`: FastAPI application instance and main router.
- `app/core/`: Core components like configuration (`config.py`).
- `app/models/`: Pydantic models for data representation (`prediction.py`).
- `app/api/v1/`: API version 1.
    - `endpoints/`: API route handlers (e.g., `predictions.py`).
    - `schemas.py`: Pydantic schemas for API request/response validation.
- `app/services/`: Business logic layer (e.g., `prediction_service.py`).
- `app/repositories/`: Data access layer (e.g., `prediction_repository.py` for MongoDB interaction).
- `app/ai_model/`: AI model loading and prediction logic (`loader.py`) and assets (`assets/`).
- `tests/`: Unit and integration tests.

## Setup and Installation

1.  **Clone the repository (if applicable).**
2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up environment variables:**
    Create a `.env` file in the `skinlesion_backend` root directory by copying `.env.example` (if provided) and fill in the necessary values (e.g., `MONGODB_URL`, `DATABASE_NAME`).
    Example `.env` content:
    ```
    MONGODB_URL=mongodb://localhost:27017
    DATABASE_NAME=skinlesion_prod_db
    # AI_MODEL_PATH=app/ai_model/assets/your_model.h5 # If different from default
    ```
5.  **Place your AI model:**
    Ensure your trained AI model (e.g., `.h5` file) is placed in the `skinlesion_backend/app/ai_model/assets/` directory and update `AI_MODEL_PATH` in `app/core/config.py` or your `.env` file if it's not named `skin_lesion_model.h5`.

## Running the Application

Use Uvicorn to run the FastAPI application:

```bash
cd skinlesion_backend
uvicorn app.main:app --reload
```

This will typically start the server at `http://127.0.0.1:8000`.
The API documentation (Swagger UI) will be available at `http://127.0.0.1:8000/docs`.

## Running Tests (Placeholder)

Tests are intended to be placed in the `tests/` directory.
To run tests (assuming you use pytest):

```bash
pytest
```

## Key Design Patterns Used (or placeholders for)

-   **Layered Architecture:** Separates concerns into Presentation (API), Business Logic (Services), and Data Access (Repositories).
-   **Repository Pattern:** `PredictionRepository` abstracts data persistence logic for MongoDB, making the service layer independent of the database specifics.
-   **Dependency Injection:** FastAPI handles injecting dependencies (like services and repositories) into route handlers.
-   **Strategy Pattern (Potential for AI Model):** The `AIModel` class in `ai_model/loader.py` can be extended to use the Strategy pattern if you need to switch between different AI models or versions easily.
-   **Singleton (for AI Model):** The `AIModel.get_model()` class method ensures the AI model is loaded only once.

## Further Development

-   Implement actual AI model loading and prediction logic in `app/ai_model/loader.py`.
-   Add comprehensive error handling and logging.
-   Write unit and integration tests for all components.
-   Implement user authentication and authorization if needed.
-   Consider a more robust dependency injection container if the project grows significantly.
-   Refine Pydantic models and API schemas as per evolving requirements. 