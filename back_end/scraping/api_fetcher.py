import requests
import os
import json

def fetch_and_save_api(url, filename):
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    # Save to temporary apis directory (will be cleaned up after processing)
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'apis')
    os.makedirs(data_dir, exist_ok=True)
    out_path = os.path.join(data_dir, filename)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📥 API data from {url} saved to {out_path}")

# Example usage:
# fetch_and_save_api('https://api.example.com/data', 'example.json')