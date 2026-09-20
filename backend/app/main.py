from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .database import Base, engine
from .config import settings
from .routers import auth, profile, skills, careers, evidence, gap, roadmap, assessments, dashboard, simulator

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CareerLens AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(skills.router)
app.include_router(careers.router)
app.include_router(evidence.router)
app.include_router(gap.router)
app.include_router(roadmap.router)
app.include_router(assessments.router)
app.include_router(dashboard.router)
app.include_router(simulator.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "ai_mode": settings.ai_mode}


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "An unexpected server error occurred."})
