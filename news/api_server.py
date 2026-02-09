from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
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

def _extract_country_from_row(row, country_idx):
    try:
        cells = row.find_all(["td", "th"])
        if country_idx is not None and country_idx < len(cells):
            cell = cells[country_idx]
            a = cell.find('a', href=True)
            if a and a.get_text(strip=True):
                return _clean_cell(a)
            fi = cell.find('span', class_='flagicon')
            if fi:
                nxt = fi.next_sibling
                if nxt and isinstance(nxt, str) and nxt.strip():
                    return nxt.strip()
                a2 = cell.find('a')
                if a2 and a2.get_text(strip=True):
                    return _clean_cell(a2)
            txt = _clean_cell(cell)
            if txt and not txt.isdigit():
                return txt
    except Exception:
        pass
    a = row.find('a', href=True)
    if a and a.get_text(strip=True):
        return _clean_cell(a)
    txt = _clean_cell(row)
    return txt if txt and not txt.isdigit() else ""

def _assign_ranks(medal_data):
    ranked = []
    for i, item in enumerate(medal_data):
        g = int(item.get("gold", 0))
        s = int(item.get("silver", 0))
        b = int(item.get("bronze", 0))
        if i == 0:
            rank = 1
        else:
            pg = int(medal_data[i-1]["gold"])
            ps = int(medal_data[i-1]["silver"])
            pb = int(medal_data[i-1]["bronze"])
            if g == pg and s == ps and b == pb:
                rank = ranked[i-1]["rank"]
            else:
                rank = i + 1
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
                    if p in h: return i
            return None

        country_idx = find_idx(["nation", "country", "team", "noc"])
        gold_idx = find_idx(["gold"])
        silver_idx = find_idx(["silver"])
        bronze_idx = find_idx(["bronze"])

        rows = table.find_all("tr")[1:]
        temp = []
        for row in rows:
            cols = row.find_all(["td", "th"])
            max_idx = max([i for i in (gold_idx, silver_idx, bronze_idx) if i is not None], default=-1)
            if len(cols) <= max_idx: continue

            country = _extract_country_from_row(row, country_idx)
            
            # [수정] 합계 행 제외 로직 추가
            if not country or "total" in country.lower():
                continue

            def safe_int_cell(idx):
                try:
                    text = _clean_cell(cols[idx]) if idx is not None and idx < len(cols) else "0"
                    return int(re.sub(r'[^\d]', '', text) or 0)
                except: return 0

            temp.append({
                "country": country,
                "gold": safe_int_cell(gold_idx),
                "silver": safe_int_cell(silver_idx),
                "bronze": safe_int_cell(bronze_idx)
            })

        temp_sorted = sorted(temp, key=lambda x: (-x["gold"], -x["silver"], -x["bronze"]))
        top10 = temp_sorted[:10]
        ranked = _assign_ranks(top10)

        for it in ranked:
            it["gold"], it["silver"], it["bronze"] = str(it["gold"]), str(it["silver"]), str(it["bronze"])

        logger.info("Fetched %d rows from web", len(ranked))
        return ranked
    except Exception:
        logger.exception("Error fetching medals from web")
        return []

def fetch_medals_from_local():
    try:
        medal_file = os.path.join(static_path, "medal.html")
        if not os.path.exists(medal_file): return []
        with open(medal_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        
        rows = soup.find_all("tr")
        medal_data = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 4:
                country = _clean_cell(cols[0])
                # [수정] 합계 행 제외 로직 추가
                if "total" in country.lower(): continue
                
                gold = int(re.sub(r'[^\d]', '', _clean_cell(cols[1]) or "0"))
                silver = int(re.sub(r'[^\d]', '', _clean_cell(cols[2]) or "0"))
                bronze = int(re.sub(r'[^\d]', '', _clean_cell(cols[3]) or "0"))
                medal_data.append({"country": country, "gold": gold, "silver": silver, "bronze": bronze})

        temp_sorted = sorted(medal_data, key=lambda x: (-x["gold"], -x["silver"], -x["bronze"]))
        top10 = temp_sorted[:10]
        ranked = _assign_ranks(top10)
        for it in ranked:
            it["gold"], it["silver"], it["bronze"] = str(it["gold"]), str(it["silver"]), str(it["bronze"])
        return ranked
    except Exception:
        logger.exception("Error reading local medal.html")
        return []

@app.get("/medals")
async def get_medals():
    global medal_cache
    now = datetime.now()
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
    if os.path.exists(index_file): return FileResponse(index_file)
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