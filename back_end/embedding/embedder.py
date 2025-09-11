# embedding/embedder.py

import openai
import json
import asyncio
import logging
import os
from dotenv import load_dotenv

# Load .env file from the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

openai.api_key = os.getenv("OPENAI_API_KEY")

async def embed_chunks_async(chunks_file, embedded_file, batch_size=256, delay_between_batches=0.6):
    logger = logging.getLogger(__name__)
    loop = asyncio.get_event_loop()
    with open(chunks_file, encoding='utf-8') as f:
        chunks = json.load(f)
    embedded_chunks = []
    texts_batch = []
    metas_batch = []

    async def batch_embed_texts(texts, model="text-embedding-3-large"):
        for _ in range(3):
            try:
                response = await loop.run_in_executor(None, lambda: openai.embeddings.create(model=model, input=texts))
                return [emb.embedding for emb in response.data]
            except Exception as e:
                logger.warning(f"Batch embedding error, retrying: {e}")
                await asyncio.sleep(2)
        return [None for _ in texts]

    for i, chunk in enumerate(chunks):
        texts_batch.append(chunk["text"])
        metas_batch.append(chunk)
        if len(texts_batch) == batch_size or i == len(chunks) - 1:
            embeddings = await batch_embed_texts(texts_batch)
            for meta, emb in zip(metas_batch, embeddings):
                meta["embedding"] = emb
                embedded_chunks.append(meta)
            logger.info(f"Embedded {len(embedded_chunks)}/{len(chunks)}")
            texts_batch, metas_batch = [], []
            await asyncio.sleep(delay_between_batches)

    with open(embedded_file, "w", encoding="utf-8") as f:
        json.dump(embedded_chunks, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved all embedded chunks to {embedded_file}")
