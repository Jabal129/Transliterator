"""
FastAPI backend for the Arabic Transliterator web app.

Run with:
    uvicorn main:app --reload --port 8000

Dependencies:
    pip install fastapi uvicorn python-multipart pandas openpyxl
    pip install fugashi pykakasi unidic-lite
    pip install python-telegram-bot nest_asyncio
    # Your local modules: Aljamiado, Xiaoerjing, Araboji, Soagyeong, Tieunhikinh
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from Araboji import japanese_to_arabic, load_mapping
from Xiaoerjing import combine_pinyin_with_tones, clean_string
from Aljamiado import convert_to_aljamiado
from Soagyeong import korean_to_arabic, adjust_arabic_output
from Tieunhikinh import transliterate_vietnamese_to_arabic


# ---------------------------------------------------------------------------
# Startup: load heavy resources once
# ---------------------------------------------------------------------------

mapping: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mapping
    mapping_path = os.getenv("MAPPING_PATH", "mapping.xlsx")
    try:
        mapping = load_mapping(mapping_path)
        print(f"[startup] Loaded {len(mapping)} romaji→Arabic entries from {mapping_path}")
    except FileNotFoundError:
        print(f"[startup] WARNING: {mapping_path} not found — Japanese transliteration will fail.")
    yield
    # (cleanup on shutdown goes here if needed)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Arabic Transliterator API",
    description="Transliterate Spanish, Chinese, Japanese, Korean, Vietnamese → Arabic script.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Transliterators registry
# ---------------------------------------------------------------------------

SUPPORTED_LANGUAGES = {
    "الإسبانية",
    "الصينية",
    "اليابانية",
    "الكورية",
    "الفيتنامية",
}


def transliterate_chinese(text: str) -> str:
    return clean_string(combine_pinyin_with_tones(text))


def transliterate_korean(text: str) -> str:
    return adjust_arabic_output(korean_to_arabic(text))


def transliterate_japanese(text: str) -> str:
    if not mapping:
        raise RuntimeError("mapping.xlsx was not loaded at startup.")
    result = japanese_to_arabic(text, mapping)
    return result[1]


def get_transliterator(language: str):
    transliterators = {
        "الإسبانية":   convert_to_aljamiado,
        "الصينية":    transliterate_chinese,
        "اليابانية":  transliterate_japanese,
        "الكورية":    transliterate_korean,
        "الفيتنامية": transliterate_vietnamese_to_arabic,
    }
    return transliterators.get(language)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TransliterateRequest(BaseModel):
    text: str
    language: str

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("text must not be empty.")
        if len(v) > 5000:
            raise ValueError("text must be 5000 characters or fewer.")
        return v

    @field_validator("language")
    @classmethod
    def language_supported(cls, v: str) -> str:
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language '{v}'. Choose from: {', '.join(SUPPORTED_LANGUAGES)}")
        return v


class TransliterateResponse(BaseModel):
    result: str
    language: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health", tags=["meta"])
def health():
    """Quick liveness check used by the frontend status indicator."""
    return {"status": "ok", "mapping_loaded": bool(mapping)}


@app.get("/languages", tags=["meta"])
def languages():
    """Return the list of supported languages."""
    return {"languages": sorted(SUPPORTED_LANGUAGES)}


@app.post("/transliterate", response_model=TransliterateResponse, tags=["core"])
def transliterate(req: TransliterateRequest):
    """
    Transliterate text from the given language into Arabic script.
    """
    fn = get_transliterator(req.language)
    if fn is None:
        raise HTTPException(status_code=400, detail=f"Language '{req.language}' is not supported.")

    try:
        result = fn(req.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transliteration failed: {exc}") from exc

    return TransliterateResponse(result=result, language=req.language)