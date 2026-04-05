from fastapi import FastAPI
from backend.api.routes import router
from backend.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for Deep Insights Copilot"
)

# Include the main application router
app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
