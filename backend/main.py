import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.n8n_bridge import get_aura_recommendations, get_biorhythm_analysis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend statically
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

class AnalyzeRequest(BaseModel):
    name: str = ""
    phone_number: str = ""
    email: str = ""
    aura_color_hex: str
    image_b64: str = "" 
    session_id: str = ""

class BiorhythmRequest(BaseModel):
    name: str = ""
    phone_number: str = ""
    email: str = ""
    birthdate: str
    period: str = "today"
    image_b64: str = ""
    session_id: str = ""

@app.post("/api/analyze")
async def analyze_aura(req: AnalyzeRequest):
    await asyncio.sleep(0.5)
    response = get_aura_recommendations(req.name, req.phone_number, req.email, req.aura_color_hex, req.image_b64, req.session_id)
    return response

@app.post("/api/biorhythm")
async def analyze_biorhythm(req: BiorhythmRequest):
    await asyncio.sleep(0.5)
    response = get_biorhythm_analysis(req.name, req.phone_number, req.email, req.birthdate, req.period, req.image_b64, req.session_id)
    return response

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("backend.main:app", host='0.0.0.0', port=8000, reload=True)
