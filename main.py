import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional
from bson.objectid import ObjectId

from database import db, create_document, get_documents
from schemas import Job, Application

app = FastAPI(title="Stuvify Jobs API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers to convert Mongo ObjectId

def serialize_doc(doc):
    if doc is None:
        return None
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# API: /api/jobs for listing jobs
@app.get("/api/jobs")
def list_jobs(department: Optional[str] = None, type: Optional[str] = None, location: Optional[str] = None):
    filter_query = {}
    if department:
        filter_query["department"] = department
    if type:
        filter_query["type"] = type
    if location:
        filter_query["location"] = location

    try:
        jobs = get_documents("job", filter_query)
        return [serialize_doc(j) for j in jobs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Seed sample jobs if collection empty
@app.post("/api/jobs/seed")
def seed_jobs():
    try:
        existing = db["job"].count_documents({}) if db else 0
        if existing > 0:
            return {"inserted": 0, "message": "Jobs already exist"}

        samples: List[Job] = [
            Job(
                title="Frontend Developer",
                department="Engineering",
                location="Remote",
                type="Full-time",
                description="Build immersive UIs with React and Three.js for Stuvify.",
                requirements=["3+ years React", "Experience with R3F/Three.js", "Strong UI skills"],
                featured=True,
            ),
            Job(
                title="3D Designer",
                department="Design",
                location="Hybrid - SF",
                type="Contract",
                description="Design GLTF assets and futuristic scenes for our career hub.",
                requirements=["GLTF/GLB workflow", "Blender/C4D", "Understanding of web performance"],
            ),
            Job(
                title="Growth Marketer",
                department="Marketing",
                location="Remote",
                type="Part-time",
                description="Drive campaigns and partnerships for student hiring.",
                requirements=["Lifecycle marketing", "Content strategy", "Analytics"],
            ),
        ]
        inserted = 0
        for job in samples:
            create_document("job", job)
            inserted += 1
        return {"inserted": inserted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# API: /api/apply for submission
class ApplyPayload(BaseModel):
    job_id: str
    name: str
    email: EmailStr
    portfolio: Optional[str] = None
    resume_url: Optional[str] = None
    cover_letter: Optional[str] = None


@app.post("/api/apply")
def apply(payload: ApplyPayload):
    # Validate job exists
    try:
        job = db["job"].find_one({"_id": ObjectId(payload.job_id)})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job id")

    try:
        app_doc = Application(
            job_id=payload.job_id,
            name=payload.name,
            email=payload.email,
            portfolio=payload.portfolio,
            resume_url=payload.resume_url,
            cover_letter=payload.cover_letter,
        )
        inserted_id = create_document("application", app_doc)
        return {"status": "ok", "application_id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
