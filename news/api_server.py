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

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="2026 Winter Olympics Medal API")

# CORS 설정: 프론트엔드에서 API 접근이 가능하도록 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 경로 설정: /static 폴더 경로 (슬래시 주의!)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")

# 텍스트 정제 함수
def _clean_text(text):
    if not text: return ""
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'\[\d+\]|\(\d+\)', '', text)
    text = re.sub(r'[\u2020\u2021\u00A0\*]', '', text)
    return text.strip()

# 위키피디아에서 메달 데이터 크롤링
def fetch_medals_from_web():
    try:
        url = "https://en.wikipedia.org/wiki/2026_Winter_Olympics_medal_table"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.content, "html.parser")
        
        # 'wikitable' 클래스를 가진 테이블 찾기
        table = soup.find("table", {"class": "wikitable"})
        if not table: 
            logger.warning("Medal table not found.")
            return []

        rows = table.find_all("tr")[1:]
        temp_list = []

        for row in rows:
            cols = row.find_all(["td", "th"])
            if len(cols) < 4: continue

            # 국가 이름 추출 (첫 번째 <a> 태그 기준)
            country_name = ""
            for col in cols:
                a_tag = col.find("a")
                if a_tag and a_tag.get_text(strip=True):
                    name = _clean_text(a_tag.get_text(strip=True))
                    # 'Total' 행이나 숫자로만 된 행 제외
                    if "total" not in name.lower() and not name.isdigit():
                        country_name = name
                        break
            
            if not country_name: continue

            # 숫자 데이터(금, 은, 동) 추출
            nums = []
            for col in cols:
                txt = re.sub(r'[^\d]', '', col.get_text(strip=True))
                if txt.isdigit():
                    nums.append(int(txt))
            
            # [순위, 금, 은, 동, 합계] 구조 대응
            if len(nums) >= 4:
                # 첫 번째 숫자가 순위인 경우 인덱스 1부터, 아니면 0부터 시작
                idx = 1 if len(nums) >= 5 else 0
                temp_list.append({
                    "country": country_name,
                    "gold": nums[idx],
                    "silver": nums[idx+1],
                    "bronze": nums[idx+2]
                })

        # 1. 메달 성적순 정렬 (금 > 은 > 동)
        temp_list.sort(key=lambda x: (-x["gold"], -x["silver"], -x["bronze"]))
        
        # 2. 공동 순위 로직 적용 및 상위 10개 추출
        ranked = []
        for i, item in enumerate(temp_list[:10]):
            if i > 0:
                prev = ranked[i-1]
                if (item["gold"] == int(prev["gold"]) and 
                    item["silver"] == int(prev["silver"]) and 
                    item["bronze"] == int(prev["bronze"])):
                    item["rank"] = prev["rank"]
                else:
                    item["rank"] = i + 1
            else:
                item["rank"] = 1
            
            # JSON 반환을 위해 숫자를 문자열로 변환 (기존 코드 유지)
            item["gold"] = str(item["gold"])
            item["silver"] = str(item["silver"])
            item["bronze"] = str(item["bronze"])
            ranked.append(item)
            
        return ranked

    except Exception as e:
        logger.error(f"Error fetching medals: {e}")
        return []

# --- API Endpoints ---

@app.get("/medals")
async def get_medals():
    """실시간 메달 순위 데이터 반환"""
    return await run_in_threadpool(fetch_medals_from_web)

@app.get("/health")
async def health_check():
    """서버 상태 확인용 엔드포인트"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "info": "2026 Winter Olympics Medal Server"
    }

@app.get("/")
async def read_index():
    """메인 페이지(index.html) 반환"""
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "index.html not found in static folder"}

# 정적 파일 서빙 (CSS, JS, 이미지 등)
app.mount("/static", StaticFiles(directory=static_path), name="static")

if __name__ == '__main__':
    import uvicorn
    # 외부 접속 허용을 위해 0.0.0.0으로 실행
    uvicorn.run(app, host="0.0.0.0", port=8000)