import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base
from app.api import health, models_info, examinations, quality, analysis, reviews, reports
from app.websocket import live_stream

# Create DB tables if not existing
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="EndoAI Vision: AI-Powered Optical Imaging for Intelligent Gastrointestinal Disease Detection and Explainable Clinical Decision Support",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static storage directory
if os.path.exists(settings.STORAGE_DIR):
    app.mount("/storage", StaticFiles(directory=settings.STORAGE_DIR), name="storage")

# Include Routers
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(models_info.router, prefix=settings.API_V1_STR)
app.include_router(examinations.router, prefix=settings.API_V1_STR)
app.include_router(quality.router, prefix=settings.API_V1_STR)
app.include_router(analysis.router, prefix=settings.API_V1_STR)
app.include_router(reviews.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(live_stream.router)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "disclaimer": "EndoAI Vision is a research/educational clinical decision-support prototype. Outputs require qualified human review."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
