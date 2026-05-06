from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from Aljamiado import convert_to_aljamiado
from Xiaoerjing import combine_pinyin_with_tones, clean_string
from Araboji import japanese_to_arabic, load_mapping
from Soagyeong import korean_to_arabic, adjust_arabic_output
from Tieunhikinh import transliterate_vietnamese_to_arabic

app = FastAPI()

# Configure CORS based on environment
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load mapping once
araboji_mapping = load_mapping("mapping.xlsx")

languages = {
    'aljamiado': convert_to_aljamiado,
    'xiaoerjing': lambda text: clean_string(combine_pinyin_with_tones(text)),
    'araboji': lambda text: japanese_to_arabic(text, araboji_mapping)[1],
    'soagyeong': lambda text: adjust_arabic_output(korean_to_arabic(text)),
    'tieunhikinh': transliterate_vietnamese_to_arabic
}

@app.post("/api/transliterate")
async def transliterate(data: dict):
    text = data.get('text')
    language = data.get('language')
    if not text or not language:
        raise HTTPException(status_code=400, detail="Missing text or language")
    func = languages.get(language.lower())
    if not func:
        raise HTTPException(status_code=400, detail="Unsupported language")
    try:
        result = func(text)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    return {"status": "ok"}

# Serve static files (React frontend)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
async def health():
    return {"status": "ok"}