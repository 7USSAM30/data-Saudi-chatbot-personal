import asyncio
import logging
import os
from scraping.scraper import scrape_site_async, scrape_api_data_async
from processing.chunking import chunk_data_async, save_chunks_async
from embedding.embedder import embed_chunks_async
from scraping.api_fetcher import fetch_and_save_api
from weaviate_db import upload_chunks_with_embeddings, create_schema
# If you want to allow user questions:
from agents.answer_agent import answer_user_question_async

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # 0. Create Weaviate schema if it doesn't exist
    create_schema()

    # 1. Fetch data from APIs in both English and Arabic
    endpoints = {
        "gastat_gdp_quarter": "https://api.datasaudi.sa/tesseract/data.jsonrecords?cube=gastat_gdp&drilldowns=Economic+Activity+Section,Quarter&measures=GDP",
        "gastat_gdp_year": "https://api.datasaudi.sa/tesseract/data.jsonrecords?cube=gastat_gdp&drilldowns=Economic+Activity+Section,Year&measures=GDP",
        "gastat_inflation_city_yoy": "https://api.datasaudi.sa/tesseract/data.jsonrecords?cube=gastat_inflation_city_yoy&drilldowns=Year,City&measures=Inflation,Consumer+Price+Index",
        "gastat_inflation_city_mom": "https://api.datasaudi.sa/tesseract/data.jsonrecords?cube=gastat_inflation_city_yoy&drilldowns=Month,City&measures=Inflation,Consumer+Price+Index",
        "gastat_wpi_city_yoy": "https://api.datasaudi.sa/tesseract/data.jsonrecords?cube=gastat_wpi_city_yoy&drilldowns=Year,City&measures=Wholesale%20Price%20Index%20Growth,Wholesale%20Price%20Index",
        "gastat_ipi_index_economic_activity": "https://api.datasaudi.sa/tesseract/data.jsonrecords?cube=gastat_ipi_index_economic_activity&drilldowns=Economic+Sectors,Month&measures=Industrial+Production+Index,Percentage+change",
        "pmi": "https://api.datasaudi.sa/tesseract/data.jsonrecords?cube=pmi&drilldowns=Month&measures=Purchasing+Manager+Index",
        "mof_government_revenues_expenditures_quarter": "https://api.datasaudi.sa/tesseract/data.jsonrecords?cube=mof_government_revenues_expenditures_quarter&drilldowns=Type,Quarter&measures=SAR+Billions",
        "sama_money_supply_year": "https://api.datasaudi.sa/tesseract/data.jsonrecords?cube=sama_money_supply_year&drilldowns=Year&measures=Million+SAR",
        "sama_money_supply_month": "https://api.datasaudi.sa/tesseract/data.jsonrecords?cube=sama_money_supply_month&drilldowns=Month&measures=Million+SAR"
    }

    for name, url in endpoints.items():
        # Fetch in English
        fetch_and_save_api(f"{url}&locale=en", f"{name}.en.json")
        # Fetch in Arabic
        fetch_and_save_api(f"{url}&locale=ar", f"{name}.ar.json")

    # 2. Scrape web and API
    html_chunks = await scrape_site_async()
    api_chunks = await scrape_api_data_async()
    all_chunks = html_chunks + api_chunks

    # 3. Chunk and Save
    chunks = await chunk_data_async(all_chunks)
    await save_chunks_async(chunks)

    # 4. Embed Chunks
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    CHUNKS_FILE = os.path.join(DATA_DIR, 'chunks.json')
    EMBEDDED_FILE = os.path.join(DATA_DIR, 'chunks_with_embeddings.json')
    await embed_chunks_async(CHUNKS_FILE, EMBEDDED_FILE)

    # 5. Upload to Weaviate Cloud
    logger.info("☁️ Uploading data to Weaviate Cloud...")
    upload_chunks_with_embeddings(EMBEDDED_FILE)
    
    # 6. Clean up local temporary files
    logger.info("🧹 Cleaning up local temporary files...")
    if os.path.exists(CHUNKS_FILE):
        os.remove(CHUNKS_FILE)
    if os.path.exists(EMBEDDED_FILE):
        os.remove(EMBEDDED_FILE)
    
    # Clean up API files
    apis_dir = os.path.join(DATA_DIR, 'apis')
    if os.path.exists(apis_dir):
        import shutil
        shutil.rmtree(apis_dir)
        logger.info("🗑️ Removed temporary API files")
    
    logger.info("✅ Pipeline finished! Ready for Q&A.")

if __name__ == "__main__":
    asyncio.run(main())
