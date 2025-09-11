import json
import asyncio
import logging

async def save_chunks_async(chunks, chunks_file):
    logger = logging.getLogger(__name__)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: json.dump(
            chunks,
            open(chunks_file, "w", encoding="utf-8"),
            ensure_ascii=False,
            indent=2
        )
    )
    logger.info(f"Saved {len(chunks)} chunks to {chunks_file}")
