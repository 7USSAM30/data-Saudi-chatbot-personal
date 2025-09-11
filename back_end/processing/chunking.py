import os
import json
import asyncio
import logging
import re

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
CHUNKS_FILE = os.path.join(DATA_DIR, 'chunks.json')

def detect_language(text):
    # Simple heuristic: if contains Arabic characters, label as 'ar', else 'en'
    if re.search(r'[\u0600-\u06FF]', text):
        return 'ar'
    return 'en'

def chunk_text(text, chunk_size=400):
    """Splits text into chunks of N words (default 400)."""
    words = text.split()
    return [
        " ".join(words[i:i+chunk_size])
        for i in range(0, len(words), chunk_size)
    ]

async def chunk_data_async(data, chunk_size=400):
    """
    Takes a list of dicts with 'source', 'text', and optional metadata keys,
    returns a list of unique chunked dicts with metadata and a score.
    """
    loop = asyncio.get_event_loop()
    def chunk_all():
        chunks = []
        seen = set()
        for item in data:
            source = item.get("source", "")
            text = item.get("text", "")
            year = item.get("year")
            ctype = item.get("type")
            language = detect_language(text)
            for chunk in chunk_text(text, chunk_size):
                chunk_dict = {
                    "source": source,
                    "text": chunk,
                    "language": language,
                    "score": 1.0
                }
                if year is not None:
                    chunk_dict["year"] = year
                if ctype is not None:
                    chunk_dict["type"] = ctype
                # Deduplication key: text + source + year + language + type
                dedup_key = (chunk, source, year, language, ctype)
                if dedup_key not in seen:
                    seen.add(dedup_key)
                    chunks.append(chunk_dict)
        return chunks
    return await loop.run_in_executor(None, chunk_all)

async def save_chunks_async(chunks):
    """
    Saves the chunks to the default CHUNKS_FILE as JSON.
    """
    logger = logging.getLogger(__name__)
    loop = asyncio.get_event_loop()
    def save():
        with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
    await loop.run_in_executor(None, save)
    logger.info(f"Saved {len(chunks)} chunks to {CHUNKS_FILE}")