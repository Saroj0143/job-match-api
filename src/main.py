from fastapi import FastAPI
from src.database import Base, engine
from src.routers import candidates, jobs, recommendations

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job Match API",
    description="Rule-based, explainable job recommendation engine.",
    version="1.0.0",
)

app.include_router(candidates.router)
app.include_router(jobs.router)
app.include_router(recommendations.router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "service": "job-match-api"}