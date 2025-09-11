import os
import json
import logging
import requests
from bs4 import BeautifulSoup
import asyncio
from urllib.parse import urljoin, urlparse
import collections

logger = logging.getLogger(__name__)

# --- Configuration ---
REQUEST_HEADERS = {
    'User-Agent': 'DataSaudiChatbot/1.0 (https://datasaudi.sa; mailto:admin@example.com)'
}
MAX_PAGES_TO_CRAWL = 20 # Safety limit for the crawler

# --- HTML Scraping (Crawler) ---

def canonicalize_url(base_url, link):
    """Resolves a link and cleans it for crawling by removing URL fragments."""
    full_url = urljoin(base_url, link)
    parsed = urlparse(full_url)
    return parsed._replace(fragment="").geturl()

async def scrape_site_async(start_url="https://datasaudi.sa/en/"):
    """
    Crawls a website starting from a given URL, scraping text and table data
    up to a maximum number of pages.
    """
    loop = asyncio.get_event_loop()
    all_chunks = []
    
    domain = urlparse(start_url).netloc
    # Use a deque for an efficient queue and a set to track all seen URLs
    urls_to_visit = collections.deque([start_url])
    visited_urls = {start_url}
    pages_crawled = 0

    while urls_to_visit and pages_crawled < MAX_PAGES_TO_CRAWL:
        url = urls_to_visit.popleft()
        pages_crawled += 1
        logger.info(f"Scraping page {pages_crawled}/{MAX_PAGES_TO_CRAWL}: {url}")

        try:
            response = await loop.run_in_executor(
                None, 
                lambda: requests.get(url, headers=REQUEST_HEADERS, timeout=10)
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            # --- Extract meaningful content ---
            if soup.title and soup.title.string:
                all_chunks.append({"source": url, "text": f"[TITLE] {soup.title.string.strip()}"})
            
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                all_chunks.append({"source": url, "text": f"[DESC] {meta_desc.get('content').strip()}"})

            for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'li']):
                text = tag.get_text(strip=True)
                if len(text) > 25:
                    all_chunks.append({"source": url, "text": text})

            for table in soup.find_all("table"):
                for row in table.find_all("tr"):
                    cells = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
                    if cells and any(cells):
                        text = " | ".join(cells)
                        all_chunks.append({"source": url, "text": f"[TABLE] {text}"})

            # --- Find new links to crawl ---
            for a_tag in soup.find_all("a", href=True):
                new_url = canonicalize_url(url, a_tag['href'])
                if urlparse(new_url).netloc == domain and new_url not in visited_urls:
                    visited_urls.add(new_url)
                    urls_to_visit.append(new_url)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
        except Exception as e:
            logger.error(f"An error occurred while scraping {url}: {e}")

    if pages_crawled >= MAX_PAGES_TO_CRAWL:
        logger.warning(f"Crawler reached max page limit of {MAX_PAGES_TO_CRAWL}.")
        
    logger.info(f"Total HTML chunks scraped from {pages_crawled} pages: {len(all_chunks)}")
    return all_chunks

# --- API Data Formatting ---

def format_gdp(row, lang):
    time_period = row.get('Quarter') or row.get('Year', 'N/A')
    if lang == 'ar':
        return (f"الناتج المحلي الإجمالي للنشاط الاقتصادي '{row.get('Economic Activity Section', 'غير متاح')}' "
                f"في {time_period} كان {row.get('GDP', 'غير متاح')}.")
    return (f"The Gross Domestic Product (GDP) for the economic activity '{row.get('Economic Activity Section', 'N/A')}' "
            f"in {time_period} was {row.get('GDP', 'N/A')}.")

def format_inflation(row, lang):
    time_period = row.get('Month') or row.get('Year', 'N/A')
    if lang == 'ar':
        return (f"في مدينة '{row.get('City', 'غير متاح')}' لفترة {time_period}, "
                f"كان الرقم القياسي لأسعار المستهلك {row.get('Consumer Price Index', 'غير متاح')} "
                f"بمعدل تضخم {row.get('Inflation', 'غير متاح')}%.")
    return (f"In {row.get('City', 'N/A')} for the period {time_period}, "
            f"the Consumer Price Index was {row.get('Consumer Price Index', 'N/A')} "
            f"with an inflation rate of {row.get('Inflation', 'N/A')}%.")

