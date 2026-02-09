from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from starlette.concurrency import run_in_threadpool
import logging
import re
import unicodedata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")

medal_cache = {"data": [], "last_update": None}
CACHE_SECONDS = 120

def _clean_cell(cell):
    for s in cell.find_all(['sup', 'span', 'small']):
        s.decompose()
    text = cell.get_text(separator=' ', strip=True)
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'\[\d+\]|\(\d+\)', '', text)
    text = re.sub(r'[\u2020\u2021\u00A0\*]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def _find_medal_table(soup):
    tables = soup.find_all("table")
    for t in tables:
        headers = [th.get_text(strip=True).lower() for th in t.find_all("th")]
        if any("gold" in h for h in headers) and any("silver" in h for h in headers) and any("bronze" in h for h in headers):
            return t
    return None

def _assign_ranks(medal_data):
    """메달 수가 같으면 같은 순위 부여"""
    ranked = []
    for i, item in enumerate(medal_data):
        gold = int(item["gold"])
        silver = int(item["silver"])
        bronze = int(item["bronze"])
        total = gold + silver + bronze
        
        # 같은 순위 찾기 (이전 항목과 메달 수 비교)
        if i == 0:
            rank = 1
        else:
            prev_gold = int(medal_data[i-1]["gold"])
            prev_silver = int(medal_data[i-1]["silver"])
            prev_bronze = int(medal_data[i-1]["bronze"])
            prev_total = prev_gold + prev_silver + prev_bronze
            
            # Gold > Silver > Bronze 순서로 비교
            if (gold == prev_gold and silver == prev_silver and bronze == prev_bronze):
                rank = ranked[i-1]["rank"]  # 같은 순위
            else:
                rank = i + 1  # 다른 순위
        
        item["rank"] = rank
        ranked.append(item)
    
    return ranked

def fetch_medals_from_web():
    try:
        url = "https://en.wikipedia.org/wiki/2026_Winter_Olympics_medal_table"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.content, "html.parser")

        table = _find_medal_table(soup)
        if not table:
            logger.warning("No medal table found on page")
            return []

        ths = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        def find_idx(preds):
            for i, h in enumerate(ths):
                for p in preds:
                    if p in h:
                        return i
            return None

        country_idx = find_idx(["nation", "country", "team", "noc", "nation/territory"])
        gold_idx = find_idx(["gold"])
        silver_idx = find_idx(["silver"])
        bronze_idx = find_idx(["bronze"])

        if country_idx is None and len(ths) >= 2:
            country_idx = 1

        rows = table.find_all("tr")[1:]
        medal_data = []
        for row in rows:
            cols = row.find_all(["td", "th"])
            max_idx = max(
                [i for i in (country_idx, gold_idx, silver_idx, bronze_idx) if i is not None],
                default=-1
            )
            if len(cols) <= max_idx:
                continue
            
            country = _clean_cell(cols[country_idx]) if country_idx is not None else _clean_cell(cols[0])
            
            # 숫자만 있거나 빈 국가명 스킵
            if not country or country.isdigit() or country.strip() == '':
                continue
            
            gold = _clean_cell(cols[gold_idx]) if gold_idx is not None else "0"
            silver = _clean_cell(cols[silver_idx]) if silver_idx is not None else "0"
            bronze = _clean_cell(cols[bronze_idx]) if bronze_idx is not None else "0"

            medal_data.append({
                "country": country,
                "gold": gold,
                "silver": silver,
                "bronze": bronze
            })
            if len(medal_data) >= 10:
                break

        # 순위 부여
        medal_data = _assign_ranks(medal_data)
        
        logger.info("Fetched %d rows from web", len(medal_data))
        return medal_data

    except Exception as e:
        logger.exception("Error fetching medals from web")
        return []

def fetch_medals_from_local():
    try:
        medal_file = os.path.join(static_path, "medal.html")
        if not os.path.exists(medal_file):
            return []
        with open(medal_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        rows = soup.find_all("tr", {"class": "country-row"})
        if not rows:
            rows = soup.find_all("tr")
        medal_data = []
        for row in rows[:10]:
            cols = row.find_all("td")
            if len(cols) >= 4:
                country = _clean_cell(cols[0])
                gold = _clean_cell(cols[1])
                silver = _clean_cell(cols[2])
                bronze = _clean_cell(cols[3])
                medal_data.append({"country": country, "gold": gold, "silver": silver, "bronze": bronze})
        
        # 순위 부여
        medal_data = _assign_ranks(medal_data)
        
        logger.info("Loaded %d rows from local file", len(medal_data))
        return medal_data
    except Exception:
        logger.exception("Error reading local medal.html")
        return []

@app.get("/medals")
async def get_medals():
    global medal_cache
    now = datetime.utcnow()
    last = medal_cache["last_update"]
    if last and (now - last).total_seconds() < CACHE_SECONDS and medal_cache["data"]:
        return medal_cache["data"]

    data = await run_in_threadpool(fetch_medals_from_web)
    if not data:
        data = await run_in_threadpool(fetch_medals_from_local)

    medal_cache["data"] = data
    medal_cache["last_update"] = now
    return data

@app.get("/")
async def read_index():
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"error": "index.html not found"}

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "medals_cached": len(medal_cache["data"]) > 0,
        "last_update": medal_cache["last_update"].isoformat() if medal_cache["last_update"] else None
    }

app.mount("/static", StaticFiles(directory=static_path), name="static")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000)
