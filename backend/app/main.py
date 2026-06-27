from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, config

app = FastAPI(
    title="ImpactGraph API",
    description="Data Impact Analysis Platform Metadata Engine APIs",
    version="1.0.0"
)

# Configure CORS policies to allow browser connections from our frontend client container
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the exact client origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API version 1 routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(config.router, prefix="/api/v1/config", tags=["Configuration"])

@app.get("/health", tags=["System"])
def health_check():
    """Lightweight endpoint for container readiness and live probes."""
    return {
        "status": "healthy",
        "app": "impactgraph",
        "version": "1.0.0"
    }
