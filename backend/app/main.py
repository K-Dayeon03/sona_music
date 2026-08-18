from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import personas, recommendations, social, spotify_catalog

app = FastAPI(
    title="Sona API",
    description="Python backend for AI music persona recommendations.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "sona-backend"}


app.include_router(personas.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(social.router, prefix="/api")
app.include_router(spotify_catalog.router, prefix="/api")
