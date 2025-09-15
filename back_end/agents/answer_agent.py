import os
import openai
from dotenv import load_dotenv
import asyncio
import logging
import re
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from weaviate_db import search_chunks
from .prompt_manager import PromptManager

# --- Configuration ---
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize prompt manager
prompt_manager = PromptManager()

# Model and API configuration
LLM_MODEL = prompt_manager.get_model_config('llm') or "gpt-5-chat-latest"
EMBEDDING_MODEL = prompt_manager.get_model_config('embedding') or "text-embedding-3-large"
SEARCH_TOP_K = prompt_manager.get_config('search_top_k') or 7
MAX_TOKENS_ANSWER = prompt_manager.get_config('max_tokens_answer') or 1500
MAX_TOKENS_TRANSLATE = prompt_manager.get_config('max_tokens_translate') or 150
TEMPERATURE_ANSWER = prompt_manager.get_config('temperature_answer') or 1.0
TEMPERATURE_TRANSLATE = prompt_manager.get_config('temperature_translate') or 1.0

logger = logging.getLogger(__name__)

# --- Core Functions ---

def detect_language(text):
    """Detects if the text is primarily Arabic or English."""
    return 'ar' if re.search(r'[\u0600-\u06FF]', text) else 'en'

async def call_openai_api(messages, model, max_tokens, temperature):
    """Generic async wrapper for OpenAI Chat Completions API."""
    loop = asyncio.get_event_loop()
    try:
        # Use max_completion_tokens for GPT-5 variants, max_tokens for other models
        token_param = "max_completion_tokens" if "gpt-5" in model else "max_tokens"
        kwargs = {
            "model": model,
            "messages": messages,
            token_param: max_tokens,
        }
        
        # Only add temperature parameter for non-GPT-5 models
        if "gpt-5" not in model:
            kwargs["temperature"] = temperature
        
        response = await loop.run_in_executor(
            None,
            lambda: openai.chat.completions.create(**kwargs)
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API call failed for model {model}: {e}")
        return None

async def translate_text(text, target_language):
    """Translates text to the target language using the LLM."""
    # Get translation prompt based on target language
    source_lang = 'ar' if target_language == 'en' else 'en'
    translation_prompt = prompt_manager.get_translation_prompt(source_lang).format(target_language=target_language)
    
    messages = [
        {"role": "system", "content": translation_prompt},
        {"role": "user", "content": text}
    ]
    return await call_openai_api(messages, LLM_MODEL, MAX_TOKENS_TRANSLATE, TEMPERATURE_TRANSLATE)

async def embed_query(question):
    """Generates an embedding for a given query."""
    loop = asyncio.get_event_loop()
    try:
        resp = await loop.run_in_executor(
            None,
            lambda: openai.embeddings.create(model=EMBEDDING_MODEL, input=[question])
        )
        return resp.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding failed for query '{question}': {e}")
        return None

async def search_and_combine_chunks(original_query, translated_query):
    """
    Performs vector search with both original and translated queries,
    then combines and deduplicates the results.
    """
    # Embed both queries concurrently
    original_embedding, translated_embedding = await asyncio.gather(
        embed_query(original_query),
        embed_query(translated_query)
    )
    
    # Search for chunks concurrently
    original_chunks, translated_chunks = await asyncio.gather(
        asyncio.to_thread(search_chunks, original_embedding, top_k=SEARCH_TOP_K),
        asyncio.to_thread(search_chunks, translated_embedding, top_k=SEARCH_TOP_K)
    )

    # Combine and deduplicate chunks
    combined = {chunk['properties']['text']: chunk for chunk in original_chunks}
    for chunk in translated_chunks:
        combined[chunk['properties']['text']] = chunk
        
    return list(combined.values())

async def answer_user_question_async(question):
    """
    Main pipeline to answer a user's question asynchronously.
    Returns a dictionary with the answer and a list of sources.
    """
    original_lang = detect_language(question)
    target_lang = 'ar' if original_lang == 'en' else 'en'
    
    translated_question = await translate_text(question, target_lang)
    if not translated_question:
        logger.warning(f"Translation failed for: {question}")
        return {
            "answer": prompt_manager.get_error_message('translation_failed', original_lang),
            "sources": []
        }

    all_chunks = await search_and_combine_chunks(question, translated_question)
    logger.info(f"Retrieved chunks: {all_chunks}")
    
    context_parts = []
    for chunk in all_chunks:
        source = chunk["properties"].get("source", "N/A")
        text = chunk["properties"].get("text", "")
        context_parts.append(f"Source: {source}\nContent: {text}")
    context_text = "\n\n---\n\n".join(context_parts)

    prompt = f"{context_text}\n\nQuestion: {question}\nAnswer:"
    logger.info(f"Full prompt sent to LLM: {prompt}")
    
    # Get system prompt in the user's language
    system_prompt = prompt_manager.get_system_prompt(original_lang)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    answer = await call_openai_api(messages, LLM_MODEL, MAX_TOKENS_ANSWER, TEMPERATURE_ANSWER)
    
    if not answer:
        return {
            "answer": prompt_manager.get_error_message('api_failed', original_lang),
            "sources": []
        }
        
    return {
        "answer": answer,
        "sources": list(set([chunk["properties"].get("source", "N/A") for chunk in all_chunks]))
    }