def format_pmi(row, lang):
    if lang == 'ar':
        return f"مؤشر مديري المشتريات (PMI) لشهر {row.get('Month', 'غير متاح')} كان {row.get('Purchasing Manager Index', 'غير متاح')}."
    return f"The Purchasing Manager Index (PMI) for {row.get('Month', 'N/A')} was {row.get('Purchasing Manager Index', 'N/A')}."

def format_wpi(row, lang):
    if lang == 'ar':
        return (f"في مدينة '{row.get('City', 'غير متاح')}' لسنة {row.get('Year', 'غير متاح')}, "
                f"كان مؤشر أسعار الجملة {row.get('Wholesale Price Index', 'غير متاح')} "
                f"بنسبة نمو {row.get('Wholesale Price Index Growth', 'غير متاح')}%.")
    return (f"In {row.get('City', 'N/A')} for the year {row.get('Year', 'N/A')}, "
            f"the Wholesale Price Index was {row.get('Wholesale Price Index', 'N/A')} "
            f"with a growth of {row.get('Wholesale Price Index Growth', 'N/A')}%.")

def format_ipi(row, lang):
    if lang == 'ar':
        return (f"بالنسبة للقطاعات الاقتصادية '{row.get('Economic Sectors', 'غير متاح')}' لشهر {row.get('Month', 'غير متاح')}, "
                f"كان مؤشر الإنتاج الصناعي {row.get('Industrial Production Index', 'غير متاح')} "
                f"بنسبة تغير {row.get('Percentage change', 'غير متاح')}%.")
    return (f"For the economic sector '{row.get('Economic Sectors', 'N/A')}' for the month {row.get('Month', 'N/A')}, "
            f"the Industrial Production Index was {row.get('Industrial Production Index', 'N/A')} "
            f"with a percentage change of {row.get('Percentage change', 'N/A')}%.")
            
def format_gov_finance(row, lang):
    if lang == 'ar':
        return (f"البيانات المالية الحكومية للربع '{row.get('Quarter', 'غير متاح')}' "
                f"تظهر أن '{row.get('Type', 'غير متاح')}' بلغت {row.get('SAR Billions', 'غير متاح')} مليار ريال سعودي.")
    return (f"Government finance data for quarter '{row.get('Quarter', 'N/A')}' "
            f"shows that '{row.get('Type', 'N/A')}' was {row.get('SAR Billions', 'N/A')} billion SAR.")

def format_money_supply(row, lang):
    time_period = row.get('Month') or row.get('Year', 'N/A')
    if lang == 'ar':
        return f"عرض النقود للفترة {time_period} بلغ {row.get('Million SAR', 'غير متاح')} مليون ريال سعودي."
    return f"Money supply for the period {time_period} was {row.get('Million SAR', 'N/A')} million SAR."

API_FORMATTERS = {
    'gastat_gdp': format_gdp,
    'gastat_inflation': format_inflation,
    'gastat_wpi': format_wpi,
    'gastat_ipi': format_ipi,
    'pmi': format_pmi,
    'mof_government': format_gov_finance,
    'sama_money_supply': format_money_supply,
}

# --- API Scraping ---
async def scrape_api_data_async():
    api_chunks = []
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'apis'))
    
    if not os.path.exists(data_dir):
        return []

    for filename in os.listdir(data_dir):
        if not filename.endswith('.json'):
            continue
            
        file_path = os.path.join(data_dir, filename)
        logger.info(f"Loading API data from {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            records = data.get('data', [])
            lang = 'ar' if '.ar.json' in filename else 'en'
            formatter = next((func for key, func in API_FORMATTERS.items() if key in filename), None)

            for row in records:
                if not isinstance(row, dict):
                    continue
                
                if formatter:
                    text = formatter(row, lang)
                else:
                    text = " | ".join([f"{k}: {v}" for k, v in row.items()])
                
                if text:
                    api_chunks.append({"source": filename, "text": text})

        except Exception as ex:
            logger.error(f"Failed to process {file_path}: {ex}")

    logger.info(f"Total API indicator chunks processed: {len(api_chunks)}")
    return api_chunks
