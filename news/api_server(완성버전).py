import os
import re
import unicodedata
import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")

def _clean_text(text):
    if not text: return ""
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'\[\d+\]|\(\d+\)', '', text)
    text = re.sub(r'[\u2020\u2021\u00A0\*]', '', text)
    return text.strip()

def fetch_medals_from_web():
    try:
        url = "https://en.wikipedia.org/wiki/2026_Winter_Olympics_medal_table"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.content, "html.parser")
        
        table = soup.find("table", {"class": "wikitable"})
        if not table: return []

        rows = table.find_all("tr")[1:]
        all_countries = []

        for row in rows:
            cols = row.find_all(["td", "th"])
            if len(cols) < 4: continue

            country_name = ""
            for col in cols:
                a_tag = col.find("a")
                if a_tag and a_tag.get_text(strip=True):
                    name = _clean_text(a_tag.get_text(strip=True))
                    if "total" not in name.lower() and not name.isdigit():
                        country_name = name
                        break
            
            if not country_name: continue

            nums = []
            for col in cols:
                txt = re.sub(r'[^\d]', '', col.get_text(strip=True))
                if txt.isdigit():
                    nums.append(int(txt))
            
            if len(nums) >= 4:
                idx = 1 if len(nums) >= 5 else 0
                all_countries.append({
                    "country": country_name,
                    "gold": nums[idx],
                    "silver": nums[idx+1],
                    "bronze": nums[idx+2]
                })

        # 1. 성적순 정렬
        all_countries.sort(key=lambda x: (-x["gold"], -x["silver"], -x["bronze"]))
        
        # 2. 전체 순위 계산 (공동 순위 포함)
        ranked_list = []
        for i, item in enumerate(all_countries):
            if i > 0:
                prev = ranked_list[i-1]
                if (item["gold"] == prev["gold"] and 
                    item["silver"] == prev["silver"] and 
                    item["bronze"] == prev["bronze"]):
                    item["rank"] = prev["rank"]
                else:
                    item["rank"] = i + 1
            else:
                item["rank"] = 1
            ranked_list.append(item)

        # 3. 결과 필터링 (TOP 10 + 한국)
        top10 = ranked_list[:10]
        # 한국 찾기 (다양한 표기 대응)
        korea = next((it for it in ranked_list if any(name in it["country"] for name in ["South Korea", "Korea, South", "Republic of Korea"])), None)
        
        final_result = []
        # 한국이 이미 TOP 10에 있는지 확인
        korea_in_top10 = any(it["country"] == (korea["country"] if korea else "") for it in top10)

        for it in top10:
            is_it_korea = korea and it["country"] == korea["country"]
            final_result.append({
                **it,
                "is_korea": is_it_korea,
                "gold": str(it["gold"]),
                "silver": str(it["silver"]),
                "bronze": str(it["bronze"])
            })

        # 한국이 10위 밖이라면 11번째로 추가
        if korea and not korea_in_top10:
            final_result.append({
                **korea,
                "is_korea": True,
                "gold": str(korea["gold"]),
                "silver": str(korea["silver"]),
                "bronze": str(korea["bronze"])
            })
            
        return final_result

    except Exception as e:
        logger.error(f"Error: {e}")
        return []

@app.get("/medals")
async def get_medals():
    return await run_in_threadpool(fetch_medals_from_web)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_path, "index.html"))

app.mount("/static", StaticFiles(directory=static_path), name="static")

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    