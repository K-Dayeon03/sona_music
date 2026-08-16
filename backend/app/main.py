from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, personas, recommendations, spotify

app = FastAPI(
    title="Sona API",
    description="Python backend for AI music persona recommendations.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:8443",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "sona-backend"}


app.include_router(personas.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(spotify.router, prefix="/api")
