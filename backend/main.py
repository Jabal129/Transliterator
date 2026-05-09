from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from Aljamiado import convert_to_aljamiado
from Xiaoerjing import combine_pinyin_with_tones, clean_string
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

# Lazy load Japanese transliteration so the app can still start if fugashi is missing
_araboji_mapping = None
_japanese_to_arabic = None
_araboji_load_error = None


def load_araboji():
    global _araboji_mapping, _japanese_to_arabic, _araboji_load_error
    if _araboji_load_error is not None:
        raise _araboji_load_error
    if _japanese_to_arabic is None:
        try:
            from Araboji import japanese_to_arabic as _japan_func, load_mapping as _load_map
            _araboji_mapping = _load_map("mapping.xlsx")
            _japanese_to_arabic = _japan_func
        except Exception as exc:
            _araboji_load_error = exc
            raise
    return _japanese_to_arabic, _araboji_mapping


def araboji_text(text):
    func, mapping = load_araboji()
    return func(text, mapping)[1]


languages = {
    'aljamiado': convert_to_aljamiado,
    'xiaoerjing': lambda text: clean_string(combine_pinyin_with_tones(text)),
    'araboji': araboji_text,
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