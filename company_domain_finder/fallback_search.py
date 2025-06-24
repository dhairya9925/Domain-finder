import requests
import json
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote


COMMON_TLDS = [
    ".com", ".io", ".net",".ai", ".biz", ".co", ".info", ".me", ".app",
    ".tech", ".dev", ".xyz", ".online", ".site", ".store", ".agency",
    ".in", ".us"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load override map
override_path = os.path.join(BASE_DIR, 'overrides.json')
if os.path.exists(override_path):
    with open(override_path) as f:
        OVERRIDES = json.load(f)
else:
    OVERRIDES = {}

# Optional: Your Bing API key
BING_API_KEY = "YOUR_BING_API_KEY_HERE"

def clean_company_name(name):
    suffixes = ['inc.', 'llc', 'corp.', 'co.', 'ltd.', 'inc', 'llc.', 'corporation']
    parts = name.lower().replace(',', '').split()
    parts = [p for p in parts if p not in suffixes]
    return ''.join(parts)  # e.g., 'GSquared Medical LLC' → 'gsquaredmedical'


def duckduckgo_search_domain(company, industry=None):
    print("Searching WEB")
    try:
        if industry:
            query = f"{company} {industry} industry"
        else:
            query = f"{company} "
        print(f"query: {query}")

        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        params = {
            "q": query,
            "kl": "us-en"
        }

        response = requests.get("https://html.duckduckgo.com/html/", headers=headers, params=params)
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("a", class_="result__a", limit=3)

        for result in results:
            href = result.get("href")
            if not href:
                continue

            raw = urlparse(href)
            query = parse_qs(raw.query)
            url = unquote(query.get("uddg", [""])[0])
            domain = urlparse(url).netloc.replace("www.", "")

            if any(ex in domain for ex in ["linkedin.com", "facebook.com", "twitter.com", "youtube.com"]):
                continue

            print(f"domain: {domain}")
            return domain
    except Exception as e:
        print(f"DuckDuckGo error: {e}")
        return None

def fallback_domain_guess(company, industry = None):
    # 1. Check override
    if company in OVERRIDES:
        return OVERRIDES[company]

    # 2. Try TLD combinations
    cleaned = clean_company_name(company)
    for ext in COMMON_TLDS:
        url = f"http://www.{cleaned}{ext}"
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                return url.replace("http://www.", "")
        except:
            continue

    # 3. DuckDuckGo Search fallback
    return duckduckgo_search_domain(company, industry=industry)
